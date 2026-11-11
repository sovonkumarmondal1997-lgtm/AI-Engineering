# Topic 13 — KMS, VPC Endpoints, and Private Networking for Data

**Stage:** 2B — AWS Data Engineering Deep Dive  
**Phase:** E — Operating, Securing, and Unifying  
**Topic:** 13 — KMS, VPC Endpoints, and Private Networking for Data  
**Position:** After Topic 12 — CloudWatch, CloudTrail, and Cost Explorer; before Topic 14 — SageMaker Unified Studio and DataZone  
**Audience:** Data Engineers progressing from cloud-aware to production AWS Data Platform engineers

> **Core outcome:** build data platforms where encryption, identity, network reachability, service access, auditability, and cost are designed together rather than debugged independently.

---

# 1. Why This Topic Matters

A production data platform needs more than a working ETL job.

It needs:

```text
Encryption
+
Identity
+
Network isolation
+
Private service access
+
Secrets management
+
Auditability
+
Least privilege
+
Cost discipline
```

A useful security mental model is:

```text
WHO?
  ↓
IAM / role / identity

CAN THEY REACH IT?
  ↓
VPC / route / endpoint / security group

CAN THEY USE THE SERVICE?
  ↓
IAM / endpoint policy

CAN THEY ACCESS THE RESOURCE?
  ↓
resource policy

CAN THEY USE THE ENCRYPTION KEY?
  ↓
KMS key policy / IAM / grants

IS THE CONNECTION PROTECTED?
  ↓
TLS / encryption

CAN WE PROVE WHAT HAPPENED?
  ↓
CloudTrail / logs
```

The central production lesson is:

> **Network security does not replace IAM. IAM does not replace KMS. KMS does not replace resource policies. Encryption does not replace private networking.**

These controls are complementary.

---

# 2. Learning Progression

This module follows:

```text
Encryption fundamentals
        ↓
AWS KMS
        ↓
Envelope encryption
        ↓
S3 encryption
        ↓
AWS data-service encryption
        ↓
VPC fundamentals
        ↓
Private subnets
        ↓
Security groups
        ↓
NAT Gateway
        ↓
VPC endpoints
        ↓
Private AWS data workloads
        ↓
Secrets Manager
        ↓
Cross-account encryption
        ↓
Data perimeters
        ↓
VPN / Direct Connect awareness
        ↓
Troubleshooting
        ↓
Production architecture
        ↓
Cost optimization
```

Every major lab follows:

```text
Learn
↓
Implement
↓
Observe
↓
Break
↓
Diagnose
↓
Fix
↓
Verify
↓
Document
```

---

# 3. Prerequisites and Scope Boundary

You should already understand:

- IAM basics
- S3
- Glue
- Athena
- Redshift
- Kinesis
- Firehose
- EMR
- MSK
- Lambda
- DMS
- Terraform
- AWS CLI
- basic networking terminology

Earlier roadmap modules provide the service-specific depth. This topic does **not** repeat those services in full.

Instead, it asks:

> **How do I run these services securely and privately?**

Do not turn this into a full networking certification course.

Focus on Data Engineering security architecture.

---

# 4. What Is Encryption?

Encryption transforms readable plaintext into ciphertext using cryptographic material.

Conceptually:

```text
Plaintext
   ↓
Encryption algorithm + key
   ↓
Ciphertext
```

Decryption reverses the process:

```text
Ciphertext
   ↓
Decryption algorithm + key
   ↓
Plaintext
```

For data platforms, encryption protects data:

- at rest
- in transit
- in backups/snapshots
- in object storage
- in databases
- in streaming systems
- in temporary compute storage where supported

Encryption is not authorization.

For example:

```text
Encrypted S3 object
```

does not mean:

```text
any IAM principal can read it.
```

Encryption and authorization solve different problems.

---

# 5. Data at Rest vs Data in Transit

## At rest

Examples:

```text
S3 objects
Redshift storage
RDS storage
EMR volumes
Kinesis stored records
MSK storage
Secrets
```

## In transit

Examples:

```text
Glue → S3
Lambda → database
application → Secrets Manager
producer → Kinesis
client → MSK
analytics client → Redshift
```

Typical controls:

```text
At rest
→ AWS service encryption + KMS where appropriate

In transit
→ TLS + private networking where appropriate
```

A production architecture normally needs both.

---

# 6. Envelope Encryption

Earlier Data Engineering foundations introduced envelope encryption. AWS KMS is the AWS-specific key-management control plane around this pattern.

Conceptually:

```text
                    AWS KMS
                       |
                       | Generate data key
                       v
                 Data Key
                 /       \
                /         \
               v           v
        Encrypt data    Encrypt data key
               |              |
               v              v
          Ciphertext     Encrypted data key
```

The data key performs bulk encryption.

KMS protects and manages the key material used to protect the data key.

This avoids sending large data payloads through KMS cryptographic APIs.

Mental model:

```text
KMS
=
key-management control plane

Data key
=
bulk-data encryption key
```

Do not confuse:

```text
KMS key
```

with:

```text
every object-specific data key
```

AWS service implementations can differ, but envelope encryption is the foundational pattern to understand.

---

# 7. AWS KMS

AWS Key Management Service provides managed creation and control of cryptographic keys and cryptographic operations used by AWS services and applications.

Important concepts:

```text
KMS key
Key policy
IAM policy
Grant
Alias
Rotation
Key state
Region
Key usage
CloudTrail
```

A customer-managed KMS key is created and managed by the customer.

AWS managed keys are created and managed by AWS services for supported integrations.

AWS also has AWS owned keys, whose management is controlled by AWS and whose details are not exposed to customers in the same way.

Source: AWS KMS key concepts and KMS best-practice documentation.

---

# 8. AWS-Managed vs Customer-Managed Keys

| Dimension | AWS-managed key | Customer-managed key |
|---|---|---|
| Created/managed by | AWS service | Customer |
| Key policy control | Limited to AWS-managed configuration | Customer controlled |
| Rotation | AWS-managed | Customer-controlled rotation options |
| Fine-grained governance | Lower | Higher |
| Cross-account design | More constrained | Stronger control options |
| Operational burden | Lower | Higher |
| Cost | No monthly key-existence fee | Key and usage charges apply according to current pricing |
| Best fit | Convenience | Granular security/control |

Use customer-managed keys when you need:

- explicit governance
- separation of duties
- controlled cross-account access
- tighter service conditions
- explicit lifecycle control
- stronger audit requirements

Do not automatically create dozens of customer-managed keys without a security-boundary rationale.

---

# 9. KMS Key Policies

Every KMS key has a key policy.

A key policy is not simply another optional IAM document.

KMS authorization can involve:

```text
Key policy
+
IAM policy
+
Grants
+
resource policy
+
VPC endpoint policy where applicable
```

AWS documents the key policy as the primary access-control mechanism for KMS keys.

A useful debugging question is:

> **Does the key policy permit the relevant account/principal to use this key?**

Then:

> **Does IAM also permit the operation?**

Do not assume an IAM `Allow` automatically makes a KMS key usable.

---

# 10. KMS Key Policy Mental Model

A simplified conceptual policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowKeyUseForDataRole",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:role/DataPipelineRole"
      },
      "Action": [
        "kms:Decrypt",
        "kms:Encrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*"
    }
  ]
}
```

This is intentionally simplified.

Production policies should constrain:

- principal
- operations
- service context
- resource use
- account boundaries
- conditions

Never copy a broad policy into production without understanding the authorization model.

---

# 11. KMS Grants

A grant is a KMS authorization mechanism that can give a principal permission to perform specific KMS operations.

AWS services commonly use grants when integrating with KMS.

Mental model:

```text
Key policy
    +
IAM
    +
Grant
    ↓
Effective KMS authorization
```

Grants are useful when:

- an AWS service needs controlled use
- permissions should be delegated without rewriting the key policy
- a temporary or service-specific authorization is appropriate

AWS documentation notes that grants are considered alongside key policies and IAM policies and are commonly used by AWS services integrated with KMS.

Do not treat grants as a replacement for all policy design.

---

# 12. Key Rotation

Key rotation changes the cryptographic material used by a KMS key while retaining the logical KMS key identity.

For supported customer-managed symmetric keys, automatic rotation can be configured.

Important distinction:

```text
Rotate key material
≠
Create an entirely different KMS key
```

Rotation is operationally useful when required by policy or governance.

It does not magically re-encrypt every existing ciphertext into a new key.

AWS KMS retains previous key material needed to decrypt ciphertext encrypted under earlier material for the key.

Source: AWS KMS rotation documentation.

---

# 13. KMS Aliases

Prefer application-facing aliases where appropriate:

```text
alias/data-platform-silver
alias/data-platform-gold
alias/data-platform-secrets
```

Instead of hard-coding key IDs everywhere.

Benefits:

- readability
- easier infrastructure management
- cleaner Terraform
- easier key-selection semantics

An alias does not itself grant permission.

Authorization still depends on the underlying KMS key and policies.

---

# 14. KMS Lifecycle

Understand:

```text
Create
  ↓
