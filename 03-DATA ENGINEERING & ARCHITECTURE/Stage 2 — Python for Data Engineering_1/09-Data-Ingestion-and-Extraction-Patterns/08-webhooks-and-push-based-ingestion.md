# Webhooks and Push-Based Ingestion

A webhook is easy to demonstrate:

```text
HTTP POST → process payload → return 200
```

A production webhook ingestion system is much more than that.

A reliable design must account for:

```text
Authentication
      ↓
Signature verification
      ↓
Replay protection
      ↓
Fast acknowledgement
      ↓
Raw event landing
      ↓
Deduplication
      ↓
Ordering/version handling
      ↓
Asynchronous processing
      ↓
Dead-letter handling
      ↓
Reconciliation
      ↓
Observability
      ↓
Replay/recovery
```

The central lesson of this chapter is:

> **A webhook is a notification mechanism, not automatically a complete source of truth.**

And:

> **At-least-once delivery means duplicates are normal, not exceptional.**

A production webhook architecture should therefore assume that events can be duplicated, delayed, reordered, malformed, or lost.

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

1. Explain pull versus push ingestion.
2. Explain what a webhook is.
3. Describe the complete webhook request lifecycle.
4. Build a minimal FastAPI webhook receiver.
5. Explain why webhook receivers should acknowledge quickly.
6. Explain why providers retry deliveries.
7. Design for at-least-once delivery.
8. Deduplicate events using stable event IDs.
9. Explain why deduplication requires atomic uniqueness protection.
10. Verify HMAC signatures securely.
11. Verify signatures against the exact raw request body.
12. Use `hmac.compare_digest()` for signature comparison.
13. Protect webhook endpoints against replay attacks.
14. Validate signed timestamps with a bounded tolerance window.
15. Rotate webhook secrets safely.
16. Understand IP allowlists as an additional, not replacement, security control.
17. Apply HTTPS and payload-size protections.
18. Land verified raw events before expensive processing.
19. Separate the ingress path from asynchronous processing.
20. Handle out-of-order events.
21. Use event timestamps or versions when the source provides reliable ordering metadata.
22. Fetch current state from a source API when blindly applying an event is unsafe.
23. Design a dead-letter path.
24. Replay failed events safely.
25. Reason about webhook event loss.
26. Build periodic reconciliation against an authoritative source API.
27. Understand object-storage notifications, queues, and event streams at an architectural level.
28. Develop and test webhook receivers locally.
29. Use recorded payloads as deterministic test fixtures.
30. Inject failure conditions deliberately.
31. Design useful webhook metrics and structured logs.
32. Build a production-oriented FastAPI reference implementation.
33. Test invalid signatures, expired timestamps, duplicates, out-of-order events, and malformed JSON.
34. Defend webhook architecture decisions in an engineering review.

---

# 2. Prerequisites

This chapter assumes you already have basic knowledge of:

- HTTP requests and responses.
- HTTP `POST`.
- status codes such as `2xx`, `4xx`, and `5xx`.
- JSON.
- Python functions and exceptions.
- Python type hints.
- `httpx`.
- API authentication concepts.
- basic SQL and database constraints.
- pagination and incremental extraction concepts.

Earlier topics cover those subjects in greater depth. This chapter applies them to event-driven ingestion.

For example:

```text
Earlier topic:
HTTP POST + status codes

This topic:
HTTP POST as an event-delivery mechanism
```

Likewise:

```text
Earlier topic:
API authentication

This topic:
Webhook-specific message authentication
```

The goal here is not to re-teach HTTP, OAuth, SQL, or distributed streaming internals.

---

# 3. What Problem Does Push-Based Ingestion Solve?

Data can enter a platform in two broad ways:

```text
Pull
```

or:

```text
Push
```

With pull ingestion, your system decides when to ask for data.

With push ingestion, another system tells your system when something happened.

Consider an e-commerce platform.

Without push:

```text
Every 5 minutes:

Your pipeline
     |
     | GET /orders?updated_since=...
     v
Source API
```

Your pipeline discovers changes by polling.

With push:

```text
Order created
     |
     v
Source system
     |
     | HTTP POST
     v
Your webhook endpoint
```

The source notifies you immediately.

---

# 4. Pull vs Push Ingestion

## 4.1 Pull

Conceptually:

```text
+----------------+
| Your Pipeline  |
+-------+--------+
        |
        | GET /changes
        v
+----------------+
| Source API     |
+-------+--------+
        |
        | response
        v
+----------------+
| Your Pipeline  |
+----------------+
```

Your system controls the request schedule.

### Advantages

- You control when extraction occurs.
- Periodic reconciliation is natural.
- The source API can often be queried again.
- Recovery can be straightforward when the source supports historical queries.

### Disadvantages

- Polling introduces latency.
- You may make requests when nothing changed.
- Rate limits can constrain polling.
- Frequent polling can increase source load.

---

## 4.2 Push

Conceptually:

```text
+----------------+
| Source System  |
+-------+--------+
        |
        | HTTP POST event
        v
+----------------+
| Webhook API    |
+----------------+
```

The source decides when to send a notification.

### Advantages

- Low-latency notification.
- Event-driven behavior.
- Less unnecessary polling.

### Disadvantages

- Duplicate delivery.
- Provider retries.
- Possible ordering problems.
- Possible event loss.
- Security requirements.
- Provider-specific delivery semantics.
- Need for replay and reconciliation.

There is no universal winner.

A production architecture may use both:

```text
webhook
+
periodic API reconciliation
```

---

# 5. What Is a Webhook?

A webhook is an HTTP callback in which a source system sends an HTTP request to an endpoint exposed by another system when an event occurs.

A generic request might look like:

```http
POST /webhooks/payments
Content-Type: application/json
X-Webhook-Timestamp: 1727776800
X-Webhook-Signature: abc123...
```

with a body such as:

```json
{
  "event_id": "evt_123",
  "event_type": "payment.created",
  "created_at": "2026-10-01T10:00:00Z",
  "data": {
    "payment_id": "pay_456",
    "amount": 1000
  }
}
```

This payload is deliberately generic.

Actual providers may use different:

- field names,
- signature headers,
- timestamp formats,
- event identifiers,
- retry behavior,
- ordering guarantees,
- payload schemas.

Never infer provider-specific behavior from a generic example.

---

# 6. Webhook Request Lifecycle

A production webhook lifecycle can look like:

```text
Source event occurs
       |
       v
Provider creates webhook request
       |
       v
Provider signs request
       |
       v
HTTPS POST
       |
       v
Webhook endpoint receives request
       |
       v
Verify signature
       |
       v
Verify timestamp
       |
       v
Validate basic event envelope
       |
       v
Persist raw verified event
       |
       v
Return 2xx quickly
       |
       v
Asynchronous processing
       |
       v
Deduplicate
       |
       v
Apply event
       |
       v
Monitor / reconcile
```

The key architectural distinction is:

```text
Ingress path
```

versus:

```text
Processing path
```

The ingress path should normally be short and deterministic.

The processing path may be much more expensive.

---

# 7. A Simple Webhook Example

Suppose a payment provider sends:

```json
{
  "event_id": "evt_123",
  "event_type": "payment.created",
  "created_at": "2026-10-01T10:00:00Z",
  "data": {
    "payment_id": "pay_456",
    "amount": 1000
  }
}
```

The fields have conceptual meanings:

| Field | Meaning |
|---|---|
| `event_id` | Identifier for this event delivery/message |
| `event_type` | Type of event |
| `created_at` | Source event timestamp |
| `data` | Event-specific information |

The receiver might initially do:

```text
receive
  ↓
verify
  ↓
store
  ↓
acknowledge
```

It should not automatically assume:

```text
receive
  ↓
trust
  ↓
perform expensive business operation
  ↓
return 200
```

---

# 8. Building a Minimal FastAPI Webhook Receiver

Start with the smallest possible receiver.

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/webhooks/events")
async def receive_webhook(request: Request):
    body = await request.body()

    print(body)

    return {"status": "received"}
```

## How it works

```python
app = FastAPI()
```

creates the FastAPI application.

```python
@app.post("/webhooks/events")
```

registers an HTTP `POST` endpoint.

```python
body = await request.body()
```

reads the raw request body.

```python
return {"status": "received"}
```

returns a successful response.

## What can go wrong?

This minimal receiver has no:

- signature verification,
- replay protection,
- deduplication,
- persistence,
- schema validation,
- observability,
- dead-letter path.

It is useful only as a starting point.

---

# 9. Why Webhooks Must Acknowledge Quickly

Webhook providers commonly retry when a delivery:

- times out,
- receives an error status,
- fails to connect,
- does not satisfy the provider's acknowledgement rules.

Imagine:

```text
Webhook request
      |
      v
Parse payload
      |
      v
Database query
      |
      v
Large transformation
      |
      v
External API call
      |
      v
Slow processing
      |
      v
200
```

If the provider has a short delivery timeout, the provider may decide:

```text
receiver did not respond
```

and retry.

The result can become:

```text
same event
   |
   +--> attempt 1
   |
   +--> attempt 2
   |
   +--> attempt 3
```

The receiver may now process the same logical event multiple times.

---

# 10. The Safer Conceptual Architecture

A better design is often:

```text
Webhook
   |
   v
