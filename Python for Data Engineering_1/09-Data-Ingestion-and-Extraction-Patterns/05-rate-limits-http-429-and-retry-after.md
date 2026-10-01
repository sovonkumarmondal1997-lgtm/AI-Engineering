# Topic 05 — Rate Limits, HTTP 429, and Retry-After

> A good data extractor is not merely fast. It is fast **and polite to the source**.

This chapter builds rate-limit engineering from first principles to production architecture. The central problem is not simply “how do I retry a failed HTTP request?” It is:

> **How do I make useful progress without overwhelming the source system, wasting quota, creating retry storms, duplicating side effects, or hiding an outage?**

---

## Learning Objectives

After completing this chapter, you should be able to:

- Explain why APIs enforce rate limits.
- Distinguish request-rate, concurrency, burst, quota, per-user, per-token, per-IP, per-organization, endpoint-specific, and weighted limits.
- Explain HTTP `429 Too Many Requests`.
- Interpret `Retry-After` in both supported forms.
- Interpret common rate-limit headers without assuming they are universal.
- Classify retryable and non-retryable failures.
- Distinguish **retryability** from **retry safety**.
- Implement bounded retries.
- Implement exponential backoff and jitter.
- Honor provider-directed `Retry-After` delays.
- Use Tenacity appropriately.
- Implement proactive throttling.
- Explain and implement a token bucket.
- Explain and implement an educational sliding-window limiter.
- Coordinate quota usage across workers.
- Understand idempotency keys for non-idempotent operations.
- Explain circuit breakers.
- Estimate request budgets and quota consumption.
- Optimize page sizes and filters to reduce unnecessary requests.
- Instrument rate-limit behavior.
- Design a production-grade, polite API extractor.

---

## Prerequisites

This topic assumes you have already studied:

- HTTP fundamentals.
- HTTP methods and status codes.
- Request/response structure.
- HTTP clients.
- Sessions and connections.
- Timeouts.
- Authentication.
- Pagination.
- Generators.

The learning sequence is:

```text
Topic 01
HTTP status codes
      ↓
Topic 02
HTTP client behavior
      ↓
Topic 03
Authentication
      ↓
Topic 04
Pagination
      ↓
Topic 05
Rate limits + retry behavior
```

Pagination naturally creates rate-limit pressure. If two million records require two thousand pages, the extractor has to make approximately two thousand page requests before considering retries, metadata calls, authentication calls, polling, or failures. Rate-limit engineering therefore becomes a natural next step after pagination.

This chapter does **not** become a full tutorial on incremental extraction, CDC, webhooks, SFTP, `dlt`, OAuth token refresh, async Python, or distributed data processing. Those topics belong elsewhere in the roadmap and are mentioned only when they help explain rate-limit behavior.

---

# 1. The Core Mental Model

Rate limiting is simultaneously:

```text
Reliability engineering
        +
Source-system protection
        +
Performance engineering
        +
Cost management
```

An extractor interacts with a provider under a contract:

```text
Provider contract
      |
      +-- request limits
      +-- concurrency limits
      +-- quotas
      +-- burst rules
      +-- endpoint rules
      +-- retry guidance
      +-- idempotency behavior
      |
      v
Your extractor
```

The extractor must respect that contract while still meeting its own operational requirements.

A production design therefore separates two concerns:

```text
RATE LIMITER
Controls traffic before requests are sent.

RETRY POLICY
Controls what happens after a request fails.
```

They complement each other.

```text
Application
    |
    v
Rate Limiter
    |
    v
HTTP Client
    |
    v
API
    |
    v
Response
    |
    +---- success ----------> Process
    |
    +---- retryable failure -> Retry Policy
                                  |
                                  v
                             Wait / Backoff
                                  |
                                  v
                                Retry
```

---

# 2. Why APIs Enforce Rate Limits

## 2.1 Infrastructure protection

An API may need to protect:

- CPU.
- Memory.
- Database connections.
- Database query capacity.
- Network bandwidth.
- Caches.
- Downstream services.
- Queue capacity.

Without controls, one consumer can create disproportionate load.

## 2.2 Fairness

A provider may have many customers:

```text
                     API Provider
                          |
                +---------+---------+
                |         |         |
              User A    User B    User C
                |         |         |
                +---------+---------+
                          |
                     Shared System
                          |
                     Rate Limiter
                          |
                   Protected Backend
```

A rate limiter prevents one consumer from monopolizing shared infrastructure.

## 2.3 Cost control

Provider infrastructure has real costs. A request may trigger:

```text
HTTP request
   ↓
API service
   ↓
Database query
   ↓
Cache / storage
   ↓
Downstream service
```

A seemingly cheap API request can create substantial internal work.

## 2.4 Abuse prevention

Rate limits also constrain accidental runaway programs and automated abuse.

For example, a bug such as:

```python
while True:
    fetch_next_page()
```

can otherwise produce traffic much faster than a human operator intended.

## 2.5 Stability

A provider wants predictable service behavior. Rate limits create a controlled boundary between demand and capacity.

---

# 3. Rate Limit Fundamentals

A rate limit controls how much traffic a client can send to a service within some period or under some resource constraint.

The simplest example is:

```text
100 requests / minute
```

That does **not** necessarily mean the implementation is simply:

```text
sleep(0.6)
```

Real APIs may enforce multiple overlapping constraints.

## 3.1 Request-rate limits

Example:

```text
60 requests/minute
```

This controls sustained request frequency.

## 3.2 Burst limits

Example:

```text
100 requests immediately
then sustained rate of 20/sec
```

A system can therefore allow short bursts while controlling long-term traffic.

## 3.3 Concurrency limits

Example:

```text
Maximum 10 simultaneous requests
```

This is different from requests per second.

You could send ten long-running requests and have:

```text
10 in flight
0 completed
```

A concurrency limit controls **simultaneous work**, not just request frequency.

## 3.4 Daily quotas

Example:

```text
1,000,000 requests/day
```

This is a budget rather than simply a short-term rate.

## 3.5 Per-user, token, IP, and organization limits

A provider may apply limits to:

- A user.
- An API token.
- An IP address.
- An organization/account.
- A project.
- A subscription tier.

Never assume which identity is being limited without reading provider documentation.

## 3.6 Endpoint-specific limits

For example:

```text
GET  /customers → 1000/min
POST /exports   → 20/hour
```

A client can be below the general quota and still exceed an endpoint-specific limit.

## 3.7 Weighted quotas

Some systems assign different costs:

```text
Simple GET       = 1 unit
Complex query    = 10 units
```

This is provider-specific. Do not assume every API uses weighted requests.

> **Provider documentation is authoritative.**

---

# 4. Rate Limit vs Concurrency vs Quota

These concepts are related but not interchangeable.

| Mechanism | Example | What it controls |
|---|---|---|
| Request rate | 100/minute | Request frequency |
| Burst | 20 immediately | Short-term traffic |
| Concurrency | 10 in flight | Simultaneous requests |
| Daily quota | 1M/day | Total budget |
| Endpoint limit | 20 exports/hour | Specific operation |
| Weighted quota | 10 units/query | Resource-weighted usage |

A robust client may need to satisfy several simultaneously.

For example:

```text
At most 100 requests/minute
AND
at most 10 concurrent requests
AND
at most 1,000,000 requests/day
AND
at most 20 export requests/hour
```

---

# 5. HTTP 429 — Too Many Requests

HTTP `429 Too Many Requests` indicates that the server is refusing a request because the client has exceeded a rate or quota constraint.

Example:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 5

{"error":"rate limit exceeded"}
```

A simple mental model is:

```text
Client
   |
   | Request 101
   v
 API
   |
   | 429
   v
Client
   |
   | wait
   v
Client
   |
   | retry
   v
 API
   |
   | success
   v
Client
```

## 5.1 Why 429 differs from 500

A `500` generally indicates a server-side failure.

A `429` indicates that the server is intentionally rejecting traffic because a rate or quota constraint was exceeded.

The response to the two should therefore be informed by different signals.

## 5.2 Why immediate retrying is dangerous

Suppose a provider says:

```text
429
Retry-After: 5
```

If one hundred workers all immediately retry:

```text
100 workers
    ↓
429
    ↓
100 immediate retries
    ↓
