# Async HTTP Extraction with httpx

> **Stage 2 — Python for Data Engineering**  
> **Module 2.10 — Concurrency and Parallelism in Practice**  
> **Topic 05 — Async HTTP Extraction with httpx**  
> **Python:** 3.13+  
> **Audience:** Beginner-to-intermediate Data Engineer progressing toward production-grade systems

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

- explain why asynchronous HTTP extraction exists;
- explain why one `httpx.AsyncClient` should normally be reused for an extraction run;
- create and close an `AsyncClient` correctly;
- use `async with`;
- make asynchronous HTTP requests with `await client.get(...)`;
- configure connection limits;
- configure explicit HTTP timeouts;
- understand practical HTTP/2 multiplexing;
- port a synchronous HTTP client to an asynchronous design;
- implement asynchronous authentication;
- implement safe OAuth client-credentials token refresh;
- prevent a token-refresh stampede;
- use `asyncio.Lock` correctly around token refresh;
- implement bounded asynchronous retries;
- use Tenacity with coroutine functions;
- respect `Retry-After`;
- distinguish independent requests from dependent cursor pagination;
- parallelize independent extraction windows;
- keep cursor pagination sequential within a window;
- use `asyncio.TaskGroup` for structured concurrency;
- implement a shared asynchronous rate limiter;
- understand a token bucket;
- use a rate limiter as an async context manager;
- distinguish concurrency limits from request-rate limits;
- stream large HTTP responses with `client.stream`;
- avoid blocking the event loop during file I/O;
- use `asyncio.to_thread()` appropriately;
- batch records before durable writes;
- land results to Parquet or JSON Lines;
- checkpoint only after durable landing;
- resume incomplete extraction windows;
- reason about adaptive throughput and AIMD-style control;
- measure requests/sec, records/sec, p95 latency, `429` count, CPU, memory, and total runtime;
- compare sequential, `ThreadPoolExecutor`, and `AsyncClient` implementations;
- build an `AsyncCustomersClient`;
- combine OAuth, token-refresh locking, retries, rate limiting, pagination, TaskGroups, landing, and checkpoints;
- diagnose common asynchronous extraction failures;
- design a high-throughput extractor that remains correct under throttling, authentication expiry, partial failure, and process interruption.

The central question is:

> **How do you combine asyncio, structured concurrency, HTTP clients, authentication, retries, rate limits, pagination, streaming, checkpoints, and observability into a correct production extraction system?**

---

# 2. Core Production Principle

Async HTTP extraction is not:

```text
send thousands of requests at once
```

It is:

```text
controlled concurrency
+
connection reuse
+
rate-limit compliance
+
bounded retries
+
correct pagination
+
safe authentication
+
bounded memory
+
durable landing
+
checkpointing
+
measurement
```

A production extractor optimizes throughput **subject to correctness and external-system constraints**.

A useful mental model is:

```text
                    Async HTTP Extractor
                           │
                           ▼
                    Shared AsyncClient
                           │
                 ┌─────────┴─────────┐
                 │                   │
            Auth Manager       Rate Limiter
                 │                   │
                 └─────────┬─────────┘
                           │
                       TaskGroup
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Window 1      Window 2      Window 3
              │            │            │
        page 1→2→3    page 1→2→3    page 1→2→3
              │            │            │
              └────────────┼────────────┘
                           ▼
                    Validate Results
                           │
                           ▼
                     Parquet / JSONL
                           │
                           ▼
                      Checkpoints
                           │
                           ▼
                     Observability
```

The architectural boundary is important:

- **independent windows** can run concurrently;
- **dependent cursor pages** normally cannot;
- the **rate limiter is shared**;
- authentication refresh must be **coordinated**;
- results must be **durably landed before checkpointing**;
- cancellation and shutdown must be explicit;
- throughput must be **measured**, not assumed.

---

# 3. Prerequisites

This topic builds on earlier work covering:

- HTTP fundamentals;
- authentication;
- pagination;
- rate limits;
- retries;
- `Retry-After`;
- idempotency;
- incremental extraction;
- checkpoints;
- Python generators;
- context managers;
- `asyncio`;
- coroutines;
- Tasks;
- `TaskGroup`;
- cancellation;
- timeouts.

You do not need to re-learn those topics from scratch.

This chapter instead combines them into a production extraction system.

---

# 4. Why Async HTTP Extraction?

Imagine an API extractor that needs to retrieve 50,000 records.

Suppose an individual HTTP request has:

```text
average latency = 200 ms
```

A sequential design performs:

```text
request 1 → wait
request 2 → wait
request 3 → wait
...
```

The program spends much of its wall-clock time waiting for external systems.

Async I/O changes the scheduling model:

```text
request A → waiting ───────────→ response
request B → waiting ─────→ response
request C → waiting ───────────────→ response
request D → waiting → response
```

The waits can overlap.

But async is not automatically faster.

The actual result depends on:

- source latency;
- API rate limits;
- connection limits;
- server capacity;
- payload sizes;
- response processing;
- serialization;
- disk I/O;
- concurrency;
- retry behavior;
- memory;
- network bandwidth.

The correct question is:

> **Can independent I/O waits be overlapped without violating the constraints of the source and the pipeline?**

---

# 5. Sequential vs Threads vs Async

Three common approaches are:

```text
Sequential
    ↓
one operation at a time
```

```text
ThreadPoolExecutor
    ↓
multiple worker threads
    ↓
blocking HTTP client
```

```text
AsyncClient
    ↓
event loop
    ↓
many coroutine tasks
    ↓
non-blocking HTTP I/O
```

For I/O-heavy extraction, all three can be valid.

## Sequential

Advantages:

- simplest;
- easy to debug;
- low coordination complexity.

Disadvantages:

- poor utilization when requests spend substantial time waiting.

## Thread pool

Advantages:

- straightforward migration from blocking code;
- works with synchronous libraries;
- useful when async equivalents are unavailable.

Disadvantages:

- thread management overhead;
- more thread stacks/resources;
- shared-state considerations;
- less natural for very high I/O concurrency.

## Async

Advantages:

- efficient waiting;
- large numbers of concurrent I/O operations can be represented as lightweight tasks;
- excellent fit for async-native HTTP clients.

Disadvantages:

- requires async-compatible libraries;
- event-loop blocking can destroy performance;
- cancellation and lifecycle semantics require discipline;
- code can become complex if structured concurrency is ignored.

Do not declare one model universally superior.

Benchmark the workload.

---

# 6. What Is `httpx.AsyncClient`?

`httpx.AsyncClient` is the asynchronous HTTP client provided by HTTPX.

The simplest form is:

```python
import httpx


async def fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

There are three important concepts here:

```text
AsyncClient
    ↓
client.get(...)
    ↓
await
```

The `await` tells the event loop:

> This coroutine is waiting for the HTTP operation. Schedule other runnable work while this operation progresses.

---

# 7. Why One Client per Run?

A common beginner pattern is:

```python
async def fetch(url: str):
    async with httpx.AsyncClient() as client:
        return (await client.get(url)).json()
```

This creates a new HTTP client for every request.

That is usually an anti-pattern for an extraction job.

A better design is:

```python
async with httpx.AsyncClient() as client:
    result_1 = await fetch(client, url_1)
    result_2 = await fetch(client, url_2)
```

where:

```python
async def fetch(
    client: httpx.AsyncClient,
    url: str,
) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

## Why reuse the client?

A long-lived client can manage:

- connection pooling;
- connection reuse;
- keep-alive behavior;
- TLS connections;
- configured limits;
- common headers;
- common authentication behavior.

Creating a client repeatedly can introduce unnecessary:

```text
connection setup
TLS setup
resource allocation
cleanup
```

For a high-throughput extractor, the client should normally live for the duration of the extraction run.

Mental model:

```text
Extraction Run
      │
      ▼
Shared AsyncClient
      │
 ┌────┼────┬────┐
 ▼    ▼    ▼    ▼
req  req  req  req
```

---

# 8. `async with` and Client Lifecycle

Use:

```python
async with httpx.AsyncClient() as client:
    ...
```

This gives the client a clear lifecycle.

Conceptually:

```text
enter
  ↓
client initialized
  ↓
requests
  ↓
exit
  ↓
connections/resources cleaned up
```

Avoid leaving an `AsyncClient` open indefinitely.

A production service that intentionally maintains a long-lived client can manage it at application scope, but it still needs explicit startup and shutdown lifecycle.

---

# 9. A Minimal Async Request

```python
import httpx


async def fetch_customer(
    client: httpx.AsyncClient,
    customer_id: int,
) -> dict:
    response = await client.get(
        f"https://api.example.com/customers/{customer_id}"
    )
    response.raise_for_status()
    return response.json()
```

Line by line:

```python
async def
```

defines a coroutine function.

```python
client.get(...)
```

creates an asynchronous HTTP operation.

```python
await
```

suspends this coroutine while the I/O operation progresses.

```python
raise_for_status()
```

turns unsuccessful HTTP statuses into exceptions.

```python
response.json()
```

parses the response body as JSON.

