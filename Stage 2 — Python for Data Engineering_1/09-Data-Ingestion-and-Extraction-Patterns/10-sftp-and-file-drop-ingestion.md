# SFTP and File-Drop Ingestion

> **Module:** Data Ingestion and Extraction Patterns  
> **Topic:** SFTP and File-Drop Ingestion  
> **Audience:** Beginner → Production Data Engineer  
> **Python:** 3.12+  
> **Focus:** Reliable ingestion from partner-managed SFTP servers, secure file drops, completeness, idempotency, validation, quarantine, archiving, and operational recovery

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- Explain what SFTP is and why it is still common in data engineering.
- Distinguish SFTP from FTP, FTPS, SCP, and ordinary HTTP downloads.
- Explain the difference between an SFTP transport and a file-drop ingestion contract.
- Identify the components of a production file-drop pipeline.
- Design a safe remote-directory discovery process.
- Download files without corrupting or partially processing them.
- Distinguish a file that is visible from a file that is complete.
- Use naming conventions, manifest files, marker files, and size stability to reason about completeness.
- Build idempotent file ingestion.
- Maintain a durable file-processing ledger.
- Generate stable file identities and avoid duplicate ingestion.
- Validate file size, checksum, extension, schema, encoding, and record counts.
- Quarantine malformed or suspicious files.
- Archive successfully processed files.
- Explain retention and replay requirements.
- Handle partial downloads and interrupted transfers.
- Handle duplicate filenames and repeated partner deliveries.
- Handle late-arriving files.
- Handle out-of-order files.
- Handle missing files.
- Handle empty files.
- Handle zero-byte and truncated files.
- Understand atomic local writes.
- Understand why remote rename is useful for producer-side atomic publication.
- Design a landing → validation → processing → archive lifecycle.
- Separate transport concerns from data-quality concerns.
- Implement an SFTP client abstraction in Python.
- Test SFTP ingestion without requiring a live partner server.
- Instrument file-drop ingestion with useful metadata.
- Design alerting for operational failures.
- Build reconciliation checks for expected deliveries.
- Design backfills and replay.
- Explain security requirements for SSH keys, host-key verification, credentials, and secret handling.
- Reason about concurrent consumers and locking.
- Defend an SFTP/file-drop architecture in a production design review.

The goal is not merely:

```text
"Download a file from SFTP."
```

The goal is:

```text
Discover
    ↓
Prove complete
    ↓
Acquire safely
    ↓
Identify deterministically
    ↓
Validate
    ↓
Land durably
    ↓
Process exactly-once-in-effect
    ↓
Archive/quarantine
    ↓
Record metadata
    ↓
Reconcile
    ↓
Alert and recover
```

---

# 2. Prerequisites

This chapter assumes familiarity with:

- Python functions and classes.
- Exceptions.
- Context managers.
- File paths.
- JSON and CSV concepts.
- HTTP ingestion fundamentals.
- Retries and timeouts.
- Idempotency.
- Incremental extraction.
- Watermarks.
- Raw/bronze landing.
- Basic SQL.

The focus here is specifically on **file-drop ingestion**.

It does not attempt to re-teach HTTP authentication, API pagination, CDC, or web scraping.

---

# 3. What Is SFTP?

SFTP means:

> **SSH File Transfer Protocol**

It is a file-transfer protocol that operates over SSH.

SFTP provides:

- Encrypted transport.
- Authentication.
- Remote directory operations.
- File upload/download.
- File metadata.
- Rename operations.
- Directory creation.
- File deletion, subject to permissions.

A typical architecture is:

```text
Partner System
      │
      │ SFTP over SSH
      ▼
SFTP Server
      │
      │ download
      ▼
Your Ingestion Pipeline
      │
      ▼
Raw Landing
      │
      ▼
Validation / Processing
      │
      ▼
Warehouse / Lake / Lakehouse
```

SFTP is particularly common when organizations exchange:

- Financial files.
- Healthcare files.
- Insurance data.
- Payroll data.
- Banking reports.
- Logistics files.
- EDI-related payloads.
- Regulatory reports.
- Legacy enterprise exports.
- Daily batch extracts.

---

# 4. SFTP vs FTP vs FTPS vs SCP

These technologies are related but not interchangeable.

| Technology | Security/Transport | Typical Role |
|---|---|---|
| FTP | Plain FTP protocol | Legacy; generally unsuitable for sensitive data |
| FTPS | FTP over TLS | Secure FTP variant |
| SFTP | SSH File Transfer Protocol | Common secure file-drop integration |
| SCP | Secure copy over SSH | Simple file copying, less suited to rich directory workflows |
| HTTPS | HTTP over TLS | API/file download over web protocols |

Do not assume:

```text
SFTP = FTP + encryption
```

SFTP is a different protocol.

---

# 5. What Is a File Drop?

A file drop is a delivery contract:

```text
Producer
   ↓
creates file
   ↓
publishes file
   ↓
consumer discovers file
   ↓
consumer validates and processes file
```

The important concept is that **transport and delivery semantics are separate**.

SFTP answers:

> How do we transfer the bytes?

The file-drop contract answers:

> How do we know which bytes represent a valid business delivery?

For example:

```text
Transport:
SFTP

Delivery:
daily customer file

Expected:
one file per business day

Name:
customers_YYYYMMDD.csv

Completeness:
producer publishes .ready marker

Validation:
SHA-256 + schema + row count

After success:
move to archive
```

This contract is far more important than merely knowing how to call an SFTP library.

---

# 6. Typical Production Architecture

A robust pipeline often looks like:

```text
                    ┌─────────────────────┐
                    │ Partner Application │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Partner SFTP Server │
                    └──────────┬──────────┘
                               │
                         discovery
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Ingestion Worker    │
                    └──────────┬──────────┘
                               │
                     download to temp
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Raw Landing         │
                    └──────────┬──────────┘
                               │
                         validation
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
             VALID FILE               INVALID FILE
                  │                         │
                  ▼                         ▼
             Processing                Quarantine
                  │
                  ▼
             Target Storage
                  │
                  ▼
               Archive
```

Each stage has a distinct responsibility.

---

# 7. The Most Important SFTP Question

A common beginner design is:

```python
for filename in sftp.listdir():
    download(filename)
    process(filename)
```

This is not enough for production.

The pipeline needs to answer:

> **How do I know the producer has finished writing the file?**

This is one of the central problems of file-drop ingestion.

---

# 8. The Partial-File Problem

Imagine the producer is writing:

```text
customers_20261001.csv
```

The file starts at:

```text
0 bytes
```

Then:

```text
100 MB
200 MB
300 MB
...
```

Your ingestion process sees the filename while the producer is still writing.

If you immediately download it:

```text
Producer
  │
  ├── writing
  │
  ▼
SFTP file visible
  │
  ▼
Consumer downloads partial content
```

The result can be:

- Truncated CSV.
- Invalid Parquet.
- Incomplete JSON.
- Missing rows.
- Corrupted ZIP.
- Incorrect checksum.
- Partial business data.

The key principle is:

> **File visibility does not prove file completeness.**

---

# 9. File Completeness Signals

Common mechanisms include:

1. Temporary filename.
2. Atomic remote rename.
3. Marker/ready file.
4. Manifest file.
5. Checksum.
6. Expected file size.
7. Stable size over time.
8. Source-provided record count.
9. Completion timestamp.
10. Partner-specific delivery protocol.

These vary in reliability.

---