more overload / more 429s
```

The retry itself becomes additional load.

## 5.3 429 is often retryable, not automatically retryable

The precise rule is:

> `429` generally indicates that waiting may make the request possible again. Retrying is often appropriate, but the operation's safety, retry budget, provider contract, and deadline still matter.

---

# 6. Retry-After

`Retry-After` gives the client server-provided guidance about when it should retry.

Two forms are defined.

## 6.1 Delta-seconds

```http
Retry-After: 5
```

Interpretation:

```text
Wait approximately 5 seconds.
```

## 6.2 HTTP-date

```http
Retry-After: Wed, 21 Oct 2026 07:28:00 GMT
```

Interpretation:

```text
Retry at approximately that HTTP date.
```

## 6.3 Why provider guidance matters

Suppose:

```text
Retry-After: 20
```

but your local exponential backoff says:

```text
8 seconds
```

The client should generally respect the provider's 20-second guidance rather than retry after only 8 seconds.

A practical model is:

```text
server-directed delay
        OR
local fallback backoff
        |
        v
effective delay
```

subject to your own safety caps and overall deadline.

---

# 7. Parsing Retry-After Safely

The parser should handle:

- Integer seconds.
- HTTP-date.
- Invalid values.
- Dates in the past.
- Clock differences.
- Maximum wait caps.

```python
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def parse_retry_after(
    value: str | None,
    *,
    now: datetime | None = None,
    max_wait_seconds: float = 300.0,
) -> float | None:
    """Return a bounded Retry-After delay, or None if unusable."""
    if not value:
        return None

    value = value.strip()

    try:
        seconds = float(value)
        if seconds < 0:
            return None
        return min(seconds, max_wait_seconds)
    except ValueError:
        pass

    try:
        retry_at = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None

    if retry_at.tzinfo is None:
        retry_at = retry_at.replace(tzinfo=timezone.utc)

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    delay = max(0.0, (retry_at - now).total_seconds())
    return min(delay, max_wait_seconds)
```

### Why each part matters

`float(value)` allows a numeric delay to be interpreted.

```python
if seconds < 0:
    return None
```

A negative delay is not meaningful provider guidance.

For an HTTP-date:

```python
parsedate_to_datetime(value)
```

parses the HTTP date representation.

Then:

```python
max(0.0, ...)
```

handles a date that is already in the past.

Finally:

```python
min(delay, max_wait_seconds)
```

prevents a malformed or unexpectedly long server-directed delay from silently blocking a job forever.

### Clock skew

HTTP-date interpretation depends on clocks. The client and server do not have to have perfectly synchronized clocks.

For this reason:

- Prefer delta-seconds when provided.
- Treat HTTP-date as approximate.
- Use a maximum retry deadline.
- Do not allow an enormous server-directed wait to bypass job-level operational limits.

---

# 8. Common Rate-Limit Headers

Providers commonly expose headers such as:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 37
X-RateLimit-Reset: 1790870400
```

These names are common but are **not universal protocol guarantees**.

## 8.1 Limit

```text
X-RateLimit-Limit: 1000
```

May indicate the capacity for a particular window.

## 8.2 Remaining

```text
X-RateLimit-Remaining: 37
```

May indicate how much capacity remains.

## 8.3 Reset

```text
X-RateLimit-Reset: 1790870400
```

Often represents a Unix timestamp at which a quota/window resets.

However, the exact semantics vary by provider.

## 8.4 Standardized RateLimit header family

Modern APIs may expose the standardized `RateLimit` header family rather than historical `X-RateLimit-*` conventions.

The important production principle is:

> Header names alone do not define semantics. Provider documentation does.

Capture these headers when useful for observability, but do not write code that assumes every API sends them.

---

# 9. Retryability vs Retry Safety

This distinction is more important than memorizing status codes.

Every retry system should ask two questions:

```text
Question 1:
Could the failure be temporary?

Question 2:
Is repeating the operation safe?
```

Conceptually:

```text
                         Retry-safe?
                      Yes             No
                  +-------------+-------------+
Temporary         | Retry       | Need        |
failure           | carefully   | idempotency |
                  +-------------+-------------+
Permanent         | Do not      | Do not      |
failure           | retry       | retry       |
                  +-------------+-------------+
```

A failure can be retryable while the operation is unsafe to repeat.

Example:

```http
POST /exports
```

Suppose the client sends the request, the server creates the export, but the network fails before the client receives the response.

The client sees:

```text
Timeout
```

The timeout may be transient.

But blindly repeating:

```http
POST /exports
```

could create a second export.

Therefore:

```text
Retryable failure
        ≠
Retry-safe operation
```

---

# 10. Retry Decision Matrix

A useful starting point is:

| Failure | Retry? | Why? | Delay strategy |
|---|---|---|---|
| Connection failure | Often | Network may recover | Backoff + jitter |
| Timeout | Often | Server/network may recover | Backoff + jitter |
| 408 | Often | Request timeout | Backoff |
| 429 | Often, when appropriate | Rate/quota constraint | `Retry-After` first |
| 500 | Often | Server failure may be temporary | Backoff + jitter |
| 502 | Often | Gateway failure may recover | Backoff |
| 503 | Often | Service unavailable | `Retry-After` / backoff |
| 504 | Often | Gateway timeout | Backoff |
| 400 | Usually no | Request is invalid | Fix request |
| 401 | Conditional | Credentials may need refresh | Refresh once, then retry once if appropriate |
| 403 | Usually no | Permission/policy issue | Fix authorization/policy |
| 404 | Usually no | Resource/path may be wrong | Fix resource/path |
| 422 | Usually no | Validation failure | Fix payload |

This table is a starting policy, not a universal law.

Provider behavior and operation semantics can override it.

---

# 11. Exponential Backoff

## 11.1 Why immediate retry is dangerous

Imagine 100 workers receive a temporary `503`.

If every worker retries immediately:

```text
100 workers
    ↓
503
    ↓
100 immediate retries
    ↓
503
    ↓
100 immediate retries
```

The clients can amplify the provider's outage.

## 11.2 Exponential backoff

A simple sequence is:

```text
Attempt 1 → wait 1 sec
Attempt 2 → wait 2 sec
Attempt 3 → wait 4 sec
Attempt 4 → wait 8 sec
Attempt 5 → wait 16 sec
```

A common formula is:

```text
delay = min(cap, base * 2^attempt)
```

Where:

- `base` controls the initial delay.
- `attempt` is the retry attempt number.
- `cap` prevents unbounded waits.

Example:

```python
def exponential_backoff(
    attempt: int,
    *,
    base: float = 1.0,
    cap: float = 60.0,
) -> float:
    return min(cap, base * (2 ** attempt))
```

If:

```text
base = 1
cap = 60
```

then the delays are approximately:

```text
1, 2, 4, 8, 16, 32, 60, 60, ...
```

The cap is important because exponential growth otherwise becomes impractical.

---

# 12. Jitter

Exponential backoff alone can still synchronize workers.

Suppose:

```text
Worker A → retry in 4 sec
Worker B → retry in 4 sec
Worker C → retry in 4 sec
Worker D → retry in 4 sec
```

They may all send requests at approximately the same time again.

Jitter randomizes the delay.

## 12.1 Full jitter

A simple strategy is:

```text
delay = random value between 0 and calculated backoff
```

Python:

```python
import random


def exponential_backoff_with_jitter(
    attempt: int,
    *,
    base: float = 1.0,
    cap: float = 60.0,
) -> float:
    exponential = min(cap, base * (2 ** attempt))
    return random.uniform(0.0, exponential)
```

For an exponential delay of `8` seconds, this can produce:

```text
0.7 sec
2.1 sec
5.8 sec
7.6 sec
...
```

instead of forcing every worker to retry at exactly eight seconds.

## 12.2 Other jitter strategies

You should be aware of:

- Full jitter.
- Equal jitter.
- Decorrelated jitter.

The exact strategy is a tuning decision. The essential purpose is to prevent synchronized retry waves.

---

# 13. Retry Budgets

Never allow unlimited retries.

A production retry policy should normally define several limits:

```text
Maximum attempts
Maximum total retry duration
Maximum individual delay
Job-level deadline
```

Example:

```text
Maximum attempts       = 5
Maximum retry duration = 2 minutes
Maximum wait           = 30 seconds
```

A retry budget prevents a hidden failure from turning into an apparently running job that makes no progress.

> Retry forever is not resilience. It is often failure concealment.

---

# 14. Honor Retry-After Before Local Backoff

Suppose:

```text
Server:
Retry-After: 20
```

and:

```text
Local backoff:
8 seconds
```

The client should generally wait about 20 seconds, subject to its maximum retry deadline.

A useful decision sequence is:

```text
429 / 503
    |
    v
Is Retry-After valid?
    |
   yes
    |
    v
Use provider-directed delay
    |
    v
Apply local safety cap/deadline
```

If `Retry-After` is invalid or absent:

```text
Fallback to local backoff + jitter
```

A server-directed delay does not mean “wait forever.” The local system still owns:

- Maximum job duration.
- Maximum retry attempts.
- Maximum acceptable delay.
- Operational cancellation.