The important design is that the client is supplied by the caller rather than constructed for every request.

---

# 10. Explicit HTTP Timeouts

A production HTTP client should not normally rely on an implicit infinite wait.

Use `httpx.Timeout`:

```python
import httpx


timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=30.0,
    pool=10.0,
)

async with httpx.AsyncClient(
    timeout=timeout,
) as client:
    ...
```

The four categories are useful because different failure points have different meanings.

## Connect timeout

How long to wait while establishing a connection.

## Read timeout

How long to wait for response data.

## Write timeout

How long to wait while sending request data.

## Pool timeout

How long to wait for an available connection from the client's pool.

These values are examples, not universal production defaults.

Choose them based on:

- source behavior;
- payload sizes;
- network conditions;
- SLA;
- retry policy;
- expected API latency.

---

# 11. Why Timeouts Matter

Without an appropriate timeout:

```text
request hangs
    ↓
coroutine remains occupied
    ↓
in-flight capacity shrinks
    ↓
other work waits
    ↓
throughput collapses
```

A timeout should be treated as part of the reliability design.

It is not merely a performance setting.

A useful policy is:

```text
timeout
    ↓
classify as transient/permanent
    ↓
retry if appropriate
    ↓
bounded attempts
    ↓
record failure
```

---

# 12. Connection Limits

HTTPX provides connection limits through `httpx.Limits`.

Example:

```python
limits = httpx.Limits(
    max_connections=50,
    max_keepalive_connections=20,
)

async with httpx.AsyncClient(
    limits=limits,
) as client:
    ...
```

These settings interact with application concurrency.

Think in layers:

```text
async tasks
    ↓
HTTP client connection pool
    ↓
network
    ↓
remote server
```

If you create:

```text
1,000 tasks
```

but configure:

```text
max_connections = 50
```

you have not created 1,000 simultaneous network connections.

Tasks may compete for the client's available connection capacity.

That can be exactly what you want.

---

# 13. Concurrency Is Not Capacity

Suppose:

```text
Task concurrency = 100
HTTP connections = 20
API limit        = 10 concurrent requests
```

The application has three different numbers.

The smallest relevant constraint can dominate effective throughput.

This is why:

> **Concurrency configuration must be designed with client and source capacity together.**

Do not assume:

```text
more tasks = more throughput
```

---

# 14. HTTP/2 Multiplexing

HTTP/2 allows multiple streams to be multiplexed over a connection.

At a practical level:

```text
HTTP/1.1
connection A → request
connection B → request
connection C → request

HTTP/2
connection A
    ├── stream 1
    ├── stream 2
    ├── stream 3
    └── stream 4
```

HTTPX can enable HTTP/2:

```python
async with httpx.AsyncClient(
    http2=True,
) as client:
    ...
```

Potential benefits include:

- reduced connection overhead;
- multiplexing;
- better utilization for suitable workloads.

But HTTP/2 does not eliminate:

- server-side concurrency limits;
- rate limits;
- request processing time;
- application-level throttling;
- authentication limits.

HTTP/2 is a transport capability, not a license for unbounded concurrency.

---

# 15. Porting a Synchronous Client to Async

Suppose a synchronous client looks like:

```python
import requests


def fetch_customer(customer_id: int) -> dict:
    response = requests.get(
        f"https://api.example.com/customers/{customer_id}"
    )
    response.raise_for_status()
    return response.json()
```

An async version becomes conceptually:

```python
import httpx


async def fetch_customer(
    client: httpx.AsyncClient,
    customer_id: int,
) -> dict:
    response = await client.get(
        f"https://api.example.com/customers/{customer_id}"
    )
    response.raise_for_status()
    return response.json()
```

The important changes are not simply:

```text
def → async def
```

You also need to migrate:

- HTTP client;
- authentication;
- retries;
- pagination;
- file I/O;
- database access if applicable;
- sleeps;
- resource lifecycle.

Simply adding `async` while keeping blocking operations inside is not a real async migration.

---

# 16. Never Block the Event Loop

The critical rule:

> **Async code must not perform long-running blocking operations directly on the event loop.**

This is bad:

```python
async def worker():
    time.sleep(5)
```

The event loop cannot use those five seconds to efficiently schedule other coroutines.

The correct async sleep is:

```python
await asyncio.sleep(5)
```

Other blocking operations include:

- synchronous HTTP clients;
- blocking database drivers;
- large blocking file writes;
- CPU-heavy Python computations.

Conceptually:

```text
blocking task
    ↓
event loop stops making progress
    ↓
all concurrent async work stalls
```

This is one of the most important async debugging principles.

---

# 17. Async Authentication

An extractor may use:

- API keys;
- bearer tokens;
- OAuth client credentials;
- short-lived access tokens.

For a client-credentials flow:

```text
client_id + client_secret
        ↓
token endpoint
        ↓
access token
        ↓
API requests
```

Never hard-code credentials:

```python
# Do not do this.
CLIENT_SECRET = "super-secret-value"
```

Instead, obtain credentials from a secure runtime configuration mechanism.

For a simple environment-variable demonstration:

```python
import os


client_id = os.environ["API_CLIENT_ID"]
client_secret = os.environ["API_CLIENT_SECRET"]
```

Do not log:

- client secrets;
- access tokens;
- authorization headers containing credentials.

---

# 18. Conceptual Authentication Manager

A production extractor benefits from a dedicated token manager:

```text
AsyncCustomersClient
        │
        ▼
TokenManager
        │
        ├── current token
        ├── expiration
        └── refresh operation
```

A conceptual interface might be:

```python
class AsyncTokenManager:
    async def get_token(self) -> str:
        ...
```

The HTTP client then asks the manager for a token rather than implementing token refresh independently in every request task.

This centralizes:

- expiration logic;
- refresh;
- locking;
- observability.

---

# 19. The Token-Refresh Stampede

Consider 100 concurrent tasks:

```text
Task 1 ─┐
Task 2 ─┤
Task 3 ─┤
...
Task 100 ┘
```

All send requests.

The access token has expired.

The API returns:

```text
401 Unauthorized
```

If every task responds:

```text
401 → refresh token
```

you can get:

```text
100 API requests
        ↓
100 refresh requests
```

This is a **token-refresh stampede**.

It can overload the authentication service and create additional failures.

---

# 20. Lock-Protected Refresh

Use an `asyncio.Lock` to ensure only one coroutine refreshes the token at a time.

Conceptually:

```python
self._refresh_lock = asyncio.Lock()
```

Then:

```python
async with self._refresh_lock:
    if token_is_still_valid():
        return existing_token

    await refresh()
    return new_token
```

The second check is essential.

Why?

Because another coroutine may have refreshed the token while the current coroutine was waiting to acquire the lock.

The correct sequence is:

```text
Task A detects expiry
Task B detects expiry
Task C detects expiry

        ↓

all attempt lock

        ↓

Task A gets lock

        ↓

Task A re-checks token

        ↓

still expired

        ↓

Task A refreshes

        ↓

Task A releases lock

        ↓

Task B gets lock

        ↓

Task B re-checks token

        ↓

token is now valid

        ↓

Task B does NOT refresh
```

This is the core anti-stampede pattern.

---

# 21. A Safe Token Manager Example

```python
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

import httpx


@dataclass
class AccessToken:
    value: str
    expires_at: float


class AsyncTokenManager:
    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        token_url: str,
        client_id: str,
        client_secret: str,
        refresh_skew_seconds: float = 30.0,
    ) -> None:
        self._client = client
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_skew_seconds = refresh_skew_seconds

        self._token: AccessToken | None = None
        self._refresh_lock = asyncio.Lock()
        self.refresh_count = 0

    def _is_valid(self) -> bool:
        if self._token is None:
            return False

        return (
            time.monotonic()
            < self._token.expires_at - self._refresh_skew_seconds
        )

    async def get_token(self) -> str:
        if self._is_valid():
            return self._token.value

        async with self._refresh_lock:
            # Re-check after waiting for the lock.
            if self._is_valid():
                return self._token.value

            response = await self._client.post(
                self._token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            response.raise_for_status()

            payload = response.json()

            self._token = AccessToken(
                value=payload["access_token"],
                expires_at=(
                    time.monotonic()
                    + float(payload["expires_in"])
                ),
            )

            self.refresh_count += 1

            return self._token.value
```

Important design decisions:

- one shared client;
- one refresh lock;
- fast path when token is valid;
- second validation after acquiring the lock;
- refresh count for observability/testing;
- monotonic time for local expiry calculations.

A production implementation would additionally validate the token response and carefully classify authentication failures.

---

# 22. Retrying Async HTTP Requests

Transient failures can include:

- connection errors;
- read timeouts;
- HTTP 408;
- HTTP 429;
- HTTP 500;
- HTTP 502;
- HTTP 503;
- HTTP 504.

Not every error is retryable.

For example:

```text
401
```

may require token refresh.

```text
403
```

may represent an authorization problem rather than a transient failure.

```text
400
```

is generally a request/client error that should not be retried blindly.

Retry policy must be explicit.

---

# 23. Async Retry With Tenacity