Enable
  ↓
Use
  ↓
Rotate
  ↓
Disable if necessary
  ↓
Schedule deletion if intentionally retiring
```

Do not delete a production KMS key casually.

A KMS key can be critical to:

```text
S3 data
database storage
snapshots
logs
secrets
backups
streaming
```

Loss of key access can make encrypted data inaccessible.

---

# 15. KMS Separation of Duties

A mature platform separates:

```text
Key administrators
```

from:

```text
Key users / workload roles
```

For example:

```text
Security team
→ create/manage key

Data platform role
→ use key for encryption/decryption

Application role
→ decrypt only where required
```

Avoid:

```text
one administrator role
=
key administration
+
application data access
```

AWS KMS best-practice guidance recommends separating key administration from key usage.

---

# 16. KMS Auditability

KMS API activity can be audited through CloudTrail.

Useful investigations:

```text
Who used the key?
Which operation?
When?
Which principal?
Was a grant created?
Was the key policy changed?
```

This connects Topic 13 to Topic 12:

```text
KMS
 ↓
CloudTrail
 ↓
Investigation
```

Do not duplicate the full CloudTrail module here. Use it as the evidence layer for KMS troubleshooting.

---

# 17. S3 Encryption Overview

S3 server-side encryption options include:

```text
SSE-S3
SSE-KMS
```

S3 can also use S3 Bucket Keys with SSE-KMS.

The high-level distinction:

```text
SSE-S3
→ S3-managed encryption mechanism

SSE-KMS
→ S3 integrates with AWS KMS
```

Use SSE-KMS when you need stronger control and KMS-integrated governance.

---

# 18. SSE-S3 vs SSE-KMS

| Concern | SSE-S3 | SSE-KMS |
|---|---|---|
| Encryption at rest | Yes | Yes |
| KMS key control | No customer KMS key | Yes |
| Fine-grained key policy | Lower | Strong |
| KMS audit trail | No KMS key usage layer | Yes |
| Cross-account governance | Simpler | More controllable |
| Operational complexity | Lower | Higher |
| KMS request costs | No | Applicable |
| Typical fit | General encrypted storage | Governed sensitive data |

Do not claim that SSE-S3 is "insecure." It provides server-side encryption; the choice is about control, governance, and operational requirements.

---

# 19. S3 Bucket Keys

S3 Bucket Keys reduce the number of S3-to-KMS requests for SSE-KMS workloads.

AWS states that S3 Bucket Keys can reduce KMS request costs by up to 99% in applicable workloads.

They are particularly useful for:

```text
millions/billions of encrypted objects
high-volume object access
large data lakes
```

Conceptual path:

```text
S3 object
   ↓
S3 Bucket Key
   ↓
SSE-KMS
   ↓
KMS
```

Bucket Keys are not supported for DSSE-KMS.

Source: Amazon S3 S3 Bucket Keys documentation.

---

# 20. S3 Bucket Policy: TLS Enforcement

A common security requirement is to deny non-TLS requests.

Conceptual pattern:

```json
{
  "Sid": "DenyInsecureTransport",
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": [
    "arn:aws:s3:::example-bucket",
    "arn:aws:s3:::example-bucket/*"
  ],
  "Condition": {
    "Bool": {
      "aws:SecureTransport": "false"
    }
  }
}
```

This is a conceptual example.

Test policy interactions carefully before applying them to production.

---

# 21. S3 VPC Endpoint Restrictions

S3 bucket policies can restrict requests to a particular VPC endpoint using:

```text
aws:SourceVpce
```

or to a VPC using:

```text
aws:SourceVpc
```

Example:

```json
{
  "Sid": "DenyOutsideApprovedEndpoint",
  "Effect": "Deny",
  "Principal": "*",
  "Action": [
    "s3:GetObject",
    "s3:PutObject"
  ],
  "Resource": [
    "arn:aws:s3:::example-bucket/*"
  ],
  "Condition": {
    "StringNotEquals": {
      "aws:SourceVpce": "vpce-0123456789abcdef0"
    }
  }
}
```

This can accidentally block valid access paths, including administrative access, if designed carelessly.

AWS explicitly warns about lockout risk with endpoint-restricted bucket policies.

Source: Amazon S3 gateway endpoint and endpoint-policy documentation.

---

# 22. AWS Data Service Encryption

The learner must understand encryption for:

```text
Glue
Athena
Redshift
Kinesis
Firehose
EMR
MSK
```

For every service ask:

```text
What is encrypted?
Where is encryption configured?
Which key can be selected?
Which IAM/service permissions are required?
What happens when KMS access fails?
```

Exact service capabilities change. Verify current AWS documentation before implementing a production policy.

---

# 23. Glue Encryption

Glue can use encryption for supported artifacts and job-related data.

For a customer-managed KMS design, investigate:

```text
KMS key
Glue role
S3 bucket
Glue security configuration where applicable
job artifacts
temporary data
CloudWatch logs where applicable
```

Production question:

> Which exact Glue artifact am I protecting, and which service role needs which KMS action?

Do not grant `kms:*` to the Glue execution role merely because the job uses encrypted data.

---

# 24. Athena Encryption

Athena supports encryption of query results and related S3 locations.

Typical architecture:

```text
Athena
  ↓
S3 query-result location
  ↓
SSE-S3 or SSE-KMS
```

For SSE-KMS:

```text
Athena execution identity
+
S3 permissions
+
KMS permissions
```

must align.

A common failure is:

```text
Athena query succeeds logically
but result write fails with KMS AccessDenied
```

Investigate the complete authorization chain.

---

# 25. Redshift Encryption

Redshift encryption protects data at rest using AWS KMS integration.

Production design questions:

```text
Which KMS key?
Who can administer it?
Which Redshift service permissions are required?
How are snapshots protected?
How does cross-account sharing affect encryption?
```

Do not confuse:

```text
Redshift encryption
```

with:

```text
TLS client connectivity
```

Both may be required.

---

# 26. Kinesis Encryption

Kinesis Data Streams supports server-side encryption.

Conceptually:

```text
Producer
 ↓
Kinesis
 ↓
encrypted retained data
 ↓
Consumer
```

The security design must cover:

```text
stream encryption
KMS key
producer permissions
consumer permissions
key policy
```

For customer-managed KMS designs, verify current Kinesis KMS permissions and service behavior.

---

# 27. Firehose Encryption

Firehose can encrypt supported destination data using service-supported encryption mechanisms and KMS integrations.

Design questions:

```text
What destination?
What data is encrypted?
Which key?
Which delivery role?
What happens on KMS denial?
```

Do not generalize one destination's encryption model to all Firehose destinations.

Verify the current destination-specific documentation.

---

# 28. EMR Encryption

EMR security architecture can involve:

```text
S3 encryption
EBS encryption
local disk/storage encryption where supported
in-transit encryption
KMS
IAM
security groups
private networking
```

For this topic, focus on:

```text
EMR
 ↓
private subnet
 ↓
S3 / AWS services
 ↓
KMS
```

Topic 09 already covers EMR execution models. Here the question is:

> **How do I operate EMR without exposing the data platform unnecessarily?**

---

# 29. MSK Encryption

MSK security includes:

```text
encryption at rest
encryption in transit
client authentication
network isolation
security groups
KMS integration
```

Do not collapse Kafka authentication and encryption into the same concept.

```text
Encryption
=
protect data

Authentication
=
prove identity

Authorization
=
decide what identity can do
```

---

# 30. VPC Fundamentals

A VPC is a logically isolated virtual network.

Core components:

```text
VPC
├── CIDR
├── Subnets
├── Route tables
├── Internet Gateway
├── NAT Gateway
├── Security Groups
├── Network ACLs
├── DNS
└── VPC Endpoints
```

Data Engineering workloads commonly place:

```text
Glue
EMR
Lambda
Redshift
databases
connectors
```

inside controlled network boundaries.

---

# 31. CIDR and Subnets

Example:

```text
VPC
10.20.0.0/16
```

Subnets:

```text
Private-A
10.20.1.0/24

Private-B
10.20.2.0/24

Public-A
10.20.101.0/24
```

Subnets are associated with route tables.

A subnet being called "private" is a design convention based on its routing; it is not a special AWS object type.

---

# 32. Public vs Private Subnets

A simplified distinction:

```text
Public subnet
→ route to Internet Gateway