---

# 15. A Robust Retry Decision Model

Instead of embedding retry behavior everywhere, define a decision object.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    delay_seconds: float
    reason: str
```

A simplified classifier:

```python
def classify_status(status_code: int) -> bool:
    """Return whether the status is a retry candidate."""
    if status_code in {408, 429, 500, 502, 503, 504}:
        return True

    return False
```

Now add the retry delay calculation:

```python
import random


def calculate_retry_delay(
    *,
    attempt: int,
    retry_after_seconds: float | None,
    base: float = 1.0,
    cap: float = 60.0,
) -> float:
    """Prefer provider guidance, otherwise use exponential backoff + jitter."""
    if retry_after_seconds is not None:
        return min(retry_after_seconds, cap)

    exponential = min(cap, base * (2 ** attempt))
    return random.uniform(0.0, exponential)
```

And combine them:

```python
def classify_response(
    *,
    status_code: int,
    attempt: int,
    retry_after_seconds: float | None,
    remaining_retry_seconds: float,
) -> RetryDecision:
    if not classify_status(status_code):
        return RetryDecision(
            retry=False,
            delay_seconds=0.0,
            reason=f"status {status_code} is not retryable by this policy",
        )

    delay = calculate_retry_delay(
        attempt=attempt,
        retry_after_seconds=retry_after_seconds,
    )

    if delay > remaining_retry_seconds:
        return RetryDecision(
            retry=False,
            delay_seconds=0.0,
            reason="retry delay exceeds remaining retry budget",
        )

    return RetryDecision(
        retry=True,
        delay_seconds=delay,
        reason=f"status {status_code} is retryable",
    )
```

This example is deliberately explicit. Production systems can become more sophisticated, but the decision should remain inspectable.

---

# 16. Tenacity

[Tenacity](https://tenacity.readthedocs.io/) is a Python library for retry behavior.

A retry library exists because hand-written retry loops often become difficult to reason about once you need:

- Stop conditions.
- Wait strategies.
- Exception predicates.
- Logging.
- Jitter.
- Attempt counts.
- Deadlines.

A simple Tenacity example:

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(
        multiplier=1,
        max=30,
    ),
    retry=retry_if_exception_type(TimeoutError),
)
def fetch_resource():
    ...
```

This demonstrates the basic building blocks:

```text
retry predicate
      +
wait strategy
      +
stop condition
```

## 16.1 Why a generic decorator is not enough

An HTTP API may communicate important information in the response:

```text
429
Retry-After: 30
```

A generic exponential backoff decorator may not know that the server explicitly requested 30 seconds.

Therefore:

> Use Tenacity as a retry mechanism, but keep HTTP-specific policy—especially `Retry-After`, response classification, operation safety, and retry deadlines—explicit.

For a mature client, you may classify the HTTP response first and then invoke a retry mechanism with the appropriate delay.

## 16.2 What to retry

A production predicate should distinguish:

```text
Timeout / connection error
429
503
selected 5xx
```

from:

```text
400
403
404
422
```

according to the provider contract.

## 16.3 Awareness: Stamina

`stamina` is another Python retry library worth knowing about. The important lesson is not which library wins; it is to centralize retry policy rather than scatter inconsistent retry loops across the codebase.

---

# 17. Proactive Throttling

There are two broad approaches.

## Reactive

```text
Send requests
      ↓
429
      ↓
Slow down
```

## Proactive

```text
Rate limiter
      ↓
Wait if necessary
      ↓
Send request
      ↓
API
```

Proactive throttling is preferable when provider limits are known because it avoids generating traffic that is expected to fail.

Benefits include:

- Fewer 429 responses.
- More predictable throughput.
- Less wasted network traffic.
- Less source-system pressure.
- More stable pipelines.
- Better quota planning.

Reactive retries remain necessary because provider conditions can change and failures can occur even when your normal request rate is within the documented limit.

---

# 18. Token Bucket

A token bucket is a common way to model rate and burst capacity.

Imagine:

```text
Bucket capacity = 10 tokens

Tokens refill continuously.

Each request consumes 1 token.

No token?
Wait.
```

Diagram:

```text
              refill
                ↓
        +----------------+
        |     TOKENS     |
        | ● ● ● ● ● ● ● |
        +----------------+
                |
             request
                |
                v
               API
```

## 18.1 Core parameters

A token bucket has:

- **Capacity** — maximum stored tokens.
- **Refill rate** — tokens added per second.
- **Consumption** — tokens removed for each request.
- **Burst allowance** — how many requests can use accumulated tokens.
- **Wait behavior** — what happens when the bucket is empty.

Example:

```text
capacity    = 10
refill_rate = 2 tokens/sec
```

Initially, ten requests may be sent rapidly.

After those tokens are consumed, new requests must wait for refill.

The sustained rate approaches:

```text
2 requests/sec
```

assuming one token per request.

This differs from:

```python
time.sleep(0.5)
```

between requests because a token bucket can allow bursts while still controlling long-term throughput.

---

# 19. Educational Token Bucket Implementation

The following implementation is deliberately readable rather than a distributed production limiter.

```python
import threading
import time


class TokenBucket:
    def __init__(
        self,
        *,
        capacity: float,
        refill_rate: float,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.updated_at = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self.updated_at
        if elapsed <= 0:
            return

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )
        self.updated_at = now

    def acquire(self, tokens: float = 1.0) -> float:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        if tokens > self.capacity:
            raise ValueError("requested tokens exceed bucket capacity")

        while True:
            with self._lock:
                now = time.monotonic()
                self._refill(now)

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return 0.0

                missing = tokens - self.tokens
                wait_seconds = missing / self.refill_rate

            time.sleep(wait_seconds)
```

## 19.1 Why `time.monotonic()`?

Rate calculations should not depend on wall-clock changes.

A wall clock can move because of:

- NTP synchronization.
- Manual clock changes.
- Daylight-saving rules.
- Virtualization behavior.

`time.monotonic()` is designed for elapsed-time measurement.

## 19.2 Why a lock?

Multiple threads could call `acquire()` concurrently.

Without synchronization:

```text
Thread A sees 1 token
Thread B sees 1 token
Thread A consumes 1
Thread B consumes 1
```

The system could accidentally spend the same token twice.

The lock makes token accounting atomic within the process.

## 19.3 Production limitation

This limiter is process-local.

It does not coordinate:

```text
Worker A
Worker B
Worker C
```

across machines.

That is a separate distributed-systems problem.

---

# 20. Token Bucket Simulation

Suppose:

```text
capacity    = 10
refill_rate = 2 tokens/sec
```

At startup:

```text
tokens = 10
```

The first ten one-token requests can consume the bucket rapidly.

After the bucket becomes empty:

```text
2 tokens/sec
```

are produced.

So the long-term request rate approaches:

```text
2 requests/sec
```

while preserving some burst capacity.

This gives the token bucket two useful properties:

```text
Burst capacity
+
Sustained rate control
```

---

# 21. Sliding-Window Limiting

Another model counts requests in a time window.

Suppose:

```text
Limit = 5 requests / 10 seconds
```

At:

```text
12:00:10
```

a sliding window might count requests from:

```text
12:00:00 → 12:00:10
```

The window moves continuously.

## 21.1 Fixed window

A fixed-window implementation might count:

```text
12:00:00 → 12:00:09
12:00:10 → 12:00:19
```

This can permit boundary bursts.

For example, a client might send five requests at:

```text
12:00:09.9
```

and another five at:

```text
12:00:10.1
```

even though only a fraction of a second separates them.

## 21.2 Sliding window

A sliding window asks:

```text
How many requests occurred during the previous 10 seconds?
```

This produces more precise control but can require more state.

## 21.3 Educational implementation

```python
from collections import deque
import time


class SlidingWindowLimiter:
    def __init__(
        self,
        *,
        limit: int,
        window_seconds: float,
    ) -> None:
        if limit <= 0:
            raise ValueError("limit must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        self.limit = limit
        self.window_seconds = window_seconds
        self.timestamps: deque[float] = deque()

    def acquire(self) -> float:
        while True:
            now = time.monotonic()

            while (
                self.timestamps
                and now - self.timestamps[0] >= self.window_seconds
            ):
                self.timestamps.popleft()

            if len(self.timestamps) < self.limit:
                self.timestamps.append(now)
                return 0.0

            wait_seconds = (
                self.window_seconds
                - (now - self.timestamps[0])
            )
            time.sleep(max(0.0, wait_seconds))
```

This is educational. A production distributed implementation needs careful concurrency control, bounded state, failure behavior, and often centralized coordination.

---

# 22. Rate Limiter vs Retry Policy

This distinction should become automatic.