Tenacity supports coroutine functions.

A conceptual pattern:

```python
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential_jitter(
        initial=1,
        max=30,
    ),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.NetworkError)
    ),
)
async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
) -> httpx.Response:
    response = await client.get(url)
    response.raise_for_status()
    return response
```

The important pieces are:

```text
retry condition
+
bounded attempts
+
backoff
+
jitter
+
async-compatible function
```

Never create an infinite retry loop.

---

# 24. Retry-After

Suppose the API responds:

```text
HTTP/1.1 429 Too Many Requests
Retry-After: 5
```

The provider is explicitly asking the client to wait.

A well-behaved extractor should interpret that instruction rather than immediately retrying.

Conceptually:

```text
429
 ↓
read Retry-After
 ↓
wait
 ↓
retry if budget remains
```

`Retry-After` may also be represented using an HTTP-date rather than a number of seconds.

A production implementation should support the formats documented by the relevant API and handle invalid values safely.

---

# 25. Retry Budget

Retries consume resources.

Suppose:

```text
10,000 original requests
+
3 retries each
```

The theoretical request volume can become much larger than the original workload.

Therefore retry design should consider:

- maximum attempts;
- maximum total retry duration;
- exponential backoff;
- jitter;
- `Retry-After`;
- provider limits;
- idempotency;
- failure budgets.

Retries should improve reliability without creating a retry storm.

---

# 26. Independent vs Dependent Requests

This is one of the most important design decisions in API extraction.

## Independent requests

```text
customer 1 ─┐
customer 2 ─┤
customer 3 ─┼──→ concurrent
customer 4 ─┤
customer 5 ─┘
```

If the requests do not depend on one another, concurrency is usually possible.

## Cursor pagination

```text
page 1
  ↓
cursor 2
  ↓
page 2
  ↓
cursor 3
  ↓
page 3
```

Page 2 normally cannot be requested until page 1 provides cursor 2.

Therefore:

> **Do not blindly parallelize dependent cursor pages.**

---

# 27. Window-Based Concurrency

Suppose the API supports a date filter:

```text
start_date
end_date
```

You need 90 days:

```text
Day 1
Day 2
Day 3
...
Day 90
```

If each day is independently queryable, you can use:

```text
Day 1 → page 1 → page 2 → page 3
Day 2 → page 1 → page 2 → page 3
Day 3 → page 1 → page 2 → page 3
```

where the **windows** run concurrently while pagination inside each window remains sequential.

This is often the correct concurrency boundary.

---

# 28. The Correct Concurrency Boundary

Think:

```text
90-day extraction
        │
        ├── Window 1
        │      └── page 1 → 2 → 3
        │
        ├── Window 2
        │      └── page 1 → 2 → 3
        │
        ├── Window 3
        │      └── page 1 → 2 → 3
        │
        └── ...
```

The outer layer is concurrent.

The inner pagination chain is sequential.

This is much safer than trying to turn:

```text
page 1 → page 2 → page 3
```

into independent requests when the cursor itself creates the dependency.

---

# 29. TaskGroup Integration

`asyncio.TaskGroup` provides structured concurrency.

A window extraction can be launched as:

```python
import asyncio


async def extract_window(window):
    ...


async def extract_all(windows):
    async with asyncio.TaskGroup() as tg:
        for window in windows:
            tg.create_task(
                extract_window(window)
            )
```

The important concept is task ownership:

```text
extract_all()
    │
    └── owns window tasks
```

If a task fails, TaskGroup gives the application structured failure propagation and cancellation semantics.

TaskGroup does not automatically make the pipeline resumable.

Resumability comes from:

```text
durable output
+
checkpoint state
+
idempotent rerun behavior
```

---

# 30. Shared Async Rate Limiting

A rate limit generally belongs to:

```text
API credential
+
API endpoint
+
provider policy
```

not to one individual coroutine.

Bad architecture:

```text
Task 1 → limiter A
Task 2 → limiter B
Task 3 → limiter C
Task 4 → limiter D
```

Each task can independently consume its own rate budget.

Correct architecture:

```text
             Shared Limiter
              /    |    \
             /     |     \
          Task1  Task2  Task3
```

All requests pass through the same limiter.

---

# 31. Concurrency Limit vs Rate Limit

These concepts are related but different.

## Concurrency limit

> At most N requests are in flight at one time.

Example:

```text
max in-flight = 20
```

## Rate limit

> At most N requests are started during a time interval.

Example:

```text
50 requests/second
```

You may need both:

```text
20 concurrent requests
+
50 requests/second
```

Why?

Because you could otherwise have:

```text
20 long-running requests
```

and still need to control how quickly new requests are admitted.

---

# 32. Token Bucket

A token bucket models a rate budget.

Conceptually:

```text
Bucket capacity = 20 tokens
Refill rate     = 10 tokens/sec
```

A request needs one token.

```text
request
  ↓
acquire token
  ↓
token available?
 ├── yes → send request
 └── no  → wait
```

A token bucket has:

- capacity;
- refill rate;
- token acquisition;
- waiting behavior.

It is useful for smoothing request admission.

---

# 33. Token Bucket as an Async Context Manager

A clean application interface is:

```python
async with rate_limiter:
    response = await client.get(url)
```

Conceptually:

```python
class AsyncTokenBucket:
    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        return False
```

The limiter can then encapsulate admission control.

The important architectural property is that all request tasks share the same limiter.

---

# 34. A Practical Async Token Bucket

A simple single-process educational implementation can be built around a lock and monotonic time:

```python
from __future__ import annotations

import asyncio
import time


class AsyncTokenBucket:
    def __init__(
        self,
        *,
        rate: float,
        capacity: float,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.updated_at = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self.updated_at

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate,
        )

        self.updated_at = now

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                self._refill(now)

                if self.tokens >= 1:
                    self.tokens -= 1
                    return

                wait_seconds = (
                    (1 - self.tokens) / self.rate
                )

            await asyncio.sleep(wait_seconds)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        return False
```

This is an educational single-process limiter.

It is not a distributed rate limiter and does not automatically coordinate multiple application instances.

---

# 35. Async Streaming

Large responses should not automatically be loaded into memory.

HTTPX provides streaming:

```python
async with client.stream(
    "GET",
    url,
) as response:
    response.raise_for_status()

    async for chunk in response.aiter_bytes():
        process(chunk)
```

The important property is:

```text
response
   ↓
chunk
   ↓
process
   ↓
chunk
   ↓
process
```

rather than:

```text
response
   ↓
load entire body
   ↓
memory
```

Streaming is particularly important for:

- large exports;
- files;
- bulk API responses;
- compressed payloads;
- large JSON Lines responses.

---

# 36. Streaming and Connection Lifetime

The connection remains associated with the streaming response until it is closed.

Therefore:

```python
async with client.stream(...) as response:
    ...
```

is important.

Do not acquire a streaming response and forget to consume or close it.

A leaked or poorly managed streaming response can reduce available connection capacity.

---

# 37. Blocking File Writes

This is dangerous inside async code:

```python
async def write_data(path, data):
    with open(path, "wb") as file:
        file.write(data)
```

For small operations, the practical impact may be minor.

For large or frequent writes, blocking file operations can interfere with event-loop responsiveness.

Potential alternatives:

- batch writes;
- use an async-native file library where appropriate;
- offload blocking file work with `asyncio.to_thread()`.

---

# 38. `asyncio.to_thread()`

`asyncio.to_thread()` can run a blocking function in a worker thread:

```python
await asyncio.to_thread(
    write_chunk,
    path,
    chunk,
)
```

This is useful when:

- the operation is blocking;
- an async-native implementation is unavailable;
- the operation is relatively bounded.

It is not magic.

The operation still consumes a thread and has thread-pool overhead.

For many tiny writes:

```text
write one record
→ to_thread
→ write one record
→ to_thread
→ ...
```

may be inefficient.

Batching can be better.

---

# 39. Batching Async Results

Instead of:

```text
request
→ parse one record
→ write one record
→ request
→ write one record
```

prefer:

```text
requests
    ↓
records
    ↓
batch
    ↓
serialize
    ↓
durable write
```

Batching reduces:

- serialization overhead;
- system calls;
- file-open/write overhead;
- metadata operations.

But larger batches consume more memory and may delay checkpointing.

The right batch size is a measured engineering parameter.

---

# 40. Landing to JSON Lines

JSON Lines is useful for append-oriented record landing.

Conceptually:

```text
{"id": 1, "name": "..."}
{"id": 2, "name": "..."}
{"id": 3, "name": "..."}
```

A batch might be:

```python
import json


def serialize_jsonl(records: list[dict]) -> bytes:
    return b"".join(
        (
            json.dumps(record, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
        for record in records
    )
```

Then write the batch using an appropriate non-blocking or offloaded I/O strategy.

---

# 41. Landing to Parquet

Parquet is often preferable for analytical landing because it provides:

- columnar storage;
- compression;
- typed schemas;
- efficient downstream scans;
- partitioning opportunities.

A practical extraction architecture can be:

```text
API records
    ↓
validation
    ↓
batch
    ↓
Parquet writer
    ↓
window-specific file
```