# 10. Temporary Filename + Rename

A producer can write:

```text
customers_20261001.csv.part
```

Then, after the write completes:

```text
customers_20261001.csv.part
        ↓
customers_20261001.csv
```

The consumer only processes:

```text
*.csv
```

This creates a clean publication boundary.

Conceptually:

```text
Producer:

write temporary file
       ↓
flush/close
       ↓
rename
       ↓
published final filename
```

This is often much safer than watching file size.

---

# 11. Why Rename Is Powerful

A rename can act as a logical commit marker.

Instead of:

```text
"the file probably stopped changing"
```

the consumer gets:

```text
"the producer explicitly published this file"
```

This is a stronger contract.

However, correctness depends on the filesystem/server semantics and on the producer actually following the protocol.

---

# 12. Marker Files

Another common pattern:

```text
customers_20261001.csv
customers_20261001.ready
```

The producer creates the data file first.

After successful completion:

```text
create .ready
```

Consumer logic:

```text
if data_file.exists() and ready_file.exists():
    process(data_file)
```

The marker should be generated only after the producer considers the data complete.

---

# 13. Manifest Files

For multi-file deliveries, a manifest is often stronger.

Example:

```text
manifest_20261001.json
```

```json
{
  "delivery_date": "2026-10-01",
  "files": [
    {
      "name": "customers_20261001.csv",
      "size_bytes": 123456789,
      "sha256": "..."
    },
    {
      "name": "orders_20261001.csv",
      "size_bytes": 987654321,
      "sha256": "..."
    }
  ]
}
```

Now the consumer can verify:

```text
expected file
+
expected size
+
expected checksum
```

This is much stronger than:

```text
"there are some files in the directory."
```

---

# 14. Checksum Validation

A checksum creates content identity.

For SHA-256:

```python
import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()
```

The function reads incrementally rather than loading the entire file into memory.

For a large file:

```text
2 GB file
+
1 MB chunks
=
bounded application memory
```

Checksum validation can detect:

- Truncation.
- Corruption.
- Wrong file content.
- Incorrect delivery.
- Unexpected replacement.

---

# 15. File Size Validation

A manifest might specify:

```text
size_bytes = 123456789
```

After download:

```python
actual_size = local_path.stat().st_size

if actual_size != expected_size:
    raise ValueError("Downloaded file size does not match manifest")
```

Size alone is weaker than a cryptographic checksum.

Two different files can have the same size.

Use:

```text
size + checksum
```

when the delivery contract provides both.

---

# 16. Stable-Size Checking

If the partner does not provide a marker, one fallback is to observe whether the remote file size remains unchanged.

Conceptually:

```text
observe size at T0
       ↓
wait
       ↓
observe size at T1
       ↓
same size?
       ↓
candidate for processing
```

Example:

```python
def size_is_stable(first: int, second: int) -> bool:
    return first == second
```

This is weaker than an explicit producer-side publication protocol.

A file can stop growing temporarily and then continue.

Therefore:

> **Stable size is a heuristic, not proof of completeness.**

---

# 17. Preferred Completeness Hierarchy

When possible, prefer stronger signals:

```text
Strongest
    │
    ├── Explicit manifest + checksum
    ├── Explicit ready/complete marker
    ├── Atomic final-name publication
    ├── Producer-provided expected size/checksum
    ├── Stable size over a contract-defined interval
    └── "File has existed for N minutes"
Weakest
```

The exact ordering can depend on the partner protocol.

The engineering lesson is:

> Use an explicit producer contract whenever possible.

---

# 18. Remote Directory Discovery

Discovery should be deterministic.

Avoid blindly processing every file.

Instead define:

```text
allowed directory
allowed filename pattern
allowed extension
expected delivery frequency
expected date range
excluded temporary suffixes
```

For example:

```text
/inbound/customers/
    customers_20261001.csv
    customers_20261001.csv.ready
    customers_20261001.csv.part
```

Consumer rule:

```text
process *.csv only when matching .ready exists
ignore *.part
ignore unrelated files
```

---

# 19. Filename Validation

A production pipeline should validate filenames.

Example:

```python
import re

PATTERN = re.compile(
    r"^customers_(?P<date>\d{8})\.csv$"
)


def parse_filename(filename: str) -> str:
    match = PATTERN.fullmatch(filename)

    if match is None:
        raise ValueError(f"Unexpected filename: {filename}")

    return match.group("date")
```

This prevents accidental processing of:

```text
customers_backup.csv
customers_test.csv
notes.txt
customers_20261001.csv.part
```

---

# 20. Never Trust Filename Metadata Alone

A filename may say:

```text
customers_20261001.csv
```

but the file contents could contain:

```text
2026-09-30
```

or:

```text
2026-10-02
```

The pipeline should validate the relationship between:

```text
filename
+
manifest
+
content
+
delivery expectation
```

Filename parsing is metadata extraction, not proof of correctness.

---

# 21. SFTP Authentication

Common authentication methods include:

- SSH username + password.
- SSH private key.
- Private key protected by passphrase.
- SSH agent.
- Managed identity/secrets integration where supported by the environment.

For production:

> Prefer key-based authentication when supported by the partner and security policy.

Never embed credentials in source code.

### BAD

```python
password = "partner-password-123"
```

### BETTER

```python
import os

password = os.environ["SFTP_PASSWORD"]
```

Even environment variables should be managed through a proper secret-management mechanism in production.

---

# 22. SSH Host-Key Verification

Authentication answers:

> Who are we?

Host-key verification answers:

> Are we connecting to the expected server?

Do not disable host-key verification merely because development is inconvenient.

### BAD

```text
Auto-accept every unknown host key.
```

This weakens protection against connecting to the wrong server.

Production systems should establish trusted host keys according to organizational security policy.

---

# 23. Secret Handling

Secrets include:

- Passwords.
- Private-key passphrases.
- API tokens used by auxiliary services.
- Cloud credentials.
- SSH keys.

Never log:

```text
password=...
private_key=...
secret=...
```

Avoid logging connection URLs that embed credentials.

Good logs:

```text
Connecting to SFTP host=partner.example.com port=22
```

Bad logs:

```text
sftp://user:password@partner.example.com:22
```

---

# 24. Python SFTP Libraries

Common Python options include:

- Paramiko.
- AsyncSSH for asynchronous SSH/SFTP workflows.
- Higher-level wrappers built around SSH/SFTP libraries.

This chapter uses **Paramiko** for synchronous examples because it is widely used and makes the transport concepts explicit.

Install:

```bash
python -m pip install paramiko
```

A production project should pin dependencies according to its dependency-management policy.

---

# 25. Basic Paramiko Connection

```python
import paramiko

client = paramiko.SSHClient()

client.load_system_host_keys()
client.connect(
    hostname="partner.example.com",
    port=22,
    username="ingestion",
    key_filename="/secure/path/id_ed25519",
)

sftp = client.open_sftp()

try:
    print(sftp.listdir("/inbound"))
finally:
    sftp.close()
    client.close()
```

The important lifecycle is:

```text
SSH client
   ↓
SFTP session
   ↓
operations
   ↓
close SFTP
   ↓
close SSH
```

Use context-manager patterns or structured cleanup in production.

---

# 26. A Reusable SFTP Client

A simple abstraction:

```python
from __future__ import annotations

from pathlib import Path
from typing import Iterator

import paramiko


class SFTPClient:
    def __init__(
        self,
        *,
        hostname: str,
        username: str,
        key_filename: str,
        port: int = 22,
    ) -> None:
        self.hostname = hostname
        self.username = username
        self.key_filename = key_filename
        self.port = port
        self._ssh: paramiko.SSHClient | None = None
        self._sftp: paramiko.SFTPClient | None = None

    def connect(self) -> None:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()

        ssh.connect(
            hostname=self.hostname,
            port=self.port,
            username=self.username,
            key_filename=self.key_filename,
        )

        self._ssh = ssh
        self._sftp = ssh.open_sftp()

    def close(self) -> None:
        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None

    def list_files(self, remote_dir: str) -> list[str]:
        if self._sftp is None:
            raise RuntimeError("SFTP client is not connected")

        return self._sftp.listdir(remote_dir)

    def download(
        self,
        remote_path: str,
        local_path: Path,
    ) -> None:
        if self._sftp is None:
            raise RuntimeError("SFTP client is not connected")

        self._sftp.get(remote_path, str(local_path))
```

The class should remain a transport abstraction.

Do not place business rules such as:

```text
"customers files must be processed every day"
```

inside the low-level SFTP transport class.

---

# 27. Separate Transport From Ingestion Logic

A useful architecture is:

```text
SFTP Transport
      ↓
File Discovery
      ↓
Completeness Check
      ↓
Download
      ↓
Validation
      ↓
Processing
      ↓
Archive / Quarantine
```

Transport should answer:

```text
Can I list/download/move the remote file?
```

Ingestion logic should answer:

```text
Should I process this file?
Is it complete?
Has it already been processed?
Is its schema valid?
Where should it go?
```

This separation improves:

- Testing.
- Reuse.
- Debugging.
- Maintainability.

---

# 28. File Identity

Filename alone is often insufficient to identify a delivery.

Consider:

```text
customers_20261001.csv
```

A partner might accidentally send a corrected replacement with the same filename.

Possible identity components:

```text
partner
filename
size
checksum
delivery date
source modification time
manifest identifier
```

A strong delivery identity might be:

```text
partner_id + filename + sha256
```

or:

```text
manifest_id + file_name
```

The correct identity depends on the contract.

---

# 29. Processing Ledger

A production pipeline should maintain a durable processing ledger.

Conceptual schema:

```sql
CREATE TABLE file_ingestion_ledger (
    source_name TEXT NOT NULL,
    remote_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size_bytes BIGINT,
    sha256 TEXT,
    source_modified_at TIMESTAMP,
    discovered_at TIMESTAMP NOT NULL,
    downloaded_at TIMESTAMP,
    processed_at TIMESTAMP,
    status TEXT NOT NULL,
    run_id TEXT,
    error_message TEXT,
    PRIMARY KEY (source_name, remote_path, sha256)
);
```

Possible statuses:

```text
DISCOVERED
DOWNLOADING
LANDED
VALIDATED
PROCESSED
ARCHIVED
QUARANTINED
FAILED
```

The exact schema should match the platform's metadata conventions.

---

# 30. Why the Ledger Matters

Without a ledger:

```text
file arrives
 ↓
process
 ↓
job crashes
 ↓
file appears again
 ↓
process again
```

With a ledger:

```text
file identity
     ↓
lookup
     ↓
already successfully processed?
     ├── yes → skip or verify
     └── no  → process
```

The ledger turns file ingestion into a stateful, auditable process.

---

# 31. Idempotent File Processing

A production pipeline should tolerate:

- Scheduler retries.
- Worker retries.
- Network interruptions.
- Duplicate partner deliveries.
- Repeated files.
- Backfills.
- Manual reruns.

A simple rule:

```text
same file identity
+
same processing contract
=
no unintended duplicate effect
```

This is often called **exactly-once-in-effect**.

It does not require pretending that the distributed system literally executes every step exactly once.

---

# 32. Local Atomic Downloads

Never process a file while it is still being downloaded.

### BAD

```text
remote file
    ↓
/landing/customers.csv
    ↓
processor starts reading
    ↓
download still running
```

Instead:

```text
remote file
    ↓
/landing/.tmp/customers.csv.part
    ↓
download complete
    ↓
validate transfer
    ↓
atomic local rename
    ↓
/landing/customers.csv
    ↓
processor reads
```

Example:

```python
from pathlib import Path


def atomic_local_download(
    downloader,
    remote_path: str,
    destination: Path,
) -> None:
    temp_path = destination.with_suffix(
        destination.suffix + ".part"
    )

    downloader(remote_path, temp_path)

    temp_path.replace(destination)
```

`Path.replace()` performs a local rename/replace operation.

The critical idea is that consumers only see the final path after the download is complete.

---

# 33. Handling Interrupted Downloads

Suppose:

```text
2 GB file
↓
1.3 GB downloaded
↓
network connection fails
```

The temporary file should not be mistaken for a complete file.

Use:

```text
*.part
```

or another explicit temporary suffix.

After failure:

```text
temporary file
    ↓
delete or retain for controlled resume
```

Do not move a partial file into the processed area.

---

# 34. Remote Rename and Local Rename Are Different

Two different safety boundaries exist:

### Remote producer publication

```text
remote temporary
       ↓
remote final
```

This protects the consumer from an incomplete producer-side file.

### Local consumer publication

```text
local temporary
       ↓
local final
```

This protects downstream consumers from an incomplete download.

A robust pipeline can use both:

```text
producer atomic publication
+
consumer atomic landing
```

---

# 35. Archive Strategy

After successful processing:

```text
/inbound/file.csv
        ↓
/archive/2026/10/01/file.csv
```

Archive purposes include:

- Audit.
- Replay.
- Incident investigation.
- Historical reconstruction.
- Partner dispute resolution.
- Reprocessing.

Do not archive before successful validation if the archive is supposed to represent accepted deliveries.

---

# 36. Quarantine Strategy

Invalid files should not necessarily be deleted.

Use a quarantine area:

```text
/quarantine/2026/10/01/file.csv
```

Record:

```text
reason
run_id
timestamp
source
checksum
validation error
```

Examples:

```text
SCHEMA_MISMATCH
CHECKSUM_MISMATCH
TRUNCATED_FILE
INVALID_FILENAME
INVALID_ENCODING
DUPLICATE_DELIVERY
UNEXPECTED_COLUMN
```

Quarantine preserves evidence.

---

# 37. Archive vs Quarantine

| Outcome | Destination |
|---|---|
| Successfully validated and processed | Archive |
| Invalid schema | Quarantine |
| Checksum mismatch | Quarantine |
| Truncated file | Quarantine or retry acquisition |
| Duplicate already processed | Skip/archive according to contract |
| Temporary network failure | Retry, not quarantine |
| Missing expected file | Alert; nothing to quarantine |

Do not classify every failure as a data-quality failure.

---

# 38. Validation Layers

A production file should pass multiple validation layers.

```text
Transport validation
        ↓
File identity validation
        ↓
Format validation
        ↓
Schema validation
        ↓
Business validation
        ↓
Reconciliation
```

## Transport

- Download completed.
- Expected size.
- Checksum.

## File Format

- CSV is parseable.
- Parquet footer is readable.
- JSON is valid.
- Compression is valid.

## Schema

- Required columns exist.
- Types are acceptable.
- Version is supported.

## Business

- Dates are valid.
- IDs are non-null.
- Amounts are within expected ranges.
- Record counts are plausible.

## Reconciliation

- Manifest count matches.
- Expected delivery arrived.
- Source totals agree where available.

---