```text
Rate limiter
=
Controls requests BEFORE they are sent.
```

```text
Retry policy
=
Controls behavior AFTER a request fails.
```

Combined:

```text
Application
    |
    v
Rate Limiter
    |
    v
HTTP Client
    |
    v
API
    |
    v
Response
    |
    +---- success
    |
    +---- retryable failure
              |
              v
        Retry Classifier
              |
              v
        Retry-After /
        Backoff + Jitter
              |
              v
         Retry Budget
```

A system that has only retries is reactive.

A system that has only a rate limiter can still fail due to timeouts, gateway failures, outages, and transient server errors.

Production clients commonly need both.

---

# 23. Shared Quotas Across Multiple Workers

Suppose the provider limit is:

```text
100 requests/minute
```

and there are three workers:

```text
Worker A = 40/min
Worker B = 40/min
Worker C = 40/min
```

Each worker may believe it is safe.

Together:

```text
40 + 40 + 40 = 120/min
```

The provider sees:

```text
120/min > 100/min
```

and returns 429s.

## 23.1 Why a process-local limiter is insufficient

A process-local limiter knows only about its own process.

```text
Worker A
  |
local limiter

Worker B
  |
local limiter

Worker C
  |
local limiter
```

There is no shared view of total quota usage.

## 23.2 Coordination options

Production architectures can use:

- Centralized rate-limit services.
- Redis-backed counters.
- Database-backed counters.
- Distributed token buckets.
- Shared quota managers.

The roadmap requires awareness, not a complete distributed limiter implementation.

## 23.3 Trade-offs

Central coordination introduces:

```text
+ accurate shared accounting
+ global fairness

- additional latency
- operational complexity
- another dependency
- availability concerns
- consistency questions
- infrastructure cost
```

The right choice depends on how important strict quota compliance is.

---

# 24. Circuit Breakers

Retries can become harmful when the source is genuinely unavailable.

Consider:

```text
request
  ↓
failure
  ↓
retry
  ↓
failure
  ↓
retry
  ↓
failure
```

A circuit breaker can stop repeated calls temporarily.

## 24.1 States

```text
CLOSED
   |
   | repeated failures
   v
OPEN
   |
   | cooldown
   v
HALF-OPEN
   |
   +---- success → CLOSED
   |
   +---- failure → OPEN
```

### Closed

Normal requests flow.

Failures are counted.

### Open

Requests are rejected locally instead of being sent to the failing provider.

### Half-open

After a cooldown, a limited recovery probe is allowed.

If the probe succeeds:

```text
HALF-OPEN → CLOSED
```

If it fails:

```text
HALF-OPEN → OPEN
```

## 24.2 Simple implementation

```python
from enum import Enum, auto
import time


class CircuitState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        cooldown_seconds: float = 10.0,
    ) -> None:
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if cooldown_seconds <= 0:
            raise ValueError("cooldown_seconds must be positive")

        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.opened_at: float | None = None
        self.state = CircuitState.CLOSED

    def before_request(self) -> None:
        now = time.monotonic()

        if self.state is CircuitState.OPEN:
            assert self.opened_at is not None

            if now - self.opened_at >= self.cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                return

            raise RuntimeError("circuit is open")

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.monotonic()
```

This is an educational state machine. Production implementations must also consider concurrent calls, probe limits, error classification, metrics, and thread/process/distributed coordination.

---

# 25. Rate-Limit Budgeting

Before running a large ingestion job, estimate request volume.

Suppose:

```text
Records = 2,000,000
Page size = 1,000
```

The theoretical number of data pages is:

```text
2,000,000 / 1,000 = 2,000 pages
```

So:

```text
Minimum page requests ≈ 2,000
```

But the actual request count can be larger:

```text
2,000 page requests
+ retries
+ authentication requests
+ metadata requests
+ polling requests
+ error recovery
```

If the system averages:

```text
0.05 retries/page
```

then expected retry volume is:

```text
2,000 × 0.05 = 100 retries
```

Approximate expected requests:

```text
2,000 + 100
= 2,100
```

before other calls.

This is why quota budgeting must account for more than the theoretical page count.

Useful measures include:

```text
requests/run
requests/day
requests/hour
expected retries
polling requests
```

---

# 26. Page Size Optimization

Pagination and rate limiting are tightly connected.

Compare:

```text
page_size = 100
2,000,000 records
```

Then:

```text
2,000,000 / 100
= 20,000 requests
```

Now:

```text
page_size = 1,000
```

gives:

```text
2,000,000 / 1,000
= 2,000 requests
```

That is a tenfold reduction in page requests.

But larger pages have trade-offs.

### Larger pages

Advantages:

- Fewer requests.
- Lower request overhead.
- Lower quota consumption.

Costs:

- Larger response bodies.
- More memory pressure.
- Potentially higher per-request latency.
- More data to replay if a page fails.

### Smaller pages

Advantages:

- Smaller individual responses.
- Easier recovery.
- Potentially lower per-request latency.

Costs:

- More requests.
- More request overhead.
- More quota consumption.

The provider's maximum page size and observed workload behavior are authoritative.

---

# 27. Filters and Request Minimization

> The best request is sometimes the request you never send.

Suppose the pipeline needs only active customers.

Instead of:

```http
GET /customers
```

followed by local filtering, prefer an API-supported filter when appropriate:

```http
GET /customers?status=active
```

Other request-reduction mechanisms can include:

- Server-side filtering.
- Field projection.
- Date filters.
- Incremental filters.
- Pagination.
- Appropriate page sizes.

The goal is to avoid paying network, quota, and source-system costs for data the pipeline does not need.

Incremental extraction is covered later; here the focus is simply on the principle of minimizing unnecessary requests.

---

# 28. Daily Quotas

Suppose:

```text
Daily quota = 1,000,000 requests
```

Expected usage:

```text
Extraction requests = 500,000
Retries             = 100,000
Metadata requests   = 50,000
```

Total expected usage:

```text
500,000
+100,000
+ 50,000
=650,000 requests
```

Remaining theoretical capacity:

```text
1,000,000 - 650,000
=350,000
```

Do not automatically plan to consume all 350,000.

Reserve capacity for:

- Other pipelines.
- Scheduled jobs.
- Backfills.
- Emergency reruns.
- Operational investigations.
- Unexpected retry amplification.

A daily quota is a shared budget, not necessarily a target.

---

# 29. Observability

A production extractor should make rate-limit behavior visible.

At minimum, measure:

```text
requests_total
requests_success
requests_failed
http_429_total
retries_total
retry_delay_seconds
retry_after_seconds
rate_limit_remaining
rate_limit_limit
rate_limit_reset
circuit_breaker_open_total
records_extracted
duration_seconds
```

## 29.1 429 rate

```text
429 rate =
429 responses / total requests
```

A rising rate can indicate:

- The configured request rate is too high.
- A provider changed limits.
- Another job is consuming the shared quota.
- The provider is experiencing unusual conditions.

## 29.2 Retry amplification

A useful measure is:

```text
retry amplification =
total HTTP requests / logical requests
```

For example:

```text
10,000 logical requests
12,000 HTTP requests
```

gives:

```text
1.2x amplification
```

The extra 2,000 calls were caused by retries or related repeated work.

## 29.3 Effective throughput

```text
effective throughput =
records extracted / elapsed seconds
```

This matters because raw request rate is not the same as useful progress.

## 29.4 Waiting time

Measure:

```text
time spent waiting for rate limits
```

If a job spends 80% of its runtime waiting, increasing worker count may not improve useful throughput.

---

# 30. Structured Logging

Rate-limit events should be structured so they can be queried.

```python
logger.info(
    "api_request",
    extra={
        "status_code": response.status_code,
        "retry_count": retry_count,
        "rate_limit_remaining": remaining,
        "retry_after_seconds": retry_after,
    },
)
```

Actual logging APIs vary by application.

Never log:

- Access tokens.
- API keys.
- Authorization headers.
- Sensitive request bodies.

The goal is to capture enough context to understand rate-limit behavior without exposing credentials or sensitive data.

---

# 31. Build a Throttled FastAPI Mock API

The following mock API is intentionally embedded in this Markdown file. Do not create a separate supporting file as part of the curriculum artifact.

The mock service demonstrates:

- Configurable request-rate capacity.
- HTTP 429.
- `Retry-After`.
- Rate-limit headers.
- Configurable 503 responses.
- A small `/customers` endpoint.

Install the dependencies in your learning environment if needed:

```bash
python -m pip install fastapi uvicorn httpx
```

Then, for the hands-on lab, copy the following embedded example into a temporary local learning file yourself. The curriculum artifact itself remains this Markdown file.