For example:

```text
landing/
  2026-01-01.parquet
  2026-01-02.parquet
  2026-01-03.parquet
```

The exact implementation depends on the chosen Parquet library and its synchronous/asynchronous I/O characteristics.

The concurrency lesson remains:

> **HTTP concurrency and durable landing should be decoupled enough that the event loop is not accidentally blocked by large synchronous writes.**

---

# 42. Checkpointing

A critical distinction is:

```text
request completed
```

versus:

```text
result durably landed
```

A checkpoint should represent durable progress.

A safe conceptual sequence is:

```text
fetch
  ↓
validate
  ↓
write output
  ↓
confirm durable completion as required
  ↓
checkpoint window
```

Do not do:

```text
fetch
  ↓
checkpoint
  ↓
write output
```

If the process crashes after the checkpoint but before the output write, the next run can incorrectly skip the missing data.

---

# 43. Window-Level Checkpointing

For a 90-day extraction:

```text
window-01
window-02
...
window-90
```

A checkpoint can record:

```text
completed_windows = {
    "2026-01-01",
    "2026-01-02",
    ...
}
```

After a crash:

```text
for window in all_windows:
    if window in completed_windows:
        continue

    await extract_window(window)
```

This makes the extraction resumable.

The checkpoint is not a cache.

It is a record of durable work completion.

---

# 44. Resumability

Suppose:

```text
90 windows
75 completed
process crashes
```

A good design resumes:

```text
windows 1–75
    ↓
skip

windows 76–90
    ↓
extract
```

This depends on:

- durable checkpoint state;
- deterministic window identity;
- deterministic output location;
- idempotent output behavior;
- duplicate prevention.

Resumability is a system property, not a single API call.

---

# 45. Failure During One Window

Suppose:

```text
Day 37
```

fails while:

```text
Day 1–36 → completed
Day 38–90 → in progress
```

The system needs explicit semantics.

Questions include:

- Should sibling windows be cancelled?
- Should partial work inside Day 37 be discarded?
- Which checkpoints are already durable?
- Should completed outputs remain?
- Can the failed window be retried independently?
- Can the job resume without duplicating records?

A structured design separates:

```text
completed durable work
```

from:

```text
in-flight work
```

---

# 46. TaskGroup and Partial Progress

`TaskGroup` may cancel sibling tasks after an unhandled task failure.

That is useful for a fail-together operation.

But remember:

> **TaskGroup does not automatically erase already-durable output or invent checkpoint semantics.**

If windows 1–20 completed and were checkpointed, those checkpoints remain useful even if window 21 causes the TaskGroup to fail.

On restart:

```text
skip durable completed windows
retry incomplete windows
```

That is how structured concurrency and resumability complement each other.

---

# 47. Adaptive Throughput

A fixed request rate may not be optimal for all conditions.

Consider:

```text
healthy API
    ↓
increase throughput carefully
```

versus:

```text
429s / rising latency
    ↓
reduce throughput
```

This introduces adaptive throughput.

One conceptual model is AIMD:

```text
Additive Increase
        +
Multiplicative Decrease
```

For example:

```text
20 req/s
  ↓
healthy
  ↓
22
  ↓
24
  ↓
26
  ↓
429 spike
  ↓
13
```

This is conceptual, not a universal tuning formula.

A production controller should use measured signals and provider-specific constraints.

---

# 48. Responding to HTTP 429

Suppose:

```text
current rate = 80 req/s
```

The API begins returning many `429` responses.

A reasonable adaptive policy may be:

```text
observe 429
    ↓
respect Retry-After where provided
    ↓
reduce admission rate
    ↓
observe health
    ↓
increase gradually when stable
```

Immediately returning to 80 req/s after one successful request can cause another burst.

The objective is stable throughput, not maximum instantaneous request rate.

---

# 49. Throughput Measurement

At minimum:

```python
throughput = records / elapsed_seconds
```

or:

```python
requests_per_second = requests / elapsed_seconds
```

But throughput alone is insufficient.

A run that achieves:

```text
100 requests/sec
```

while producing:

```text
30% 429s
```

is not necessarily healthier than a run at:

```text
70 requests/sec
```

with:

```text
0% 429s
```

Measure throughput together with:

- success rate;
- retry count;
- `429` count;
- p95 latency;
- CPU;
- memory;
- source health.

---

# 50. Latency Percentiles

Average latency can hide tail behavior.

Consider:

```text
p50 = 150 ms
p95 = 800 ms
p99 = 2.5 s
```

Most requests are fast, but the slow tail is substantial.

The key percentiles are:

- p50 — median;
- p95 — 95th percentile;
- p99 — 99th percentile.

This chapter emphasizes p95 because it is a useful production signal for extraction health.

As concurrency rises, monitor whether:

```text
throughput ↑
```

while:

```text
p95 latency ↑↑
```

That can indicate the system is approaching a saturation point.

---

# 51. Observability

A production async extractor should expose at least:

```text
requests_total
successful_requests
failed_requests
http_429_total
retry_total
retry_delay_seconds
records_extracted
records_landed
windows_completed
windows_failed
request_latency
p50_latency
p95_latency
throughput
```

Useful log fields include:

```text
run_id
window
request_id
endpoint
status_code
attempt
duration
record_count
error
```

Never include:

```text
Authorization: Bearer <secret-token>
```

in logs.

---

# 52. Complete `AsyncCustomersClient` Design

A useful central abstraction is:

```text
AsyncCustomersClient
│
├── shared AsyncClient
├── authentication manager
├── token refresh lock
├── retry policy
├── Retry-After handling
├── shared rate limiter
├── request method
├── pagination
├── window extraction
├── validation
├── landing
└── metrics
```

Build this incrementally rather than creating a giant class immediately.

---

# 53. OAuth Client-Credentials Flow

The client-credentials flow is conceptually:

```text
client_id
client_secret
     │
     ▼
token endpoint
     │
     ▼
access token
     │
     ▼
API request
```

A simplified token acquisition method:

```python
async def request_token(
    client: httpx.AsyncClient,
    token_url: str,
    client_id: str,
    client_secret: str,
) -> tuple[str, int]:

    response = await client.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )

    response.raise_for_status()

    payload = response.json()

    return (
        payload["access_token"],
        int(payload["expires_in"]),
    )
```

A real provider may require:

- HTTP Basic authentication;
- different form fields;
- scopes;
- audience;
- custom headers.

Follow the provider's specification.

---

# 54. Request Method With Token Refresh

A production-oriented request method often looks conceptually like:

```python
async def get_json(
    self,
    path: str,
) -> dict:

    token = await self._token_manager.get_token()

    response = await self._client.get(
        self._build_url(path),
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if response.status_code == 401:
        token = await self._token_manager.get_token()

        response = await self._client.get(
            self._build_url(path),
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

    response.raise_for_status()

    return response.json()
```

In a real implementation, the second token lookup should support an explicit refresh/invalidation signal when the cached token is known to have been rejected.

The important principle is:

```text
401
 ↓
coordinate refresh
 ↓
retry safely
```

not:

```text
401
 ↓
every task refreshes independently
```

---

# 55. Forced Token-Expiry Experiment

The roadmap requires proving that the refresh lock works.

Use:

```text
100 concurrent tasks
```

and force the token to be considered expired.

Then arrange for all tasks to encounter the same expired token.

The expected result is:

```text
100 tasks
     ↓
401 responses
     ↓
refresh coordination
     ↓
exactly one refresh
     ↓
99 tasks reuse new token
```

Expose a metric:

```python
refresh_count
```

Then assert:

```python
assert refresh_count == 1
```

under the controlled experiment.

The exact test harness can use a mock API; the important property is deterministic verification.

---

# 56. Ninety-Day Extraction

Suppose an API accepts:

```text
start_date
end_date
```

Generate 90 independent windows:

```python
from datetime import date, timedelta


def daily_windows(
    start: date,
    days: int,
):
    for offset in range(days):
        current = start + timedelta(days=offset)

        yield (
            current,
            current + timedelta(days=1),
        )
```

Then run the windows concurrently:

```python
async def extract_90_days(
    client,
    windows,
):
    async with asyncio.TaskGroup() as tg:
        for window in windows:
            tg.create_task(
                client.extract_window(window)
            )
```

Inside each window:

```text
page 1
 ↓
cursor
 ↓
page 2
 ↓
cursor
 ↓
page 3
```

must remain sequential if each cursor depends on the previous response.

---

# 57. Window Extractor

A conceptual implementation:

```python
async def extract_window(
    self,
    start_date,
    end_date,
) -> list[dict]:

    cursor = None
    records = []

    while True:
        payload = await self.fetch_page(
            start_date=start_date,
            end_date=end_date,
            cursor=cursor,
        )

        page_records = payload["records"]
        records.extend(page_records)

        cursor = payload.get("next_cursor")

        if cursor is None:
            break

    return records
```

The important dependency is:

```text
page response
    ↓
next cursor
    ↓
next request
```

This is why pages inside one window remain sequential.

---