Verify
   |
   v
Persist raw event
   |
   v
Return 2xx
   |
   v
Asynchronous processor
   |
   v
Business processing
```

This separates:

```text
delivery acknowledgement
```

from:

```text
event processing
```

The exact acknowledgement contract is provider-specific.

A provider may require a particular status code or response behavior, so always follow its documentation.

---

# 11. Provider Retries

A retry can happen because:

```text
Attempt 1
   |
   v
timeout
   |
   v
Provider retries
   |
   v
Attempt 2
   |
   v
200
```

The receiver therefore needs to be prepared for:

```text
evt_123
evt_123
```

rather than assuming:

```text
evt_123
```

will arrive exactly once.

Do not assume every provider uses the same retry schedule.

The source contract determines:

- retry duration,
- retry count,
- retry delays,
- terminal failure behavior.

---

# 12. At-Least-Once Delivery

At-least-once delivery means the system attempts to deliver an event, but the same event may be delivered more than once.

Compare three conceptual delivery models:

```text
Exactly once
```

The consumer observes one successful delivery.

```text
At least once
```

The consumer should eventually receive the event, but duplicates are possible.

```text
At most once
```

The consumer may receive the event zero or one time.

Webhook systems commonly require consumers to behave as though delivery is at least once unless the provider explicitly documents stronger guarantees.

Therefore:

> **Duplicate delivery must be expected and safely handled.**

---

# 13. Duplicate Webhook Events

Suppose the provider sends:

```text
evt_123
```

and because of a timeout retries:

```text
evt_123
```

Again.

The receiver should be able to recognize:

```text
same event
```

rather than treating it as:

```text
two independent events
```

This leads to idempotency.

---

# 14. Idempotency and Event Deduplication

An operation is idempotent when repeating it produces the same intended final effect.

For webhook ingestion, a stable event ID is often the foundation.

Conceptually:

```text
Receive evt_123
       |
       v
Is evt_123 already processed?
       |
    +--+--+
    |     |
   yes    no
    |      |
 ignore   process
           |
           v
        mark done
```

A simple database table could be:

```sql
CREATE TABLE processed_webhook_events (
    event_id TEXT PRIMARY KEY,
    received_at TIMESTAMPTZ NOT NULL
);
```

The primary key creates a database-enforced uniqueness boundary.

---

# 15. Why a Unique Constraint Matters

Consider the naïve design:

```text
SELECT event_id
FROM processed_webhook_events
WHERE event_id = 'evt_123';
```

Suppose two workers receive the same event concurrently.

```text
Worker A → SELECT → not found
Worker B → SELECT → not found
```

Both workers may then process:

```text
Worker A → process
Worker B → process
```

The check was not atomic with the work.

A database uniqueness constraint can help establish a race-safe ownership boundary.

Conceptually:

```text
event_id PRIMARY KEY
```

or another unique constraint.

A robust design should define what happens when the insert conflicts:

```text
first worker
    ↓
claims event
    ↓
processes

second worker
    ↓
unique conflict
    ↓
recognizes duplicate
```

Exactly how processing and claiming are combined depends on transaction semantics and whether the downstream operation itself is idempotent.

---

# 16. HMAC Signatures

Webhook security commonly uses a shared secret and HMAC.

Conceptually:

```text
shared secret
      +
raw request body
      |
      v
     HMAC
      |
      v
signature
```

The provider sends a signature in a header.

For example:

```http
X-Webhook-Signature: abc123...
```

The receiver computes the expected signature using the shared secret.

A simplified Python calculation is:

```python
import hashlib
import hmac

expected = hmac.new(
    secret,
    body,
    hashlib.sha256,
).hexdigest()
```

The exact algorithm and encoding are provider-specific.

Do not assume every provider uses SHA-256 or this exact header format.

---

# 17. Why the Raw Request Body Matters

This is one of the most important security details.

Signature verification should normally operate on the exact raw bytes that the sender signed.

Dangerous conceptual flow:

```text
raw JSON
   |
   v
parse JSON
   |
   v
reformat JSON
   |
   v
serialize JSON
   |
   v
verify signature
```

Consider:

```json
{"a":1,"b":2}
```

versus:

```json
{
  "a": 1,
  "b": 2
}
```

These can represent equivalent JSON data while being different byte sequences.

If the provider signs the original bytes, re-serializing the parsed object can produce a different signature input.

Therefore:

```python
body = await request.body()
```

should be obtained before parsing the structured JSON.

Then:

```text
raw body
   |
   v
signature verification
   |
   v
JSON parsing
```

Only trust the structured payload after the security checks have succeeded.

---

# 18. Constant-Time Signature Comparison

Use:

```python
hmac.compare_digest(expected, received)
```

rather than an ordinary equality comparison for signature verification.

Example:

```python
if not hmac.compare_digest(expected, received):
    raise ValueError("Invalid signature")
```

The purpose is to reduce timing side-channel information during comparison.

You do not need to implement cryptographic comparison yourself.

Use the standard library primitive.

---

# 19. A Secure HMAC Verification Helper

```python
from __future__ import annotations

import hashlib
import hmac


def verify_hmac_signature(
    body: bytes,
    received_signature: str,
    secret: bytes,
) -> bool:
    """Verify a SHA-256 HMAC signature over raw request bytes."""
    expected = hmac.new(
        secret,
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected,
        received_signature,
    )
```

## What it does

It computes the expected signature from:

```text
secret + raw body
```

and compares it using:

```python
hmac.compare_digest()
```

## What can go wrong?

- wrong secret,
- wrong encoding,
- wrong algorithm,
- wrong signature format,
- provider-specific prefixes,
- accidental whitespace,
- verifying parsed JSON instead of raw bytes.

The provider's signing specification is authoritative.

---

# 20. Replay Attacks

A valid signature does not automatically mean a request is fresh.

Imagine:

```text
10:00
legitimate webhook
      |
      v
attacker captures request
```

Later:

```text
12:00
attacker sends exact request again
```

The HMAC may still be valid because the body and signature have not changed.

This is a replay attack.

Therefore:

> **Signature verification authenticates the signed content, but freshness requires an additional mechanism when replay protection is part of the source protocol.**

---

# 21. Signed Timestamps

A common pattern is to include a timestamp in the signed material.

Conceptually:

```text
timestamp + "." + raw_body
            |
            v
           HMAC
```

Example headers:

```http
X-Webhook-Timestamp: 1727776800
X-Webhook-Signature: abc...
```

The receiver should conceptually perform:

```text
1. Parse timestamp
2. Check freshness
3. Construct the provider-defined signed message
4. Compute expected HMAC
5. Compare signatures in constant time
6. Continue only if all checks succeed
```

The exact header names and signing construction are provider-specific.

---

# 22. Timestamp Tolerance Windows

Suppose:

```text
current time = 12:00
allowed skew = ±5 minutes
```

Then conceptually:

```text
11:58 → accept
12:02 → accept
12:20 → reject
```

A Python implementation can use a configurable value:

```python
MAX_SKEW_SECONDS = 300
```

The exact value should come from your threat model, provider behavior, clock synchronization, and operational requirements.

Do not arbitrarily choose an extremely large window.

Also ensure production systems have sensible clock synchronization.

---

# 23. Timestamp Validation Example

```python
from __future__ import annotations

import time


def is_timestamp_fresh(
    timestamp: int,
    *,
    max_skew_seconds: int,
    now: int | None = None,
) -> bool:
    """Return whether a webhook timestamp is within the allowed skew."""
    current = int(time.time()) if now is None else now

    return abs(current - timestamp) <= max_skew_seconds
```

This helper deliberately separates:

```text
timestamp validation
```

from:

```text
signature validation
```

A complete provider implementation must combine both according to its documented signing protocol.

---

# 24. Secret Rotation

Webhook signing secrets eventually need to be rotated.

Conceptually:

```text
Old secret
New secret
```

During a controlled rotation period, the receiver may need to accept signatures generated using both secrets.

A safe conceptual flow is:

```text
incoming request
      |
      v
try active secret
      |
      +---- valid → accept
      |
      v
try previous secret
      |
      +---- valid → accept during transition
      |
      v
reject
```

The exact rotation mechanism depends on the provider.

Security requirements include:

- store secrets securely,
- never commit them to Git,
- avoid logging them,
- rotate deliberately,
- revoke compromised secrets,
- coordinate provider and receiver changes,
- remove old secrets after the transition period.

---

# 25. IP Allowlists

Some providers publish stable source IP ranges.

An IP allowlist can add another layer:

```text
incoming request
      |
      v
known provider network?
      |
      v
signature valid?
      |
      v
accept
```

But:

> **IP allowlisting is not a replacement for cryptographic signature verification.**

IP controls have operational limitations:

- provider ranges can change,
- proxies/load balancers can obscure source addresses,
- configuration can become stale,
- infrastructure can be reconfigured.

Use IP allowlisting where appropriate and where the provider supports a reliable documented source range.

---

# 26. HTTPS

Production webhook endpoints should use HTTPS.

Conceptually:

```text
HTTP
```

versus:

```text
HTTPS
```

HTTPS protects the connection against network-level interception and modification in transit.

Webhook security is layered:

```text
HTTPS
+
signature verification
+
replay protection
+
input validation
```

No single layer should be treated as the entire security model.

---

# 27. Payload Size Limits

A webhook endpoint is exposed to external input.

An attacker or faulty provider could send an unexpectedly large payload.

Large payloads can consume:

- memory,
- CPU,
- network bandwidth,
- storage,
- processing capacity.

Therefore establish a maximum acceptable payload size.

Conceptually:

```text
request
  |
  v