```python
from __future__ import annotations

import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


@dataclass
class RateLimitState:
    limit: int
    window_seconds: float
    timestamps: deque[float]
    lock: Lock


RATE_LIMIT = RateLimitState(
    limit=10,
    window_seconds=10.0,
    timestamps=deque(),
    lock=Lock(),
)

SIMULATE_503 = False


def check_rate_limit() -> tuple[bool, int, float]:
    now = time.monotonic()

    with RATE_LIMIT.lock:
        while (
            RATE_LIMIT.timestamps
            and now - RATE_LIMIT.timestamps[0]
            >= RATE_LIMIT.window_seconds
        ):
            RATE_LIMIT.timestamps.popleft()

        remaining = max(
            0,
            RATE_LIMIT.limit - len(RATE_LIMIT.timestamps),
        )

        if remaining == 0:
            retry_after = (
                RATE_LIMIT.window_seconds
                - (now - RATE_LIMIT.timestamps[0])
            )
            return False, 0, max(0.0, retry_after)

        RATE_LIMIT.timestamps.append(now)
        remaining -= 1

        return True, remaining, 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/customers")
async def customers(request: Request):
    allowed, remaining, retry_after = check_rate_limit()

    if not allowed:
        response = JSONResponse(
            status_code=429,
            content={"error": "rate limit exceeded"},
        )
        response.headers["Retry-After"] = str(
            max(1, int(retry_after + 0.999))
        )
        response.headers["X-RateLimit-Limit"] = str(
            RATE_LIMIT.limit
        )
        response.headers["X-RateLimit-Remaining"] = "0"
        return response

    if SIMULATE_503:
        response = JSONResponse(
            status_code=503,
            content={"error": "simulated service outage"},
        )
        response.headers["Retry-After"] = "2"
        response.headers["X-RateLimit-Limit"] = str(
            RATE_LIMIT.limit
        )
        response.headers["X-RateLimit-Remaining"] = str(
            remaining
        )
        return response

    response = JSONResponse(
        content={
            "customers": [
                {"id": 1, "name": "Ada"},
                {"id": 2, "name": "Grace"},
            ]
        }
    )
    response.headers["X-RateLimit-Limit"] = str(
        RATE_LIMIT.limit
    )
    response.headers["X-RateLimit-Remaining"] = str(
        remaining
    )
    return response
```

## What the mock API teaches

The critical sequence is:

```text
Request
  |
  v
check_rate_limit()
  |
  +-- capacity available --> 200
  |
  +-- capacity exhausted --> 429
                              |
                              +-- Retry-After
                              +-- Limit
                              +-- Remaining
```

The mock is intentionally simple. A real provider can use much more complicated distributed rate-limit state.

---

# 32. Curl Lab

Assume the mock service is running locally on port `8000`.

## 32.1 Basic request

```bash
curl -i http://127.0.0.1:8000/customers
```

Inspect:

```text
HTTP status
response body
X-RateLimit-Limit
X-RateLimit-Remaining
```

## 32.2 Verbose HTTP diagnostics

```bash
curl -v http://127.0.0.1:8000/customers
```

Use this to inspect request/response details during debugging.

## 32.3 Trigger 429

Send requests rapidly:

```bash
for i in $(seq 1 12); do
  curl -s -D - http://127.0.0.1:8000/customers -o /dev/null
done
```

Expected behavior:

```text
Some requests → 200
Later requests → 429
```

The exact boundary depends on timing.

## 32.4 Inspect Retry-After

Look for:

```http
Retry-After: ...
```

The correct client behavior is to use the provider's delay guidance rather than immediately hammering the endpoint again.

---

# 33. Hands-On Exercise — Three Polite-Client Strategies

You will compare three clients against the same throttled API.

```text
Client A
No rate-limit handling

Client B
Reactive retry

Client C
Proactive throttling + reactive retry
```

## 33.1 Experimental setup

Use a workload of logical requests such as:

```text
100 logical requests
```

Use the same:

- API.
- Dataset.
- Network environment.
- Client timeout.
- Request operation.

Change only the rate-limit strategy.

## 33.2 Client A — No handling

Conceptually:

```python
for _ in range(100):
    response = client.get(url)
```

Measure:

```text
total runtime
429 count
retry count
requests made
records extracted
time spent waiting
```

Expected:

```text
Very fast initial sending
+
Many 429s
+
Potentially incomplete work
```

The lesson is that raw request speed is not useful if the provider rejects the traffic.

## 33.3 Client B — Reactive retry

Conceptually:

```python
for _ in range(100):
    response = request()

    if response.status_code == 429:
        wait_using_retry_after()
        retry()
```

Measure the same metrics.

Expected:

```text
Fewer failed logical requests
+
More waiting
+
More total HTTP requests
```

## 33.4 Client C — Proactive throttling + reactive retry

Conceptually:

```text
rate limiter
     ↓
request
     ↓
response
     ↓
429?
  /    \
no      yes
 |       |
done   Retry-After
         ↓
       retry
```

Expected:

```text
Fewer 429s
+
More predictable request rate
+
Potentially lower wasted request volume
+
Intentional waiting before requests
```

The objective is not to declare a universal winner.

Instead ask:

> Which strategy provides the required useful throughput while respecting the provider contract and operational constraints?

---

# 34. Measuring the Three Clients

Record a table like:

| Strategy | Runtime | 429s | Retries | HTTP requests | Records | Wait time |
|---|---:|---:|---:|---:|---:|---:|
| No handling | | | | | | |
| Reactive retry | | | | | | |
| Proactive + reactive | | | | | | |

## Questions

1. Did the fastest client complete all logical work?
2. How many extra HTTP requests were caused by 429s?
3. How much time was spent waiting?
4. Did proactive throttling reduce 429s?
5. Did proactive throttling reduce retry amplification?
6. What happens if the provider lowers its limit?
7. What happens if several clients share the same quota?

### Reasoning target

A mature conclusion should sound like:

```text
Client C deliberately sacrificed some instantaneous request
throughput to reduce rejected requests and make total useful
throughput more predictable.
```

Do not conclude:

```text
Token bucket is always best.
```

The provider contract and workload determine the appropriate design.

---

# 35. Tenacity Exercise

Implement a policy that:

- Retries only selected transient failures.
- Honors `Retry-After`.
- Uses exponential backoff when provider guidance is absent.
- Adds jitter to fallback delays.
- Enforces a maximum total retry time.

## Test 1 — 404

Input:

```text
404
```

Expected:

```text
No retry
```

Reason:

```text
The resource/path is likely wrong or absent.
Repeating the same request immediately does not fix it.
```

## Test 2 — 503 with Retry-After

Input:

```text
503
Retry-After: 2
```

Expected:

```text
Wait approximately 2 seconds.
```

The provider explicitly supplied a recovery hint.

## Test 3 — Permanent outage

Input:

```text
503 repeatedly
```

Expected:

```text
Stop within the retry budget.
```

A job should fail clearly rather than remain indefinitely “healthy” while doing no useful work.

---

# 36. Circuit Breaker Exercise

Configure:

```text
Failure threshold = 5
Cooldown          = 10 seconds
```

Simulate:

```text
5 consecutive 5xx responses
```

Expected:

```text
CLOSED
  ↓
five failures
  ↓
OPEN
```

During the open period:

```text
Requests should fail locally or be suppressed
rather than repeatedly hitting the provider.
```

After ten seconds:

```text
OPEN
  ↓
cooldown
  ↓
HALF-OPEN
```

Send a recovery probe.

Success:

```text
HALF-OPEN → CLOSED
```

Failure:

```text
HALF-OPEN → OPEN
```

### Production lesson

Circuit breakers are not a replacement for retries. They control what happens when repeated failures indicate that continued traffic may be harmful.

---

# 37. Idempotency Keys

Consider:

```http
POST /exports
```

The client sends the request.

The server creates:

```text
Export A
```

But the network fails before the client receives the response.

The client cannot distinguish:

```text
Server did not process request
```

from:

```text
Server processed request but response was lost
```

If the client blindly retries:

```http
POST /exports
```

the server might create:

```text
Export A
Export B
```

when the client intended one export.

## 37.1 Idempotency key

Some APIs support:

```http
Idempotency-Key: abc-123
```

The conceptual flow is:

```text
First request
    |
    | Idempotency-Key: abc-123
    v
Server creates export
    |
    v
Logical result stored

Retry with same key
    |
    v
Server recognizes operation
    |
    v
Same logical result
```

Idempotency-key behavior is provider-specific.

Not every API supports it.

Clients must follow provider documentation regarding:

- Key format.
- Retention period.
- Scope.
- Duplicate response behavior.
- Error behavior.

---