# 58. Shared Limiter Inside the Request Path

A request path can enforce global rate admission:

```python
async def request(
    self,
    method: str,
    url: str,
    **kwargs,
):
    async with self._rate_limiter:
        return await self._client.request(
            method,
            url,
            **kwargs,
        )
```

Now every coroutine uses the same limiter.

The rate policy is centralized rather than duplicated across window tasks.

---

# 59. Retry and Rate Limiting Together

A subtle issue is where the limiter sits relative to retries.

Conceptually:

```text
retry attempt
    ↓
rate limiter
    ↓
HTTP request
```

This ensures each actual request attempt consumes rate budget.

For a `429`:

```text
request
 ↓
429
 ↓
Retry-After
 ↓
wait
 ↓
next attempt
 ↓
rate limiter
```

Do not create a retry loop that bypasses the global rate limiter.

Otherwise retries themselves can violate the provider's rate policy.

---

# 60. Streaming Large API Exports

Suppose the provider offers:

```text
GET /exports/customers
```

and the response is several hundred megabytes.

Use:

```python
async with client.stream(
    "GET",
    export_url,
) as response:

    response.raise_for_status()

    async for chunk in response.aiter_bytes():
        await process_chunk(chunk)
```

Do not automatically do:

```python
data = response.content
```

for very large bodies.

The correct choice depends on:

- payload size;
- downstream parser;
- memory budget;
- compression;
- disk throughput.

---

# 61. Streaming to a Temporary File

A safe pattern is:

```text
HTTP stream
   ↓
temporary file
   ↓
complete
   ↓
atomic rename
   ↓
final file
```

This prevents downstream systems from interpreting an incomplete file as complete.

Conceptually:

```python
async with client.stream(
    "GET",
    url,
) as response:
    response.raise_for_status()

    await asyncio.to_thread(
        write_stream_to_file,
        response,
        temp_path,
    )
```

The exact helper must respect the asynchronous response interface. For an async stream, a better implementation usually reads chunks asynchronously and batches them before offloading grouped blocking writes.

---

# 62. Batching Stream Writes

Instead of:

```text
chunk
 ↓
thread hop
 ↓
write
 ↓
chunk
 ↓
thread hop
```

accumulate a bounded batch:

```text
chunk 1 ─┐
chunk 2 ─┤
chunk 3 ─┼──→ batch
chunk 4 ─┘
             ↓
         one write
```

This reduces thread-hop overhead.

But do not allow the batch to grow without a bound.

A safe streaming design has a memory ceiling.

---

# 63. Parquet Landing Architecture

For analytical data:

```text
window
 ↓
pages
 ↓
records
 ↓
validation
 ↓
batch
 ↓
Parquet
 ↓
durable completion
 ↓
checkpoint
```

Window-level files can simplify recovery:

```text
landing/
├── window=2026-01-01.parquet
├── window=2026-01-02.parquet
├── window=2026-01-03.parquet
└── ...
```

This makes the checkpoint mapping straightforward:

```text
completed window
        ↕
durable output
```

The exact partitioning scheme should reflect downstream query patterns and operational requirements.

---

# 64. JSONL Landing Architecture

JSONL can be useful for raw or semi-structured landing:

```text
window=2026-01-01.jsonl
```

Advantages:

- easy inspection;
- line-oriented recovery;
- flexible schema;
- convenient raw landing.

Trade-offs:

- larger storage footprint;
- weaker analytical performance;
- less efficient typed columnar scans.

A mature ingestion architecture may use:

```text
raw JSONL
    ↓
validated/typed Parquet
```

when both raw preservation and analytical consumption are required.

---

# 65. Correctness Before Performance

Always maintain a sequential baseline.

The comparison is:

```text
sequential result
       ↓
reference

async result
       ↓
candidate
```

Then compare:

```python
assert async_result == sequential_result
```

or compare normalized records when ordering is not part of the contract.

For example:

```python
assert (
    sorted(async_records, key=lambda x: x["id"])
    ==
    sorted(sequential_records, key=lambda x: x["id"])
)
```

A faster extractor that silently drops records is not an optimization.

It is a correctness defect.

---

# 66. Idempotency

Resumability depends on safe reruns.

Useful mechanisms include:

- deterministic window IDs;
- deterministic output paths;
- atomic writes;
- completed-window checkpoints;
- overwrite/replace policies;
- duplicate detection;
- stable record identifiers.

For example:

```text
window = 2026-01-17
```

should consistently map to:

```text
window=2026-01-17.parquet
```

Then a rerun can safely decide whether the file is:

- absent;
- incomplete;
- complete and checkpointed.

---

# 67. TaskGroup Failure Semantics

Suppose 10 windows are running:

```text
W1 W2 W3 W4 W5 W6 W7 W8 W9 W10
```

W4 fails.

TaskGroup can propagate that failure and cancel sibling tasks that are still running.

But completed durable work remains:

```text
W1 checkpointed
W2 checkpointed
W3 checkpointed
```

A robust system therefore separates:

```text
durable completed state
```

from:

```text
in-flight task state
```

On restart:

```text
skip checkpointed windows
retry incomplete windows
```

---

# 68. Failure Injection Lab

A serious extractor must be tested under controlled failure.

## Scenario 1 — Timeout

```text
request
 ↓
read timeout
 ↓
retry
 ↓
success/failure
```

## Scenario 2 — 429

```text
request
 ↓
429
 ↓
Retry-After
 ↓
wait
 ↓
retry
```

## Scenario 3 — 503

```text
request
 ↓
503
 ↓
bounded backoff
 ↓
retry
```

## Scenario 4 — Token expiry

```text
request
 ↓
401
 ↓
refresh coordination
 ↓
retry
```

## Scenario 5 — Mid-window failure

```text
page 1
 ↓
page 2
 ↓
page 3 fails
```

The window must not be checkpointed as complete.

## Scenario 6 — Process interruption

```text
75 windows checkpointed
25 incomplete
 ↓
process dies
 ↓
restart
 ↓
skip 75
 ↓
run 25
```

## Scenario 7 — File write failure

```text
HTTP success
 ↓
landing fails
 ↓
NO checkpoint
```

## Scenario 8 — Malformed page

```text
HTTP success
 ↓
schema validation failure
 ↓
record/window failure
 ↓
NO false checkpoint
```

---

# 69. Adaptive Throughput Experiment

Start with a conservative request rate.

Measure:

```text
requests/sec
429 count
p95 latency
```

If healthy:

```text
increase gradually
```

If unhealthy:

```text
reduce aggressively
```

For example:

```text
10 req/s
 ↓ healthy
12
 ↓ healthy
14
 ↓ healthy
16
 ↓ 429 spike
8
 ↓ healthy
9
 ↓ healthy
10
```

The exact values are illustrative.

The experiment should demonstrate the control principle rather than a universal formula.

---

# 70. Fifty-Thousand-Record Benchmark

Use the same mock API conditions for three implementations:

```text
1. Sequential
2. ThreadPoolExecutor
3. AsyncClient
```

Measure:

| Implementation | Runtime | Requests/sec | CPU | Memory | Errors | 429s | p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sequential | | | | | | | |
| ThreadPoolExecutor | | | | | | | |
| AsyncClient | | | | | | | |

Do not invent numbers.

Populate the table from actual measurements.

The benchmark is only meaningful when:

- source conditions are equivalent;
- payloads are equivalent;
- retry policies are equivalent;
- correctness is equivalent;
- concurrency/rate limits are controlled;
- warm-up effects are understood.

---

# 71. Benchmark Interpretation

Ask:

### Did async improve throughput?

If yes, by how much?

### Did CPU increase?

Async can reduce thread overhead but still spend CPU parsing responses and serializing data.

### Did memory increase?

Large numbers of in-flight requests can retain response/task state.

### Did 429s increase?

If yes, the system may have crossed the source's capacity boundary.

### Did p95 latency increase?

A throughput increase accompanied by severe tail-latency growth may not be operationally desirable.

### Was the API the bottleneck?

If the source is saturated, additional local optimization may not help.

### Were all three implementations correct?

Never compare runtime before correctness.

---

# 72. Performance Tuning Workflow

Use:

```text
Baseline
   ↓
Measure
   ↓
Identify bottleneck
   ↓
Change one variable
   ↓
Measure again
   ↓
Compare correctness
   ↓
Keep only verified improvements
```

Potential variables:

- task concurrency;
- `max_connections`;
- `max_keepalive_connections`;
- request rate;
- batch size;
- timeout;
- retry policy;
- window size;
- payload size;
- write frequency.

Do not simultaneously change every parameter.

You will not know which change caused the observed result.

---

# 73. Concurrency and Source Health

A healthy extractor optimizes:

```text
throughput
```

subject to:

```text
source limits
+
error budget
+
latency
+
correctness
```

A useful conceptual objective is:

```text
maximize useful records/sec
```

while maintaining:

```text
acceptable error rate
acceptable p95 latency
provider compliance
correct output
```

This is much closer to real Data Engineering than:

```text
maximize requests/sec
```

---

# 74. Anti-Patterns