payload size acceptable?
  |
 +----+
 |    |
yes   no
 |     |
 v     v
process reject
```

The exact implementation can live at the API gateway, reverse proxy, web server, application, or multiple layers.

The important principle is:

> **Do not allow an external caller to consume unbounded resources merely by sending a request.**

---

# 28. Land First, Process Later

Raw event landing is a central design pattern.

```text
Webhook
   |
   v
Verify
   |
   v
Raw event landing
   |
   v
ACK
   |
   v
Process later
```

Why land the raw event?

Because the raw payload is useful for:

- replay,
- debugging,
- auditability,
- schema evolution,
- processing bug recovery,
- downstream reconstruction,
- incident investigation.

Example metadata:

```json
{
  "_received_at": "2026-10-01T10:01:02Z",
  "_source": "payments",
  "_event_id": "evt_123",
  "_request_id": "req_789",
  "payload": {}
}
```

The exact metadata model is platform-specific.

---

# 29. Asynchronous Webhook Processing

The ingestion path can be:

```text
Ingress
   |
   v
Raw event store / queue
   |
   v
Processing workers
   |
   v
Target tables
```

This provides separation between:

```text
receiving the event
```

and:

```text
processing the event
```

Benefits include:

- faster acknowledgements,
- backpressure,
- retryable processing,
- failure isolation,
- independent worker scaling.

This chapter does not teach Kafka or distributed streaming internals in depth. Those belong to later modules.

At this stage, think of a queue as:

```text
producer
   |
   v
buffer
   |
   v
consumer
```

---

# 30. Event Ordering Problems

Suppose two events exist:

```text
Event A:
payment.created

Event B:
payment.updated
```

The logical order is:

```text
A → B
```

But network delivery might produce:

```text
B → A
```

Therefore:

```text
arrival order != event order
```

unless the provider explicitly guarantees otherwise.

---

# 31. Event Timestamps and Versions

Useful ordering metadata can include:

```text
event_created_at
event_updated_at
version
sequence_number
```

For example:

```text
customer_id = 123

version 1 → name = Alice
version 2 → name = Alicia
```

If version 2 arrives first:

```text
version 2
   ↓
version 1
```

Blindly applying both can regress the target state.

If the source provides a trustworthy monotonic version, the target can conceptually enforce:

```text
apply incoming event only if:

incoming_version > current_version
```

The source contract determines whether this is safe.

Not every webhook system provides a version.

---

# 32. Applying Events in Version Order

Suppose current target state is:

```text
customer_id = 123
version = 2
name = Alicia
```

An incoming event says:

```text
customer_id = 123
version = 1
name = Alice
```

A version-aware processor can recognize:

```text
incoming_version = 1
current_version = 2
```

and ignore the stale event.

Conceptually:

```python
if incoming_version > current_version:
    apply_event()
else:
    ignore_as_stale()
```

This is appropriate only when the version has the documented semantics required by the design.

---

# 33. When Ordering Cannot Be Trusted

Sometimes the webhook payload does not contain enough information to safely reconstruct state.

In that case, a useful strategy is:

```text
webhook
   |
   v
notification
   |
   v
GET latest source state
   |
   v
update target
```

Example:

```text
customer.updated
      |
      v
GET /customers/123
      |
      v
current authoritative state
      |
      v
target
```

This treats the webhook as:

```text
"something changed"
```

rather than:

```text
"this payload is the final authoritative state"
```

This can be safer when ordering matters, but it costs more.

Potential costs:

- additional API calls,
- increased latency,
- source rate-limit usage,
- dependence on source availability,
- possible source eventual consistency.

Use this approach when its additional cost is justified by correctness requirements and source semantics.

---

# 34. Dead-Letter Handling

Not every event can be processed successfully.

Examples:

- malformed JSON,
- missing event ID,
- invalid schema,
- unknown event type,
- unsupported schema version,
- business validation failure,
- downstream processing failure.

A conceptual architecture is:

```text
Webhook
   |
   v
Raw landing
   |
   v
Processor
   |
   +---- success ------> Target
   |
   +---- failure ------> Dead Letter
```

Do not silently discard malformed or unprocessable events.

---

# 35. What Belongs in a Dead-Letter Event?

A dead-letter record can include:

- original raw payload,
- event ID,
- event type,
- failure reason,
- error timestamp,
- processing attempt,
- relevant metadata,
- correlation/run identifier.

Example:

```json
{
  "event_id": "evt_123",
  "status": "dead_lettered",
  "failure_reason": "unknown_event_type",
  "attempt": 3,
  "payload": {}
}
```

Do not put secrets into the dead-letter record merely because the raw request contained them.

Apply the same security and data-minimization principles to error storage.

---

# 36. Replaying Failed Events

Raw events enable replay.

Conceptually:

```text
Dead Letter
     |
     v
Fix processing bug
     |
     v
Replay original payload
     |
     v
Processor
     |
     v
Target
```

Replay safety depends on idempotency.

If the event is replayed:

```text
evt_123
```

the system must be able to determine whether its effect has already been applied.

Replay design should consider:

- event ID,
- processing version,
- target state,
- idempotency keys,
- schema compatibility,
- operator controls,
- observability.

---

# 37. Webhook Event Loss

Webhooks can be lost.

Potential causes include:

- provider outage,
- receiver outage,
- network failure,
- misconfiguration,
- expired subscriptions,
- provider bugs,
- provider delivery limits,
- operational mistakes.

For example:

```text
Source event
    |
    X
receiver unavailable
```

The source may retry, but retries are not a universal guarantee of permanent recoverability.

Therefore:

> **Do not treat webhook delivery as the only mechanism for maintaining source-of-truth state when the provider exposes an authoritative API.**

---

# 38. Reconciliation Pulls

A robust architecture can combine:

```text
webhook notification
```

with:

```text
periodic API reconciliation
```

Conceptually:

```text
                 Source
                 /    \
                /      \
          Webhook       API
             |            |
             v            v
       Fast updates   Reconciliation
             |            |
             +-----+------+
                   |
                   v
              Target state
```

The webhook provides low-latency change notification.

The API provides a mechanism to discover:

- missing events,
- stale state,
- inconsistencies.

---

# 39. Example Reconciliation

Suppose your target contains:

```text
payment IDs:
1, 2, 3, 4
```

The source API reports:

```text
payment IDs:
1, 2, 3, 4, 5
```

But no webhook for payment 5 was recorded.

Reconciliation discovers:

```text
source - target = {5}
```

The pipeline can then repair the missing state.

The exact reconciliation query depends on source capabilities.

---

# 40. Webhooks + APIs as a Combined Architecture

A useful mental model is:

```text
                 +---------------+
                 | Source System |
                 +-------+-------+
                         |
              +----------+----------+
              |                     |
              v                     v
          Webhooks                 API
              |                     |
              v                     v
       Event ingestion       Reconciliation
              |                     |
              +----------+----------+
                         |
                         v
                    Target state
```

The roles differ:

```text
Webhook:
fast notification
```

versus:

```text
API:
authoritative state / recovery / reconciliation
```

This distinction is fundamental to reliable event-driven ingestion.

---

# 41. Object-Storage Notifications

Push-based ingestion is not limited to webhooks.

Object storage systems can emit notifications when an object is created.

Conceptually:

```text
Object created
     |
     v
Storage notification
     |
     v
Ingestion pipeline
     |
     v
Fetch object
```

The notification may contain:

```text
"object X exists"
```

rather than the entire object contents.

The ingestion system can then fetch:

```text
bucket/key
```

from the object store.

This pattern is useful for file-based data pipelines.

---

# 42. Message Queues

A queue provides a buffer between producers and consumers.

```text
Producer
   |
   v
+-------+
| Queue |
+---+---+
    |
    v
Consumer
```

Queues can help with:

- buffering,
- retries,
- backpressure,
- asynchronous processing,
- worker scaling.

The webhook receiver can write an event into a queue and acknowledge the provider quickly.

---

# 43. Event Streams

An event stream is another push-oriented architecture.

Conceptually:

```text
Producer
   |
   v
Event stream
   |
   +----> Consumer A
   |
   +----> Consumer B
   |
   +----> Consumer C
```

The important awareness-level distinction is:

```text
webhook:
HTTP delivery to an endpoint

queue:
buffered message delivery

event stream:
persistent ordered/log-like event distribution model
```

Later modules can cover streaming platforms in greater depth.

---

# 44. Local Webhook Development

An external provider cannot normally reach:

```text
localhost:8000
```

directly from the public internet.

Conceptually:

```text
Internet
   |
   X
localhost
```

During development, a tunnel can expose a temporary public URL:

```text
Provider
   |
   v
Public temporary URL
   |
   v
Local tunnel
   |
   v