# 38. FastAPI Idempotency Mock

The following embedded example illustrates the concept:

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

created_exports: dict[str, dict] = {}


@app.post("/exports")
def create_export(
    idempotency_key: str | None = Header(default=None),
):
    if idempotency_key is None:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key is required",
        )

    existing = created_exports.get(idempotency_key)

    if existing is not None:
        return existing

    export = {
        "export_id": f"export-{len(created_exports) + 1}",
        "status": "accepted",
    }

    created_exports[idempotency_key] = export
    return export
```

The key idea is:

```python
existing = created_exports.get(idempotency_key)
```

A repeated logical operation can return the same stored result.

This is only an educational demonstration. A production implementation needs durable state, expiration rules, concurrent access control, and provider-specific semantics.

---

# 39. Failure Scenarios

## Scenario 1 — 429 without Retry-After

### Symptoms

The API returns:

```http
429 Too Many Requests
```

but no `Retry-After`.

### Diagnosis

The provider has signaled a rate/quota violation but has not supplied a specific delay.

### Correct response

Use a bounded local backoff with jitter, while respecting the provider's documented limits.

### Implementation consideration

Do not immediately retry.

### Production lesson

Absence of `Retry-After` does not mean “retry immediately.”

---

## Scenario 2 — 429 with Retry-After: 30

### Symptoms

```http
429
Retry-After: 30
```

### Diagnosis

The provider explicitly requests approximately 30 seconds.

### Correct response

Wait approximately 30 seconds, subject to your retry deadline.

### Production lesson

Server guidance should generally take precedence over a shorter local fallback backoff.

---

## Scenario 3 — Retry-After HTTP-date

### Symptoms

```http
Retry-After: Wed, 21 Oct 2026 07:28:00 GMT
```

### Diagnosis

The server supplied an absolute HTTP date.

### Correct response

Parse the date, compare it to the current time, clamp negative values to zero, and enforce a maximum wait/deadline.

### Production lesson

Do not assume `Retry-After` is always an integer.

---

## Scenario 4 — 503 storm

### Symptoms

Hundreds of workers repeatedly receive:

```text
503
```

### Diagnosis

The source may be unavailable or overloaded.

### Correct response

Use bounded exponential backoff, jitter, and potentially a circuit breaker.

### Production lesson

Retry traffic can amplify an outage.

---

## Scenario 5 — 100 workers retry simultaneously

### Symptoms

Every worker waits exactly:

```text
4 seconds
```

then sends a request.

### Diagnosis

Deterministic backoff synchronized the workers.

### Correct response

Add jitter.

### Production lesson

Randomized waiting spreads load over time.

---

## Scenario 6 — Shared API quota

### Symptoms

Each worker reports:

```text
Within its local limit
```

but the provider reports repeated 429s.

### Diagnosis

The workers share a quota.

### Correct response

Coordinate quota usage through a centralized or distributed limiter when strict shared-quota compliance is required.

### Production lesson

Local correctness does not imply global correctness.

---

## Scenario 7 — POST export duplicate

### Symptoms

A retry creates multiple exports.

### Diagnosis

The initial POST may have succeeded even though the response was lost.

### Correct response

Use an idempotency key if supported.

### Production lesson

Retry safety depends on operation semantics.

---

## Scenario 8 — Daily quota exhausted

### Symptoms

The provider reports quota exhaustion.

### Diagnosis

The pipeline has consumed its daily budget.

### Correct response

Do not blindly continue retrying. Stop or defer work according to the provider's reset schedule and pipeline SLA.

### Production lesson

A daily quota is a finite operational budget.

---

## Scenario 9 — Provider suddenly reduces the rate limit

### Symptoms

A previously successful extractor starts producing many 429s.

### Diagnosis

The provider may have changed the contract or dynamically reduced available capacity.

### Correct response

Observe current rate-limit headers and documentation, reduce traffic, and avoid assuming yesterday's limit still applies.

### Production lesson

External service limits can change.

---

## Scenario 10 — Retry-After is absurdly large

### Symptoms

```http
Retry-After: 864000
```

### Diagnosis

The server has requested an extremely long delay, or the client may have received unexpected/misconfigured data.

### Correct response

Apply a job-level deadline and operational policy. Do not sleep indefinitely inside a worker.

### Production lesson

Server guidance matters, but the client still needs bounded operational behavior.

---

# 40. Production Architecture

A complete rate-limit-aware extraction architecture can look like:

```text
                 Data Pipeline
                      |
                      v
               Request Scheduler
                      |
                      v
                 Rate Limiter
                      |
                      v
                  HTTP Client
                      |
                      v
                     API
                      |
              +-------+-------+
              |               |
             2xx             Error
              |               |
              v               v
           Process       Retry Classifier
                              |
                    +---------+---------+
                    |                   |
                  Retry                Fail
                    |
                    v
            Retry-After / Backoff
                    |
                    v
                  Jitter
                    |
                    v
              Retry Budget
```

The circuit breaker sits around the provider interaction:

```text
Rate Limiter
     |
     v
Circuit Breaker
     |
     v
HTTP Client
     |
     v