# 39. Schema Versioning

A partner may change:

```text
v1:
id,name,email

v2:
id,name,email,phone
```

The pipeline should know which versions are supported.

Possible approaches:

```text
schema_version in manifest
```

or:

```text
filename contains version
```

or:

```text
schema registry / contract metadata
```

Avoid silently accepting arbitrary schema changes.

---

# 40. Schema Evolution

Adding a nullable column may be backward-compatible.

Removing a required column may not be.

Changing:

```text
integer → string
```

can break downstream assumptions.

A production ingestion system should explicitly define:

```text
supported schema versions
compatibility rules
migration process
failure behavior
```

---

# 41. CSV Example

A simple parser:

```python
import csv
from pathlib import Path


REQUIRED_COLUMNS = {
    "customer_id",
    "name",
    "updated_at",
}


def validate_csv(path: Path) -> None:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        columns = set(reader.fieldnames or [])

        missing = REQUIRED_COLUMNS - columns

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )
```

This checks schema presence, not full business correctness.

---

# 42. Empty Files

An empty file can mean:

1. Legitimately zero records.
2. Failed partner export.
3. Partial/truncated delivery.
4. Placeholder file.
5. Test file.

Therefore:

```text
file size = 0
```

is not automatically:

```text
valid empty dataset
```

The delivery contract should define expected behavior.

---

# 43. Record Count Validation

A manifest might say:

```text
record_count = 1,250,000
```

After parsing:

```python
if actual_count != expected_count:
    raise ValueError(
        f"Expected {expected_count}, got {actual_count}"
    )
```

Record counts provide useful evidence, but count agreement alone does not prove content correctness.

A corrupted file could still contain the expected number of records.

Use multiple validation signals.

---

# 44. Missing Files

Suppose the contract says:

```text
one file every day
```

Today:

```text
no file
```

That is not the same as:

```text
empty delivery
```

The pipeline should maintain an expected-delivery schedule:

```text
expected date
expected file
deadline
received?
validated?
processed?
```

Example:

```text
2026-10-01
expected: yes
received: no
deadline: 06:00 UTC
status: LATE
```

This enables proactive alerting.

---

# 45. Late Files

A file can arrive after the expected time.

The system should distinguish:

```text
late
```

from:

```text
missing
```

A reasonable state model:

```text
EXPECTED
   ↓
LATE
   ↓
RECEIVED
   ↓
VALIDATED
   ↓
PROCESSED
```

The exact SLA is business-specific.

---

# 46. Out-of-Order Files

Suppose files arrive:

```text
2026-10-03
2026-10-01
2026-10-02
```

Do not assume arrival order equals business order.

The pipeline should use:

```text
file's business date
```

or manifest sequence:

```text
delivery_sequence
```

rather than:

```text
arrival timestamp
```

when determining logical ordering.

---

# 47. Duplicate Files

A partner may resend:

```text
customers_20261001.csv
```

The duplicate may have:

- Same content.
- Different content.
- Same filename.
- Different checksum.

These cases must be distinguished.

### Same identity, same checksum

Likely duplicate delivery.

### Same filename, different checksum

Potential correction or conflicting delivery.

Do not silently overwrite evidence.

Record both identities and apply the partner contract.

---

# 48. Corrected Files

Suppose:

```text
customers_20261001.csv
sha256 = AAA
```

was processed.

Later:

```text
customers_20261001.csv
sha256 = BBB
```

arrives.

This may be:

- A corrected delivery.
- A replacement.
- An accidental overwrite.
- A malicious or unexpected change.

A robust ledger makes this visible.

The processing policy should be explicit:

```text
reject
+
quarantine
+
replace
+
version
```

depending on the contract.

---

# 49. Concurrency

Two workers can discover the same file:

```text
Worker A → sees file
Worker B → sees file
```

Without coordination:

```text
both download
both process
duplicate effects
```

Possible controls include:

- Database uniqueness constraints.
- Processing ledger with atomic claim.
- Distributed lock.
- Single-consumer scheduling.
- Object-store-style conditional creation where applicable.

The database constraint is often an important final defense.

---

# 50. Atomic Claim

Conceptually:

```sql
INSERT INTO file_ingestion_ledger (
    source_name,
    remote_path,
    sha256,
    status
)
VALUES (
    :source,
    :path,
    :sha256,
    'CLAIMED'
)
ON CONFLICT DO NOTHING;
```

If the insert succeeds:

```text
this worker owns processing
```

If it conflicts:

```text
another worker already claimed/processed it
```

Exact syntax varies by database.

---

# 51. SFTP Directory Race Conditions

Consider:

```text
Worker lists files
     ↓
Producer replaces file
     ↓
Worker downloads path
```

The bytes downloaded may not be the bytes the worker expected from discovery.

Therefore:

- Prefer immutable published files.
- Use manifests/checksums.
- Record remote metadata.
- Avoid assuming filename identity implies content identity.

A file-drop protocol should ideally make published files immutable.

---

# 52. Remote File Deletion

Should the consumer delete the source file after processing?

Possible policies:

```text
Consumer deletes
Partner archives
Consumer moves to /processed
Partner retains
```

Deletion is a destructive operation.

Before deleting:

- Confirm contract.
- Confirm successful durable processing.
- Confirm replay requirements.
- Confirm whether another consumer needs the file.

A safer pattern is often:

```text
/inbound
   ↓
/processed
```

rather than:

```text
/inbound
   ↓
delete forever
```

---

# 53. Retention

Define retention for:

```text
raw files
archive
quarantine
processing metadata
manifests
checksums
logs
```

Example policy:

```text
inbound: short-lived
archive: 90 days
quarantine: 30 days
metadata: 1 year
```

These are examples only.

Retention must follow:

- Business requirements.
- Regulatory obligations.
- Security policy.
- Storage cost.
- Replay needs.

---

# 54. Replay

If the target must be rebuilt:

```text
archive
   ↓
reprocess
   ↓
new target
```

This is why preserving immutable raw input is valuable.

A strong architecture separates:

```text
acquisition
```

from:

```text
transformation
```

so the same source delivery can be replayed without reconnecting to the partner.

---

# 55. Backfill From Archived Files

Suppose the pipeline had a bug for:

```text
2026-09-01 → 2026-09-10
```

If raw files were archived:

```text
archive
  ↓
select affected deliveries
  ↓
reprocess corrected logic
  ↓
validate
  ↓
target correction
```

Without archive:

```text
partner must resend
```

which may be impossible.

---

# 56. Security Architecture

A production SFTP pipeline should consider:

```text
Identity
+
Host verification
+
Least privilege
+
Secret management
+
Encryption
+
Logging
+
File access controls
+
Retention
```

### Least privilege

The SFTP account should have only the required permissions.

If ingestion only needs:

```text
read /inbound
```

do not grant:

```text
delete everything
write everywhere
shell access
```

unless required.

---

# 57. Host Key Management

A production environment should have an explicit process for:

- Initial host-key verification.
- Host-key storage.
- Key rotation.
- Host migration.
- Unexpected host-key changes.

An unexpected host-key change should be treated as an operational/security event, not silently accepted.

---

# 58. Network Reliability

SFTP transfers can fail because of:

- Connection reset.
- Network interruption.
- Server restart.
- Idle timeout.
- Bandwidth constraints.
- Partner maintenance.
- Authentication failures.
- Disk quota.
- Permission errors.

Classify failures.

```text
Transient
    ↓
retry may help

Permanent/configuration
    ↓
retry alone will not help
```