localhost:8000
```

Use tunnel tools carefully.

Consider:

- public exposure,
- test secrets,
- sensitive payloads,
- access controls,
- temporary URLs,
- logging,
- accidental production traffic.

Do not depend on a particular commercial tunnel provider.

---

# 45. Recorded Payload Testing

Real or representative webhook payloads are valuable regression fixtures.

A safe workflow is:

```text
Test event
    |
    v
Capture safely
    |
    v
Sanitize sensitive fields
    |
    v
Store fixture
    |
    v
Replay during tests
```

Benefits include:

- deterministic tests,
- regression testing,
- debugging,
- schema evolution testing,
- reproducibility.

Never casually commit production secrets, authentication headers, or unnecessary personal data into fixtures.

---

# 46. Testing Webhook Receivers

A production webhook receiver needs tests for security, reliability, recovery, and operations.

## Security tests

1. valid signature,
2. invalid signature,
3. modified payload,
4. expired timestamp,
5. malformed signature,
6. wrong secret.

## Reliability tests

7. duplicate event,
8. provider retry,
9. out-of-order events,
10. missing event ID,
11. malformed JSON,
12. processing failure.

## Recovery tests

13. dead-letter event,
14. replay,
15. reconciliation.

## Operational tests

16. oversized payload,
17. slow processor,
18. receiver restart.

---

# 47. A Testable HMAC Receiver

The following example demonstrates the core security sequence without tying it to a particular provider's exact header format.

```python
from __future__ import annotations

import hashlib
import hmac
import time

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

WEBHOOK_SECRET = b"development-only-secret"
MAX_SKEW_SECONDS = 300


def verify_timestamp(
    timestamp: int,
    *,
    now: int | None = None,
) -> bool:
    """Return whether a signed timestamp is within the allowed window."""
    current = int(time.time()) if now is None else now
    return abs(current - timestamp) <= MAX_SKEW_SECONDS


def verify_signature(
    body: bytes,
    timestamp: str,
    received_signature: str,
) -> bool:
    """Verify a generic timestamp + body HMAC construction."""
    signed_message = f"{timestamp}.".encode() + body

    expected = hmac.new(
        WEBHOOK_SECRET,
        signed_message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        expected,
        received_signature,
    )


@app.post("/webhooks/events")
async def receive_webhook(request: Request):
    body = await request.body()

    timestamp_text = request.headers.get("X-Webhook-Timestamp")
    signature = request.headers.get("X-Webhook-Signature")

    if timestamp_text is None or signature is None:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook authentication headers",
        )

    try:
        timestamp = int(timestamp_text)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook timestamp",
        ) from exc

    if not verify_timestamp(timestamp):
        raise HTTPException(
            status_code=401,
            detail="Expired webhook timestamp",
        )

    if not verify_signature(
        body,
        timestamp_text,
        signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    # Only parse the payload after verification.
    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Malformed JSON",
        ) from exc

    event_id = payload.get("event_id")

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing event_id",
        )

    # Educational placeholder:
    # durably land the verified raw event here.

    return {"status": "received"}
```

## What this example demonstrates

The order is intentional:

```text
raw body
  ↓
timestamp validation
  ↓
signature validation
  ↓
JSON parsing
  ↓
event validation
  ↓
durable landing
  ↓
fast response
```

## What it does not implement yet

It does not yet provide:

- durable raw storage,
- deduplication,
- asynchronous queueing,
- version handling,
- DLQ,
- replay,
- reconciliation.

Those are added progressively below.

---

# 48. Failure Injection

A good webhook test harness should deliberately simulate failures.

At minimum, simulate:

```text
duplicate event
out-of-order event
invalid signature
expired timestamp
malformed JSON
receiver timeout
receiver failure
```

The goal is not merely to prove that the happy path works.

The goal is to prove that the system behaves safely when delivery does not behave as expected.

---

# 49. Failure Injection Matrix

| Failure | Expected behavior |
|---|---|
| Invalid signature | Reject request |
| Expired timestamp | Reject request |
| Duplicate event | Do not apply event twice |
| Out-of-order event | Apply only if safe, or reconcile/fetch state |
| Malformed JSON | Reject or dead-letter according to architecture |
| Processing failure | Preserve event and retry/DLQ |
| Receiver outage | Provider may retry; reconciliation must detect gaps |
| Replay | Idempotent processing prevents unintended duplicate effect |
| Oversized payload | Reject before expensive processing |
| Unknown event type | Preserve and route to controlled failure path |

---

# 50. Observability

Webhook systems need dedicated observability.

Useful metrics include:

```text
webhooks_received
webhooks_verified
webhooks_rejected
webhooks_duplicate
webhooks_processed
webhooks_failed
webhooks_dead_lettered
webhooks_replayed
processing_latency
ack_latency
```

Also useful:

```text
event_age
retry_count
source/provider
event_type
queue_depth
reconciliation_mismatch_count
```

---

# 51. Acknowledgement Latency vs Processing Latency

These are different metrics.

```text
Webhook arrives
    |
    +---- acknowledgement latency
    |
    v
queue / raw landing
    |
    +---- processing latency
    |
    v
target
```

A receiver can acknowledge quickly while the downstream processor takes several seconds.

That is not necessarily a problem.

The important requirement is that the provider's delivery contract is satisfied while the event is preserved safely.

---

# 52. Structured Logging

Webhook logs should be structured.

For example:

```python
import logging

logger = logging.getLogger(__name__)


def log_webhook_received(
    *,
    event_id: str,
    event_type: str,
) -> None:
    logger.info(
        "webhook_received",
        extra={
            "event_id": event_id,
            "event_type": event_type,
        },
    )
```

Useful fields include:

- event ID,
- event type,
- source,
- request/correlation ID,
- processing attempt,
- result,
- latency.

Do **not** log:

```text
webhook secrets
authorization headers
private signing keys
raw sensitive payloads unnecessarily
```

Observability must not become a data-leak mechanism.

---

# 53. Production Architecture

A complete conceptual architecture is:

```text
                         External Provider
                                |
                                | HTTPS POST
                                v
                     +-----------------------+
                     |   Webhook API Layer    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Signature Validation   |
                     | Replay Protection      |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Raw Event Landing      |
                     +-----------+-----------+
                                 |
                             fast 2xx
                                 |
                                 v
                     +-----------------------+
                     | Queue / Work Buffer    |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Event Processor        |
                     | Deduplication          |
                     | Ordering               |
                     +-----------+-----------+
                                 |
                       +---------+---------+
                       |                   |
                       v                   v
                  Target State           DLQ
                                           |
                                           v
                                         Replay

                     Periodic API Reconciliation
                                  |
                                  v
                            Target Repair
```

---

# 54. Component Responsibilities

## Webhook API Layer

Responsible for:

- HTTPS,
- request acceptance,
- payload-size controls,
- basic request handling.

## Signature Validation

Responsible for:

- raw-body HMAC verification,
- timestamp validation,
- replay protection.

## Raw Event Landing

Responsible for:

- durable event preservation,
- event metadata,
- replayability.

## Queue / Work Buffer

Responsible for:

- decoupling ingress from processing,
- buffering,
- retryable downstream work.

## Event Processor

Responsible for:

- event validation,
- deduplication,
- ordering/version handling,
- business transformations.

## DLQ

Responsible for:

- preserving failed processing attempts,
- operator investigation,
- controlled replay.

## Reconciliation

Responsible for:

- detecting missing events,
- detecting stale target state,
- repairing discrepancies.

---

# 55. Database Design Example

A conceptual event table could be:

```sql
CREATE TABLE webhook_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    event_timestamp TIMESTAMPTZ,
    version BIGINT,
    payload JSONB NOT NULL,
    status TEXT NOT NULL
);
```

Possible statuses:

```text
received
processed
failed
dead_lettered
replayed
```

This is an educational model, not a universal schema.

The important design properties are:

- stable event identity,
- raw payload retention,
- receipt time,
- source event time where available,
- ordering metadata where available,
- processing state.

---

# 56. Transactional Idempotency

The dangerous pattern is:

```text
SELECT event_id
     ↓
not found
     ↓
process
     ↓
INSERT event_id
```

Two workers can race:

```text
Worker A → SELECT → not found
Worker B → SELECT → not found

Worker A → process
Worker B → process
```

A safer design uses a database-enforced uniqueness constraint and a transaction strategy appropriate to the downstream side effects.

Conceptually:

```text
event_id PRIMARY KEY
```

The first worker can claim or record the event.

A second worker encounters a uniqueness conflict and can treat the event as already claimed/processed according to the transaction state.

For non-database side effects, additional idempotency mechanisms may be required.

---

# 57. Ordering Strategy

There is no single ordering solution.

Choose based on source guarantees.

### Strategy A — Trust a documented version

```text
incoming version > stored version
```

Apply only newer versions.

### Strategy B — Buffer and order

If the source provides a sequence and the system can safely wait, events can be buffered until the required ordering condition is satisfied.

### Strategy C — Fetch latest source state

Treat the webhook as a notification:

```text
something changed
```

Then fetch:

```text
current state
```

### Strategy D — Eventual correction

Apply events as they arrive, but use reconciliation to correct stale state.

The correct strategy depends on:

- source guarantees,
- latency requirements,
- consistency requirements,
- API capabilities.

---

# 58. Reference Implementation — Version 1: Minimal Receiver

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/webhooks/events")
async def receive_event(request: Request):
    body = await request.body()
    print(body)
    return {"status": "received"}
```