API
```

If repeated failures cross the configured threshold, the circuit opens and prevents unnecessary requests.

---

# 41. Complete Request Lifecycle

A production request lifecycle should be explicit:

```text
1. Determine whether request is allowed.
2. Wait for rate limiter if necessary.
3. Send request.
4. Record latency and status.
5. Inspect response.
6. If success → process.
7. If 429 → inspect Retry-After.
8. If retryable → calculate delay.
9. Apply retry budget.
10. Apply jitter where appropriate.
11. Retry.
12. If repeated failures → circuit breaker.
13. If terminal failure → fail clearly.
14. Emit metrics.
```

## Step 1 — Admission

The rate limiter asks:

```text
Can this request be sent now?
```

## Step 2 — Wait

If not:

```text
wait until request is allowed
```

## Step 3 — Send

The HTTP client performs the request.

## Step 4 — Observe

Capture:

```text
latency
status
rate-limit headers
```

## Step 5 — Classify

Determine:

```text
success?
retry candidate?
terminal failure?
```

## Step 6 — Apply provider guidance

For 429/503:

```text
Retry-After?
```

## Step 7 — Apply local policy

Check:

```text
attempt limit
deadline
maximum delay
operation safety
```

## Step 8 — Retry or fail

Do not hide terminal failures.

## Step 9 — Protect the source

Repeated failure may open the circuit.

## Step 10 — Measure

Every important decision should be observable.

---

# 42. Common Mistakes

## 42.1 Retrying every HTTP error

Danger:

```text
400
→ retry
→ retry
→ retry
```

The request itself may be invalid.

Fix:

```text
Classify before retrying.
```

## 42.2 Retrying immediately

Danger:

```text
429
→ immediate retry
→ 429
→ immediate retry
```

Fix:

```text
Retry-After or bounded backoff.
```

## 42.3 Ignoring Retry-After

Danger:

The client disregards explicit provider guidance.

Fix:

```text
Honor Retry-After subject to local deadlines/caps.
```

## 42.4 No jitter

Danger:

Workers synchronize.

Fix:

```text
Use randomized fallback delays.
```

## 42.5 Infinite retries

Danger:

The job never clearly fails.

Fix:

```text
Use attempt and time budgets.
```

## 42.6 No retry deadline

Danger:

A single request can consume the entire job's runtime.

Fix:

```text
Use job-level deadlines.
```

## 42.7 Reactive retries only

Danger:

The client generates failures before slowing down.

Fix:

```text
Use proactive throttling when limits are known.
```

## 42.8 No proactive throttling

Danger:

Unnecessary 429s consume traffic and quota.

Fix:

```text
Control normal request rate before sending.
```

## 42.9 Workers ignore shared quotas

Danger:

```text
10 safe workers
```

can collectively become unsafe.

Fix:

```text
Coordinate shared quota usage.
```

## 42.10 Consume 100% of daily quota

Danger:

No capacity remains for operational recovery.

Fix:

```text
Maintain a safety margin.
```

## 42.11 Retry unsafe POST operations

Danger:

A retry can create duplicate side effects.

Fix:

```text
Use idempotency mechanisms when supported.
```

## 42.12 No metrics

Danger:

Rate-limit behavior becomes invisible.

Fix:

Measure:

```text
429s
retries
waiting
remaining quota
throughput
```

## 42.13 Treat 429 as permanent API failure

Danger:

A temporary rate constraint is confused with a broken endpoint.

Fix:

```text
Classify 429 separately.
```

## 42.14 Treat 429 as permission failure

Danger:

`429` is not the same semantic category as `403`.

Fix:

```text
429 → traffic/quota problem
403 → authorization/policy problem
```

## 42.15 Assume provider limits never change

Danger:

A previously safe extractor can become aggressive overnight.

Fix:

```text
Observe actual responses and provider documentation.
```

---

# 43. Benchmarking Experiment

Compare:

```text
1. No throttling
2. Reactive retry only
3. Fixed-delay throttling
4. Token bucket + retry
5. Token bucket + retry + jitter
```

Measure:

```text
runtime
429s
retries
HTTP requests
records/sec
waiting time
```

Use the same workload and provider conditions.

Record:

| Strategy | Runtime | 429s | Retries | Requests | Records/sec | Wait time |
|---|---:|---:|---:|---:|---:|---:|
| No throttling | | | | | | |
| Reactive retry | | | | | | |
| Fixed delay | | | | | | |
| Token bucket + retry | | | | | | |
| Token bucket + retry + jitter | | | | | | |

The objective is **not** to find a universal winner.

The objective is to understand:

```text
throughput
vs
politeness
vs
quota consumption
vs
latency
vs
complexity
```

A strategy that has slightly lower raw request throughput may produce better useful throughput because it generates fewer rejected requests.

---

# 44. Data Engineering Example — SaaS CRM API

Consider:

```text
SaaS CRM API
2,000,000 customers
API limit = 100 requests/minute
page size = 1,000
```

## 44.1 Theoretical page count

```text
2,000,000 / 1,000
= 2,000 pages
```

## 44.2 Minimum page requests

Assuming perfect pagination:

```text
≈ 2,000 requests
```

This is the theoretical minimum for the page-fetch portion.

## 44.3 Minimum runtime under a strict 100/minute limit

Ignoring bursts and assuming the limit behaves as a sustained 100 requests/minute:

```text
2,000 / 100
= 20 minutes
```

So approximately:

```text
20 minutes
```

is the theoretical lower bound from the request-rate constraint alone.

Real execution can be longer because of:

- Response latency.
- Retries.
- Rate-limit waiting.
- Authentication.
- Metadata calls.
- Failures.
- Provider-side variability.

## 44.4 Add retries

Suppose the expected retry rate is:

```text
5%
```

Then:

```text
2,000 × 0.05
= 100 retry requests
```

Approximate HTTP requests:

```text
2,000 + 100
= 2,100
```

At 100 requests/minute:

```text
2,100 / 100
= 21 minutes
```

Again, this is a simplified quota calculation, not a guaranteed runtime.

## 44.5 What should be observed?

At minimum:

```text
pages completed
records extracted
429 count
retry count
Retry-After values
remaining quota
elapsed time
records/sec
```

## 44.6 What if page size is 100?

Then:

```text
2,000,000 / 100
= 20,000 requests
```

At 100 requests/minute:

```text
20,000 / 100
= 200 minutes
```

That is approximately:

```text
3 hours 20 minutes
```

before accounting for latency and retries.

This illustrates why page size can be a rate-limit optimization.

---

# 45. Advanced Design Questions

## 1. What happens if the provider limit is shared across 20 workers?

A process-local limiter cannot enforce the global limit. Aggregate traffic can exceed the quota.

Use centralized or distributed coordination if strict shared-quota compliance is required.

## 2. What if the provider gives different limits per endpoint?

Model limits by endpoint or operation rather than assuming one global number.

For example:

```text
GET /customers → high capacity
POST /exports  → low capacity
```

The limiter should apply the appropriate policy.

## 3. What if Retry-After conflicts with your retry deadline?

The deadline wins operationally.

For example:

```text
Retry-After = 5 minutes
Job deadline = 30 seconds
```

The worker should not sleep beyond the job's allowed runtime. It should fail/defer clearly according to pipeline policy.

## 4. What if the API returns 429 without rate-limit headers?

Use:

- Provider documentation.
- `Retry-After` if present.
- Bounded fallback backoff.
- Observed behavior.
- Conservative proactive throttling.

Do not invent an exact quota.

## 5. What if the API returns 503 repeatedly?

Use bounded retries, jitter, and potentially a circuit breaker. Eventually fail or defer rather than producing unbounded traffic.

## 6. What if a POST request times out after the server processed it?

The client cannot safely assume failure.

Use an idempotency key if the provider supports one. Otherwise, consult provider-specific mechanisms for determining whether the operation completed.

## 7. What if the API quota changes dynamically?

Use observed headers when available and design the client to adapt rather than hard-coding a permanently assumed rate.

## 8. What if multiple pipelines share the same credentials?

They may share the same quota. A pipeline-local limiter may be insufficient.

Consider centralized quota coordination or explicit traffic allocation.

## 9. What if a backfill competes with the daily ingestion pipeline?

Treat quota as a shared resource.

For example:

```text
Production ingestion → reserved priority
Backfill              → opportunistic capacity
```

The exact policy is a business/operational decision, but the architecture should make priority explicit.

## 10. How would you prioritize production traffic?

Separate workloads by priority and allocate quota deliberately.

Avoid allowing a large backfill to consume all available capacity needed for an SLA-critical ingestion job.

## 11. How would you prevent a retry storm?

Use:

```text
exponential backoff
+
jitter
+
Retry-After
+
retry budgets
+
circuit breakers
```

and avoid unnecessary retries.

## 12. How would you design rate-limit observability?

Capture:

```text
429 count
retry count
retry delay
Retry-After
remaining quota
limit
reset
request volume
logical work
effective throughput
circuit state
```

Then alert on abnormal changes rather than only absolute error counts.

---

# 46. Knowledge Check

## Basic

### 1. What is a rate limit?

A constraint controlling how much traffic a client can send under a defined policy such as requests per second, minute, day, concurrency, or resource units.

### 2. Why do APIs enforce rate limits?

To protect infrastructure, provide fairness, control costs, reduce abuse, and maintain service stability.

### 3. What is HTTP 429?

`429 Too Many Requests` indicates that the server is refusing traffic because a rate or quota constraint has been exceeded.

### 4. What is Retry-After?

A response header that can tell the client how long to wait or the HTTP date after which retrying is appropriate.

### 5. What does X-RateLimit-Remaining mean?

Commonly, it indicates remaining capacity in a provider-defined rate-limit window. Its exact semantics are provider-specific.

## Intermediate

### 6. Why should Retry-After be honored?

Because the provider is giving explicit guidance about when another attempt is appropriate. Ignoring it can create unnecessary load and additional 429s.

### 7. What is exponential backoff?

A retry delay strategy where the delay grows exponentially between attempts, usually with a maximum cap.

### 8. Why is jitter useful?

It prevents many workers from retrying at exactly the same time.

### 9. What is proactive throttling?

Controlling request traffic before sending requests so the client attempts to stay within the provider's limits.

### 10. What is a token bucket?

A rate-control model in which tokens accumulate at a defined rate up to a capacity and requests consume tokens.

### 11. What is the difference between retry logic and rate limiting?

Rate limiting controls traffic before requests are sent. Retry logic controls what happens after failures.

## Advanced

### 12. How would you coordinate 100 workers against a shared quota?

Use a centralized or distributed quota mechanism rather than 100 independent process-local limiters.

### 13. Why can retries make outages worse?

Every retry adds more traffic to a potentially overloaded service. Many synchronized retries can create a feedback loop.

### 14. How does a circuit breaker help?

It stops repeatedly sending requests to a source that is failing, allowing the source and client to recover.

### 15. How would you retry a POST safely?

First determine whether the operation is retry-safe. If the provider supports idempotency keys, use one consistently for the logical operation.

### 16. How would you budget a daily API quota?

Estimate page requests plus expected retries, metadata calls, polling, and other traffic; reserve capacity for other workloads and recovery.

### 17. How would you measure retry amplification?

One useful measure is:

```text
total HTTP requests / logical requests
```

A result of `1.2x` means approximately 20% more HTTP traffic than the logical workload.

---

# 47. Interview Preparation

## 1. Explain HTTP 429.

`429 Too Many Requests` indicates that a server is refusing traffic because a rate or quota constraint has been exceeded. It is often recoverable by waiting, but the client should consider `Retry-After`, operation safety, retry budgets, and provider-specific behavior.

## 2. What is Retry-After?

It is a response header that can express either a delay in seconds or an HTTP date.

## 3. What formats can Retry-After use?

Two forms:

```text
Retry-After: 10
```

and:

```text
Retry-After: Wed, 21 Oct 2026 07:28:00 GMT
```

## 4. Which HTTP failures should normally be retried?

Common retry candidates include timeouts, connection failures, 408, 429, and selected 5xx responses. The exact policy depends on operation safety and provider behavior.

## 5. Why is retryability different from retry safety?

A failure can be temporary while repeating the operation can still create duplicate side effects.

## 6. Explain exponential backoff.

Increase the delay between retries:

```text
1 → 2 → 4 → 8 → ...
```

and cap the delay.

## 7. Explain jitter.

Randomize the fallback delay to prevent synchronized retries across workers.

## 8. Why can synchronized retries cause a retry storm?

If many workers retry at the same instant, the provider receives another traffic spike exactly when it may still be recovering.

## 9. What is a token bucket?

A limiter that stores tokens up to a capacity and refills them continuously. Each request consumes tokens, allowing controlled bursts and a bounded sustained rate.

## 10. Token bucket vs fixed-delay throttling?

Fixed delay generally spaces requests uniformly. A token bucket can accumulate capacity and allow bursts while preserving a long-term rate.

## 11. What is proactive throttling?

Limiting normal traffic before requests are sent, rather than waiting for 429 responses to force a slowdown.

## 12. How do you handle shared quotas across workers?

Use shared coordination, such as a distributed token bucket or centralized quota service, when strict aggregate control is required.

## 13. Explain circuit breakers.

A circuit breaker moves from closed to open after repeated failures, suppresses traffic during a cooldown, and then permits limited recovery probes in half-open state.

## 14. How do you safely retry POST?

Use provider-supported idempotency mechanisms when available and reason about whether the server may already have completed the operation.

## 15. What is an idempotency key?

A provider-supported identifier for a logical operation that allows repeated requests to be recognized as the same operation.

## 16. How do you estimate API request volume?

Start with:

```text
ceil(records / page_size)
```

then add expected retries, metadata, authentication, polling, and other request categories.

## 17. How do you design rate-limit observability?

Measure both physical HTTP traffic and logical work, including 429s, retry counts, delay, quota state, request volume, records processed, and effective throughput.

## 18. What would you do if an API suddenly reduced its rate limit?

Reduce traffic, honor current provider guidance, inspect rate-limit headers, adjust proactive throttling, and investigate whether the provider contract changed.

## 19. How would you design a polite ingestion client for 100 million records?

First minimize requests through appropriate page sizes and server-side filtering. Then use proactive throttling, bounded retries, `Retry-After`, jitter, retry budgets, idempotency where needed, shared-quota coordination, observability, and failure isolation. The final design must be driven by the provider's actual limits and the pipeline's SLA.

## 20. How would you handle a backfill without starving the production pipeline?

Treat quota as a shared resource and explicitly allocate capacity. Give SLA-critical ingestion a protected budget while allowing backfill to consume remaining capacity without violating the provider contract.

---

# 48. Production Checklist

## Rate limits

```text
[ ] Provider limits documented
[ ] Request limits understood
[ ] Concurrency limits understood
[ ] Burst behavior understood
[ ] Daily quota understood
[ ] Endpoint-specific limits understood
[ ] Weighted limits understood if applicable
```

## Retry

```text
[ ] Retryable failures identified
[ ] Non-retryable failures fail fast
[ ] Retry-After honored
[ ] Exponential backoff implemented
[ ] Jitter implemented
[ ] Retry budget enforced
[ ] Job-level deadline enforced
[ ] Maximum individual delay enforced
```

## Throttling

```text
[ ] Proactive limiter exists
[ ] Burst behavior understood
[ ] Token bucket considered
[ ] Sliding-window behavior understood
[ ] Shared quotas coordinated
```

## Reliability

```text
[ ] Circuit breaker considered
[ ] Idempotency keys used where supported
[ ] POST retry safety understood
[ ] Provider-specific semantics documented
```

## Observability

```text
[ ] 429 count
[ ] Retry count
[ ] Retry delay
[ ] Retry-After
[ ] Remaining quota
[ ] Quota limit
[ ] Quota reset
[ ] Request count
[ ] Logical request count
[ ] Retry amplification
[ ] Effective throughput
[ ] Waiting time
[ ] Circuit-breaker state
```

---

# 49. Final Checkpoint

Before moving to Topic 06, verify:

```text
[ ] I understand why APIs enforce rate limits.
[ ] I understand HTTP 429.
[ ] I can interpret Retry-After.
[ ] I understand both Retry-After formats.
[ ] I understand common rate-limit headers.
[ ] I can distinguish request rate from concurrency and quota.
[ ] I can classify retryable failures.
[ ] I understand retry safety vs retryability.
[ ] I can implement exponential backoff.
[ ] I understand jitter.
[ ] I can implement bounded retries.
[ ] I can use Tenacity appropriately.
[ ] I understand proactive throttling.
[ ] I can explain token buckets.
[ ] I can implement an educational token bucket.
[ ] I understand sliding-window limiting.
[ ] I can distinguish rate limiting from retry logic.
[ ] I understand shared API quotas.
[ ] I understand circuit breakers.
[ ] I can budget API requests.
[ ] I understand page-size effects on quota consumption.
[ ] I understand request minimization through filters.
[ ] I understand idempotency keys.
[ ] I can instrument rate-limit behavior.
[ ] I completed the polite-client exercise.
[ ] I tested 404 as non-retryable.
[ ] I tested 503 with Retry-After.
[ ] I tested permanent outages.
[ ] I can explain how to prevent retry storms.
[ ] I can reason about production quota allocation.
```

> **Do not move to Topic 06 until you can explain the concepts, implement the exercises, and reason about failure scenarios without blindly copying the solution.**

---

# 50. The Production Decision Loop

When designing or reviewing an extractor, use this sequence:

```text
1. What limits does the provider actually enforce?
                ↓