## Anti-pattern 1 — New AsyncClient per request

Bad:

```python
async def fetch(url):
    async with httpx.AsyncClient() as client:
        ...
```

for every request.

Why it is bad:

- repeated client lifecycle;
- less effective connection reuse;
- unnecessary overhead.

Better:

```text
one client
    ↓
many requests
```

---

## Anti-pattern 2 — Unlimited requests

Bad:

```python
tasks = [
    asyncio.create_task(fetch(item))
    for item in millions_of_items
]
```

This can create enormous task state and overload the source.

Bound the workload.

---

## Anti-pattern 3 — Ignoring rate limits

A high local concurrency setting does not override:

```text
429
Retry-After
provider policy
```

---

## Anti-pattern 4 — Parallelizing dependent cursor pages

Do not do:

```text
page 1
page 2
page 3
```

concurrently if page 2 depends on page 1's cursor.

---

## Anti-pattern 5 — Refreshing tokens independently

Avoid:

```text
100 tasks
↓
100 refreshes
```

Use coordinated refresh.

---

## Anti-pattern 6 — Blocking the event loop

Avoid:

```python
time.sleep(...)
```

and large blocking operations inside async functions.

---

## Anti-pattern 7 — Infinite retries

Infinite retries can turn a temporary outage into a permanently stuck extraction.

Use bounded attempts and/or bounded retry duration.

---

## Anti-pattern 8 — Checkpointing before durable landing

Never mark a window complete before its output is safely persisted.

---

## Anti-pattern 9 — No timeout

A stuck request can occupy scarce concurrency indefinitely.

---

## Anti-pattern 10 — No correctness comparison

A benchmark without correctness verification is incomplete.

---

## Anti-pattern 11 — Holding millions of records in memory

Stream or batch records where possible.

---

## Anti-pattern 12 — Assuming async is automatically faster

Async is an execution model, not a performance guarantee.

---

# 75. Debugging Scenario 1 — Async Is No Faster Than Sequential

### Symptom

```text
sequential = 60 sec
async      = 59 sec
```

### Possible causes

- source is already fast;
- concurrency is too low;
- connection limits are too restrictive;
- rate limiter is too restrictive;
- blocking code exists;
- response processing dominates;
- benchmark workload is too small.

### Investigation

Measure:

```text
in-flight requests
request latency
rate limiter wait
connection-pool wait
CPU
```

### Fix

Only change the actual bottleneck.

---

# 76. Debugging Scenario 2 — Requests Appear Sequential

### Symptom

Logs show:

```text
request A start
request A end
request B start
request B end
```

### Likely causes

- `await` is placed in a loop without creating concurrent tasks;
- blocking operation exists;
- concurrency limit is one;
- rate limiter allows only one request at a time.

For example:

```python
for item in items:
    await fetch(item)
```

is sequential.

Concurrent task creation requires explicit task orchestration, for example with `TaskGroup`.

---

# 77. Debugging Scenario 3 — Event Loop Is Blocked

### Symptom

All async requests become slow.

### Likely causes

- `time.sleep`;
- blocking file writes;
- synchronous HTTP library;
- blocking database driver;
- CPU-heavy processing.

### Investigation

Search async code for synchronous operations.

### Fix

Use:

```python
await asyncio.sleep(...)
```

for sleeps, async-native clients where available, and `asyncio.to_thread()` for suitable bounded blocking operations.

---

# 78. Debugging Scenario 4 — Many 429 Responses

### Symptom

```text
429 count increases rapidly
```

### Likely causes

- request rate too high;
- concurrency too high;
- retry loop creates additional bursts;
- each task has its own limiter;
- `Retry-After` ignored.

### Fix

Use:

```text
shared limiter
+
bounded concurrency
+
Retry-After
+
adaptive reduction
```

---

# 79. Debugging Scenario 5 — 100 Token Refreshes

### Symptom

```text
refresh_count = 100
```

### Likely cause

Every task independently refreshed after receiving 401.

### Fix

Use:

```python
asyncio.Lock()
```

and re-check token validity after acquiring the lock.

Expected:

```text
refresh_count ≈ 1
```

for the controlled simultaneous-expiry experiment.

---

# 80. Debugging Scenario 6 — Duplicate or Missing Cursor Pages

### Symptom

Record counts do not match the baseline.

### Likely causes

- cursor state shared incorrectly;
- page requests parallelized incorrectly;
- cursor overwritten by another task;
- retry logic repeats a non-idempotent operation incorrectly.

### Fix

Make cursor state local to each window:

```text
window A → cursor A
window B → cursor B
```

and keep page traversal sequential inside the window.

---

# 81. Debugging Scenario 7 — Memory Grows Continuously

### Possible causes

- too many concurrent tasks;
- responses retained unnecessarily;
- all records accumulated in memory;
- unbounded batches;
- unbounded retry metadata;
- no streaming for large bodies.

### Fix

Introduce explicit bounds:

```text
task concurrency
+
connection count
+
batch size
+
in-memory records
+
streaming
```

---

# 82. Debugging Scenario 8 — Job Completes With Missing Records

### Likely causes

- task exception was not observed;
- window marked complete too early;
- response parsing silently skipped records;
- cancellation interrupted work;
- pagination terminated incorrectly.

### Investigation

Compare:

```text
requests
pages
records extracted
records landed
windows completed
```

A good observability system makes the missing stage visible.

---

# 83. Debugging Scenario 9 — Resume Does Not Work

### Symptom

Restarted job either:

- repeats everything;
- skips incomplete windows;
- duplicates data.

### Likely causes

- checkpoint state is not durable;
- checkpoint written before output;
- output identity is nondeterministic;
- completed-window state is ambiguous.

### Correct sequence

```text
fetch
↓
validate
↓
land
↓
confirm durable output
↓
checkpoint
```

---

# 84. Debugging Scenario 10 — p95 Explodes

### Symptom

```text
concurrency ↑
p95 latency ↑↑
```

### Possible causes

- source saturation;
- connection contention;
- network congestion;
- server throttling;
- local resource contention.

### Response

Do not automatically increase concurrency again.

Measure:

```text
throughput
p95
429s
connection wait
CPU
memory
```

and find the saturation point.

---

# 85. Complete Production Architecture

A mature implementation can look like:

```text
Scheduler
    ↓
Extraction Configuration
    ↓
Window Generator
    ↓
TaskGroup
    ↓
Shared AsyncCustomersClient
    │
    ├── AsyncClient
    ├── Auth Manager
    ├── Refresh Lock
    ├── Retry Policy
    ├── Retry-After Handler
    └── Shared Rate Limiter
    ↓
Window Extractors
    ↓
Validation
    ↓
Batching
    ↓
Parquet / JSONL Landing
    ↓
Checkpoint Store
    ↓
Metrics / Logs
```

Each component has one primary responsibility.

---

# 86. Component Responsibilities

## Scheduler

Determines when extraction runs.

## Extraction Configuration

Defines:

- source;
- date range;
- concurrency;
- rate limit;
- timeout;
- retry policy;
- destination.

## Window Generator

Produces independent extraction windows.

## TaskGroup

Owns concurrent window tasks.

## AsyncCustomersClient

Centralizes HTTP behavior.

## Auth Manager

Owns token acquisition and refresh.

## Refresh Lock

Prevents token-refresh stampedes.

## Retry Policy

Classifies and retries transient failures.

## Rate Limiter

Controls global request admission.

## Window Extractor

Traverses pagination for one window.

## Validation

Checks response shape and business rules.

## Batching

Controls memory and write efficiency.

## Landing

Durably stores results.

## Checkpoint Store

Records completed durable windows.

## Metrics/Logs

Make the pipeline observable.

---

# 87. Realistic Data Engineering Scenario

> A company must extract 50,000+ customer records from a rate-limited SaaS API every night.

Constraints:

```text
API latency
API rate limit
OAuth authentication
cursor pagination
90-day date windows
Parquet landing
checkpointed recovery
```

A reasonable architecture is:

```text
90 independent date windows
        ↓
TaskGroup
        ↓
shared AsyncCustomersClient
        │
        ├── one AsyncClient
        ├── OAuth token manager
        ├── refresh lock
        ├── retry policy
        └── shared token bucket
        ↓
sequential pagination per window
        ↓
validation
        ↓
batched Parquet landing
        ↓
durable checkpoint
        ↓
metrics
```

Why?

### Windows can be concurrent

Each date range is independently queryable.

### Pages remain sequential

A cursor for page 2 may depend on page 1.

### One client is reused

Connection reuse improves efficiency.

### Authentication is shared

All tasks use the same token manager.

### Refresh is locked

Only one refresh occurs during simultaneous expiry.

### Rate limiting is shared

All requests consume one global request budget.

### Checkpoints are window-level

A completed durable window can be skipped on restart.

---

# 88. Production Trade-Off: Async vs Threads

## Async can be attractive when:

- the HTTP client is async-native;
- concurrency is high;
- the workload is dominated by network waits;
- many independent I/O operations must be coordinated.

## Threads can be attractive when:

- the existing client is synchronous;
- async support is unavailable;
- the workload has modest concurrency;
- migration cost matters.