### What changed?

Nothing beyond basic reception.

### Why start here?

The learner should first understand:

```text
HTTP POST
+
request body
+
response
```

before adding security and reliability mechanisms.

---

# 59. Reference Implementation — Version 2: Raw Body

```python
@app.post("/webhooks/events")
async def receive_event(request: Request):
    body = await request.body()

    # Do not parse or modify `body` before signature verification.

    return {"status": "received"}
```

### Why?

Because the exact raw bytes can be part of the cryptographic verification input.

---

# 60. Reference Implementation — Version 3: HMAC

```python
import hashlib
import hmac


def calculate_signature(
    body: bytes,
    secret: bytes,
) -> str:
    return hmac.new(
        secret,
        body,
        hashlib.sha256,
    ).hexdigest()
```

Then:

```python
expected = calculate_signature(
    body,
    secret,
)

if not hmac.compare_digest(
    expected,
    received_signature,
):
    raise HTTPException(
        status_code=401,
        detail="Invalid signature",
    )
```

### Why?

The receiver must establish authenticity before trusting the payload.

---

# 61. Reference Implementation — Version 4: Replay Protection

Add a signed timestamp:

```text
timestamp
+
raw body
```

Then verify:

```python
if not is_timestamp_fresh(
    timestamp,
    max_skew_seconds=300,
):
    raise HTTPException(
        status_code=401,
        detail="Expired timestamp",
    )
```

The timestamp tolerance is configurable.

The provider's signing format is authoritative.

---

# 62. Reference Implementation — Version 5: Event Deduplication

After verifying the request:

```text
event_id
    |
    v
unique database constraint
```

Conceptual SQL:

```sql
INSERT INTO processed_webhook_events (
    event_id,
    received_at
)
VALUES (
    :event_id,
    CURRENT_TIMESTAMP
)
ON CONFLICT (event_id) DO NOTHING;
```

The exact SQL syntax depends on the database.

The important property is atomic uniqueness.

---

# 63. Reference Implementation — Version 6: Raw Event Landing

The receiver should preserve the verified raw body and useful metadata.

Conceptually:

```python
event = {
    "event_id": event_id,
    "received_at": received_at,
    "raw_body": body,
}
```

In production, the landing destination might be:

- object storage,
- a database,
- a durable queue,
- another durable event store.

The important requirement is durability and replayability.

---

# 64. Reference Implementation — Version 7: Asynchronous Processing

Conceptually:

```text
POST /webhooks/events
       |
       v
verify
       |
       v
land
       |
       v
200
       |
       v
queue
       |
       v
worker
```

Do not place expensive business processing directly in the HTTP acknowledgement path unless the provider contract and latency budget explicitly support it.

---

# 65. Reference Implementation — Version 8: Version Handling

Suppose events include:

```json
{
  "event_id": "evt_123",
  "entity_id": "cust_1",
  "version": 7,
  "data": {}
}
```

The processor can conceptually do:

```python
if incoming_version <= current_version:
    return "stale"
```

Otherwise:

```python
apply_event()
```

Only use this pattern when `version` has documented ordering semantics.

---

# 66. Reference Implementation — Version 9: Dead-Letter Handling

If processing fails after the configured retry policy:

```text
processor
   |
   +---- success → target
   |
   +---- retry
   |
   +---- terminal failure → DLQ
```

The DLQ record should preserve enough information to:

- identify the event,
- understand the failure,
- reproduce the processing attempt,
- replay safely.

---

# 67. Reference Implementation — Version 10: Replay and Reconciliation

Replay:

```text
DLQ
 ↓
operator selects event
 ↓
reprocess original event
 ↓
idempotent processor
```

Reconciliation:

```text
source API
   |
   v
current state
   |
   v
compare with target
   |
   v
repair discrepancies
```

Together, replay and reconciliation provide different recovery capabilities.

---

# 68. Complete Educational Reference Receiver

The following implementation combines the major ingress concepts while intentionally leaving durable storage and queue integrations as small interfaces.

```python
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Protocol

from fastapi import FastAPI, HTTPException, Request

logger = logging.getLogger(__name__)

app = FastAPI()

WEBHOOK_SECRET = b"development-only-secret"
MAX_SKEW_SECONDS = 300


@dataclass(frozen=True)
class StoredEvent:
    event_id: str
    event_type: str
    received_at: int
    raw_body: bytes
    payload: dict[str, Any]


class EventStore(Protocol):
    """Durable event-store abstraction."""

    def save_if_new(
        self,
        event: StoredEvent,
    ) -> bool:
        """Return True when the event was newly stored."""
        ...


class InMemoryEventStore:
    """Educational store.

    Production systems should use durable storage with uniqueness
    enforced by the persistence layer.
    """

    def __init__(self) -> None:
        self._events: dict[str, StoredEvent] = {}

    def save_if_new(
        self,
        event: StoredEvent,
    ) -> bool:
        if event.event_id in self._events:
            return False

        self._events[event.event_id] = event
        return True


event_store = InMemoryEventStore()


def verify_timestamp(
    timestamp: int,
    *,
    now: int | None = None,
) -> bool:
    current = int(time.time()) if now is None else now
    return abs(current - timestamp) <= MAX_SKEW_SECONDS


def calculate_signature(
    body: bytes,
    timestamp_text: str,
) -> str:
    signed_message = (
        f"{timestamp_text}.".encode()
        + body
    )

    return hmac.new(
        WEBHOOK_SECRET,
        signed_message,
        hashlib.sha256,
    ).hexdigest()


def verify_signature(
    body: bytes,
    timestamp_text: str,
    received_signature: str,
) -> bool:
    expected = calculate_signature(
        body,
        timestamp_text,
    )

    return hmac.compare_digest(
        expected,
        received_signature,
    )


@app.post("/webhooks/events")
async def receive_event(
    request: Request,
) -> dict[str, str]:
    body = await request.body()

    timestamp_text = request.headers.get(
        "X-Webhook-Timestamp"
    )
    signature = request.headers.get(
        "X-Webhook-Signature"
    )

    if timestamp_text is None or signature is None:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook authentication",
        )

    try:
        timestamp = int(timestamp_text)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid timestamp",
        ) from exc

    if not verify_timestamp(timestamp):
        raise HTTPException(
            status_code=401,
            detail="Expired timestamp",
        )

    if not verify_signature(
        body,
        timestamp_text,
        signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature",
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="Malformed JSON",
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail="Webhook payload must be an object",
        )

    event_id = payload.get("event_id")
    event_type = payload.get("event_type")

    if not isinstance(event_id, str) or not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing event_id",
        )

    if not isinstance(event_type, str) or not event_type:
        raise HTTPException(
            status_code=400,
            detail="Missing event_type",
        )

    event = StoredEvent(
        event_id=event_id,
        event_type=event_type,
        received_at=int(time.time()),
        raw_body=body,
        payload=payload,
    )

    is_new = event_store.save_if_new(event)

    logger.info(
        "webhook_received",
        extra={
            "event_id": event_id,
            "event_type": event_type,
            "duplicate": not is_new,
        },
    )

    if not is_new:
        return {"status": "duplicate"}

    # Production architecture:
    # enqueue the event for asynchronous processing here.

    return {"status": "received"}
```

## What this example demonstrates

It combines:

- raw-body access,
- timestamp verification,
- HMAC verification,
- constant-time comparison,
- JSON parsing after verification,
- event ID validation,
- deduplication,
- raw payload retention,
- structured logging,
- fast response.

## What remains educational

The in-memory store is not durable.

A production implementation should replace it with a durable persistence mechanism.

The queue is also represented as a conceptual boundary rather than a specific infrastructure product.

---

# 69. Why the Raw Event Must Be Preserved

Suppose the processor contains a bug:

```text
Webhook received
     |
     v
Raw event stored
     |
     v
Processor bug
     |
     v
Wrong target state
```

Without the raw event, debugging can require asking the source to resend the original event.

With the raw event:

```text
Stored payload
     |
     v
fix processor
     |
     v
replay
     |
     v
correct target
```

Raw event retention therefore turns many processing failures into recoverable incidents.

---

# 70. Debugging Scenario 1 — Provider Sends the Same Event Five Times

### Symptom

Logs show:

```text
evt_123
evt_123
evt_123
evt_123
evt_123
```

### Possible causes

- provider retries,
- receiver timeout,
- slow acknowledgement,
- network failure.

### Investigation

Compare:

```text
event_id
request timestamps
ack latency
HTTP status
provider retry metadata if available
```

### Root cause

The provider retried the same event.

### Fix

Deduplicate by stable event ID.

### Prevention

- fast acknowledgement,
- durable event ID uniqueness,
- observability for duplicates.

---

# 71. Debugging Scenario 2 — Signature Verification Fails Only in Production

### Symptom

Development succeeds, production rejects valid provider requests.

### Possible causes