Examples:

```text
connection reset → potentially transient
timeout → potentially transient
permission denied → usually configuration
unknown host key → security/configuration
file not found → may be race/contract issue
checksum mismatch → delivery integrity issue
```

---

# 59. Retry Carefully

A retry should not blindly repeat every operation.

For downloads:

```text
connect
  ↓
download
  ↓
failure
  ↓
retry
```

But repeated downloads can:

- Increase source load.
- Consume bandwidth.
- Create duplicate temporary files.
- Hide persistent failures.

Use:

- Bounded attempts.
- Exponential backoff where appropriate.
- Clear classification.
- Idempotent download handling.
- Strong logging.

---

# 60. Timeouts

A production SFTP connection should have bounded network operations.

Do not allow a worker to hang indefinitely.

The exact timeout configuration depends on the SFTP library and environment.

At minimum define operational expectations for:

```text
connection establishment
authentication
directory listing
file transfer
overall job duration
```

A timeout should produce an observable failure and a recoverable state.

---

# 61. Large Files

For a 20 GB file:

```text
DO NOT:
read entire file into memory
```

Prefer:

```text
stream / chunk
   ↓
write incrementally
```

The memory goal is:

```text
O(chunk_size)
```

rather than:

```text
O(file_size)
```

The same principle applies to checksum computation and downstream parsing.

---

# 62. Compression

Partners may deliver:

```text
.csv.gz
.zip
.parquet
.json.gz
```

Compression affects:

- Transfer size.
- CPU.
- Memory.
- Validation.
- File identity.

A checksum may apply to:

```text
compressed bytes
```

rather than:

```text
decompressed records
```

Document exactly what the manifest checksum covers.

---

# 63. Archives Are Not Automatically Safe to Extract

ZIP archives can contain:

```text
../../unexpected/path
```

or unexpected files.

Do not blindly extract untrusted archives.

Validate:

- Member paths.
- Expected filenames.
- File count.
- Uncompressed size.
- Compression ratio where relevant.
- Allowed file types.

This is especially important for external partners.

---

# 64. Path Traversal

Unsafe:

```python
destination = root / archive_member.filename
```

The member name could escape the intended directory.

Production archive extraction should normalize and validate paths before writing.

A conceptual invariant is:

```text
resolved_destination
must remain inside
resolved_root
```

---

# 65. Example Safe Extraction Concept

```python
from pathlib import Path


def safe_destination(root: Path, member_name: str) -> Path:
    root = root.resolve()
    destination = (root / member_name).resolve()

    if root not in destination.parents and destination != root:
        raise ValueError("Archive member escapes destination")

    return destination
```

This is a conceptual guard; archive-specific validation should also reject unexpected member types and files according to the delivery contract.

---

# 66. File-Drop State Machine

A useful state model:

```text
EXPECTED
   ↓
DISCOVERED
   ↓
CLAIMED
   ↓
DOWNLOADING
   ↓
LANDED
   ↓
VALIDATING
   ├───────────────┐
   │               │
   ▼               ▼
VALID              INVALID
   │                 │
   ▼                 ▼
PROCESSING       QUARANTINED
   │
   ▼
PROCESSED
   │
   ▼
ARCHIVED
```

Failure paths:

```text
DISCOVERED → FAILED
DOWNLOADING → FAILED
VALIDATING → QUARANTINED
PROCESSING → FAILED
```

A state machine makes recovery explicit.

---

# 67. End-to-End Example

Imagine a bank partner delivers:

```text
transactions_20261001.csv.gz
```

The contract says:

```text
Delivery:
daily by 04:00 UTC

Publication:
upload .part
then rename to .csv.gz

Manifest:
SHA-256 + expected bytes + record count

Retention:
partner retains 7 days

Consumer:
read-only SFTP access
```

The pipeline:

```text
04:00 scheduler
      ↓
connect
      ↓
list inbound
      ↓
discover final filename
      ↓
check manifest
      ↓
claim delivery
      ↓
download to .part
      ↓
verify bytes
      ↓
verify SHA-256
      ↓
atomically rename local file
      ↓
parse/decompress
      ↓
validate schema
      ↓
validate record count
      ↓
land
      ↓
process
      ↓
commit
      ↓
archive
      ↓
record success
```

This is a production workflow.

---

# 68. Complete Python-Oriented Ingestion Skeleton

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RemoteFile:
    path: str
    size_bytes: int
    modified_at: object


class FileDropIngestion:
    def __init__(
        self,
        *,
        sftp_client,
        landing_root: Path,
        archive_root: Path,
        quarantine_root: Path,
        ledger,
    ) -> None:
        self.sftp = sftp_client
        self.landing_root = landing_root
        self.archive_root = archive_root
        self.quarantine_root = quarantine_root
        self.ledger = ledger

    def discover(self) -> list[RemoteFile]:
        # Discover only contract-approved files.
        raise NotImplementedError

    def process_file(self, remote_file: RemoteFile) -> None:
        # 1. Check whether already successfully processed.
        # 2. Claim delivery.
        # 3. Download to temporary local path.
        # 4. Verify transfer.
        # 5. Atomically publish local file.
        # 6. Validate schema/content.
        # 7. Process idempotently.
        # 8. Commit.
        # 9. Archive.
        # 10. Mark ledger state.
        raise NotImplementedError

    def run(self) -> None:
        for remote_file in self.discover():
            self.process_file(remote_file)
```

This intentionally separates orchestration from implementation details.

---

# 69. Testing Strategy

Do not make your unit tests depend on a real partner SFTP server.

Test:

- Filename parsing.
- Delivery selection.
- Marker detection.
- Manifest validation.
- Checksum validation.
- Duplicate detection.
- Ledger transitions.
- Local atomic rename.
- Schema validation.
- Quarantine decisions.
- Missing-file detection.
- Late-file detection.
- Archive decisions.

Integration tests can use:

- A containerized SFTP server.
- A test SSH server.
- A dedicated partner sandbox.

The key testing principle:

> Most correctness logic should be testable without network access.

---

# 70. Fake Transport

Define an interface:

```python
from typing import Protocol


class FileTransferClient(Protocol):
    def list(self, remote_dir: str) -> list[str]:
        ...

    def download(
        self,
        remote_path: str,
        local_path: str,
    ) -> None:
        ...

    def rename(
        self,
        remote_source: str,
        remote_destination: str,
    ) -> None:
        ...
```

Production:

```text
Paramiko implementation
```

Tests:

```text
in-memory fake
```

This prevents every unit test from becoming an integration test.

---

# 71. Fake SFTP Example

```python
from pathlib import Path
import shutil


class FakeSFTP:
    def __init__(self, root: Path) -> None:
        self.root = root

    def list(self, remote_dir: str) -> list[str]:
        directory = self.root / remote_dir.lstrip("/")
        return [path.name for path in directory.iterdir()]

    def download(
        self,
        remote_path: str,
        local_path: str,
    ) -> None:
        source = self.root / remote_path.lstrip("/")
        shutil.copyfile(source, local_path)