Private subnet
→ no direct route to Internet Gateway for workload egress
```

A private subnet may still reach the internet indirectly through:

```text
NAT Gateway
```

or reach AWS services privately through:

```text
VPC endpoints
```

---

# 33. Route Tables

Routing determines where traffic goes.

Example:

```text
10.20.0.0/16
→ local

0.0.0.0/0
→ NAT Gateway
```

For an S3 gateway endpoint:

```text
S3 prefix
→ gateway endpoint
```

The route table is therefore part of the security and connectivity model.

---

# 34. Security Groups

Security groups are stateful virtual firewalls.

They control traffic to resources/ENIs using:

```text
protocol
port
source/destination
```

For an interface endpoint:

```text
Client security group
        ↓
Endpoint security group
        ↓
AWS service
```

A common mistake is allowing:

```text
0.0.0.0/0
```

when only an application subnet/security group needs access.

Prefer narrowly scoped rules.

---

# 35. DNS in Private Data Platforms

Private networking can fail even when routing is correct.

Why?

```text
DNS resolution
```

A workload may need to resolve:

```text
secretsmanager.<region>.amazonaws.com
glue.<region>.amazonaws.com
sts.<region>.amazonaws.com
```

to an endpoint/private address depending on the endpoint and DNS configuration.

Troubleshooting must therefore include:

```text
DNS
+
routing
+
security groups
+
endpoint
```

---

# 36. NAT Gateway

A common private-subnet architecture is:

```text
Private subnet
      ↓
NAT Gateway
      ↓
Internet Gateway
      ↓
Internet
```

NAT provides outbound internet access for private resources.

It is useful when workloads need:

```text
public package repositories
external APIs
internet-hosted dependencies
```

But NAT can be unnecessary for AWS-service access when a suitable VPC endpoint exists.

Do not say:

> "Endpoints always eliminate NAT."

A workload may still need internet access for external destinations.

---

# 37. VPC Endpoints

A VPC endpoint provides private connectivity from a VPC to supported AWS services.

Two major categories:

```text
Gateway endpoint
Interface endpoint
```

This distinction is central to AWS Data Engineering networking.

---

# 38. Gateway Endpoints

Gateway endpoints use route tables.

Supported core services include:

```text
S3
DynamoDB
```

For S3:

```text
Private subnet
     ↓
Route table
     ↓
S3 gateway endpoint
     ↓
S3
```

AWS documents that gateway endpoints for S3 and DynamoDB do not have an additional endpoint charge.

Gateway endpoints do not use AWS PrivateLink.

Source: AWS VPC gateway endpoint documentation.

---

# 39. Why S3 Gateway Endpoints Matter

Data platforms frequently move:

```text
GBs
TBs
PBs
```

through S3.

Using an S3 gateway endpoint can provide:

```text
private AWS-network path
+
no NAT requirement for that S3 path
+
no additional gateway endpoint charge
```

This makes it foundational for private data platforms.

---

# 40. Interface Endpoints

Interface endpoints use:

```text
Elastic Network Interfaces
+
private IP addresses
+
security groups
```

Conceptually:

```text
Private workload
      ↓
Interface endpoint ENI
      ↓
AWS PrivateLink
      ↓
AWS service
```

Interface endpoints generally incur endpoint-related charges, including hourly endpoint/AZ and data-processing charges according to current AWS pricing.

Never hard-code current prices in a learning artifact.

---

# 41. AWS PrivateLink

AWS PrivateLink is the underlying private-connectivity technology used by interface VPC endpoints.

Mental model:

```text
Client VPC
    ↓
ENI with private IP
    ↓
PrivateLink
    ↓
Supported service
```

Benefits:

- private IP connectivity
- no need for public internet routing to the supported service
- security-group control
- service-specific private connectivity

Not every AWS service is available through an interface endpoint in every Region.

Always verify current endpoint availability.

---

# 42. Gateway vs Interface Endpoints

| Feature | Gateway | Interface |
|---|---|---|
| Mechanism | Route table | ENI |
| Private IP ENI | No | Yes |
| PrivateLink | No | Yes |
| Common service | S3/DynamoDB | Many AWS services |
| Security groups | Not the same model | Yes |
| Endpoint policy | Yes | Yes |
| Hourly endpoint pricing | No additional charge for gateway endpoints | Applies |
| Data processing charge | Verify current service/pricing | Applies under current model |
| On-premises access | Not through gateway path | Possible with supported connectivity |
| Data Engineering value | Extremely high for S3 | High for private AWS services |

AWS documents that S3 supports both gateway and interface endpoints.

---

# 43. Endpoint Policies

An endpoint policy is a resource-based policy attached to a VPC endpoint.

It controls which principals can use the endpoint to access a service.

Important:

> **An endpoint policy does not replace IAM or resource policies.**

Authorization can look like:

```text
Network path
      ↓
Endpoint
      ↓
Endpoint policy
      ↓
IAM policy
      ↓
Resource policy
      ↓
KMS policy
```

Not every request uses every layer, but the layered model is essential for troubleshooting.

---

# 44. Endpoint Policy Example

Conceptual S3 endpoint policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowDataBucketOnly",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::data-platform-gold",
        "arn:aws:s3:::data-platform-gold/*"
      ]
    }
  ]
}
```

This is intentionally simplified.

Production policies should be reviewed with:

```text
IAM
bucket policy
service dependencies
AWS-managed buckets
automation roles
```

---

# 45. Private Glue

A production Glue architecture can be:

```text
                 AWS Data Platform VPC
                         |
                  Private subnet
                         |
                      Glue job
                    /    |    \
                   /     |     \
                  v      v      v
                 S3   Secrets   KMS
                  |   Manager
                  |      |
                  +------+
                 VPC endpoints
```

Required design questions:

- S3 access path
- Glue service connectivity
- Secrets Manager endpoint if required
- STS endpoint where required by the workload
- KMS/network path
- security groups
- DNS
- route tables
- IAM role
- endpoint policies
- external dependencies

Do not assume "put Glue in a private subnet" automatically makes the job work.

---

# 46. Glue Without NAT

A private Glue workload may avoid NAT for AWS-service dependencies if the required services are reachable through appropriate private endpoints and the job has no external internet dependency.

Example:

```text
Glue
 ↓
Private subnet
 ↓
S3 gateway endpoint
 ↓
S3
```

and:

```text
Glue
 ↓
Secrets Manager interface endpoint
 ↓
Secrets
```

However:

```text
external PyPI
external API
GitHub
public package repository
```

may still require an appropriate egress design.

Therefore:

> **"No NAT" is a workload-specific architecture decision, not a universal rule.**

---

# 47. EMR Private Networking

EMR can run in private subnets.

Core concerns:

```text
EMR compute
 ↓
private subnet
 ↓
security groups
 ↓
S3 / AWS services
 ↓
KMS
```

Depending on the EMR deployment model and workload, the cluster/application may need access to:

- S3
- logging services
- STS
- Glue APIs
- Secrets Manager
- KMS
- package/dependency sources
- other AWS services

Topic 09 covers EMR execution models; this topic focuses on private connectivity and authorization.

---

# 48. Redshift Private Networking

A private Redshift architecture includes:

```text
VPC
 ├── private subnets
 ├── Redshift subnet group
 └── security groups
```

Applications connect through private network paths.

Security layers:

```text
Network
+
authentication
+
authorization
+
encryption
+
KMS
```

Private placement does not eliminate the need for identity controls.

---

# 49. Lambda in a VPC

Lambda can attach to VPC subnets to reach private resources.

Example:

```text
Lambda
 ↓
Private subnet
 ↓
RDS
```

But VPC attachment can change how the function reaches other services.

Possible symptoms:

```text
timeout
```

may result from:

- missing route
- missing NAT
- missing interface endpoint
- security-group restriction
- DNS failure
- wrong subnet
- service connectivity problem

Therefore:

> **Lambda timeout does not automatically mean application code is wrong.**

---

# 50. Secrets Manager

Never hard-code:

```text
database passwords
API keys
tokens
credentials
```

Use AWS Secrets Manager for managed secret storage.

Conceptual flow:

```text
Application / Glue / DMS
        ↓
Secrets Manager
        ↓
Secret value
```

Security layers:

```text
IAM
+
Secrets Manager resource policy where applicable
+
KMS
+
network path
```

---

# 51. Secrets Manager Python Example

```python
import json
import boto3

client = boto3.client("secretsmanager")

response = client.get_secret_value(
    SecretId="prod/data/orders"
)

secret = json.loads(response["SecretString"])

print(secret["username"])
```

Production requirements:

- use the AWS credential chain
- never hard-code credentials
- avoid printing secret values
- handle `ClientError`
- restrict `secretsmanager:GetSecretValue`
- use KMS appropriately
- use a private endpoint when the workload requires private AWS-service access
- understand rotation behavior

---

# 52. Secrets Manager + Glue

Architecture:

```text
Glue job
   ↓
Secrets Manager
   ↓
database credentials
   ↓
private database
```

Required controls:

```text
Glue execution role
→ GetSecretValue

KMS
→ decrypt permission as required

VPC
→ endpoint/network path

Database
→ security group / authentication
```

---

# 53. Secrets Manager + DMS

DMS credentials should be managed through supported secure mechanisms rather than source-code literals.

Architecture:

```text
DMS
 ├── source credentials
 └── target credentials
          ↓
    Secrets Manager
          ↓
        KMS
```

Also verify:

```text
DMS network path
source connectivity
target connectivity
IAM permissions
secret access
```

Topic 11 covers DMS replication; this section focuses on secure credential management.

---

# 54. Secrets Manager + Redshift

Use Secrets Manager where supported for database credentials and integrate it with:

```text
Redshift
+
private networking
+
KMS
+
IAM
```

Prefer short-lived/identity-based authentication where appropriate and supported rather than creating permanent credentials unnecessarily.

---

# 55. Cross-Account Encryption

Example:

```text
Account A
Data Platform
    |
    v
Encrypted S3
    |
    v
Customer-managed KMS key
    |
    v
Account B
Analytics Consumer
```

Cross-account access commonly requires alignment between:

```text
KMS key policy
+
consumer IAM policy
+
S3 bucket policy
+
cross-account role/trust
+
resource ownership
```

A single missing layer can produce `AccessDenied`.

---

# 56. Cross-Account KMS Troubleshooting Matrix

| Symptom | Check |
|---|---|
| S3 AccessDenied | Bucket policy + IAM |
| KMS AccessDenied | Key policy + IAM + grant |
| Consumer cannot decrypt | `kms:Decrypt` + key policy |
| Producer cannot encrypt | `kms:GenerateDataKey` / encryption permission |
| Role assumption fails | Trust policy |
| Data visible but unreadable | KMS authorization |
| Works in owner account only | Cross-account policy alignment |

Never solve cross-account issues by adding:

```text
kms:*
```

to every role.

---

# 57. Cross-Account Data Lake Architecture

One possible enterprise pattern:

```text
             Security / Governance Account
                         |
                 Governance controls
                         |
                         v
                Data Platform Account
                  /       |       \
                 S3      Glue     Lake Formation
                  |
                  v
             Encrypted Data
                  |
          Cross-account sharing
                  |
          +-------+-------+
          |               |
      Analytics A     Analytics B
```

This is one pattern, not a universal mandate.

Alternatives include:

- domain-owned KMS keys
- centralized key administration with delegated usage
- separate security boundaries
- organization-level controls

Choose based on ownership and blast radius.

---

# 58. Data Perimeters

Data perimeter thinking expands security beyond:

```text
Who are you?
```

to:

```text
Which identity?
Which resource?
Which network?
Which organization?
Which service path?
```

Mental model:

```text
Trusted identity
       +
trusted resource
       +
expected network
       =
allowed access
```

Important concepts:

- identity perimeter
- resource perimeter
- network perimeter
- VPC endpoints
- resource policies
- AWS Organizations
- service control policies
- organization condition keys

This is awareness, not a full SCP course.

---

# 59. VPC Endpoint + Data Perimeter

A private endpoint can become part of a network-perimeter design:

```text
Workload
   ↓
Approved VPC
   ↓
Approved VPC endpoint
   ↓
Approved AWS resource
```

Resource policies can enforce:

```text
only approved VPC
or
only approved endpoint
or
only approved organization
```

Use defense in depth.

---

# 60. VPN Awareness

VPN can connect an AWS VPC to an external network.

```text
Corporate Network
       ↕
Encrypted VPN
       ↕
AWS VPC
```

Useful for:

- private databases
- on-premises data sources
- hybrid ETL
- internal APIs

Consider:

```text
latency
throughput
resilience
routing
security
operational ownership
```

---

# 61. Direct Connect Awareness

Direct Connect provides dedicated connectivity between an external network and AWS.

Conceptually:

```text
Corporate network
       ↓
Direct Connect
       ↓
AWS connectivity
       ↓
VPC
```

Compare it with VPN based on:

```text
latency
predictability
resilience
bandwidth
cost
operational complexity
```

Do not insert current pricing without checking AWS pricing documentation.

---

# 62. Layered Troubleshooting Model

When a private data workload fails:

```text
1. DNS
2. Route
3. Security Group
4. Endpoint
5. Endpoint Policy
6. IAM
7. Resource Policy
8. KMS
9. Application Configuration
```

Not every failure uses every layer.

Use evidence to eliminate layers.

---

# 63. Required Incident — KMS AccessDenied

Scenario:

```text
Glue
  ↓
S3 SSE-KMS
  ↓
AccessDenied
```

Investigate in order:

```text
1. Which IAM role is Glue using?
2. Does IAM permit S3?
3. Which KMS key protects the object?
4. Does the key policy trust the relevant principal/account?
5. Is the required KMS operation allowed?
6. Is a grant involved?
7. Does the bucket policy permit the request?
8. Did CloudTrail record the denial/change?
```

Do not immediately grant:

```text
kms:*
```

Fix the smallest missing permission.

---

# 64. Required Incident — Private Network Timeout

Scenario:

```text
Private Glue job
      ↓
Secrets Manager
      ↓
Timeout
```

Investigate:

```text
DNS
↓
subnet
↓
route table
↓
interface endpoint
↓
endpoint subnet
↓
endpoint security group
↓
endpoint policy
↓
IAM
↓
Secrets Manager service status
↓
NAT if external access is involved
```

A timeout usually indicates connectivity.

An `AccessDenied` usually indicates authorization.

But validate rather than assuming.

---

# 65. Break/Fix Scenario Matrix

| Failure | Expected symptom | First evidence |
|---|---|---|
| KMS key policy denial | AccessDenied | CloudTrail + key policy |
| S3 bucket policy denial | AccessDenied | S3/IAM/CloudTrail |
| Missing endpoint | Timeout / connection failure | DNS/routes/endpoints |
| Endpoint policy denial | AccessDenied | endpoint policy |
| Security group failure | timeout | SG rules/flow evidence |
| DNS failure | hostname resolution failure | DNS tests |
| Secrets endpoint missing | timeout | endpoint/DNS |
| Cross-account KMS failure | decrypt/encrypt denied | key policy + IAM |
| NAT cost spike | bill increase | Cost Explorer |
| Interface endpoint cost spike | bill increase | cost/service dimensions |

---

# 66. Hands-On Project — `infra/network_security/`

Build a complete learning environment conceptually under:

```text
infra/network_security/
```

Do not create project files as part of this Markdown artifact.

The lab should contain:

```text
network/
kms/
s3/
endpoints/
security/
secrets/
tests/
docs/
```

The goal is a secure private data lab.

---

# 67. Lab 1 — Customer-Managed KMS Keys

Create:

```text
silver KMS key
gold KMS key
```

Practice:

- aliases
- key policies
- administrators
- workload users
- rotation
- CloudTrail auditing
- S3 integration

Deliver:

```text
key policy
IAM policy
architecture diagram
test results
runbook
```

---

# 68. Lab 2 — Private VPC

Create:

```text
VPC
├── private subnet A
├── private subnet B
├── route tables
├── S3 gateway endpoint
├── required interface endpoints
└── security groups
```

Validate:

```text
DNS
routing
S3 access
Secrets Manager access
KMS access
```

---

# 69. Lab 3 — S3 Gateway Endpoint

Create an S3 gateway endpoint.

Validate:

```text
Private workload
→ S3
```

without requiring NAT for the S3 path.

Test:

```bash
aws s3 ls s3://YOUR_BUCKET/
```

from the appropriate workload environment.

Confirm route-table behavior.

---

# 70. Lab 4 — Interface Endpoints

Select only the AWS services actually required by your workload.

Examples may include:

```text
Secrets Manager
STS
KMS
Glue
Kinesis
```

Verify endpoint support in your Region before creating them.

For each endpoint document:

```text
service
subnets
security group
private DNS
endpoint policy
reason
cost consideration
```

---

# 71. Lab 5 — Private Glue

Run a Glue workload in a VPC.

Validate:

```text
S3
Secrets Manager
KMS
required Glue dependencies
```

without NAT if the workload has no external-internet dependency.

Break:

```text
remove an endpoint
```

Observe:

```text
failure
```

Restore it.

Verify:

```text
successful execution
```

---

# 72. Lab 6 — S3 Bucket Policy Restrictions

Implement:

```text
TLS-only access
+
approved VPC endpoint access
```

Test:

```text
approved endpoint
→ allowed

unapproved path
→ denied
```

Document the risk of accidentally locking out administrative access.

---

# 73. Lab 7 — Secrets Manager

Create a test secret.

Use:

```text
IAM
+
KMS
+
private endpoint
```

Test:

```text
valid role
→ allowed

wrong role
→ denied
```

Never print the secret value in logs.

---

# 74. Lab 8 — Endpoint vs NAT Cost Analysis

Build a spreadsheet or notebook calculation externally during the lab.

Compare:

```text
NAT Gateway
vs
Gateway endpoint
vs
Interface endpoint
```

Variables:

```text
monthly hours
GB processed
number of AZs
number of endpoints
number of services
cross-AZ traffic
```

Use current AWS pricing.

Do not use prices copied from old tutorials.

---

# 75. Lab 9 — KMS AccessDenied Incident

Intentionally make the key policy too restrictive.

Expected:

```text
Glue/S3
→ AccessDenied
```

Diagnose:

```text
IAM
→ KMS key policy
→ grant
→ S3 policy
→ CloudTrail
```

Fix only the required authorization.

---

# 76. Lab 10 — Private Network Timeout Incident

Remove an interface endpoint.

Expected:

```text
Secrets Manager
→ timeout
```

Diagnose:

```text
DNS
→ endpoint
→ route
→ SG
→ endpoint policy
→ IAM
```

Restore the endpoint and verify recovery.

---

# 77. AWS CLI — KMS

Describe a key:

```bash
aws kms describe-key \
  --key-id alias/data-platform-gold
```

Inspect policy:

```bash
aws kms get-key-policy \
  --key-id alias/data-platform-gold \
  --policy-name default
```

List aliases:

```bash
aws kms list-aliases
```

Verify the exact CLI syntax against the installed AWS CLI version.

---

# 78. AWS CLI — VPC Endpoints

List endpoints:

```bash
aws ec2 describe-vpc-endpoints
```

Filter by VPC where appropriate.

Inspect:

```text
VpcEndpointId
VpcId
ServiceName
VpcEndpointType
RouteTableIds
SubnetIds
Groups
PolicyDocument
PrivateDnsEnabled
State
```

Do not assume all fields apply equally to gateway and interface endpoints.

---

# 79. AWS CLI — Security Groups

```bash
aws ec2 describe-security-groups \
  --group-ids sg-0123456789abcdef0
```

Look for:

```text
ingress
egress
protocol
port
source
destination
```

---

# 80. AWS CLI — Secrets Manager

List secrets:

```bash
aws secretsmanager list-secrets
```

Retrieve a specific secret only when authorized:

```bash
aws secretsmanager get-secret-value \
  --secret-id prod/data/orders
```

Do not paste returned secret values into tickets, logs, shell history, or source control.

---

# 81. Python / boto3 — KMS

```python
import boto3

kms = boto3.client("kms")

response = kms.describe_key(
    KeyId="alias/data-platform-gold"
)

print(response["KeyMetadata"]["Arn"])
```

Production considerations:

```text
credential chain
Region
IAM permission
error handling
CloudTrail
```

Never embed access keys.

---

# 82. Python / boto3 — VPC Endpoints

```python
import boto3

ec2 = boto3.client("ec2")

response = ec2.describe_vpc_endpoints(
    Filters=[
        {
            "Name": "vpc-id",
            "Values": ["vpc-0123456789abcdef0"],
        }
    ]
)

for endpoint in response["VpcEndpoints"]:
    print(
        endpoint["VpcEndpointId"],
        endpoint["VpcEndpointType"],
        endpoint["ServiceName"],
        endpoint["State"],
    )
```

Use the AWS credential provider chain.

Handle:

```text
AccessDenied
Throttling
invalid IDs
Region mismatch
```

---

# 83. Python / boto3 — Secrets Manager

```python
import json
import boto3
from botocore.exceptions import ClientError

client = boto3.client("secretsmanager")

try:
    response = client.get_secret_value(
        SecretId="prod/data/orders"
    )
    secret = json.loads(response["SecretString"])
except ClientError as exc:
    raise RuntimeError("Unable to retrieve secret") from exc
```

Do not log:

```python
secret
```

or individual credentials.

---

# 84. Terraform — KMS Key

```hcl
resource "aws_kms_key" "gold" {
  description         = "KMS key for gold data"
  enable_key_rotation = true

  tags = {
    Environment = var.environment
    DataClass   = "gold"
    ManagedBy   = "terraform"
  }
}

resource "aws_kms_alias" "gold" {
  name          = "alias/data-platform-gold"
  target_key_id = aws_kms_key.gold.key_id
}
```

Important:

```text
resource creation
≠
complete authorization design
```

Add a deliberate key policy.

Verify current AWS provider behavior before production use.

---

# 85. Terraform — S3 SSE-KMS + Bucket Key

```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "gold" {
  bucket = aws_s3_bucket.gold.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.gold.arn
    }

    bucket_key_enabled = true
  }
}
```

Validate current Terraform AWS provider syntax before applying.

---

# 86. Terraform — S3 Gateway Endpoint

```hcl
resource "aws_vpc_endpoint" "s3" {
  vpc_id          = aws_vpc.data.id
  service_name    = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.private_a.id,
    aws_route_table.private_b.id,
  ]
}
```

The exact service name and provider behavior are Region/provider dependent; verify before deployment.

---

# 87. Terraform — Interface Endpoint

Conceptual pattern:

```hcl
resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.data.id
  service_name        = "com.amazonaws.${var.aws_region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnet_ids
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true
}
```

Do not create an interface endpoint just because a service has one.

First ask:

```text
Do we need it?
Which workload needs it?
Which AZs?
What traffic?
What cost?
What policy?
```

---

# 88. Terraform — Endpoint Security Group

```hcl
resource "aws_security_group" "endpoints" {
  name   = "data-endpoints"
  vpc_id = aws_vpc.data.id

  ingress {
    description     = "HTTPS from data workloads"
    protocol        = "tcp"
    from_port       = 443
    to_port         = 443
    security_groups = [aws_security_group.data_workloads.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

The egress rule is an example, not a universal production recommendation.

Review least privilege for the actual architecture.

---

# 89. Terraform — Secrets Manager

```hcl
resource "aws_secretsmanager_secret" "orders" {
  name = "prod/data/orders"

  kms_key_id = aws_kms_key.secrets.arn

  tags = {
    Environment = "prod"
    Owner       = "data-platform"
  }
}
```

Store the secret value through an appropriate secure workflow.

Do not put plaintext credentials in Terraform source or state unless your state-security model explicitly accounts for them.

---

# 90. Production Security Best Practices

## KMS

- separate administrators and users
- use least privilege
- avoid broad `kms:*`
- use aliases
- rotate where required
- audit usage
- use service conditions where appropriate
- protect key lifecycle
- document ownership

## S3

- encrypt at rest
- use SSE-KMS where governance requires it
- consider Bucket Keys
- enforce TLS
- restrict network paths where justified
- block public access
- audit sensitive data access

## VPC

- use private subnets for sensitive workloads
- minimize internet exposure
- use least-privilege security groups
- use VPC endpoints for supported AWS services
- design DNS deliberately
- document routes

## Secrets

- use Secrets Manager
- rotate credentials
- do not hard-code secrets
- do not log secrets
- limit `GetSecretValue`
- protect the KMS key

## IAM

- workload-specific roles
- short-lived credentials
- no unnecessary admin
- separate operators from applications
- review cross-account trust

---

# 91. Decision Matrix — SSE-S3 vs SSE-KMS

| Question | SSE-S3 | SSE-KMS |
|---|---|---|
| Need simple encryption? | Strong fit | Also works |
| Need customer key control? | No | Yes |
| Need KMS audit evidence? | No KMS key layer | Yes |
| Need granular key policy? | No | Yes |
| Need cross-account key governance? | Limited | Stronger |
| Operational burden | Low | Higher |
| Cost complexity | Lower | Higher |

Decision principle:

```text
Use SSE-KMS when the security/control requirement justifies KMS.
Do not use KMS solely because "production means KMS."
```

---

# 92. Decision Matrix — AWS-Managed vs Customer-Managed KMS

| Dimension | AWS-managed | Customer-managed |
|---|---|---|
| Setup | Easy | More work |
| Key policy control | Limited | High |
| Lifecycle control | AWS | Customer |
| Cross-account | More constrained | Stronger control |
| Governance | Moderate | Strong |
| Operational burden | Low | Higher |
| Best fit | Standard workloads | Security boundaries |

---

# 93. Decision Matrix — NAT vs VPC Endpoint

| Dimension | NAT Gateway | VPC Endpoint |
|---|---|---|
| Primary purpose | Internet egress | Private AWS-service access |
| Public internet path | Yes, outbound | No for supported endpoint path |
| External APIs | Yes | No |
| AWS service access | Often works | Targeted |
| Cost model | Hourly + processing | Endpoint-specific |
| S3 gateway option | Not required | Strong fit |
| Security posture | Broader egress | Narrower |
| Operational model | Central egress | Service-specific |

Do not eliminate NAT if the workload genuinely needs external internet access.

---

# 94. Decision Matrix — Gateway vs Interface Endpoint

| Dimension | Gateway | Interface |
|---|---|---|
| Route table | Yes | No |
| ENI | No | Yes |
| Security group | Not endpoint-ENI based | Yes |
| PrivateLink | No | Yes |
| S3 | Yes | Yes |
| DynamoDB | Yes | Yes |
| Many AWS services | No | Yes |
| On-premises access | Not via gateway endpoint | Possible |
| Cost | No additional gateway endpoint charge | Endpoint charges apply |

Always verify current regional service support.

---

# 95. Production Architecture — Secure Data Lake

```text
                         AWS Organization
                                |
                    +-----------+-----------+
                    |                       |
              Security Account        Data Platform Account
                    |                       |
               CloudTrail              VPC / Private Subnets
                                            |
                          +-----------------+-----------------+
                          |                 |                 |
                        Glue              EMR             Redshift
                          |                 |                 |
                          +--------+--------+-----------------+
                                   |
                              VPC Endpoints
                              /     |      \
                             S3   Secrets   KMS
                              |
                         Encrypted S3
                              |
                        SSE-KMS + Bucket Key
                              |
                         Glue / Athena
                              |
                        Consumer Accounts