- proxy modified body,
- middleware parsed/re-serialized JSON,
- incorrect secret,
- different header normalization,
- encoding differences,
- production gateway altered the request.

### Investigation

Capture safely:

```text
raw body bytes
signature header
timestamp header
```

Do not log secrets.

Compare the exact bytes reaching the application.

### Root cause example

The production application verified a re-serialized JSON body rather than the exact raw bytes.

### Fix

Verify the raw request body before parsing.

---

# 72. Debugging Scenario 3 — Valid Signatures Are Rejected Intermittently

### Possible causes

- clock skew,
- inconsistent server clocks,
- timestamp parsing bug,
- rotating secret configuration,
- multiple application versions with different secrets.

### Investigation

Check:

```text
server clock
provider timestamp
configured tolerance
active secret
previous secret during rotation
```

### Prevention

- synchronized clocks,
- controlled secret rotation,
- consistent configuration,
- metrics for rejection reason.

---

# 73. Debugging Scenario 4 — Same Payment Processed Twice

### Symptom

A payment appears twice downstream.

### Possible causes

- duplicate webhook,
- race between workers,
- check-then-insert deduplication,
- non-idempotent downstream side effect.

### Investigation

Inspect:

```text
event_id
worker IDs
processing timestamps
database uniqueness
```

### Root cause example

Two workers both executed:

```text
SELECT → not found
```

before either inserted the event ID.

### Fix

Use atomic uniqueness protection and an appropriate transaction/idempotency strategy.

---

# 74. Debugging Scenario 5 — Events Arrive Out of Order

### Symptom

Target contains an older state than expected.

### Example

```text
version 2 arrives
version 1 arrives
```

### Investigation

Compare:

```text
event timestamp
version
arrival timestamp
current target version
```

### Fix

Depending on source semantics:

- ignore stale versions,
- order by reliable sequence,
- fetch latest source state,
- reconcile later.

---

# 75. Debugging Scenario 6 — Receiver Returns 200 but Target Never Updates

### Symptom

Provider dashboard says delivery succeeded.

Target state is missing.

### Possible cause

The receiver acknowledged before the event was durably preserved.

Dangerous flow:

```text
receive
  ↓
200
  ↓
process
  ↓
crash
```

### Fix

Preserve the event before acknowledgement:

```text
receive
  ↓
verify
  ↓
durably land
  ↓
200
  ↓
process
```

---

# 76. Debugging Scenario 7 — Provider Retries Because Receiver Is Slow

### Symptom

One event produces multiple delivery attempts.

### Investigation

Measure:

```text
ack_latency
processing_latency
```

If:

```text
ack_latency ≈ processing_latency
```

the receiver may be performing too much work synchronously.

### Fix

Move expensive processing behind:

```text
raw landing / queue
```

and acknowledge quickly.

---

# 77. Debugging Scenario 8 — Valid Event Replayed Hours Later

### Symptom

A valid signature is received long after the original event.

### Possible cause

Replay attack or delayed legitimate delivery.

### Investigation

Check:

```text
signed timestamp
current time
configured tolerance
event ID
provider retry information
```

### Fix

Reject stale signed timestamps when the provider's security protocol supports them.

---

# 78. Debugging Scenario 9 — Events Disappear During Receiver Outage

### Symptom

Target is missing changes after an outage.

### Possible causes

- provider did not retry indefinitely,
- subscription delivery failed,
- receiver configuration was incorrect,
- provider delivery queue expired.

### Investigation

Compare:

```text
source state
received event IDs
target state
```

### Fix

Run reconciliation against the source API.

This is why:

```text
webhooks + reconciliation
```

is often stronger than webhooks alone.

---

# 79. Debugging Scenario 10 — Malformed Events Repeatedly Enter Processing

### Symptom

The same invalid event repeatedly fails.

### Possible causes

- no schema validation,
- retrying permanent errors,
- no DLQ,
- provider repeatedly sending an invalid event.

### Fix

Classify failures:

```text
transient → retry
permanent → dead-letter
```

Preserve the event for investigation and controlled replay after correction.

---

# 80. Debugging Scenario 11 — Target State Is Older Than Source

### Investigation

Compare:

```text
source current state
target current state
last event version
last event timestamp
```

Possible root causes:

- missing event,
- out-of-order event,
- stale event applied,
- processing failure,
- reconciliation gap.

The repair path depends on source capabilities.

---

# 81. Debugging Scenario 12 — Reconciliation Finds Missing Events

### Symptom

Source contains:

```text
payment 123
```

but target does not.

### Investigation

Search:

```text
event store
DLQ
processing logs
provider delivery history
```

### Possible root causes

- event was never delivered,
- event was rejected,
- event was dead-lettered,
- event was processed but target write failed.

### Fix

Use reconciliation to recover the state through the authoritative source API.

---

# 82. Common Production Mistakes

## Mistake 1 — Heavy processing before `2xx`

This increases timeout and retry risk.

## Mistake 2 — No signature verification

Anyone who can reach the endpoint may be able to submit fake events.

## Mistake 3 — Verify after parsing/re-serializing JSON

The bytes may no longer match what was signed.

## Mistake 4 — Ordinary equality for signatures

Use `hmac.compare_digest()`.

## Mistake 5 — No replay protection

A captured valid request may be reused.

## Mistake 6 — Assume exactly-once delivery

Duplicates are normal under at-least-once semantics.

## Mistake 7 — Assume ordered delivery

Arrival order may differ from event order.

## Mistake 8 — Use arrival time as event time

Network delay can change arrival order.

## Mistake 9 — No event deduplication

Retries can produce duplicate side effects.

## Mistake 10 — Non-atomic deduplication

A check-then-insert race can process an event twice.

## Mistake 11 — Discard raw events

Without raw events, replay and debugging become harder.

## Mistake 12 — No DLQ

Permanent failures become invisible or repeatedly retry forever.

## Mistake 13 — No replay mechanism

Processing bugs become manual recovery incidents.

## Mistake 14 — Treat webhooks as the only source of truth

Events can be lost.

## Mistake 15 — No reconciliation

Missing state can remain undetected.

## Mistake 16 — Log secrets

Secrets in logs can become a security incident.

## Mistake 17 — Accept arbitrary payload sizes

External input should not consume unbounded resources.

## Mistake 18 — Silently ignore unknown events

Unknown event types should be observable and handled deliberately.

---

# 83. Trade-Offs

Webhook architecture involves several decisions.

## 83.1 Webhooks vs Polling

| Webhooks | Polling |
|---|---|
| Low-latency notification | Controlled schedule |
| Less unnecessary requests | Easy periodic reconciliation |
| Duplicate delivery | Repeated requests |
| Retry handling required | Poll interval determines latency |
| Security endpoint required | Client initiates requests |

A hybrid design often uses both.

---

## 83.2 Synchronous vs Asynchronous Processing

### Synchronous

```text
request
 ↓
process
 ↓
response
```

Simple, but long processing can create delivery timeouts.

### Asynchronous

```text
request
 ↓
land/queue
 ↓
response
 ↓
worker
```

More moving parts, but better separation and failure isolation.

---

## 83.3 Process Immediately vs Land First

Immediate processing:

```text
lower storage delay
simpler path
```

Land first:

```text
replayability
auditability
recovery
debugging
```

The choice depends on durability and operational requirements.

---

## 83.4 Event Payload vs Latest State

Payload-based:

```text
fast
fewer API calls
```

Latest-state fetch:

```text
can avoid stale/out-of-order state
more API calls
higher latency
```

---

## 83.5 Reconciliation Frequency

More frequent reconciliation:

```text
faster detection
higher source load
```

Less frequent reconciliation:

```text
lower source load
longer inconsistency window
```

The correct frequency depends on business requirements.

---

## 83.6 Queue vs Direct Processing

Direct:

```text
Webhook → processor
```

Queue:

```text
Webhook → queue → processor
```

A queue adds infrastructure and operational complexity, but can provide buffering and independent scaling.

---

# 84. Performance Considerations

Important performance dimensions include:

- webhook acknowledgement latency,
- payload size,
- request concurrency,
- raw landing throughput,
- queue throughput,
- worker throughput,
- deduplication lookup cost,
- database contention,
- reconciliation frequency.

The critical distinction is:

```text
Ingress latency
```

versus:

```text
Processing latency
```

A receiver can acknowledge in milliseconds while downstream processing takes seconds.

The goal is not necessarily to make the entire workflow synchronous and fast.

The goal is to make the delivery boundary reliable and appropriately fast.

---

# 85. Security Checklist

```text
[ ] HTTPS
[ ] Signature verification
[ ] Raw-body verification
[ ] Constant-time signature comparison
[ ] Replay protection
[ ] Timestamp validation
[ ] Secret rotation
[ ] Least privilege
[ ] IP allowlisting where appropriate
[ ] Payload-size limits
[ ] Input validation
[ ] No secrets in logs
[ ] Sensitive-data minimization
[ ] Audit logging
```

### HTTPS

Protects the connection in transit.

### Signature verification

Authenticates the sender according to the provider's signing protocol.

### Raw-body verification

Ensures the cryptographic input matches what the sender signed.

### Constant-time comparison

Uses the standard library's appropriate comparison primitive.

### Replay protection