```

Now ingestion logic can be tested with ordinary local files.

---

# 72. Required Unit Tests

At minimum, write tests conceptually equivalent to:

```text
test_filename_accepts_expected_pattern
test_filename_rejects_unexpected_pattern
test_ready_marker_required
test_part_file_ignored
test_checksum_matches
test_checksum_mismatch_quarantines
test_duplicate_file_is_not_reprocessed
test_same_filename_different_checksum_is_detected
test_partial_download_is_not_published
test_schema_mismatch_quarantines
test_missing_expected_file_is_alerted
test_late_file_is_processed
test_successful_file_is_archived
test_failed_file_is_not_marked_processed
test_two_workers_cannot_claim_same_delivery
```

---

# 73. Reconciliation

Reconciliation answers:

> Did the delivery we expected actually arrive and get processed correctly?

Possible checks:

```text
expected file count
vs
received file count
```

```text
manifest record count
vs
parsed record count
```

```text
manifest checksum
vs
downloaded checksum
```

```text
expected delivery dates
vs
processed delivery dates
```

```text
source total
vs
target total
```

No single check proves everything.

Use multiple independent signals.

---

# 74. Expected-Delivery Metadata

A simple table:

```sql
CREATE TABLE expected_file_deliveries (
    partner TEXT NOT NULL,
    business_date DATE NOT NULL,
    expected_pattern TEXT NOT NULL,
    deadline TIMESTAMP NOT NULL,
    received_at TIMESTAMP,
    processed_at TIMESTAMP,
    status TEXT NOT NULL,
    PRIMARY KEY (partner, business_date)
);
```

This allows operational queries such as:

```text
Which files are overdue?

Which files arrived but failed validation?

Which business dates are missing?

Which partner has repeated late deliveries?
```

---

# 75. Observability

Useful metrics include:

```text
sftp_connection_failures
sftp_authentication_failures
files_discovered
files_claimed
files_downloaded
files_validated
files_processed
files_quarantined
files_archived
files_duplicate
files_late
files_missing
bytes_downloaded
download_duration_seconds
validation_duration_seconds
processing_duration_seconds
```

Useful dimensions:

```text
partner
file_type
delivery_date
status
```

Avoid high-cardinality dimensions such as full raw filenames in metrics systems unless the observability platform explicitly supports that use safely.

---

# 76. Logging

A useful structured log:

```json
{
  "event": "file_processed",
  "partner": "acme",
  "file_name": "customers_20261001.csv",
  "run_id": "run-001",
  "bytes": 123456789,
  "records": 1250000,
  "status": "success"
}
```

Do not log:

- Passwords.
- Private keys.
- Secret values.
- Entire sensitive records.
- Unnecessary personal data.

Use identifiers and metadata instead.

---

# 77. Alerting

Alert on conditions that require action.

Examples:

### Critical

```text
SFTP authentication failure
host-key mismatch
checksum mismatch
unexpected schema
processing corruption
```

### Warning

```text
file late
file missing after SLA
unusual file size
unusual record count
```

### Informational

```text
duplicate delivery skipped
empty file received
```

Alert severity should reflect operational impact.

---

# 78. File Size Anomaly Detection

Suppose normal daily files are:

```text
900 MB
1.1 GB
950 MB
1.0 GB
```

Today:

```text
2 MB
```

Even if technically valid, this may indicate an upstream failure.

A useful control is:

```text
expected size range
```

or historical anomaly detection.

Do not hard-code arbitrary thresholds without understanding normal variability.

---

# 79. Record Count Anomaly Detection

Similarly:

```text
normal:
~1.2 million records

today:
3,000 records
```

The file might pass schema validation while being materially incomplete.

Use:

```text
record count validation
+
historical comparison
+
business expectations
```

This is data-quality monitoring, not merely file-transfer monitoring.

---

# 80. The Difference Between Transport Success and Data Success

This distinction is critical.

```text
SFTP download succeeded
```

means:

```text
bytes were transferred
```

It does not mean:

```text
business data is correct
```

A successful pipeline requires:

```text
transport success
+
integrity validation
+
schema validation
+
business validation
+
target commit
```

---

# 81. Common Mistake: Process Immediately After `listdir`

### BAD

```python
for filename in sftp.listdir("/inbound"):
    sftp.get(filename, local_path)
    process(local_path)
```

Problems:

- May process temporary files.
- May process incomplete files.
- May process unrelated files.
- No checksum.
- No idempotency.
- No ledger.
- No quarantine.
- No archive contract.

### Better

```text
discover
  ↓
filter
  ↓
prove complete
  ↓
claim
  ↓
download safely
  ↓
validate
  ↓
process idempotently
  ↓
archive
  ↓
record metadata
```

---

# 82. Common Mistake: Trusting File Extension

### BAD

```python
if filename.endswith(".csv"):
    process(filename)
```

A `.csv` file can contain:

```text
HTML
error text
partial content
wrong schema
malicious content
```

Extension is a routing hint, not a validation mechanism.

---

# 83. Common Mistake: Using Modification Time as a Guarantee

### BAD

```text
"File has not changed for 5 minutes, therefore it is complete."
```

The producer may:

```text
pause for 10 minutes
resume writing
```

Use modification time as supporting evidence, not a substitute for a producer contract.

---

# 84. Common Mistake: Deleting the Source Immediately

### BAD

```text
download
process
delete remote file
```

If processing later proves incorrect:

```text
source copy is gone
```

Prefer:

```text
archive
```

or ensure the partner retains an agreed replay window.

---

# 85. Common Mistake: No Processing Ledger

Without durable state:

```text
Did we process this file?
```

becomes:

```text
"I think so."
```

Production systems should be able to answer with evidence.

---

# 86. Common Mistake: Assuming Filename Uniqueness

A filename may be reused.

Use:

```text
filename
+
checksum
+
source
```

or an explicit manifest/delivery ID.

---

# 87. Common Mistake: One Giant Job

### Fragile design

```text
download 100 files
    ↓
process all
    ↓
commit once
```

One failure can make recovery difficult.

### Better

```text
file 1 → validate → process → commit
file 2 → validate → process → commit
...
```

The optimal batching model depends on source volume and target transaction semantics.

---

# 88. Production Workflow

A mature file-drop ingestion workflow can be summarized as:

```text
1. Establish expected delivery
2. Connect securely
3. Discover candidates
4. Filter by contract
5. Verify publication/completeness
6. Compute identity
7. Atomically claim
8. Download to temporary path
9. Validate transfer integrity
10. Publish local landing atomically
11. Validate file format
12. Validate schema
13. Validate business rules
14. Reconcile counts/checksums
15. Process idempotently
16. Commit target
17. Archive
18. Record success
19. Monitor freshness
20. Alert on exceptions
```

---

# 89. Hands-On Lab

Build the complete workflow conceptually in one Python module.

The lab should include:

```text
FakeSFTP
ExpectedDeliveryStore
FileLedger
ChecksumValidator
FileValidator
ArchiveManager
IngestionRunner
```

Do not create helper files for this chapter. Keep all code in this document.

---

# 90. Hands-On Lab — Fake SFTP

```python
from pathlib import Path
import shutil


class FakeSFTP:
    def __init__(self, root: Path) -> None:
        self.root = root

    def list(self, remote_dir: str) -> list[str]:
        path = self.root / remote_dir.strip("/")
        return [item.name for item in path.iterdir()]

    def download(
        self,
        remote_path: str,
        local_path: Path,
    ) -> None:
        source = self.root / remote_path.strip("/")
        shutil.copyfile(source, local_path)
```

Create a temporary test environment:

```python
from tempfile import TemporaryDirectory