```

Security layers:

```text
IAM
+
VPC
+
Endpoints
+
Endpoint policies
+
S3 policies
+
KMS
+
CloudTrail
```

---

# 96. Production Architecture — Private ETL

```text
Private VPC
│
├── Private Subnet A
│     └── Glue / compute
│
├── Private Subnet B
│     └── Glue / compute
│
├── S3 Gateway Endpoint
│
├── Secrets Manager Interface Endpoint
│
├── KMS Interface Endpoint where required by workload
│
├── STS Interface Endpoint where required
│
└── Endpoint Security Groups
```

Goal:

```text
No unnecessary internet path
+
private AWS service access
+
least privilege
+
encrypted data
```

---

# 97. Production Architecture — Hybrid Data Platform

```text
On-Premises
     |
     +---- VPN
     |
     +---- Direct Connect
     |
     v
AWS VPC
     |
Private subnets
     |
+----+----------------------+
|                           |
Data workloads           AWS endpoints
|                           |
RDS / EMR / Glue        S3 / Secrets / KMS
|
Encrypted data
```

Use hybrid connectivity when data sources or enterprise systems remain outside AWS.

---

# 98. Cost Engineering

Security architecture has cost implications.

Potential costs include:

```text
KMS key usage
KMS key existence
NAT Gateway
NAT data processing
Interface endpoints
Endpoint data processing
Cross-AZ traffic
VPN
Direct Connect
CloudWatch
CloudTrail
```

Never optimize cost by disabling a required security control.

Optimize:

```text
unnecessary NAT
unnecessary endpoints
unnecessary cross-AZ traffic
unnecessary KMS requests
unnecessary logs
unnecessary data transfer
```

---

# 99. Endpoint vs NAT Cost Model

Do not hard-code prices.

Use formulas.

### NAT

```text
Monthly cost
=
NAT hourly charge
+
NAT data-processing charge
+
related network-transfer effects
```

### Interface endpoints

```text
Monthly cost
=
endpoint/AZ hourly charges
+
endpoint data-processing charges
```

### Gateway endpoint

```text
Gateway endpoint usage
=
no additional gateway endpoint charge
```

Then compare:

```text
traffic volume
+
number of AZs
+
number of services
+
endpoint count
+
NAT count
```

Use current AWS pricing pages when calculating actual dollars.

---

# 100. Cost Scenario

Suppose:

```text
Private workloads
→ 20 TB/month
→ 3 AZs
→ 5 AWS services
```

Do not immediately choose:

```text
5 × 3 interface endpoints
```

Ask:

```text
Which services truly require interface endpoints?
Can S3 use gateway endpoint?
Can endpoints be shared safely?
What is the cross-AZ path?
Does the workload still need NAT?
What are the security requirements?
```

The cheapest architecture is not always the correct architecture.

---

# 101. Security vs Cost Trade-off

Use:

```text
Security
+
Reliability
+
Performance
+
Cost
```

Do not optimize one dimension blindly.

Example:

```text
centralized endpoint architecture
```

may reduce endpoint count but introduce:

```text
cross-AZ traffic
+
routing complexity
+
blast radius
```

An endpoint per workload/AZ may improve isolation but increase cost.

Architect for the actual operating model.

---

# 102. ADR Exercise — KMS Key Strategy

Decision:

> Should the data platform use one KMS key or separate keys for bronze, silver, and gold?

Evaluate:

```text
blast radius
ownership
access boundaries
rotation
cross-account
audit
cost
operational burden
```

Record:

```text
Context
Decision
Alternatives
Security consequences
Cost consequences
Operational consequences
```

---

# 103. ADR Exercise — NAT vs Endpoints

Decision:

> Should a private Glue workload use NAT or VPC endpoints?

Document:

```text
AWS dependencies
external dependencies
traffic volume
security requirements
cost
availability
operations
```

---

# 104. ADR Exercise — S3 Access Boundary

Decision:

> Should the gold bucket allow access only through approved VPC endpoints?

Evaluate:

```text
workload access
operator access
cross-account access
break-glass access
CloudTrail evidence
lockout risk
```

---

# 105. ADR Exercise — Cross-Account KMS

Decision:

> Where should the customer-managed KMS key live?

Compare:

```text
data-owner account
security account
central key-management account
domain-specific keys
```

Do not assume centralization is always better.

---

# 106. Runbook — KMS AccessDenied

**Symptom**

```text
AccessDeniedException
```

**Evidence**

```text
caller identity
resource ARN
KMS key ARN
CloudTrail
IAM policy
key policy
grant
bucket policy
```

**Diagnosis**

```text
Identify the missing authorization layer.
```

**Fix**

```text
Add only the required permission.
```

**Verification**

```text
retry
→ successful operation
→ confirm CloudTrail
```

**Prevention**

```text
policy tests
IaC review
least privilege
```

---

# 107. Runbook — Private Network Timeout

**Symptom**

```text
connection timeout
```

**Check**

```text
DNS
route table
subnet
endpoint
endpoint ENI
security group
endpoint policy
IAM
service availability
NAT if applicable
```

**Fix**

Restore the missing connectivity layer.

**Verify**

```text
DNS resolves
→ TCP/TLS connects
→ AWS API works
→ workload succeeds
```

---

# 108. Runbook — S3 AccessDenied Through Endpoint

Check:

```text
IAM
↓
S3 bucket policy
↓
aws:SourceVpce / aws:SourceVpc
↓
endpoint policy
↓
KMS
```

Remember:

```text
S3 access
+
KMS access
```

are separate authorization problems.

---

# 109. Runbook — Secrets Manager Timeout

Check:

```text
DNS
endpoint exists
endpoint private DNS
route
endpoint SG
endpoint policy
IAM
KMS
secret state
```

If DNS resolves but connection times out:

```text
network path
```

is more likely than IAM.

If connection works but access is denied:

```text
authorization
```

is more likely.

---

# 110. Runbook — Endpoint Cost Spike

Investigate:

```text
number of endpoints
number of AZs
traffic volume
services
data processing
cross-AZ traffic
new workloads
```

Do not delete endpoints before understanding which workloads depend on them.

---

# 111. Common Mistakes

## Mistake 1

> "Private subnet means no internet."

Correction:

A private subnet can have NAT-based internet egress.

## Mistake 2

> "Endpoint means no IAM."

Correction:

Endpoints provide connectivity, not blanket authorization.

## Mistake 3

> "KMS permission is enough."

Correction:

KMS authorization can require key policy + IAM + grants.

## Mistake 4

> "NAT is always required."

Correction:

AWS service dependencies can often use VPC endpoints.

## Mistake 5

> "Endpoints are always cheaper."

Correction:

Interface endpoints have their own cost model.

## Mistake 6

> "Use kms:* to fix AccessDenied."

Correction:

Fix the specific missing authorization.

## Mistake 7

> "Lambda timeout means code bug."

Correction:

VPC networking can cause timeouts.

## Mistake 8

> "Every AWS service has an endpoint."

Correction:

Verify service and Region support.

## Mistake 9

> "Cross-account access only needs IAM."

Correction:

Resource and KMS policies may also be involved.

## Mistake 10

> "Encryption means authorization is solved."

Correction:

Encryption and authorization are different controls.

---

# 112. Interview Preparation — Beginner

### Q1. What is AWS KMS?

**Model answer:**  
A managed AWS service for creating and controlling cryptographic keys and performing or enabling cryptographic operations used by AWS services and applications.

### Q2. What is a customer-managed KMS key?

**Model answer:**  
A KMS key created and controlled by the customer, including its policy, lifecycle, and rotation configuration.

### Q3. What is a VPC endpoint?

**Model answer:**  
A private connectivity mechanism that allows resources in a VPC to reach supported AWS services without relying on the public internet path.

### Q4. Gateway vs interface endpoint?

**Model answer:**  
Gateway endpoints integrate with route tables and are commonly used for S3/DynamoDB. Interface endpoints create ENIs with private IPs and use AWS PrivateLink.

### Q5. Why use Secrets Manager?

**Model answer:**  
To store and retrieve secrets securely instead of embedding credentials in source code or configuration.

---

# 113. Interview Preparation — Intermediate

### Q6. Why can a Glue job in a private subnet fail?

**Answer:**  
Because the workload may lack a route, required VPC endpoint, DNS resolution, security-group permission, endpoint policy, IAM permission, or KMS access.

### Q7. Why does an S3 bucket policy use `aws:SourceVpce`?

**Answer:**  
To restrict bucket access to requests originating through a specified VPC endpoint, when that network restriction is appropriate.

### Q8. Why can SSE-KMS create additional operational complexity?

**Answer:**  
It introduces KMS authorization, key lifecycle, key-policy, grants, auditing, and KMS-related request considerations.

### Q9. Why can interface endpoints cost more than expected?

**Answer:**  
Endpoint charges depend on factors such as endpoint/AZ count and data processed, so large numbers of endpoints and high traffic can materially affect cost.

### Q10. Why is NAT not automatically replaced by endpoints?

**Answer:**  
Endpoints target supported AWS services. Workloads may still need external internet destinations.

---

# 114. Interview Preparation — Senior

### Q11. Design a private Glue data platform without NAT.

**Model answer:**

```text
Private subnets
+
S3 gateway endpoint
+
required interface endpoints
+
DNS
+
security groups
+
endpoint policies
+
IAM
+
KMS
+
Secrets Manager
```

Then explicitly identify any external dependencies that would still require egress.

### Q12. Diagnose KMS AccessDenied.

**Model answer:**

```text
caller
→ IAM
→ key ARN
→ key policy
→ grant
→ service context
→ resource policy
→ CloudTrail
```

Fix the smallest missing permission.

### Q13. How would you design cross-account encrypted S3?

**Model answer:**

```text
S3 bucket policy
+
consumer IAM
+
KMS key policy
+
cross-account role/trust
+
least privilege
+
audit
```

### Q14. When should you use customer-managed KMS keys?

**Model answer:**  
When the platform needs explicit control over key policy, lifecycle, audit, cross-account authorization, or security boundaries.

---

# 115. Interview Preparation — Staff Level

### Q15. Design a zero-trust AWS data platform.

A strong answer includes:

```text
identity perimeter
resource perimeter
network perimeter
private subnets
VPC endpoints
least privilege
KMS
Secrets Manager
S3 policy controls
organization governance
CloudTrail
centralized audit
```

### Q16. How do you balance endpoint security and cost?

Use:

```text
required service paths
+
gateway endpoints where appropriate
+
selective interface endpoints
+
AZ-aware design
+
traffic analysis
+
shared vs isolated architecture
```

### Q17. What is the difference between network isolation and data protection?

Network isolation controls:

```text
where traffic can travel
```

Encryption controls:

```text
whether intercepted/stored data can be read
```

Identity controls:

```text
who can perform actions
```

All three are required in mature systems.

---

# 116. Practice Questions — Conceptual

1. What problem does KMS solve?
2. What is envelope encryption?
3. What is a customer-managed key?
4. What is an AWS-managed key?
5. Why does every KMS key have a key policy?
6. What is a KMS grant?
7. What is key rotation?
8. SSE-S3 vs SSE-KMS?
9. What are S3 Bucket Keys?
10. What is a VPC?
11. What makes a subnet private?
12. What is a route table?
13. What is a security group?
14. What is a NAT Gateway?
15. What is a gateway endpoint?
16. What is an interface endpoint?
17. What is AWS PrivateLink?
18. What is an endpoint policy?
19. Why is DNS important for private endpoints?
20. What is a data perimeter?

---

# 117. Practice Questions — Scenario

21. Glue in a private subnet cannot write to S3. Diagnose it.
22. Glue can reach S3 but cannot retrieve a secret.
23. Athena writes query results but fails with KMS AccessDenied.
24. Redshift is private but applications cannot connect.
25. Lambda times out after VPC attachment.
26. S3 access works from one subnet but not another.
27. An endpoint exists but calls are denied.
28. Cross-account S3 reads fail only on encrypted objects.
29. An EMR workload needs an external package repository.
30. A platform wants to remove NAT entirely.
31. Security wants gold data reachable only from an approved VPC.
32. Finance asks why interface endpoint costs increased.
33. KMS access suddenly fails after a policy change.
34. A secret is readable from an unauthorized role.
35. An S3 bucket becomes inaccessible after a `SourceVpce` restriction.

---

# 118. Practice Questions — Troubleshooting

36. How do you distinguish timeout from AccessDenied?
37. What do you check first when DNS fails?
38. What do you inspect when an endpoint is `available` but traffic fails?
39. How do endpoint policies interact with IAM?
40. How do KMS key policies interact with IAM?
41. How do you investigate cross-account KMS failure?
42. How do you diagnose S3 `AccessDenied` with SSE-KMS?
43. How do you diagnose Secrets Manager timeout?
44. How do you diagnose Lambda VPC timeout?
45. How do you diagnose an unexpected NAT bill?

---

# 119. Practice Questions — Architecture

46. Design a private AWS lakehouse.
47. Design a private Glue environment without NAT.
48. Design a cross-account encrypted data lake.
49. Design centralized security boundaries for multiple data domains.
50. Design endpoint strategy across three AZs.
51. Design KMS key boundaries for bronze/silver/gold.
52. Design a hybrid AWS/on-premises data platform.
53. Design private Redshift connectivity.
54. Design private EMR connectivity.
55. Design a zero-trust data perimeter.

---

# 120. Practice Questions — Reasoning Answers

### Q21 — Glue cannot write to S3

Expected reasoning:

```text
IAM
→ bucket policy
→ S3 endpoint
→ route
→ DNS where applicable
→ KMS if SSE-KMS
```

### Q28 — Cross-account encrypted S3 fails

Expected reasoning:

```text
S3 policy
+
consumer IAM
+
KMS key policy
+
kms:Decrypt
+
cross-account trust
```

### Q30 — Remove NAT

Expected reasoning:

```text
Inventory all outbound dependencies.
Replace supported AWS-service paths with endpoints.
Retain another egress mechanism if external destinations remain.
```

### Q36 — Timeout vs AccessDenied

```text
Timeout
→ connectivity path