Do not convert a stable synchronous pipeline to async merely because async is fashionable.

Ask:

```text
What bottleneck does async solve?
```

If the answer is unclear, benchmark first.

---

# 89. Production Trade-Off: Large vs Small Windows

## Large windows

Advantages:

- fewer scheduling operations;
- potentially fewer output files.

Disadvantages:

- coarse checkpoints;
- larger failure/retry scope;
- more data in memory if not streamed.

## Small windows

Advantages:

- fine-grained recovery;
- smaller output units;
- better parallelism.

Disadvantages:

- more request overhead;
- more metadata;
- more files;
- more checkpoint records.

The optimal window size depends on:

- API semantics;
- data volume;
- output format;
- recovery requirements.

---

# 90. Production Trade-Off: Checkpoint Frequency

Frequent checkpoints:

```text
better recovery
+
more checkpoint overhead
```

Infrequent checkpoints:

```text
lower checkpoint overhead
+
more work lost after failure
```

A window-level checkpoint is often a useful balance for date-window extraction.

---

# 91. Production Trade-Off: Aggressive Retries

Aggressive retries can improve availability during transient failures.

But they can also:

- extend run duration;
- increase source load;
- create duplicate operations;
- increase rate-limit pressure.

Therefore:

```text
reliability
```

must be balanced with:

```text
source pressure
+
runtime
+
idempotency
```

---

# 92. Security Requirements

Never hard-code:

- API keys;
- OAuth client secrets;
- access tokens;
- passwords.

Use:

```text
secret management
    ↓
runtime injection
    ↓
application
```

Do not log:

```text
Authorization
client_secret
access_token
refresh_token
```

Use safe redaction if request logging is required.

---

# 93. Code Quality Requirements

Examples should be:

- Python 3.13+ compatible;
- HTTPX-based;
- type-hinted where useful;
- syntactically valid;
- beginner-readable;
- production-conscious;
- explicit about error handling.

Typical imports include:

```python
import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx
```

Use additional libraries only when necessary.

Use Tenacity where retry behavior requires it.

Do not hide important logic behind unexplained helpers.

---

# 94. Hands-On Project

## Project: Production-Style Async Customer Extractor

Build an extractor with:

```text
AsyncCustomersClient
+
shared AsyncClient
+
OAuth client credentials
+
lock-protected token refresh
+
Tenacity retries
+
Retry-After handling
+
shared async token bucket
+
90-day independent windows
+
TaskGroup
+
sequential pagination per window
+
Parquet landing
+
checkpoints
+
resume
+
metrics
```

The project should simulate a realistic API.

A mock API can provide:

- customer records;
- date filters;
- cursor pagination;
- token expiry;
- 429;
- 503;
- delayed responses.

Do not use production credentials in the exercise.

---

# 95. Hands-On Phase 1 — Sequential Baseline

First build:

```text
sequential HTTP extractor
```

Requirements:

- same API;
- same filters;
- same response schema;
- same validation;
- same landing behavior.

Measure:

```text
runtime
requests
records
errors
```

This becomes the correctness and performance baseline.

---

# 96. Hands-On Phase 2 — Thread Pool

Implement the same workload using:

```python
ThreadPoolExecutor
```

Measure:

```text
runtime
CPU
memory
requests/sec
errors
```

Verify:

```text
threaded output == sequential output
```

---

# 97. Hands-On Phase 3 — AsyncClient

Convert the same extraction to:

```python
httpx.AsyncClient
```

Use:

```text
one client
explicit timeout
connection limits
```

Then compare:

```text
sequential
threads
async
```

Do not declare a winner until measurements and correctness checks are complete.

---

# 98. Hands-On Phase 4 — AsyncCustomersClient

Build the central client progressively:

1. shared AsyncClient;
2. basic GET;
3. timeout;
4. connection limits;
5. authentication;
6. token manager;
7. refresh lock;
8. retries;
9. Retry-After;
10. rate limiter;
11. pagination;
12. window extraction;
13. TaskGroup;
14. landing;
15. checkpointing;
16. metrics.

This progression mirrors production engineering.

---

# 99. Hands-On Phase 5 — OAuth

Implement client-credentials authentication.

Verify:

```text
token obtained
token reused
token expiry detected
```

Then force token expiry.

---

# 100. Hands-On Phase 6 — Refresh Stampede

Run:

```text
100 concurrent tasks
```

Force the access token to expire.

Verify:

```text
401s occur
refresh_count == 1
tasks reuse refreshed token
```

This is a key production correctness test.

---

# 101. Hands-On Phase 7 — Shared Token Bucket

Configure a shared rate limiter.

Verify that:

```text
all windows
    ↓
same limiter
```

Then measure:

```text
requests/sec
```

and confirm that the measured rate remains within the intended test limit.

---

# 102. Hands-On Phase 8 — Ninety-Day Windows

Split:

```text
90 days
```

into independent windows.

Run:

```python
asyncio.TaskGroup
```

for concurrent windows.

Inside each window:

```text
page 1
↓
page 2
↓
page 3
```

remains sequential.

---

# 103. Hands-On Phase 9 — Parquet Landing

For each window:

```text
fetch
 ↓
validate
 ↓
batch
 ↓
write Parquet
 ↓
confirm durable output
```

Only then:

```text
checkpoint complete
```

---

# 104. Hands-On Phase 10 — Kill and Resume

Simulate:

```text
90 windows
75 completed
process interrupted
```

Restart.

Verify:

```text
75 skipped
15 executed
```

Then verify final data against a clean full sequential run.

---

# 105. Hands-On Phase 11 — Failure Injection

Force:

```text
timeouts
429
503
401
file-write failure
malformed page
```

For each failure verify:

```text
detected
classified
retried/cancelled appropriately
not incorrectly checkpointed
observable
recoverable
```

---

# 106. Hands-On Phase 12 — Final Metrics

The final report should include:

```text
total runtime
requests/sec
records/sec
successful requests
failed requests
429 count
retry count
refresh count
p50 latency
p95 latency
windows completed
windows failed
```

Also compare:

```text
sequential
threads
async
```

---

# 107. Benchmark Table

Use a measured table:

| Metric | Sequential | ThreadPoolExecutor | AsyncClient |
|---|---:|---:|---:|
| Runtime | | | |
| Requests/sec | | | |
| Records/sec | | | |
| CPU | | | |
| Memory | | | |
| Errors | | | |
| 429 count | | | |
| p95 latency | | | |

Never fill the table with invented values.

---

# 108. Code-Reading Assessment

Consider:

```python
async def fetch_all(
    client: httpx.AsyncClient,
    urls: list[str],
) -> list[dict]:

    results = []

    for url in urls:
        response = await client.get(url)
        response.raise_for_status()
        results.append(response.json())

    return results
```

Questions:

1. Is this concurrent?
2. Why or why not?
3. What would happen if each request took 200 ms?
4. How could independent requests be executed concurrently?
5. What new concerns appear when concurrency is introduced?

Correct reasoning:

```text
for loop
+
await each request
=
sequential request scheduling
```

Concurrency requires explicit task orchestration.

---

# 109. Architecture Assessment

Design an extractor for:

```text
5 million records
API limit = 100 req/s
max concurrent requests = 25
OAuth tokens expire every 15 minutes
cursor pagination
daily windows
Parquet landing
must resume after process failure
```

Your design should include:

```text
AsyncClient
connection limits
TaskGroup
window concurrency
sequential cursor pages
shared token bucket
refresh lock
retry policy
Retry-After
streaming/batching
checkpointing
metrics
```

A good architecture is more important than a particular code listing.

---

# 110. Interview Questions — Basic

## 1. What is `httpx.AsyncClient`?

An asynchronous HTTP client that integrates with Python's async/await execution model and supports connection pooling, timeouts, HTTP/2, streaming, and other HTTP client capabilities.

## 2. Why use one AsyncClient per extraction run?

To reuse connections and centralize client configuration instead of repeatedly creating and destroying HTTP clients.

## 3. What does `await client.get()` do?

It waits asynchronously for the HTTP operation while allowing the event loop to run other eligible tasks.

## 4. Why are timeouts important?

They prevent stuck operations from occupying concurrency indefinitely.

## 5. What is HTTP/2 multiplexing?

The ability to carry multiple independent streams over an HTTP/2 connection, potentially reducing connection overhead.

---

# 111. Interview Questions — Intermediate

## 6. How do you retry async HTTP requests?

Use an async-compatible retry mechanism such as Tenacity, with bounded attempts, appropriate retry conditions, backoff/jitter, and provider-aware handling such as `Retry-After`.

## 7. How do you handle 429?

Respect `Retry-After` where provided, delay before retrying, maintain a bounded retry budget, and coordinate admission through a shared rate limiter.

## 8. What is a token-refresh stampede?

A condition where many concurrent tasks detect an expired token and independently refresh it at the same time.

## 9. How do you prevent it?

Use an `asyncio.Lock` around the refresh operation and re-check token validity after acquiring the lock.

## 10. Why can cursor pages not always be parallelized?