with TemporaryDirectory() as tmp:
    root = Path(tmp)

    inbound = root / "inbound"
    inbound.mkdir()

    source_file = inbound / "customers_20261001.csv"
    source_file.write_text(
        "customer_id,name,updated_at\n"
        "1,Alice,2026-10-01T00:00:00Z\n",
        encoding="utf-8",
    )

    client = FakeSFTP(root)

    print(client.list("/inbound"))
```

---

# 91. Hands-On Lab — Checksum

```python
import hashlib


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()
```

Exercise:

1. Create a test file.
2. Compute checksum.
3. Modify one byte.
4. Compute checksum again.
5. Confirm that the checksum changes.

---

# 92. Hands-On Lab — Atomic Landing

```python
def download_atomically(
    client: FakeSFTP,
    remote_path: str,
    destination: Path,
) -> None:
    temp_path = destination.with_name(
        destination.name + ".part"
    )

    client.download(remote_path, temp_path)

    if temp_path.stat().st_size == 0:
        raise ValueError("Downloaded file is empty")

    temp_path.replace(destination)
```

Exercise:

1. Inject a download failure.
2. Confirm `.part` remains or is cleaned according to policy.
3. Confirm final destination does not appear.
4. Run successful download.
5. Confirm final destination appears only after download completion.

---

# 93. Hands-On Lab — Idempotency

Simulate:

```text
Run 1:
file A → processed

Run 2:
file A discovered again
```

Expected:

```text
ledger lookup
     ↓
already processed
     ↓
skip processing
```

Then simulate:

```text
same filename
different checksum
```

Expected:

```text
do not silently skip
```

Instead:

```text
detect conflict
record metadata
apply correction policy
```

---

# 94. Hands-On Lab — Quarantine

Create a validator:

```python
def validate_required_columns(
    path: Path,
    required: set[str],
) -> None:
    import csv

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        actual = set(reader.fieldnames or [])

    missing = required - actual

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )
```

Then:

```python
try:
    validate_required_columns(
        path,
        {"customer_id", "name", "updated_at"},
    )
except ValueError:
    quarantine(path)
```

The exercise should verify:

```text
invalid file
   ↓
not processed
   ↓
quarantined
   ↓
reason recorded
```

---

# 95. Hands-On Lab — Missing Delivery

Create an expected schedule:

```python
expected_dates = {
    "2026-09-29",
    "2026-09-30",
    "2026-10-01",
}
```

Discovered files:

```python
received_dates = {
    "2026-09-29",
    "2026-10-01",
}
```

Then:

```python
missing = expected_dates - received_dates
```

Result:

```text
2026-09-30
```

Now classify it:

```text
not necessarily failed yet
→ compare against delivery deadline
```

If deadline has passed:

```text
MISSING / LATE
```

---

# 96. Hands-On Lab — Late Delivery

Create:

```text
expected deadline = 04:00 UTC
actual arrival    = 05:15 UTC
```

The pipeline should:

- Process the file.
- Record actual arrival.
- Mark delivery as late.
- Emit an operational metric.
- Trigger an alert if the SLA requires it.

A late file is not necessarily an invalid file.

---

# 97. Hands-On Lab — Duplicate Delivery

Simulate:

```text
file_name = customers_20261001.csv
sha256 = ABC
```

Run twice.

Expected:

```text
first → process
second → duplicate
```

Then:

```text
same filename
sha256 = XYZ
```

Expected:

```text
conflict detected
```

This is a useful production test because filename-only deduplication would miss the distinction.

---

# 98. Hands-On Lab — Crash Recovery

Simulate:

```text
download
 ↓
validate
 ↓
process target
 ↓
CRASH before ledger update
```

On restart:

```text
same file discovered
```

The design must ensure that target processing is idempotent.

Possible solution:

```text
transactional target write
+
ledger update
```

when both are in the same database transaction.

If they are separate systems:

```text
idempotent target key
+
durable ledger
+
reconciliation
```

---

# 99. Hands-On Lab — Expected End-to-End Output

A successful run should produce metadata conceptually like:

```text
run_id: run-20261001-001
partner: acme
file: customers_20261001.csv
remote_path: /inbound/customers_20261001.csv
size_bytes: 123456789
sha256: ...
records: 1250000
status: PROCESSED
download_seconds: 41.2
validation_seconds: 8.1
processing_seconds: 23.4
archived: true
```

This makes the run auditable.

---

# 100. Production Design Exercise

## Scenario

A partner sends:

```text
orders_YYYYMMDD.csv.gz
```

every day.

Contract:

```text
Delivery deadline: 03:00 UTC
Publication: .part → final rename
Manifest: available
Checksum: SHA-256
Expected record count: available
Partner retention: 7 days
Data volume: 5–20 GB/day
Hard deletes: not relevant
Correction files: possible
```

Design the ingestion system.

Your answer should cover:

1. Authentication.
2. Host-key verification.
3. Discovery.
4. Completeness.
5. Manifest validation.
6. Large-file download.
7. Atomic local landing.
8. Checksum.
9. Schema validation.
10. Record-count validation.
11. Idempotency.
12. Duplicate detection.
13. Correction handling.
14. Archive.
15. Quarantine.
16. Processing ledger.
17. Monitoring.
18. Alerting.
19. Replay.
20. Recovery.

---

# 101. Reference Architecture

A reasonable architecture is:

```text
Partner
  │
  │ SFTP
  ▼
Inbound directory
  │
  ├── final filename only
  └── manifest
  │
  ▼
Discovery worker
  │
  ▼
Delivery claim
  │
  ▼
Temporary local/object-store landing
  │
  ├── checksum
  ├── size
  └── transfer validation
  │
  ▼
Atomic publish
  │
  ▼
Decompression
  │
  ▼
Schema + record-count validation
  │
  ├───────────────┐
  │               │
  ▼               ▼
VALID           INVALID
  │               │
  ▼               ▼
Process         Quarantine
  │
  ▼
Commit
  │
  ▼
Archive
  │
  ▼