Prevents stale valid messages from being accepted indefinitely when the protocol supports freshness checks.

### Secret rotation

Limits long-term exposure of a signing credential.

### Least privilege

The webhook service should have only the permissions it needs.

### IP allowlisting

Adds a network-level control where appropriate.

### Payload-size limits

Protects resources.

### Input validation

Prevents malformed or unexpected events from entering downstream processing.

### No secrets in logs

Avoids turning observability systems into credential stores.

---

# 86. Reliability Checklist

```text
[ ] Fast acknowledgement
[ ] Raw event landing
[ ] Idempotent processing
[ ] Event ID deduplication
[ ] Durable state
[ ] Retry handling
[ ] Dead-letter handling
[ ] Replay
[ ] Ordering strategy
[ ] Reconciliation
[ ] Monitoring
[ ] Alerting
```

A webhook system is not production-ready merely because it returns `200`.

---

# 87. Hands-On Project

Build a webhook ingestion system using FastAPI.

The implementation should progressively support:

1. HMAC signature verification.
2. Timestamp verification.
3. Invalid-request rejection.
4. Raw request-body handling.
5. Durable-event abstraction.
6. Fast acknowledgement.
7. Event ID deduplication.
8. Version-aware event application.
9. Out-of-order event handling.
10. Latest-state fetching strategy.
11. Malformed JSON handling.
12. Dead-letter handling.
13. Replay.
14. Provider retry simulation.
15. Duplicate-delivery simulation.
16. Reconciliation against a mock source API.

The entire learning implementation should remain understandable.

Do not turn the project into a framework-building exercise.

---

# 88. Hands-On Exercise 1 — Pull vs Push

Create a short design comparison for the following requirement:

```text
A source changes approximately 1,000 records per hour.
The target should normally reflect changes within 1 minute.
```

Describe:

- a polling architecture,
- a webhook architecture,
- a hybrid architecture.

For each, identify:

- latency,
- source load,
- failure recovery,
- reconciliation strategy.

### Expected result

You should recognize that the correct architecture depends on source capabilities and correctness requirements rather than simply selecting “webhooks.”

---

# 89. Hands-On Exercise 2 — Minimal FastAPI Receiver

Build:

```http
POST /webhooks/events
```

Requirements:

- read the raw body,
- return a successful response,
- log only safe metadata.

Then add:

- event ID validation,
- event type validation.

### Expected result

You can receive and validate the basic event envelope before adding security.

---

# 90. Hands-On Exercise 3 — HMAC Verification

Implement:

```python
verify_hmac_signature()
```

Test:

1. valid signature,
2. invalid signature,
3. modified body,
4. wrong secret.

### Expected result

Any change to the signed input causes verification failure.

---

# 91. Hands-On Exercise 4 — Replay Protection

Add a timestamp.

Test:

```text
fresh timestamp → accepted
stale timestamp → rejected
```

Then test different clock values.

### Expected result

The timestamp tolerance is deterministic and configurable.

---

# 92. Hands-On Exercise 5 — Deduplication

Send:

```text
evt_1
evt_2
evt_1
evt_3
evt_2
```

Expected processing behavior:

```text
evt_1 → process
evt_2 → process
evt_1 → duplicate
evt_3 → process
evt_2 → duplicate
```

Verify that the database uniqueness mechanism prevents concurrent duplicate processing.

---

# 93. Hands-On Exercise 6 — Out-of-Order Events

Create:

```text
version 1
version 2
version 3
```

Send:

```text
version 2
version 1
version 3
```

Implement a version-aware target.

Expected final state:

```text
version 3
```

Then repeat without version metadata and design a latest-state-fetch strategy.

---

# 94. Hands-On Exercise 7 — Dead Letter

Create a processor that intentionally fails on:

```text
event_type = "invalid.example"
```

Verify:

```text
event
 ↓
processing failure
 ↓
retry
 ↓
DLQ
```

Then repair the processor and replay the event.

---

# 95. Hands-On Exercise 8 — Reconciliation

Create a mock source API with:

```text
source:
A B C D E

target:
A B C E
```

The webhook event for `D` was lost.

Implement reconciliation that discovers:

```text
D missing from target
```

and repairs the target.

---

# 96. Hands-On Exercise 9 — Failure Injection

Simulate:

```text
invalid signature
expired timestamp
duplicate
out-of-order event
malformed JSON
processor failure
receiver restart
```

Record:

```text
expected behavior
actual behavior
root cause if incorrect
fix
```

---

# 97. Hands-On Exercise 10 — Observability

Add metrics or counters for:

```text
received
verified
rejected
duplicate
processed
failed
dead_lettered
replayed
ack_latency
processing_latency
```

Then produce a small incident report for a simulated failure.

---

# 98. Advanced Design Challenge

Design an ingestion architecture for:

```text
Payment provider

Requirements:
- low-latency ingestion
- duplicate deliveries possible
- events can arrive out of order
- HMAC signatures
- signed timestamps
- provider retries
- occasional event loss
- reconciliation API
- payment state must eventually be correct
```

Design:

- webhook endpoint,
- authentication,
- signature validation,
- replay protection,
- raw event storage,
- acknowledgement strategy,
- deduplication,
- ordering,
- processing,
- DLQ,
- replay,
- reconciliation,
- observability,
- security controls.

---

# 99. Advanced Challenge — Reference Architecture

A strong conceptual answer is:

```text
                         Payment Provider
                               |
                               | HTTPS POST
                               v
                     +-----------------------+
                     | Webhook Endpoint      |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Raw Body Validation   |
                     | HMAC + Timestamp      |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Durable Raw Event     |
                     | event_id UNIQUE       |
                     +-----------+-----------+
                                 |
                               2xx
                                 |
                                 v
                     +-----------------------+
                     | Queue / Work Buffer   |
                     +-----------+-----------+
                                 |
                                 v
                     +-----------------------+
                     | Event Processor       |
                     | Dedup + Versioning    |
                     +-----------+-----------+
                                 |
                    +------------+------------+
                    |                         |
                    v                         v
                Payment DB                  DLQ
                                              |
                                              v
                                            Replay

                   Periodic Reconciliation API
                               |
                               v
                         State comparison
                               |
                               v
                         Repair target
```

### Why this architecture works

It separates:

```text
security
delivery
durability
processing
recovery
reconciliation
```

Each has a clear responsibility.

---

# 100. Architecture / Interview Questions

## Questions

1. What is a webhook?
2. What is the difference between polling and webhooks?
3. Why should a webhook receiver acknowledge quickly?
4. Why do webhook providers retry?
5. What does at-least-once delivery mean?
6. Why are duplicate events normal?
7. How would you deduplicate webhook events?
8. Why should event IDs have a uniqueness constraint?
9. Why must HMAC verification use the raw request body?
10. Why use `hmac.compare_digest()`?
11. What is a replay attack?
12. How does a signed timestamp help?
13. How do you handle secret rotation?
14. Why isn't IP allowlisting sufficient by itself?
15. Why should raw events be persisted before processing?
16. How would you handle out-of-order events?
17. What if the webhook payload is stale?
18. When would you fetch the latest state from the API?
19. Why do webhooks need reconciliation?
20. How would you handle a malformed event?
21. What belongs in a dead-letter queue?
22. How would you safely replay a failed webhook?
23. How would you design webhook ingestion for 100,000 events per minute?
24. What happens if your receiver is unavailable for 30 minutes?
25. How would you prove that webhook ingestion is not silently losing events?

---

# 101. Reference Answers

## 1. What is a webhook?

A webhook is an HTTP callback where a source sends an HTTP request to a receiver when an event occurs.

---

## 2. What is the difference between polling and webhooks?

Polling means the consumer requests changes. Webhooks mean the source pushes notifications to the consumer.

Polling gives the consumer timing control. Webhooks can provide lower latency but introduce delivery, retry, security, and ordering concerns.

---

## 3. Why should a webhook receiver acknowledge quickly?

Because providers may retry requests when delivery takes too long. Fast acknowledgement reduces unnecessary retries and separates delivery from expensive processing.

---

## 4. Why do webhook providers retry?

Retries provide resilience against temporary receiver or network failures. Exact retry behavior is provider-specific.

---

## 5. What does at-least-once delivery mean?

The provider attempts to deliver the event, but duplicate delivery is possible.

---

## 6. Why are duplicate events normal?

A provider may retry after a timeout even when the original request was actually received and processed.

---

## 7. How would you deduplicate webhook events?

Use a stable event ID and durable uniqueness protection, typically enforced by a database or equivalent durable store.

---

## 8. Why should event IDs have a uniqueness constraint?

Because application-level check-then-insert logic can race when multiple workers process the same event concurrently. Database-enforced uniqueness provides an atomic protection boundary.

---

## 9. Why must HMAC verification use the raw request body?

The sender signs bytes. Parsing and re-serializing JSON can change those bytes even when the logical JSON data remains equivalent.

---

## 10. Why use `hmac.compare_digest()`?

It is the standard library's appropriate constant-time comparison primitive for sensitive signature comparisons.

---

## 11. What is a replay attack?

An attacker captures a valid signed request and sends it again later.

---

## 12. How does a signed timestamp help?

It provides freshness information. The receiver can reject requests outside an allowed timestamp tolerance.