Because a subsequent page may require a cursor returned by the preceding page.

## 11. How do you create concurrency around dependent pagination?

Parallelize across independent windows while keeping page traversal sequential inside each window.

---

# 112. Interview Questions — Advanced

## 12. How would you design a 50,000-record async extractor?

I would use one shared AsyncClient, explicit timeouts and connection limits, bounded concurrency, a shared rate limiter, centralized authentication, bounded retries, window-level parallelism, sequential cursor pagination, batched durable landing, checkpoints, structured observability, and a sequential correctness baseline.

## 13. How would you prevent rate-limit violations?

Combine a concurrency limit with a shared rate limiter, respect `Retry-After`, and monitor 429 frequency.

## 14. How would you checkpoint?

Checkpoint a window only after all pages have been validated and its output has been durably landed.

## 15. How would you stream large responses?

Use `client.stream()` and consume the body incrementally rather than loading the entire response into memory.

## 16. How would you measure p95 latency?

Collect request durations and calculate the percentile over the request-duration distribution for the run or an appropriate time window.

---

# 113. Interview Questions — Senior Architecture

## 17. Design a resumable async ingestion platform.

A strong answer includes:

```text
scheduler
window planner
TaskGroup
shared AsyncClient
auth manager
refresh lock
retry policy
rate limiter
window extractor
validation
batched landing
checkpoint store
metrics/logs
```

with explicit failure and restart semantics.

## 18. How do you choose concurrency?

Based on:

- source limits;
- HTTP connection capacity;
- rate limits;
- response latency;
- local CPU/memory;
- downstream capacity;
- measured throughput;
- p95 latency.

## 19. How do you combine concurrency and rate limits?

Use:

```text
concurrency control
+
global rate admission
```

because limiting in-flight requests does not necessarily control requests started per second.

## 20. How do you recover from partial window failure?

Keep successful durable windows checkpointed, avoid checkpointing incomplete windows, and retry only incomplete work on restart.

## 21. How do you prove correctness?

Compare normalized async output against a trusted sequential baseline and verify record counts, keys, duplicates, missing records, and window completeness.

## 22. When is async not worth the complexity?

When concurrency is low, the existing synchronous implementation already meets the SLA, the source is the bottleneck, or async migration would introduce significant complexity without measurable benefit.

---

# 114. Final Knowledge Check

## HTTP Client

1. Why should one AsyncClient normally serve a run?
2. What does connection pooling provide?
3. What is a pool timeout?
4. When might HTTP/2 help?
5. Does HTTP/2 remove API rate limits?

## Async Execution

6. Why is `await` different from a blocking call?
7. Why does `await` inside a simple `for` loop not automatically create concurrency?
8. What blocks the event loop?
9. When can `asyncio.to_thread()` help?

## Authentication

10. What is OAuth client credentials?
11. What is a token-refresh stampede?
12. Why is the second token check inside the lock necessary?
13. What should never be logged?

## Reliability

14. Which HTTP statuses are commonly candidates for retry?
15. Why must retries be bounded?
16. What is `Retry-After`?
17. Why can retries themselves violate rate limits?

## Pagination

18. What makes cursor pagination dependent?
19. How can date windows create concurrency?
20. Why should cursor state remain local to each window?

## Rate Limiting

21. What is a concurrency limit?
22. What is a rate limit?
23. Why can both be necessary?
24. What does a token bucket represent?

## Landing

25. Why batch writes?
26. Why stream large responses?
27. Why should a checkpoint follow durable landing?
28. How does window-level checkpointing enable resume?

## Observability

29. Why is p95 useful?
30. Why measure 429 count?
31. Why measure retry count?
32. Why measure throughput and latency together?

## Architecture

33. Design the 90-day extractor.
34. Explain the refresh-lock architecture.
35. Explain the shared rate limiter.
36. Explain the failure/restart flow.

---

# 115. Final Production Checklist

## HTTP

- [ ] One shared `AsyncClient` per run.
- [ ] Explicit timeouts.
- [ ] Connection limits configured.
- [ ] HTTP/2 considered where appropriate.
- [ ] Streaming used for large responses.

## Authentication

- [ ] Credentials externalized.
- [ ] Access token managed centrally.
- [ ] Token refresh implemented.
- [ ] Refresh protected by `asyncio.Lock`.
- [ ] Token state re-checked inside the lock.
- [ ] Tokens/secrets never logged.

## Reliability

- [ ] Retry policy is bounded.
- [ ] Retryable errors are explicitly classified.
- [ ] `Retry-After` is respected.
- [ ] Retry budget exists.
- [ ] Request timeouts are configured.

## Concurrency

- [ ] Independent requests can run concurrently.
- [ ] Cursor-dependent pagination remains sequential.
- [ ] Independent windows run concurrently.
- [ ] TaskGroup owns window tasks.
- [ ] Concurrency is bounded.

## Rate Limiting

- [ ] Shared limiter.
- [ ] Token bucket or equivalent admission control.
- [ ] Rate and concurrency limits are distinguished.
- [ ] Adaptive reduction is considered for sustained 429s.

## Landing

- [ ] Large responses are streamed where appropriate.
- [ ] Results are batched.
- [ ] Parquet or JSONL landing is defined.
- [ ] Writes are safe against partial output.
- [ ] Checkpoints occur only after durable landing.

## Resumability

- [ ] Window identity is deterministic.
- [ ] Completed windows are durable.
- [ ] Incomplete windows remain retryable.
- [ ] Reruns are idempotent.
- [ ] Duplicate output is prevented.

## Observability

- [ ] Request count.
- [ ] Success count.
- [ ] Failure count.
- [ ] 429 count.
- [ ] Retry count.
- [ ] Token refresh count.
- [ ] Records extracted.
- [ ] Records landed.
- [ ] Windows completed.
- [ ] Windows failed.
- [ ] p50 latency.
- [ ] p95 latency.
- [ ] Throughput.
- [ ] Runtime.

## Correctness

- [ ] Async output matches sequential baseline.
- [ ] No missing windows.
- [ ] No duplicate windows.
- [ ] No silent record loss.
- [ ] Failure behavior is explicit.
- [ ] Restart behavior is tested.

---

# 116. Final Mental Model

The complete production flow is:

```text
Classify workload
        ↓
Create one AsyncClient
        ↓
Configure timeouts/connections
        ↓
Authenticate safely
        ↓
Protect token refresh
        ↓
Respect rate limits
        ↓
Retry transient failures
        ↓
Parallelize independent work
        ↓
Keep dependent pagination sequential
        ↓
Stream/batch results
        ↓
Land durably
        ↓
Checkpoint
        ↓
Measure throughput + p95
        ↓
Validate against baseline
        ↓
Resume safely after failure
```

Each stage has a specific responsibility.

### Classify the workload

Determine whether asynchronous I/O is actually the right execution model.

### Create one AsyncClient

Enable connection reuse and centralized HTTP configuration.

### Configure timeouts/connections

Prevent hangs and bound client-side resources.

### Authenticate safely

Centralize token management and protect credentials.

### Protect token refresh

Prevent many concurrent tasks from refreshing the same expired token.

### Respect rate limits

Coordinate all request tasks through a shared admission mechanism.

### Retry transient failures

Recover from temporary problems without creating retry storms.

### Parallelize independent work

Use concurrency where dependencies permit it.

### Keep dependent pagination sequential

Do not violate cursor dependencies for the sake of concurrency.

### Stream/batch results

Control memory and improve write efficiency.

### Land durably

Make output safe and observable.

### Checkpoint

Record only work that has actually completed durably.

### Measure throughput + p95

Understand both capacity and tail behavior.

### Validate against baseline

Prove that performance did not come at the cost of correctness.

### Resume safely

Treat failure and restart as normal production conditions rather than exceptional events.

---

# 117. Final Production Principle

> **High-throughput async HTTP extraction is controlled concurrency around an external system with limits, dependencies, failures, authentication state, and durable state.**

The mature mental model is:

```text
AsyncClient
    +
structured concurrency
    +
bounded concurrency
    +
shared rate limiting
    +
safe authentication
    +
lock-protected refresh
    +
bounded retries
    +
correct pagination
    +
streaming/batching
    +
durable landing
    +
checkpointing
    +
observability
    +
measurement
    +
correctness verification
```

The objective is not to send the maximum possible number of requests.

The objective is:

```text
maximum useful throughput
        subject to
correctness
+
source health
+
resource limits
+
recoverability
```

A production Data Engineer should be able to answer all of the following before shipping an async extractor:

```text
Why async?

What is the concurrency boundary?

How many requests can be in flight?

How many requests can start per second?

What happens at 429?

What happens when the token expires?

Can 100 tasks trigger 100 refreshes?

Which pages depend on previous cursors?

What happens when one window fails?

What is checkpointed?

When is output considered durable?

How does the job resume?

What is the p95 latency?

What is the actual throughput?

Did async beat threads?

Did it beat sequential execution?

Did correctness remain identical?
```

If those questions have explicit, tested answers, the extractor is moving beyond an async coding exercise toward a production Data Engineering system.