Ledger + metrics
```

Because files are 5–20 GB, avoid holding them in memory.

---

# 102. Architecture Decision Questions

Before implementing, ask:

### Source contract

- What exactly constitutes a published file?
- Are files immutable after publication?
- Is a manifest available?
- Is a checksum provided?
- Can a file be replaced?

### Security

- How is the SSH key managed?
- How are host keys verified?
- What permissions does the SFTP account have?

### Reliability

- What happens when a transfer is interrupted?
- Can downloads resume?
- What is the retry policy?
- How long should a worker wait?

### Data quality

- What schema is expected?
- How are schema versions communicated?
- What record-count checks exist?
- What anomalies should alert?

### Operations

- How do we detect missing files?
- How do we detect late files?
- How do we replay a historical delivery?
- How long is the archive retained?

---

# 103. Interview Questions

1. What is SFTP?
2. How is SFTP different from FTP?
3. Why is file visibility not proof of completeness?
4. Why is `.part` → final rename useful?
5. What is a ready marker?
6. Why are manifests useful?
7. What does a checksum prove?
8. Why is file size alone insufficient?
9. How do you safely download a 20 GB file?
10. Why should local downloads use temporary paths?
11. What is a processing ledger?
12. How do you make file ingestion idempotent?
13. How do you detect duplicate deliveries?
14. What if the same filename arrives with a different checksum?
15. How do you handle missing files?
16. How do you handle late files?
17. What belongs in quarantine?
18. Why should raw files be archived?
19. How do you handle correction files?
20. How do you prevent two workers from processing the same file?
21. How do you validate SSH host identity?
22. What should never appear in logs?
23. How would you design SFTP ingestion for 100 GB files?
24. How would you test the pipeline without a real partner?
25. How do you prove a daily delivery was complete?

Strong answers should discuss:

```text
contract
+
integrity
+
idempotency
+
state
+
security
+
reconciliation
+
recovery
```

---

# 104. Debugging Scenarios

## Scenario 1 — File Is Corrupted

Symptoms:

```text
checksum mismatch
```

Investigate:

```text
remote checksum
local checksum
download logs
network failures
partner publication timing
```

Do not simply process the file anyway.

---

## Scenario 2 — CSV Parser Fails

Symptoms:

```text
unexpected end of file
```

Investigate:

```text
file size
checksum
producer completion marker
download interruption
compression
encoding
```

A parser failure may actually be a transport/completeness failure.

---

## Scenario 3 — Duplicate Data

Investigate:

```text
same filename?
same checksum?
same delivery ID?
same processing run?
ledger state?
concurrent workers?
```

Do not immediately delete duplicate target rows without identifying the cause.

---

## Scenario 4 — Expected File Missing

Investigate:

```text
partner delivery schedule
deadline
remote directory
filename pattern
holiday calendar
partner outage
manifest availability
```

Classify:

```text
not due
late
missing
partner outage
configuration error
```

---

## Scenario 5 — Corrected File Arrives

Symptoms:

```text
same filename
different checksum
```

Investigate:

```text
partner correction policy
previous processing status
target replacement requirements
audit requirements
```

Never silently overwrite the original audit evidence.

---

# 105. Failure Matrix

| Failure | Likely classification | Typical action |
|---|---|---|
| Authentication denied | Configuration/security | Alert, fix credentials |
| Host-key mismatch | Security | Stop and investigate |
| Connection reset | Transient | Retry |
| Transfer timeout | Potentially transient | Retry with bounds |
| File missing | Delivery/contract | Wait or alert based on SLA |
| `.part` only | Producer still writing | Do not process |
| Checksum mismatch | Integrity | Retry/reacquire or quarantine |
| Schema mismatch | Data contract | Quarantine + alert |
| Duplicate same checksum | Duplicate delivery | Skip safely |
| Same filename, new checksum | Correction/conflict | Apply explicit policy |
| Target write failure | Processing | Retry idempotently |
| Archive failure | Operational | Do not falsely mark complete |
| Ledger update failure | State consistency | Reconcile before retry |

---

# 106. Completion Checklist

## Transport

- [ ] SFTP protocol understood.
- [ ] Authentication configured securely.
- [ ] Host-key verification enabled.
- [ ] Least privilege applied.
- [ ] Timeouts/retry behavior defined.

## Discovery

- [ ] Remote directory is explicit.
- [ ] Filename pattern is validated.
- [ ] Temporary files are ignored.
- [ ] Expected deliveries are tracked.
- [ ] Late/missing delivery logic exists.

## Completeness

- [ ] Producer publication contract documented.
- [ ] Ready/manifest/rename mechanism understood.
- [ ] Checksum validation implemented where available.
- [ ] Size validation implemented where useful.
- [ ] Stable-size heuristics are not treated as absolute proof.

## Acquisition

- [ ] Large files use bounded memory.
- [ ] Downloads use temporary paths.
- [ ] Final local path is published atomically.
- [ ] Interrupted transfers cannot be mistaken for complete files.

## Data Quality

- [ ] File format validated.
- [ ] Schema validated.
- [ ] Schema versioning understood.
- [ ] Record counts checked where available.
- [ ] Business validations defined.
- [ ] Invalid files quarantined.

## State and Idempotency

- [ ] Durable processing ledger exists.
- [ ] File identity is deterministic.
- [ ] Duplicate deliveries are handled.
- [ ] Concurrent workers cannot double-process safely.
- [ ] Correction files have an explicit policy.

## Lifecycle

- [ ] Successful files archived.
- [ ] Quarantined files retained.
- [ ] Retention policy documented.
- [ ] Replay is possible.
- [ ] Backfill process exists.

## Operations

- [ ] Metrics exist.
- [ ] Structured logs exist.
- [ ] Secrets are redacted.
- [ ] Missing-file alerts exist.
- [ ] Late-file alerts exist.
- [ ] Integrity/schema alerts exist.
- [ ] Run metadata is auditable.

---

# 107. Final Mental Model

```text
                 FILE-DROP INGESTION
                         │
                         ▼
                  EXPECTED DELIVERY
                         │
                         ▼
                     DISCOVERY
                         │
                         ▼
                PROVE COMPLETENESS
                         │
            ┌────────────┼────────────┐
            │            │            │
         marker       manifest      contract
            │            │            │
            └────────────┼────────────┘
                         ▼
                       CLAIM
                         │
                         ▼
                 DOWNLOAD TO TEMP
                         │
                         ▼
                TRANSFER VALIDATION
                         │
                 ┌───────┴───────┐
                 │               │
              VALID            INVALID
                 │               │
                 ▼               ▼
             ATOMIC LAND      RETRY/QUARANTINE
                 │
                 ▼
            DATA VALIDATION
                 │
                 ▼
             IDEMPOTENT
             PROCESSING
                 │
                 ▼
                COMMIT
                 │
                 ▼
              ARCHIVE
                 │
                 ▼
            LEDGER + METRICS
                 │
                 ▼
            RECONCILIATION
```

The deepest principle is:

> **SFTP is only the transport. Production file-drop ingestion is a delivery protocol, state-management problem, integrity problem, and operational reliability problem.**

A mature pipeline therefore does not ask only:

```text
"Did the file download?"
```

It asks:

```text
Was the expected delivery received?
Was it completely published?
Did we receive the correct bytes?
Can we prove their integrity?
Did we validate the expected schema?
Did we process the delivery exactly once in effect?
Can we recover from a crash?
Can we replay it?
Can we explain what happened?
Can we detect when the partner failed to deliver?
```

---

# 108. Exit Criteria

You have completed this topic when you can independently design and explain:

```text
SFTP connection
      ↓
secure authentication
      ↓
host-key verification
      ↓
remote discovery
      ↓
publication/completeness detection
      ↓
file identity
      ↓
idempotent claim
      ↓
bounded-memory download
      ↓
atomic local landing
      ↓
checksum/size validation
      ↓
schema/business validation
      ↓
quarantine
      ↓
idempotent processing
      ↓
archive
      ↓
ledger
      ↓
reconciliation
      ↓
monitoring
      ↓
replay/recovery
```

You should also be able to answer:

> **What evidence proves that this file-drop pipeline processed the correct file completely, safely, exactly once in effect, and in a way that can be recovered and audited?**

If your answer includes:

```text
delivery contract
+
publication signal
+
checksum
+
file identity
+
processing ledger
+
idempotent target operation
+
archive
+
quarantine
+
reconciliation
+
observability
```

you have moved beyond “SFTP scripting” into production Data Engineering.

---

# 109. Final Production Principle

The production mindset for file-drop ingestion is:

```text
Never trust filename alone.
Never trust file visibility alone.
Never trust transfer success alone.
Never trust schema alone.
Never assume delivery order.
Never assume retries are harmless.
Never delete evidence prematurely.

Instead:

Define the contract.
Verify publication.
Acquire safely.
Validate integrity.
Validate data.
Track state.
Process idempotently.
Archive evidence.
Quarantine failures.
Reconcile expectations.
Monitor the entire lifecycle.
```

That is how a simple partner file drop becomes a reliable production ingestion system.