AccessDenied
→ authorization path
```

But validate with actual evidence.

### Q45 — NAT bill increases

Investigate:

```text
new workload
+
traffic volume
+
external dependencies
+
cross-AZ path
+
endpoint adoption
```

---

# 121. Decision Tree — Private Workload Cannot Reach AWS Service

```text
START
 |
 v
Does DNS resolve?
 |
 +-- NO --> DNS configuration
 |
 +-- YES
       |
       v
Does a route exist?
 |
 +-- NO --> route table
 |
 +-- YES
       |
       v
Is required endpoint present?
 |
 +-- NO --> create appropriate endpoint
 |
 +-- YES
       |
       v
Does SG allow traffic?
 |
 +-- NO --> fix SG
 |
 +-- YES
       |
       v
Does endpoint policy allow it?
 |
 +-- NO --> fix endpoint policy
 |
 +-- YES
       |
       v
Does IAM allow it?
 |
 +-- NO --> fix IAM
 |
 +-- YES
       |
       v
Does resource policy allow it?
 |
 +-- NO --> fix resource policy
 |
 +-- YES
       |
       v
Does KMS allow it?
 |
 +-- NO --> fix KMS authorization
 |
 +-- YES
       |
       v
Inspect application/service configuration
```

---

# 122. Decision Tree — KMS AccessDenied

```text
AccessDenied
    ↓
Identify caller
    ↓
Identify key
    ↓
Identify requested operation
    ↓
Check IAM
    ↓
Check key policy
    ↓
Check grants
    ↓
Check service context
    ↓
Check resource policy
    ↓
Check CloudTrail
    ↓