2. What traffic does this workload generate?
                ↓
3. Can requests be reduced?
                ↓
4. Can normal traffic be proactively throttled?
                ↓
5. Which failures are temporary?
                ↓
6. Is the operation safe to repeat?
                ↓
7. Does the provider give Retry-After?
                ↓
8. What backoff + jitter policy applies?
                ↓
9. What is the retry budget?
                ↓
10. Is quota shared across workers?
                ↓
11. Do we need a circuit breaker?
                ↓
12. What metrics prove the design is behaving correctly?
```

This is the real production skill.

Do not memorize:

```text
"429 means retry three times."
```

Instead reason:

```text
429
 ↓
Why did the provider reject us?
 ↓
What does the provider tell us to do?
 ↓
Is the operation safe to repeat?
 ↓
How much retry budget remains?
 ↓
Will retrying help or increase load?
 ↓
Should we throttle future requests?
```

---

# 51. Technical Precision Rules

Avoid simplistic claims.

Do **not** say:

> “429 always means retry.”

Prefer:

> `429` generally indicates that the client exceeded a rate or quota constraint, and retrying after the provider-directed delay is often appropriate, subject to operation safety, retry budget, and the provider contract.

Do **not** say:

> “All 5xx responses should be retried.”

Prefer:

> Retryability depends on the specific operation, failure mode, provider behavior, and retry budget.

Do **not** say:

> “Exponential backoff solves rate limiting.”

Prefer:

> Backoff is primarily a failure-recovery mechanism. Proactive rate limiting is a separate mechanism for controlling normal request traffic.

Do not assume:

- Every API exposes `X-RateLimit-*`.
- Every API supports idempotency keys.
- Every POST is unsafe to retry.
- Every 429 includes `Retry-After`.
- Every 5xx is retryable.
- Every provider uses one global quota.
- Provider limits remain static forever.

The provider contract wins.

---

# 52. What You Should Be Able to Explain in an Architecture Review

A senior engineer should be able to defend decisions such as:

### Why use proactive throttling?

Because the provider's documented limit is known, so intentionally staying below it avoids predictable 429 traffic.

### Why still keep retries?

Because transient failures can occur even when normal traffic is compliant.

### Why add jitter?

Because multiple workers can otherwise synchronize their retry schedules.

### Why enforce a retry deadline?

Because an ingestion job must eventually produce a clear terminal state rather than waiting forever.

### Why use a distributed limiter?

Because a shared provider quota cannot be reliably enforced by independent process-local counters.

### Why use idempotency keys?

Because a network timeout does not prove that the server failed to execute a side-effecting operation.

### Why use a circuit breaker?

Because repeated requests to a failing source can amplify an outage.

### Why measure retry amplification?

Because HTTP request volume can be substantially larger than the logical workload and therefore consume more quota and source capacity than expected.

---

# 53. Final Production Principle

A production extractor should optimize for:

```text
Useful throughput
+
Correctness
+
Source protection
+
Predictable failure behavior
+
Quota efficiency
+
Observability
```

not simply:

```text
maximum requests per second
```

The best extractor is not the one that sends the most requests.

It is the one that makes the required progress **within the provider contract**, survives transient failures, avoids duplicate side effects, preserves quota for other work, and makes its behavior observable.

> **Fast and polite is the production goal.**