---

## 13. How do you handle secret rotation?

Use secure secret storage, coordinate provider and receiver changes, support the documented transition mechanism, and remove the old secret after the rotation period.

---

## 14. Why isn't IP allowlisting sufficient by itself?

Source IP addresses can change and network infrastructure can introduce proxies or other intermediaries. IP filtering does not cryptographically authenticate the message.

---

## 15. Why persist raw events before processing?

Raw persistence enables replay, debugging, auditing, schema evolution, and recovery after downstream failures.

---

## 16. How would you handle out-of-order events?

If the source provides a reliable version or sequence, use it. Otherwise consider fetching current source state or using reconciliation rather than blindly applying arrival order.

---

## 17. What if the webhook payload is stale?

Do not blindly overwrite newer target state. Use reliable version metadata if available or fetch current source state when correctness requires it.

---

## 18. When would you fetch latest state from the API?

When the webhook is better treated as a change notification and the event payload/order cannot safely establish current authoritative state.

---

## 19. Why do webhooks need reconciliation?

Because events can be lost, delayed, rejected, or otherwise fail to update the target. Reconciliation compares the target with authoritative source state.

---

## 20. How would you handle a malformed event?

Reject it at the appropriate boundary or preserve it in a controlled dead-letter path, depending on whether the failure is an ingress validation error or a downstream processing error.

---

## 21. What belongs in a dead-letter queue?

Events that could not be successfully processed after the appropriate retry policy, along with enough metadata and original payload information to diagnose and safely replay them.

---

## 22. How would you safely replay a failed webhook?

Replay the preserved raw event through the same idempotent processing path after fixing the underlying problem. Verify that repeated application cannot create unintended duplicate effects.

---

## 23. How would you design webhook ingestion for 100,000 events per minute?

Separate ingress from processing:

```text
load-balanced HTTPS receivers
        ↓
signature/replay validation
        ↓
durable event landing / queue
        ↓
scalable workers
        ↓
idempotent target updates
        ↓
DLQ + replay
        ↓
reconciliation
```

Then measure and capacity-plan each layer.

The exact architecture depends on provider limits, payload size, processing cost, storage system, and consistency requirements.

---

## 24. What happens if your receiver is unavailable for 30 minutes?

The provider may retry, but the exact outcome depends on its delivery contract. The system should also use reconciliation to detect missing events if possible.

---

## 25. How would you prove webhook ingestion is not silently losing events?

Use multiple signals:

```text
provider/source state
+
received event counts
+
unique event IDs
+
processing outcomes
+
DLQ counts
+
target state
+
periodic reconciliation
```

No single metric proves completeness in every system.

---

# 102. Production Design Checklist

## Security

- [ ] HTTPS is used in production.
- [ ] Webhook signatures are verified.
- [ ] Verification uses the raw request body.
- [ ] Signature comparison uses `hmac.compare_digest()`.
- [ ] Replay protection is implemented where supported.
- [ ] Timestamp freshness is validated.
- [ ] Secrets are securely stored.
- [ ] Secret rotation is defined.
- [ ] IP allowlisting is used only as an additional control where appropriate.
- [ ] Payload-size limits exist.
- [ ] Secrets are absent from logs.
- [ ] Sensitive payload data is minimized.

## Correctness

- [ ] Stable event ID is identified.
- [ ] Event IDs are deduplicated.
- [ ] Database uniqueness is enforced where appropriate.
- [ ] Ordering guarantees are documented.
- [ ] Version/sequence handling exists when available.
- [ ] Stale-event behavior is defined.
- [ ] Latest-state fetching is considered where ordering is unsafe.
- [ ] Reconciliation exists where event loss is possible.

## Reliability

- [ ] Receiver acknowledges quickly.
- [ ] Raw verified events are durably landed.
- [ ] Processing is separated from ingress when necessary.
- [ ] Provider retries are expected.
- [ ] Duplicate delivery is safe.
- [ ] Dead-letter handling exists.
- [ ] Replay exists.
- [ ] Receiver outage recovery is understood.
- [ ] Processing retries are bounded and observable.

## Observability

- [ ] Received count is measured.
- [ ] Verified count is measured.
- [ ] Rejected count is measured.
- [ ] Duplicate count is measured.
- [ ] Processed count is measured.
- [ ] Failed count is measured.
- [ ] DLQ count is measured.
- [ ] Replay count is measured.
- [ ] Acknowledgement latency is measured.
- [ ] Processing latency is measured.
- [ ] Reconciliation mismatches are measured.
- [ ] Logs contain safe correlation metadata.

## Testing

- [ ] Valid signature.
- [ ] Invalid signature.
- [ ] Modified payload.
- [ ] Expired timestamp.
- [ ] Wrong secret.
- [ ] Duplicate event.
- [ ] Provider retry.
- [ ] Out-of-order event.
- [ ] Missing event ID.
- [ ] Malformed JSON.
- [ ] Processing failure.
- [ ] DLQ.
- [ ] Replay.
- [ ] Reconciliation.
- [ ] Oversized payload.
- [ ] Slow processor.
- [ ] Receiver restart.

---

# 103. Final Self-Assessment

## Basics

- [ ] I can explain pull versus push.
- [ ] I can explain what a webhook is.
- [ ] I can describe the webhook lifecycle.
- [ ] I understand why providers retry.
- [ ] I understand at-least-once delivery.

## Security

- [ ] I can verify HMAC signatures.
- [ ] I understand why raw request bodies matter.
- [ ] I can use constant-time comparison.
- [ ] I understand replay attacks.
- [ ] I can validate signed timestamps.
- [ ] I understand secret rotation.
- [ ] I understand the role and limits of IP allowlists.

## Reliability

- [ ] I can deduplicate events.
- [ ] I understand atomic uniqueness.
- [ ] I can handle out-of-order delivery.
- [ ] I can land raw events.
- [ ] I can separate ingress from processing.
- [ ] I can use a DLQ.
- [ ] I can replay events.
- [ ] I can reconcile against the source.

## Production

- [ ] I can design a production webhook receiver.
- [ ] I can define webhook metrics.
- [ ] I can debug failed deliveries.
- [ ] I can explain webhook failure modes.
- [ ] I can design for provider retries.
- [ ] I can explain how event loss is detected.
- [ ] I can defend the architecture in a design review.

---

# 104. Key Takeaways

The complete learning progression is:

```text
Beginner
   ↓
Understand pull vs push
   ↓
Understand webhooks
   ↓
Build a minimal receiver
   ↓
Understand fast acknowledgement
   ↓
Understand provider retries
   ↓
Understand at-least-once delivery
   ↓
Implement event-ID deduplication
   ↓
Implement HMAC verification
   ↓
Verify the raw request body
   ↓
Use constant-time comparison
   ↓
Understand replay attacks
   ↓
Validate signed timestamps
   ↓
Rotate secrets safely
   ↓
Apply HTTPS and payload limits
   ↓
Land raw events
   ↓
Separate ingestion from processing
   ↓
Handle event ordering
   ↓
Use versions where trustworthy
   ↓
Fetch latest state when appropriate
   ↓
Handle dead letters
   ↓
Replay failed events
   ↓
Understand event loss
   ↓
Build reconciliation
   ↓
Test failure modes
   ↓
Add observability
   ↓
Design the production architecture
   ↓
Defend the architecture in an interview/design review
```

The most important principles are:

> **A webhook is a delivery mechanism, not automatically the source of truth.**

> **Assume webhook delivery is at least once unless the provider explicitly guarantees otherwise.**

> **Duplicate delivery must be expected and safely handled.**

> **Verify the raw request before trusting the payload.**

> **A valid signature does not automatically mean the request is fresh.**

> **Acknowledge quickly and process asynchronously when processing is expensive.**

> **Persist raw events so they can be replayed.**

> **Never assume webhook events arrive in order unless the provider explicitly guarantees it.**

> **When ordering matters and reliable versions are unavailable, fetching current source state may be safer than blindly applying events.**

> **Webhooks should be reconciled with the source when event loss is possible.**

> **Dead-lettered events should be recoverable rather than silently discarded.**

> **Security, correctness, and observability are part of ingestion design—not optional additions.**

A production webhook system is therefore not:

```text
POST → process → 200
```

It is closer to:

```text
                 Source
                   |
                   | HTTPS POST
                   v
            +--------------+
            | Authenticate |
            | + Verify     |
            +------+-------+
                   |
                   v
            +--------------+
            | Replay       |
            | Protection   |
            +------+-------+
                   |
                   v
            +--------------+
            | Raw Event    |
            | Landing      |
            +------+-------+
                   |
                   v
                 2xx
                   |
                   v
            +--------------+
            | Queue /      |
            | Async Work   |
            +------+-------+
                   |
                   v
            +--------------+
            | Dedup +      |
            | Ordering     |
            +------+-------+
                   |
             +-----+-----+
             |           |
             v           v
          Target       DLQ
                         |
                         v
                       Replay

                   +-----------+
                   | Source API |
                   | Reconcile |
                   +-----+-----+
                         |
                         v
                    Target Repair
```

That architecture turns webhook delivery from a fragile HTTP callback into a controlled, observable, recoverable data-ingestion system.