Fix smallest missing permission
```

---

# 123. Security Checklist

## KMS

- [ ] Customer-managed key only when justified
- [ ] Separate administrators/users
- [ ] Least privilege
- [ ] Rotation policy
- [ ] Alias
- [ ] CloudTrail
- [ ] Deletion protection/process
- [ ] Cross-account policy reviewed

## S3

- [ ] Encryption enabled
- [ ] SSE-KMS where required
- [ ] Bucket Keys evaluated
- [ ] TLS enforced
- [ ] Public access blocked
- [ ] Endpoint restriction evaluated
- [ ] Lockout risk tested

## VPC

- [ ] Private subnets
- [ ] Correct routes
- [ ] Security groups
- [ ] DNS
- [ ] NAT only when required
- [ ] Endpoints justified
- [ ] Endpoint policies reviewed

## Secrets

- [ ] Secrets Manager
- [ ] Rotation
- [ ] IAM least privilege
- [ ] KMS
- [ ] Private endpoint where appropriate
- [ ] No secret logging

---

# 124. Cost Checklist

Before deploying:

```text
How many KMS keys?
How many interface endpoints?
How many AZs?
How much data?
Do we need NAT?
Can S3 use a gateway endpoint?
Is there cross-AZ traffic?
Are endpoints shared or isolated?
Are there external dependencies?
```

After deployment:

```text
Cost Explorer
→ service
→ usage type
→ account
→ Region
→ tags
```

---

# 125. Teardown Checklist

After labs:

```text
Delete test Glue jobs
Delete test VPC endpoints
Delete test security groups
Delete test subnets
Delete test VPC
Delete test secrets
Remove test S3 objects
Review KMS key lifecycle
Check Cost Explorer
Verify no NAT Gateway remains
Verify no interface endpoint remains
```

Do not immediately schedule deletion of a KMS key unless you understand the implications and the test environment has no required ciphertext.

---

# 126. Completion Checklist

## KMS

- [ ] Encryption fundamentals
- [ ] AWS KMS
- [ ] AWS-managed keys
- [ ] Customer-managed keys
- [ ] Key policies
- [ ] Grants
- [ ] Rotation
- [ ] Envelope encryption
- [ ] Data keys
- [ ] Least privilege
- [ ] CloudTrail auditing

## S3

- [ ] SSE-S3
- [ ] SSE-KMS
- [ ] S3 Bucket Keys
- [ ] Bucket policies
- [ ] TLS enforcement
- [ ] VPC endpoint restrictions

## Data Services

- [ ] Glue encryption
- [ ] Athena encryption
- [ ] Redshift encryption
- [ ] Kinesis encryption
- [ ] Firehose encryption
- [ ] EMR encryption
- [ ] MSK encryption

## Networking

- [ ] VPC
- [ ] CIDR
- [ ] Subnets
- [ ] Private subnets
- [ ] Route tables
- [ ] Security groups
- [ ] DNS
- [ ] NAT Gateway
- [ ] Gateway endpoints
- [ ] Interface endpoints
- [ ] PrivateLink
- [ ] Endpoint policies

## Secrets

- [ ] Secrets Manager
- [ ] Rotation
- [ ] Glue integration
- [ ] DMS integration
- [ ] Redshift integration

## Advanced Security

- [ ] Cross-account KMS
- [ ] Cross-account encrypted data
- [ ] Data perimeter awareness
- [ ] VPN awareness
- [ ] Direct Connect awareness

## Operations

- [ ] KMS troubleshooting
- [ ] Network troubleshooting
- [ ] Endpoint troubleshooting
- [ ] DNS troubleshooting
- [ ] Security-group troubleshooting
- [ ] Cost analysis
- [ ] Terraform
- [ ] AWS CLI
- [ ] boto3
- [ ] Production runbooks
- [ ] Teardown

---

# 127. AWS Documentation Safety

AWS evolves continuously.

Before production use, verify current official documentation for:

```text
KMS APIs
KMS permissions
KMS rotation behavior
service encryption support
endpoint service availability
endpoint pricing
regional support
Terraform provider arguments
AWS CLI syntax
VPC quotas
cross-account behavior
```

Do not trust an old blog because the architecture looks familiar.

Prefer:

```text
AWS service documentation
AWS API reference
AWS CLI reference
AWS pricing
AWS provider documentation
```

---

# 128. Current Reference Notes

The following current AWS documentation points are particularly important:

1. AWS KMS documents customer-managed and AWS-managed key behavior and key lifecycle differences.
2. AWS KMS documents key policies as the primary key-access mechanism and explains the interaction with IAM.
3. AWS KMS documents grants and their common use by integrated AWS services.
4. AWS KMS documents automatic and on-demand rotation for supported customer-managed keys.
5. Amazon S3 documents SSE-KMS and S3 Bucket Keys and states that Bucket Keys can substantially reduce KMS request costs.
6. Amazon VPC documents gateway endpoints for S3/DynamoDB and the absence of an additional gateway endpoint charge.
7. Amazon S3 documents S3 gateway and interface endpoint options and `aws:SourceVpce`/`aws:SourceVpc` restrictions.
8. Amazon VPC documents endpoint policies as resource-based policies that do not replace IAM/resource policies.

Always check current documentation immediately before a production deployment.

---

# 129. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where |
|---|---:|---|
| AWS-managed KMS keys | Yes | Sections 7–8 |
| Customer-managed KMS keys | Yes | Sections 7–16 |
| Key policies | Yes | Sections 9–10 |
| Grants | Yes | Section 11 |
| Key rotation | Yes | Section 12 |
| SSE-S3 | Yes | Sections 17–18 |
| SSE-KMS | Yes | Sections 17–20 |
| S3 Bucket Keys | Yes | Section 19 |
| Glue encryption | Yes | Section 23 |
| Athena encryption | Yes | Section 24 |
| Redshift encryption | Yes | Section 25 |
| Kinesis encryption | Yes | Section 26 |
| Firehose encryption | Yes | Section 27 |
| EMR encryption | Yes | Section 28 |
| MSK encryption | Yes | Section 29 |
| VPC basics | Yes | Sections 30–31 |
| Private subnets | Yes | Section 32 |
| Security groups | Yes | Section 34 |
| NAT Gateway | Yes | Section 36 |
| Gateway endpoints | Yes | Sections 37–39 |
| Interface endpoints | Yes | Sections 40–42 |
| AWS PrivateLink | Yes | Section 41 |
| Endpoint policies | Yes | Sections 43–44 |
| VPC-restricted bucket policies | Yes | Sections 20–21 |
| TLS-only bucket access | Yes | Section 20 |
| Private Glue | Yes | Sections 45–46, 71 |
| Private EMR | Yes | Section 47 |
| Private Redshift | Yes | Section 48 |
| Private Lambda | Yes | Section 49 |
| Secrets Manager | Yes | Sections 50–54 |
| Cross-account encryption | Yes | Sections 55–57 |
| Data perimeters | Yes | Sections 58–59 |
| VPN awareness | Yes | Section 60 |
| Direct Connect awareness | Yes | Section 61 |
| KMS troubleshooting | Yes | Sections 62–63, 75 |
| Network timeout troubleshooting | Yes | Sections 64, 76, 121 |
| Network Security hands-on lab | Yes | Sections 66–76 |
| Endpoint vs NAT cost analysis | Yes | Sections 98–100 |
| Production architecture | Yes | Sections 95–97 |
| Security best practices | Yes | Section 90 |
| Cost optimization | Yes | Sections 98–100, 124 |

## Coverage Result

**Actual roadmap coverage: 100% of the explicit Topic 13 requirements.**

The percentage refers to the requirements enumerated in the authoritative Topic 13 specification. It does not claim that every AWS networking or security capability is covered.

---

# 130. Final Operating Standard

You are ready to move to the next topic when you can independently explain and implement:

```text
Encrypted data
+
least-privilege KMS
+
private subnet
+
correct routes
+
correct security groups
+
gateway/interface endpoints
+
endpoint policies
+
Secrets Manager
+
cross-account authorization
+
data-perimeter thinking
+
CloudTrail evidence
+
cost-aware network architecture
```

And when a production workload fails, you do not guess.

You work through:

```text
DNS
 ↓
Route
 ↓
Security Group
 ↓
Endpoint
 ↓
Endpoint Policy
 ↓
IAM
 ↓
Resource Policy
 ↓
KMS
 ↓
Application
```

---

# 131. Final Principle

Production AWS Data Engineering security is not one feature.

It is a system:

```text
                    SECURITY
                       |
        +--------------+--------------+
        |              |              |
      Identity       Network       Encryption
        |              |              |
       IAM          VPC/Endpoints     KMS
        |              |              |
        +--------------+--------------+
                       |
                  Resource Policy
                       |
                  Secrets Manager
                       |
                    Audit
                       |
                   CloudTrail
                       |
                     Cost
                       |
                   FinOps
```

The target mindset is:

> **Do not merely make the pipeline work. Make it private where appropriate, encrypted by design, least-privileged, auditable, diagnosable, and economically defensible.**

That is production-grade AWS Data Engineering security architecture.
