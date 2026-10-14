# HTTPX and Requests — Sessions and Timeouts

HTTP clients are infrastructure in a production data-ingestion system. A small script can get away with “send a request and parse JSON.” A production ingestion client must also control connection reuse, timeouts, memory, file integrity, response validation, observability, security, testing, and failure boundaries.

The central progression in this chapter is:

```text
Basic HTTP client usage
        ↓
Reusable sessions/clients
        ↓
Timeouts
        ↓
Streaming
        ↓
Error handling
        ↓
Connection pools
        ↓
Reusable API client design
        ↓
Testing
        ↓
Observability
        ↓
Retry boundaries
        ↓
TLS / proxies / HTTP/2
        ↓
Production architecture
```

> **Primary objective:** move from “How do I send an HTTP request in Python?” to “How do I design a reliable, efficient, observable, testable, secure HTTP client for a production data-ingestion pipeline?”

---

# 1. Learning Objectives

By the end of this chapter, you should be able to:

- make HTTP requests with `httpx`;
- understand equivalent `requests` patterns;
- reuse HTTP clients and sessions;
- configure base URLs, headers, query parameters, and JSON bodies;
- configure explicit timeouts;
- understand connect, read, write, and pool timeouts;
- stream large responses without loading the entire payload into memory;
- safely write downloaded files using temporary files and atomic rename;
- validate status codes, content types, and JSON bodies;
- handle invalid JSON, HTML error pages, truncated responses, and unexpected content types;
- configure connection-pool limits;
- close clients correctly;
- design a reusable API client class;
- return useful parsed records rather than leaking HTTP details into business logic;
- test HTTP clients without real network access;
- use `httpx.MockTransport`, `respx`, and `responses`;
- instrument request count, latency, status codes, and failures;
- redact credentials and sensitive URLs from logs;
- understand the boundary between transport-level and application-level retries;
- understand `urllib3.Retry` and Requests adapters;
- configure TLS verification and custom CA bundles;
- understand proxies and their operational implications;
- understand practical HTTP/2 support in HTTPX;
- benchmark one-off requests against a reused client without inventing results;
- explain how to productionize an HTTP ingestion client.

---

# 2. Prerequisites

This chapter assumes that you completed Topic 01, **HTTP Fundamentals for Data Extraction**.

You should already understand:

- request/response;
- HTTP methods;
- status codes;
- headers;
- content types;
- HTTP errors;
- connection reuse conceptually;
- streaming conceptually;
- idempotency conceptually.

We will use small reminders where necessary, but this chapter does **not** re-teach HTTP fundamentals.

---

# 3. Why HTTP Clients Matter in Data Engineering

A data-ingestion job often performs repeated network operations:

```text
API
 ↓
page / resource
 ↓
parse
 ↓
store
 ↓
next request
 ↓
repeat
```

That makes the HTTP client part of the ingestion infrastructure.

A production HTTP client has to answer questions such as:

- How long may a connection attempt wait?
- How long may a response stall?
- How many connections may be open?
- What happens when the response is huge?
- What happens when the API returns HTML instead of JSON?
- What happens when a connection breaks halfway through a download?
- Where are credentials stored?
- What gets logged?
- How are failures tested?
- How do we measure latency?
- Which failures belong to the transport layer?
- Which failures belong to the application retry policy?
- How do we avoid leaving a half-written file that looks complete?

## Toy script vs production ingestion client

A toy script might look like:

```python
import requests

response = requests.get("https://api.example.com/customers")
data = response.json()
```

A production ingestion client needs a much stronger boundary:

```text
                    Data Ingestion Job
                           │
                           ▼
                    API Client
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Timeouts       Pooling       Validation
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                      HTTP transport
                           │
                    TLS / Proxy / HTTP2
                           │
                           ▼
                       External API
```

The point is not to make every HTTP call complicated. The point is to centralize the complexity where it belongs.

---

# 4. The First Important Lesson — One-Off Requests vs Reused Clients

## 4.1 One-off `httpx.get()`

The simplest HTTPX call is:

```python
import httpx

response = httpx.get("https://example.com")
```

This is useful for small scripts and quick experiments.

For repeated extraction work, however, you generally want a reusable client:

```python
import httpx

with httpx.Client() as client:
    response = client.get("https://example.com")
```

The important difference is lifecycle.

With one-off calls, the code asks the library to perform an independent request each time.

With a client, the client owns reusable connection state and configuration.

---

## 4.2 One-off `requests.get()`

The equivalent Requests pattern is:

```python
import requests

response = requests.get("https://example.com")
```

For repeated calls:

```python
import requests

with requests.Session() as session:
    response = session.get("https://example.com")
```

A `requests.Session` provides persistent session behavior, including connection reuse.

---

## 4.3 Why connection reuse matters

Think about repeatedly calling an API:

```text
Request 1
Request 2
Request 3
...
Request 1000
```

Without effective reuse, requests may repeatedly incur connection-establishment work.

With a reusable client:

```text
Client
 ├── connection pool
 ├── reusable connection
 ├── reusable connection
 └── connections created as needed
```

HTTP keep-alive allows an established connection to remain available for subsequent requests when the protocol and server permit it.

Conceptually:

```text
Without reuse:

request
   ↓
connect
   ↓
TLS setup
   ↓
request
   ↓
response
   ↓
close

repeat...
```

With reuse:

```text
client
   ↓
connection pool
   ├── request
   ├── request
   ├── request
   └── request
```

Connection establishment has cost. Depending on the environment, that can involve DNS resolution, TCP connection establishment, TLS negotiation, and server-side processing.

The exact savings depend on network conditions, server behavior, HTTP version, and workload.

### Why this matters at different scales

For 10 requests, the difference may be modest.

For 1,000 requests, repeated connection setup can become measurable.

For 100,000 requests, inefficient connection management can materially affect throughput, latency, resource consumption, and source-system load.

The correct engineering approach is to **measure your workload rather than assume a particular speedup**.

---

# 5. HTTPX Client Fundamentals

A basic reusable HTTPX client:

```python
import httpx

with httpx.Client() as client:
    response = client.get("https://example.com")

print(response.status_code)
```

The important pieces are:

- `httpx.Client()` creates a reusable synchronous HTTP client;
- `client.get(...)` performs a GET;
- the `with` block manages the client lifecycle;
- leaving the block closes the client and its resources.

---

## 5.1 `base_url`

Instead of repeating the API host:

```python
import httpx

with httpx.Client() as client:
    client.get("https://api.example.com/customers")
    client.get("https://api.example.com/orders")
```

centralize it:

```python
import httpx

with httpx.Client(
    base_url="https://api.example.com",
) as client:
    client.get("/customers")
    client.get("/orders")
```

This improves maintainability because the API endpoint is configured once.

It also makes testing easier because a client can be pointed at a test server or mock transport without changing every endpoint path.

---

# 6. Default Headers

Headers that apply to many requests can be configured at the client level:

```python
import httpx

headers = {
    "Accept": "application/json",
    "User-Agent": "my-data-ingestion-client/1.0",
}

with httpx.Client(
    base_url="https://api.example.com",
    headers=headers,
) as client:
    response = client.get("/customers")
```

## `Accept`

`Accept` communicates which response media types the client expects.

For a JSON API:

```http
Accept: application/json
```

## `Content-Type`

`Content-Type` describes the media type of the request body.

For JSON request data, the HTTP client normally handles the appropriate serialization and content type when you use its JSON request interface.

## `User-Agent`

A descriptive User-Agent can identify your application to the upstream service:

```text
my-data-ingestion-client/1.0
```

This is more useful than an anonymous or misleading identifier because API operators can understand which system is generating traffic.

A production User-Agent might include an application name and version, but should not expose credentials or sensitive internal information.

### Never place secrets into ordinary logs

Do not log:

- API keys;
- bearer tokens;
- passwords;
- refresh tokens;
- secret request headers;
- sensitive query parameters;
- signed URLs containing credentials.

Bad:

```text
GET /customers?api_key=super-secret-key
Authorization: Bearer eyJ...
```

Safe:

```text
GET /customers
Authorization: Bearer REDACTED
```

---

# 7. Query Parameters

Use the client's `params` argument:

```python
import httpx

with httpx.Client(base_url="https://api.example.com") as client:
    response = client.get(
        "/customers",
        params={
            "limit": 100,
            "status": "active",
        },
    )
```

Conceptually:

```text
params={
    "limit": 100,
    "status": "active"
}

            ↓

/customers?limit=100&status=active
```

The client handles URL encoding.

Avoid manually concatenating query strings:

```python
# BAD EXAMPLE
url = (
    "https://api.example.com/customers"
    "?limit=" + str(limit)
    + "&status=" + status
)
```

Manual construction is error-prone when values contain spaces, reserved characters, Unicode, or other characters requiring encoding.

---

# 8. JSON Request Bodies

HTTPX provides a `json=` parameter:

```python
import httpx

with httpx.Client(base_url="https://api.example.com") as client:
    response = client.post(
        "/exports",
        json={
            "resource": "customers",
            "format": "jsonl",
        },
    )
```

This separates the Python representation of the request body from the mechanics of serializing it as JSON.

The important concepts are:

```text
Python object
     ↓
JSON serialization
     ↓
HTTP request body
     ↓
Content-Type
```

The server processes the JSON and returns a response that you then validate and parse.

POST idempotency and retry semantics are important production concerns, but they are deliberately not developed into a full retry chapter here.

---

# 9. Understanding the Response Object

A response contains several useful representations.

```python
response.status_code
response.headers
response.json()
response.text
response.content
```

## `status_code`

```python
if response.status_code == 200:
    ...
```

Use it when you need explicit status-specific logic.

## `headers`

```python
content_type = response.headers.get("content-type")
```

Headers can contain metadata such as:

- content type;
- content length;
- caching information;
- server metadata;
- request identifiers.

## `json()`

```python
data = response.json()
```

Use when you expect a JSON response.

It can fail if the body is not valid JSON.

## `text`

```python
body = response.text
```

Useful when the response is textual and you need decoded text.

## `content`

```python
body = response.content
```

Returns the complete response body as bytes.

This is convenient for small payloads but can be dangerous for very large downloads.

---

# 10. `raise_for_status()`

A common safe pattern is:

```python
response.raise_for_status()
data = response.json()
```

`raise_for_status()` checks whether the response indicates an HTTP error and raises an appropriate HTTPX exception for error status codes.

Compare:

```python
# WEAK PATTERN
if response.status_code == 200:
    data = response.json()
```

with:

```python
# BETTER PATTERN
response.raise_for_status()
data = response.json()
```

The second pattern is easier to maintain because it does not assume that only `200` is the meaningful success status.

However:

> A successful HTTP status does not guarantee that the response body contains valid JSON or the expected data structure.

For example, a server, proxy, or gateway could return:

```text
200 OK
Content-Type: text/html
```

with an HTML body.

HTTP success and payload correctness are separate validation layers.

---

# 11. Requests Equivalent

Requests uses a similar programming model:

```python
import requests

with requests.Session() as session:
    response = session.get("https://api.example.com/customers")
    response.raise_for_status()
    data = response.json()
```

## HTTPX vs Requests

| Concept | HTTPX | Requests |
|---|---|---|
| One-off GET | `httpx.get(url)` | `requests.get(url)` |
| Reusable client | `httpx.Client()` | `requests.Session()` |
| Headers | `headers=` | `headers=` |
| Query params | `params=` | `params=` |
| JSON body | `json=` | `json=` |
| Status handling | `raise_for_status()` | `raise_for_status()` |
| JSON parsing | `response.json()` | `response.json()` |
| Streaming | `client.stream(...)` / streaming APIs | `stream=True` |
| HTTP/2 | HTTPX supports it | Not the same HTTP/2 model |
| Sync API | Yes | Yes |
| Async API | Yes | Requests is synchronous |

Requests remains extremely common in existing Python systems. Production engineers need to be able to read, maintain, test, and improve Requests-based code.

HTTPX is emphasized in this chapter because it provides a modern client interface with synchronous and asynchronous APIs and practical HTTP/2 support.

This is not a claim that one library is universally better. The right choice depends on the existing system, requirements, team knowledge, and operational constraints.

Async HTTP programming is intentionally not developed into a full tutorial here; it belongs to later material.

---

# 12. Timeouts — The Most Important Production Habit

Ask:

> What happens if the server never responds?

If the client can wait forever, a worker can become stuck indefinitely.

That can cause:

```text
API hangs
   ↓
worker waits
   ↓
job remains occupied
   ↓
other work queues
   ↓
pipeline capacity decreases
```

A production HTTP client should explicitly define timeout behavior.

HTTPX supports four useful timeout categories:

```python
import httpx

timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=5.0,
)
```

These are different resources and should not be treated as one generic number.

---

# 13. Connect Timeout

The connect timeout controls how long the client waits while establishing a connection.

Conceptually, this covers connection establishment work such as:

```text
resolve/connect
    ↓
TCP connection
    ↓
TLS negotiation where applicable
    ↓
connection established
```

Example:

```python
import httpx

timeout = httpx.Timeout(connect=5.0)
```

A connect timeout can protect the ingestion worker from an unreachable or inaccessible endpoint.

### Too small

If the value is too small, temporary network conditions may create false failures.

### Too large

If the value is too large, an unreachable service can consume worker time for too long.

The right value depends on the network and endpoint.

---

# 14. Read Timeout

The read timeout controls how long the client waits for response data.

This is important for slow or stalled servers.

A read timeout is **not simply**:

> “The entire request must finish within 30 seconds.”

For streaming workloads, response data can arrive progressively. The relevant question is whether the client continues to receive data within the configured read-timeout behavior.

Consider:

```text
Request sent
     ↓
Server begins responding
     ↓
chunk
     ↓
chunk
     ↓
chunk
     ↓
stall
```

If the server stalls beyond the allowed read interval, the client can fail rather than waiting indefinitely.

A large response may legitimately take a long time overall while still making steady progress.

---

# 15. Write Timeout

The write timeout controls how long the client waits while sending request data.

This matters more when request bodies are larger or the destination is slow.

Conceptually:

```text
application
   ↓
request body
   ↓
network
   ↓
server
```

If the destination stops accepting data, a bounded write timeout prevents an indefinite wait.

---

# 16. Pool Timeout

The pool timeout controls how long a request waits for an available connection from the client's connection pool.

Consider:

```text
20 workers
5 available connections
```

Potentially:

```text
5 workers → active connections
15 workers → waiting
```

The waiting workers consume no connection while waiting, but the wait itself must be bounded.

A pool timeout makes pool contention visible as a failure rather than allowing unbounded waiting.

---

# 17. Requests Has No Default Timeout

One of the most important Requests production habits is:

```python
# BAD EXAMPLE
import requests

requests.get(url)
```

Without an explicit timeout, the call does not provide the bounded waiting behavior expected of a production ingestion system.

Use an explicit timeout:

```python
import requests

requests.get(
    url,
    timeout=(5, 30),
)
```

Requests accepts a tuple for connect and read timeout configuration.

Compare with HTTPX:

```python
import httpx

timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=5.0,
)
```

The key engineering principle is:

> Never let an external network dependency decide how long your worker is allowed to wait.

---

# 18. Timeout Design Trade-Offs

There is no universal timeout value.

Timeouts depend on:

- API type;
- endpoint behavior;
- payload size;
- network environment;
- service-level expectations;
- expected latency;
- retry policy;
- batch size.

A poor design might use:

```python
# BAD EXAMPLE
timeout = 600
```

for every endpoint simply because “ten minutes is safe.”

That may hide failures and tie up workers unnecessarily.

A better design starts with endpoint expectations:

```text
small metadata endpoint
    → short read timeout

large export endpoint
    → longer read timeout

connection establishment
    → bounded connect timeout

highly contended pool
    → deliberate pool timeout
```

Timeouts should be measured and justified rather than copied blindly.

---

# 19. Streaming Large Downloads

Consider:

```python
# DANGEROUS FOR VERY LARGE RESPONSES
response = client.get(url)
data = response.content
```

If the response is 2 GB, this approach attempts to hold the entire body in memory.

That can produce:

```text
2 GB response
    ↓
RAM
    ↓
memory pressure
    ↓
possible process termination
```

Instead, stream the response:

```python
with client.stream("GET", url) as response:
    response.raise_for_status()

    for chunk in response.iter_bytes():
        ...
```

Conceptually:

```text
Bad:

2 GB response
      ↓
     RAM
      ↓
   process


Good:

network
   ↓
small chunk
   ↓
disk
   ↓
small chunk
   ↓
disk
```

Streaming creates a bounded-memory design.

---

# 20. `client.stream(...)`

A streamed HTTPX request has an explicit lifecycle:

```python
with client.stream("GET", url) as response:
    response.raise_for_status()

    for chunk in response.iter_bytes():
        ...
```

The context manager matters because the response is a live resource associated with the network connection.

Leaving the context closes the streaming response correctly.

Do not treat a streaming response as though it were already fully materialized in memory.

---

# 21. `iter_bytes()`

`iter_bytes()` allows the application to process response data incrementally.

Example:

```python
with client.stream("GET", url) as response:
    response.raise_for_status()

    for chunk in response.iter_bytes():
        process(chunk)
```

The key properties are:

- chunks instead of the complete body;
- bounded memory;
- incremental disk writes;
- suitability for multi-GB payloads.

The exact chunking behavior is managed by the HTTP client and transport; application code should not assume that each chunk corresponds to a file record, JSON object, or application-level message.

---

# 22. Safe Large-File Download

A production-oriented download function should:

1. stream;
2. use bounded memory;
3. validate status;
4. write to a temporary file;
5. only publish the final filename after successful completion;
6. clean up temporary data on failure.

Example:

```python
from pathlib import Path
import os
import tempfile

import httpx


def download_file(
    client: httpx.Client,
    url: str,
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with client.stream("GET", url) as response:
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{destination.name}.",
                suffix=".tmp",
                dir=destination.parent,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                for chunk in response.iter_bytes():
                    temporary_file.write(chunk)

                temporary_file.flush()
                os.fsync(temporary_file.fileno())

        os.replace(temporary_path, destination)
        temporary_path = None

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

### Why each part exists

`destination.parent.mkdir(...)`

Ensures the destination directory exists.

`client.stream(...)`

Prevents the full response from being loaded into memory.

`response.raise_for_status()`

Prevents an HTTP error body from being treated as a successful file.

`NamedTemporaryFile(...)`

Creates an incomplete intermediate object rather than publishing the final filename immediately.

`flush()`

Pushes Python's buffered writes toward the operating system.

`os.fsync(...)`

Requests that the operating system flush file data and metadata to stable storage where supported. Whether this is necessary depends on the durability requirement and storage system.

`os.replace(...)`

Publishes the completed file under the final name as an atomic replacement operation on the same filesystem.

`finally`

Ensures the temporary file is removed if an exception interrupts the download.

---

# 23. Atomic File Writes

The pattern is:

```text
download
   ↓
temporary file
   ↓
flush / close
   ↓
atomic rename
   ↓
final file
```

Writing directly to the final name is dangerous:

```text
large.zip
  ↓
50% downloaded
  ↓
process crashes
  ↓
large.zip exists
  ↓
another job assumes it is complete
```

A safer pattern is:

```text
large.zip.tmp
  ↓
complete download
  ↓
rename
  ↓
large.zip
```

This creates an important state distinction:

```text
final file exists
        ≈
download reached publication point
```

It is not a complete end-to-end data-quality guarantee, but it is much safer than exposing a partially downloaded final file.

---

# 24. Handling Bad Response Bodies

HTTP status is only one validation layer.

A response can be:

```text
HTTP 200
Content-Type: text/html
Body: <html>...</html>
```

or:

```text
HTTP 200
Content-Type: application/json
Body: malformed JSON
```

or:

```text
HTTP 200
Content-Type: application/json
Body: valid JSON with unexpected structure
```

A robust client handles these separately.

## Invalid JSON

```python
try:
    data = response.json()
except ValueError as exc:
    raise RuntimeError("API returned invalid JSON") from exc
```

The exact exception hierarchy can vary by library/version; the important application behavior is to treat malformed JSON as a parsing failure, not as valid data.

## HTML error page

A reverse proxy, gateway, load balancer, or web server may return:

```html
<html>
    <body>
        <h1>Bad Gateway</h1>
    </body>
</html>
```

Attempting `.json()` immediately can produce a confusing parsing error.

## Truncated response

An incomplete response can cause:

- invalid JSON;
- corrupt files;
- incomplete records;
- downstream parsing failures.

For large files, the temporary-file pattern prevents a partial response from being published as a completed file.

## Unexpected content type

Inspect the header:

```python
content_type = response.headers.get("content-type", "")
```

Then validate it before parsing when the endpoint contract requires a particular media type.

---

# 25. Production Response Validation

A focused helper can centralize JSON-response validation:

```python
import httpx


def expect_json(response: httpx.Response) -> dict:
    response.raise_for_status()

    content_type = response.headers.get("content-type", "").lower()

    if "application/json" not in content_type:
        raise ValueError(
            f"Expected JSON response, got content type {content_type!r}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Response contained invalid JSON") from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object, got {type(data).__name__}"
        )

    return data
```

The validation order is deliberate:

```text
1. status
   ↓
2. content type
   ↓
3. body parsing
   ↓
4. expected structure
```

This is not a full schema-validation framework. It is HTTP-client-level response validation.

---

# 26. Connection Pools

A connection pool is a managed collection of reusable network connections.

Think of it as a parking area:

```text
Client
  │
  ▼
Connection Pool
  ├── connection A
  ├── connection B
  ├── connection C
  └── ...
```

Requests can use an available connection and return it to the pool when the response lifecycle allows reuse.

HTTPX lets you configure pool limits:

```python
import httpx

limits = httpx.Limits(
    max_connections=20,
    max_keepalive_connections=10,
)

with httpx.Client(limits=limits) as client:
    ...
```

## `max_connections`

Controls the maximum number of concurrent connections.

## `max_keepalive_connections`

Controls how many idle connections may be retained for reuse.

## Why limits matter

Too many connections can:

- consume local resources;
- increase TLS/network overhead;
- overwhelm the source system;
- create unnecessary concurrency.

Too few connections can:

- create queueing;
- increase latency;
- underutilize available capacity.

Connection-pool sizing should therefore be considered together with workload concurrency and upstream limits.

---

# 27. Pool Timeout + Connection Limits

Suppose:

```text
20 workers
5 connections
```

A simplified view is:

```text
5 workers → connections
15 workers → waiting
```

If requests wait indefinitely for a connection, pool contention becomes hidden latency.

With a bounded pool timeout:

```text
request
   ↓
try to acquire connection
   ↓
available?
 ┌───────┴───────┐
 yes             no
  ↓               ↓
request        wait up to pool timeout
                  ↓
              timeout/failure
```

The pool timeout therefore turns resource contention into observable behavior.

This does not replace upstream rate limiting or concurrency design. It is one layer of resource control.

---

# 28. Closing HTTP Clients Correctly

Prefer context managers:

```python
import httpx

with httpx.Client(...) as client:
    response = client.get(...)
```

The equivalent explicit lifecycle is:

```python
import httpx

client = httpx.Client(...)

try:
    response = client.get(...)
finally:
    client.close()
```

Do the same with Requests:

```python
import requests

with requests.Session() as session:
    response = session.get(...)
```

The client/session owns resources that should not be left indefinitely.

A common production design is to create one client for a job or service component and reuse it for the requests that belong to that lifecycle.

---

# 29. Designing a Reusable API Client Class

Instead of spreading HTTP configuration throughout ingestion code:

```python
for customer_id in customer_ids:
    requests.get(...)
```

create a boundary:

```python
class CustomersClient:
    ...
```

A useful client can centralize:

- base URL;
- default headers;
- User-Agent;
- timeout configuration;
- connection limits;
- authentication placeholder;
- request execution;
- response handling;
- logging;
- metrics/event hooks.

Conceptually:

```text
CustomersClient
      │
      ├── base URL
      ├── headers
      ├── timeout
      ├── connection pool
      ├── auth
      ├── request method
      ├── response handling
      └── metrics/logging
```

The rest of the pipeline can then work at the business level.

---

# 30. Separate HTTP Infrastructure From Business Logic

Bad:

```python
# BAD EXAMPLE
for customer_id in customer_ids:
    response = requests.get(
        f"https://api.example.com/customers/{customer_id}"
    )
    data = response.json()
```

The loop now knows:

- the URL;
- HTTP library;
- response parsing;
- error behavior;
- authentication;
- configuration.

Better:

```python
client = CustomersClient(...)

for customer_id in customer_ids:
    customer = client.get_customer(customer_id)
    process_customer(customer)
```

The client owns HTTP concerns.

This improves:

- testing;
- maintainability;
- observability;
- configuration;
- reliability;
- reuse.

---

# 31. API Client Return Design

Callers should generally not need to understand raw HTTP mechanics for ordinary business operations.

Prefer:

```python
customer = client.get_customer(customer_id)
```

and:

```python
for customer in client.list_customers():
    process(customer)
```

rather than forcing every caller to write:

```python
response = client.get(...)
response.raise_for_status()
data = response.json()
```

The API client becomes an abstraction boundary.

Raw HTTP response handling still belongs somewhere. It belongs inside the client layer where status handling, parsing, validation, logging, and instrumentation can be centralized.

---

# 32. Testing Without the Network

Most unit tests should not require a live external API.

The architecture becomes:

```text
Application
    ↓
HTTP client abstraction
    ↓
mock transport
    ↓
fake response
```

Benefits include:

- deterministic tests;
- fast tests;
- no API quota consumption;
- no network dependency;
- predictable failure scenarios.

A test should be able to answer:

> “What does my client do when the API returns 500?”

without actually waiting for a real API to return 500.

---

# 33. `httpx.MockTransport`

HTTPX provides a transport-level testing mechanism:

```python
import httpx


def handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(
        200,
        json={"customers": []},
    )


transport = httpx.MockTransport(handler)

with httpx.Client(
    base_url="https://api.example.com",
    transport=transport,
) as client:
    response = client.get("/customers")

print(response.json())
```

Conceptually:

```text
client.get(...)
      ↓
HTTPX transport
      ↓
MockTransport
      ↓
handler()
      ↓
fake Response
```

No real network connection is required.

This is particularly useful when you want direct control over the request and response behavior.

---

# 34. `respx`

`respx` is useful for mocking HTTPX requests at a higher testing level.

Illustrative examples:

```python
import httpx
import pytest
import respx


@respx.mock
def test_success():
    respx.get("https://api.example.com/customers").mock(
        return_value=httpx.Response(
            200,
            json={"customers": [{"id": 1}]},
        )
    )

    with httpx.Client() as client:
        response = client.get("https://api.example.com/customers")

    response.raise_for_status()
    assert response.json()["customers"][0]["id"] == 1
```

## Testing a 500

```python
@respx.mock
def test_server_error():
    respx.get("https://api.example.com/customers").mock(
        return_value=httpx.Response(500, text="server error")
    )

    with httpx.Client() as client:
        response = client.get("https://api.example.com/customers")

    assert response.status_code == 500

    with pytest.raises(httpx.HTTPStatusError):
        response.raise_for_status()
```

## Testing invalid JSON

```python
@respx.mock
def test_invalid_json():
    respx.get("https://api.example.com/customers").mock(
        return_value=httpx.Response(
            200,
            text="{not valid json",
            headers={"content-type": "application/json"},
        )
    )

    with httpx.Client() as client:
        response = client.get("https://api.example.com/customers")

    with pytest.raises(ValueError):
        response.json()
```

## Testing an unexpected content type

```python
@respx.mock
def test_unexpected_content_type():
    respx.get("https://api.example.com/customers").mock(
        return_value=httpx.Response(
            200,
            text="<html>not an api response</html>",
            headers={"content-type": "text/html"},
        )
    )

    with httpx.Client() as client:
        response = client.get("https://api.example.com/customers")

    assert "application/json" not in response.headers["content-type"]
```

## Testing a timeout

A timeout can be represented by making the mocked route raise the relevant exception:

```python
@respx.mock
def test_timeout():
    route = respx.get("https://api.example.com/customers")
    route.side_effect = httpx.ReadTimeout("API did not respond in time")

    with httpx.Client() as client:
        with pytest.raises(httpx.ReadTimeout):
            client.get("https://api.example.com/customers")
```

The test proves the application can handle the failure without making a real network request.

---

# 35. `responses` for Requests

For existing Requests-based systems, `responses` provides a similar approach.

Illustrative example:

```python
import requests
import responses


@responses.activate
def test_requests_client():
    responses.add(
        responses.GET,
        "https://api.example.com/customers",
        json={"customers": []},
        status=200,
    )

    with requests.Session() as session:
        response = session.get(
            "https://api.example.com/customers",
            timeout=(5, 30),
        )

    response.raise_for_status()
    assert response.json() == {"customers": []}
```

The important lesson is broader than a specific testing package:

> Legacy Requests code does not require a real API in every unit test.

---

# 36. Recorded Fixtures

Recorded fixtures replay known request/response interactions.

They can be useful when:

- a real response is complicated;
- the payload is expensive to generate;
- you need stable regression cases;
- you want deterministic replay.

However, fixtures must be managed carefully.

### Risks

- secrets can accidentally be captured;
- sensitive customer data can be captured;
- old responses can become unrealistic;
- fixture maintenance can become burdensome.

Before committing a recorded response:

```text
real response
    ↓
sanitize
    ↓
remove credentials
    ↓
remove sensitive data
    ↓
store stable fixture
```

Fixture reproducibility is useful only if the fixture itself is safe and maintainable.

---

# 37. Event Hooks

HTTPX supports request and response event hooks.

Conceptually:

```python
import httpx

event_hooks = {
    "request": [],
    "response": [],
}

client = httpx.Client(event_hooks=event_hooks)
```

A simple timing design can record start time on the request and calculate elapsed time on the response.

Illustrative example:

```python
from time import perf_counter

import httpx


def record_request(request: httpx.Request) -> None:
    request.extensions["started_at"] = perf_counter()


def record_response(response: httpx.Response) -> None:
    started_at = response.request.extensions.get("started_at")

    if started_at is not None:
        latency_seconds = perf_counter() - started_at
        print(
            "http_request",
            response.request.method,
            response.status_code,
            f"{latency_seconds:.3f}s",
        )


client = httpx.Client(
    event_hooks={
        "request": [record_request],
        "response": [record_response],
    }
)
```

For production systems, replace `print()` with the project's structured logging or metrics system.

Useful metrics include:

- request count;
- HTTP method;
- URL path without secrets;
- status code;
- latency;
- timeout count;
- exception count.

---

# 38. Secret Redaction

This is mandatory production behavior.

Never log:

- API keys;
- bearer tokens;
- passwords;
- refresh tokens;
- sensitive query parameters;
- secret headers.

Unsafe:

```python
logger.info("request headers=%s", dict(request.headers))
```

That can leak:

```text
Authorization: Bearer ...
```

Safer:

```python
def safe_headers(headers: httpx.Headers) -> dict[str, str]:
    result = dict(headers)

    for name in ("authorization", "proxy-authorization"):
        if name in result:
            result[name] = "REDACTED"

    return result
```

Then:

```python
logger.info(
    "HTTP request method=%s headers=%s",
    request.method,
    safe_headers(request.headers),
)
```

Also consider URLs:

```text
https://example.com/export?token=SECRET
```

A logger that records the complete URL can leak credentials even if headers are redacted.

Use normalized or sanitized URLs in logs.

---

# 39. Measuring HTTP Client Performance

Useful measurements include:

- request count;
- request latency;
- connection reuse;
- errors;
- timeout count;
- throughput.

A simple timing measurement:

```python
from time import perf_counter

start = perf_counter()

response = client.get("/customers")
response.raise_for_status()

elapsed = perf_counter() - start

print(f"request_latency_seconds={elapsed:.3f}")
```

In a production system, send the measurement to the application's metrics system instead of printing it.

The engineering principle is:

> Measure before making performance claims.

Connection reuse may reduce latency, but the magnitude depends on:

- network;
- server;
- TLS;
- connection lifetime;
- HTTP version;
- local environment;
- endpoint behavior.

---

# 40. Transport-Level Retries vs Application-Level Retries

This distinction is critical.

## Transport-level failures

Examples include:

- connection reset;
- connection refused;
- DNS/network failure;
- low-level transport failure.

These occur below the application's HTTP response semantics.

## Application-level failures

Examples include:

- HTTP 429;
- HTTP 500;
- HTTP 503;
- API-specific retry semantics.

These are responses or conditions interpreted by application reliability logic.

A useful architecture is:

```text
HTTP client transport
        ↓
application retry policy
        ↓
business/data ingestion logic
```

Do not mix these layers carelessly.

For example, a connection failure and a `429 Too Many Requests` response may require different handling and different evidence.

The complete retry/backoff system is deliberately deferred to the dedicated rate-limit/retry topic.

---

# 41. `urllib3.Retry` and Requests Adapters

Requests is built on top of urllib3, and adapters can customize transport behavior.

A common pattern uses `HTTPAdapter` with `urllib3.Retry`:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


retry = Retry(
    total=3,
    connect=3,
    read=3,
    backoff_factor=0.5,
    status_forcelist=(502, 503, 504),
    allowed_methods=frozenset({"GET", "HEAD"}),
)

adapter = HTTPAdapter(max_retries=retry)

with requests.Session() as session:
    session.mount("https://", adapter)

    response = session.get(
        "https://api.example.com/customers",
        timeout=(5, 30),
    )
    response.raise_for_status()
```

This illustrates where adapter-level transport behavior can be configured.

Important considerations:

- adapters exist as a transport integration point;
- retries must be deliberate;
- retrying every failure is unsafe;
- request method semantics matter;
- application-level status handling may still be necessary;
- retry budgets must be bounded.

This chapter establishes the architecture rather than duplicating the complete retry curriculum.

---

# 42. TLS Verification

TLS protects the connection between the client and server, but encryption alone is not enough.

The client must verify that the certificate is trusted for the intended server.

HTTPX verifies TLS certificates by default.

Explicitly:

```python
import httpx

client = httpx.Client(verify=True)
```

Certificate verification helps prevent the client from silently accepting an unintended endpoint.

---

# 43. `verify=` and Custom CA Bundles

Enterprise environments may use private certificate authorities.

HTTPX can be configured with a custom CA bundle:

```python
import httpx

client = httpx.Client(
    verify="/path/to/ca-bundle.pem",
)
```

This can be necessary when an organization's network infrastructure legitimately uses certificates signed by an internal CA.

Do **not** treat disabling verification as the normal solution.

Avoid:

```python
# UNSAFE DEFAULT FOR PRODUCTION
client = httpx.Client(verify=False)
```

If certificate verification fails, determine why:

```text
certificate problem?
        ↓
wrong CA trust?
        ↓
wrong hostname?
        ↓
proxy interception?
        ↓
server certificate problem?
```

Then fix the trust configuration.

---

# 44. Proxies

A proxy places an intermediary between the application and the destination:

```text
Application
    ↓
  Proxy
    ↓
Internet / API
```

Legitimate enterprise use cases include:

- corporate egress;
- security inspection;
- network routing;
- controlled outbound traffic.

Proxy configuration can affect:

- latency;
- connectivity;
- TLS behavior;
- authentication;
- debugging.

When debugging a failure, distinguish:

```text
application
   ↓
proxy
   ↓
external service
```

from:

```text
application
   ↓
external service
```

A failure may originate at the proxy rather than the target API.

Never log proxy credentials.

---

# 45. HTTP/2

HTTP/2 can improve API-client efficiency through mechanisms such as multiplexing multiple streams over a connection.

Conceptually:

```text
HTTP/1.1-style model

connection A → request 1
connection B → request 2
connection C → request 3
```

versus an HTTP/2 connection that can multiplex streams:

```text
HTTP/2 connection
 ├── stream 1 → request 1
 ├── stream 2 → request 2
 └── stream 3 → request 3
```

HTTPX can request HTTP/2 support:

```python
import httpx

client = httpx.Client(http2=True)
```

HTTP/2 is negotiated with the server; setting `http2=True` does not guarantee that every endpoint will actually use HTTP/2.

HTTP/2 can matter when:

- the server supports it;
- the workload has concurrent requests;
- connection efficiency matters;
- protocol negotiation succeeds.

This chapter focuses on the practical client implications rather than protocol engineering internals.

---

# 46. Production API Client Architecture

Bring the pieces together:

```text
                 ┌──────────────────────┐
                 │  Data Ingestion Job  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   CustomersClient    │
                 ├──────────────────────┤
                 │ base_url             │
                 │ headers              │
                 │ auth                 │
                 │ timeouts             │
                 │ connection pool      │
                 │ response validation  │
                 │ logging/metrics      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │       HTTPX         │
                 ├──────────────────────┤
                 │ transport            │
                 │ connection pool      │
                 │ TLS                  │
                 │ HTTP/2               │
                 └──────────┬───────────┘
                            │
                            ▼
                       External API
```

## Responsibilities

### Data ingestion job

Owns:

- business workflow;
- extraction strategy;
- downstream storage;
- pipeline-level state.

### API client

Owns:

- HTTP configuration;
- endpoint paths;
- response handling;
- HTTP-level errors;
- instrumentation;
- client lifecycle.

### HTTPX

Owns:

- transport;
- connections;
- streaming mechanics;
- TLS;
- HTTP protocol implementation.

This separation prevents business logic from becoming tightly coupled to network mechanics.

---

# 47. Complete `CustomersClient` Example

The following example combines the core ideas without turning the client into an unnecessarily large framework.

```python
from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

import httpx


logger = logging.getLogger(__name__)


def _request_started(request: httpx.Request) -> None:
    request.extensions["started_at"] = perf_counter()


def _response_received(response: httpx.Response) -> None:
    started_at = response.request.extensions.get("started_at")

    if started_at is None:
        return

    latency = perf_counter() - started_at

    logger.info(
        "http_request method=%s path=%s status=%s latency_seconds=%.3f",
        response.request.method,
        response.request.url.path,
        response.status_code,
        latency,
    )


class CustomersClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: httpx.Timeout,
        max_connections: int = 20,
        max_keepalive_connections: int = 10,
        user_agent: str = "customers-ingestion-client/1.0",
    ) -> None:
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )

        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            limits=limits,
            headers={
                "Accept": "application/json",
                "User-Agent": user_agent,
            },
            event_hooks={
                "request": [_request_started],
                "response": [_response_received],
            },
        )

    def __enter__(self) -> "CustomersClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        response = self._client.get(
            f"/customers/{customer_id}",
        )
        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" not in content_type:
            raise ValueError(
                f"Expected JSON, got {content_type!r}"
            )

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError(
                f"Expected object, got {type(data).__name__}"
            )

        return data

    def list_customers(
        self,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        response = self._client.get(
            "/customers",
            params={"limit": limit},
        )
        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" not in content_type:
            raise ValueError(
                f"Expected JSON, got {content_type!r}"
            )

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")

        customers = data.get("customers")

        if not isinstance(customers, list):
            raise ValueError(
                "Expected 'customers' to be a list"
            )

        return customers
```

Example usage:

```python
import httpx

timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=5.0,
)

with CustomersClient(
    base_url="https://api.example.com",
    timeout=timeout,
) as client:
    customer = client.get_customer("123")
    print(customer)
```

## Why this design is useful

The caller does not need to know:

- which headers are required;
- how timeouts are configured;
- how the connection pool is configured;
- how JSON is validated;
- how latency is recorded;
- how the client is closed.

That is infrastructure centralization.

---

# 48. Debugging Scenarios

## Scenario 1 — Requests hangs forever

### Bug

```python
# BAD EXAMPLE
import requests

requests.get(url)
```

### Diagnosis

The request has no explicit timeout.

### Fix

```python
response = requests.get(
    url,
    timeout=(5, 30),
)
```

Then determine whether the endpoint needs a different read timeout based on observed behavior.

---

## Scenario 2 — New client created inside every loop

### Bug

```python
# BAD EXAMPLE
for item in items:
    response = httpx.get(
        f"https://api.example.com/items/{item}"
    )
```

### Diagnosis

The code is using independent one-off requests rather than a deliberately reused client.

### Fix

```python
with httpx.Client(
    base_url="https://api.example.com",
) as client:
    for item in items:
        response = client.get(f"/items/{item}")
        response.raise_for_status()
```

The exact performance improvement should be measured rather than assumed.

---

## Scenario 3 — 2 GB download crashes memory

### Bug

```python
# BAD EXAMPLE
response = client.get(url)
data = response.content
```

### Diagnosis

The complete response is materialized in memory.

### Fix

```python
with client.stream("GET", url) as response:
    response.raise_for_status()

    for chunk in response.iter_bytes():
        output.write(chunk)
```

For production ingestion, combine this with a temporary file and atomic publication.

---

## Scenario 4 — API returns HTML instead of JSON

### Symptom

```python
data = response.json()
```

raises a JSON parsing error.

### Diagnosis

Inspect:

```python
print(response.status_code)
print(response.headers.get("content-type"))
print(response.text[:500])
```

In production logs, sanitize and limit body content. Do not blindly log entire responses because they may contain sensitive data.

Potential causes include:

- reverse proxy error;
- authentication gateway;
- upstream failure;
- wrong endpoint;
- unexpected content negotiation.

---

## Scenario 5 — Connection pool exhaustion

Suppose:

```text
workers = 50
max_connections = 5
```

Many workers may wait for connections.

Symptoms can include:

- high latency;
- pool timeout errors;
- low useful throughput despite many workers.

Debug:

1. measure concurrency;
2. inspect pool limits;
3. inspect pool timeout;
4. determine whether the upstream can tolerate the intended concurrency;
5. avoid solving every queueing problem by simply increasing connections.

---

## Scenario 6 — Secret appears in logs

Unsafe:

```python
logger.info("url=%s", request.url)
```

if the URL contains:

```text
?api_key=SECRET
```

Fix by logging a sanitized path or normalized URL:

```python
logger.info(
    "HTTP request method=%s path=%s",
    request.method,
    request.url.path,
)
```

And redact secret headers:

```text
Authorization: Bearer REDACTED
```

---

## Scenario 7 — TLS certificate failure

First classify the failure:

```text
TLS certificate error
       │
       ├── wrong CA trust?
       ├── wrong hostname?
       ├── expired certificate?
       ├── enterprise proxy interception?
       └── server certificate problem?
```

Do not immediately use:

```python
verify=False
```

Instead establish the actual trust-chain problem and configure the appropriate CA bundle if required.

---

# 49. Hands-On Lab — `api_client.py`

The roadmap requires a complete practical client. Keep the implementation in this Markdown file; the filename here is a lab label, not an instruction to create a separate Python file.

Build a `CustomersClient` that contains:

- `httpx.Client`;
- `base_url`;
- descriptive User-Agent;
- explicit timeout configuration;
- connection limits;
- request metrics;
- safe logging;
- response validation;
- streaming download support.

A compact lab target is:

```python
from pathlib import Path
import httpx


class CustomersClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: httpx.Timeout,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            limits=httpx.Limits(
                max_connections=20,
                max_keepalive_connections=10,
            ),
            headers={
                "Accept": "application/json",
                "User-Agent": "customers-ingestion-client/1.0",
            },
        )

    def close(self) -> None:
        self._client.close()

    def get_customer(self, customer_id: str) -> dict:
        response = self._client.get(
            f"/customers/{customer_id}"
        )
        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" not in content_type:
            raise ValueError("Expected JSON response")

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Expected JSON object")

        return data

    def download_export(
        self,
        url: str,
        destination: Path,
    ) -> None:
        download_file(
            self._client,
            url,
            destination,
        )
```

The exercise is to extend this client with:

1. request timing;
2. safe logging;
3. authentication placeholder;
4. event hooks;
5. tests;
6. controlled failure handling.

---

# 50. Required 2 GB Download Exercise

Implement:

```python
download_export(url, path)
```

Requirements:

- stream the response;
- bounded memory;
- temporary file;
- successful completion detection;
- atomic rename;
- cleanup on failure;
- timeout;
- `raise_for_status()`.

Reference implementation:

```python
from pathlib import Path
import os
import tempfile

import httpx


def download_export(
    client: httpx.Client,
    url: str,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None

    try:
        with client.stream("GET", url) as response:
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{path.name}.",
                suffix=".tmp",
                dir=path.parent,
                delete=False,
            ) as file:
                temporary_path = Path(file.name)

                for chunk in response.iter_bytes():
                    file.write(chunk)

                file.flush()
                os.fsync(file.fileno())

        os.replace(temporary_path, path)
        temporary_path = None

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
```

### Why each requirement exists

| Requirement | Reason |
|---|---|
| Stream | Avoid loading 2 GB into RAM |
| Bounded memory | Keep memory use independent of total file size |
| Temporary file | Hide incomplete output |
| Successful completion | Publish only after the stream finishes |
| Atomic rename | Make the completed file visible as one filesystem operation |
| Cleanup | Avoid accumulating failed partial files |
| Timeout | Avoid indefinite network waits |
| `raise_for_status()` | Do not save HTTP error bodies as files |

---

# 51. Required Unit Tests

The test suite should cover:

1. successful request;
2. timeout;
3. HTTP 500;
4. invalid JSON;
5. unexpected content type;
6. truncated download;
7. safe logging behavior where practical.

A test design matrix:

| Scenario | What it proves |
|---|---|
| Success | Normal parsing works |
| Timeout | Network failure is bounded and handled |
| HTTP 500 | Status errors are not silently accepted |
| Invalid JSON | Parsing failures are detected |
| Wrong content type | Content contract is validated |
| Truncated download | Incomplete output is not published |
| Secret logging | Sensitive data does not enter logs |

For a truncated-download test, the mocked stream should fail partway through iteration. The assertion should verify that the final destination does not appear as a successfully published file.

Illustrative failure-stream design:

```python
class FailingStream:
    def __iter__(self):
        yield b"first chunk"
        raise httpx.ReadError("connection lost")
```

The exact mocking mechanics depend on the test layer used. The important property is that the test exercises the application's failure path, not a real network connection.

---

# 52. Required Benchmark — 1,000 Requests

The roadmap requires a benchmark comparing:

```text
Approach A:
one-off request/client

versus

Approach B:
reused client/session
```

The benchmark should measure:

- total time;
- average latency;
- requests completed;
- errors.

A benchmark against a real HTTP endpoint can look like:

```python
from time import perf_counter

import httpx


URL = "https://api.example.com/health"
REQUEST_COUNT = 1_000


def benchmark_one_off() -> tuple[float, int]:
    completed = 0
    started = perf_counter()

    for _ in range(REQUEST_COUNT):
        try:
            response = httpx.get(
                URL,
                timeout=10.0,
            )
            response.raise_for_status()
            completed += 1
        except httpx.HTTPError:
            pass

    elapsed = perf_counter() - started
    return elapsed, completed


def benchmark_reused_client() -> tuple[float, int]:
    completed = 0
    started = perf_counter()

    with httpx.Client(timeout=10.0) as client:
        for _ in range(REQUEST_COUNT):
            try:
                response = client.get(URL)
                response.raise_for_status()
                completed += 1
            except httpx.HTTPError:
                pass

    elapsed = perf_counter() - started
    return elapsed, completed
```

Calculate:

```python
elapsed, completed = benchmark_reused_client()

average_latency = elapsed / completed if completed else float("nan")

print(f"total_seconds={elapsed:.3f}")
print(f"completed={completed}")
print(f"average_seconds={average_latency:.6f}")
```

### Important benchmark discipline

Do not fabricate results.

Benchmark outcomes depend on:

- network;
- server;
- TLS;
- connection reuse;
- HTTP version;
- local environment;
- endpoint behavior;
- rate limits;
- source-system load.

For a fair comparison:

- use the same endpoint;
- use the same request payload;
- use the same timeout policy;
- run the same number of requests;
- record failures;
- repeat the experiment;
- distinguish warm and cold conditions;
- avoid comparing one-off requests against a client under different external conditions.

The benchmark is evidence for **your workload**, not a universal statement about the libraries.

---

# 53. Production Checklist

## Client lifecycle

- [ ] Reuse client/session where repeated requests belong to the same lifecycle.
- [ ] Close the client correctly.

## Timeouts

- [ ] Connect timeout configured.
- [ ] Read timeout configured.
- [ ] Write timeout configured where relevant.
- [ ] Pool timeout configured.

## Reliability

- [ ] Correct status handling.
- [ ] Safe retry boundaries.
- [ ] Failure handling.

## Memory

- [ ] Large responses are streamed.
- [ ] Multi-GB payloads are not loaded entirely into RAM.

## Files

- [ ] Temporary download file.
- [ ] Atomic rename/publication.
- [ ] Temporary artifacts cleaned up after failure.

## Security

- [ ] TLS verification enabled.
- [ ] Secrets are not logged.
- [ ] User-Agent is safe and descriptive.
- [ ] Proxy credentials are protected.
- [ ] Custom CA bundles are used where legitimately required.

## Observability

- [ ] Request count.
- [ ] Latency.
- [ ] Status codes.
- [ ] Errors/timeouts.

## Testing

- [ ] Network is mocked for unit tests.
- [ ] Failure scenarios are tested.
- [ ] Malformed responses are tested.
- [ ] Logging behavior is tested where practical.

---

# 54. Common Mistakes

## 1. Creating a new client for every request

This prevents deliberate connection reuse and can add unnecessary resource overhead.

## 2. No timeout

An external service can consume a worker indefinitely.

## 3. Relying on default timeout behavior

Do not assume that a library's default behavior matches your pipeline's reliability requirements.

## 4. Loading huge responses into memory

`response.content` is dangerous for multi-GB payloads.

## 5. Writing directly to final filenames

A failed download can leave a file that looks complete.

## 6. Blindly calling `.json()`

The body may be HTML, malformed JSON, or another media type.

## 7. Assuming HTTP 200 means valid data

Status validation and payload validation are separate.

## 8. Ignoring content type

The body may not match the format your parser expects.

## 9. Leaking secrets in logs

Headers and URLs can contain credentials.

## 10. Incorrectly configuring connection pools

Too many connections can overload the source; too few can create queueing.

## 11. Forgetting to close clients

Client resources have a lifecycle.

## 12. Mixing transport retries with application retries

Different failure layers require different policies.

## 13. Disabling TLS verification casually

`verify=False` can remove an important security control.

## 14. Assuming HTTP/2 is always available

HTTP/2 requires successful negotiation and server support.

## 15. Testing only successful responses

Production failures are not limited to the happy path.

## 16. Benchmarking unrealistic workloads

A benchmark that does not represent the real endpoint, payload, concurrency, or environment can produce misleading conclusions.

---

# 55. Knowledge Check

Attempt these before reading the solutions.

## Basic

1. What is the difference between `httpx.get()` and `httpx.Client()`?
2. Why does connection reuse matter?
3. What is a timeout?
4. What does `raise_for_status()` do?
5. What does `response.json()` do?
6. What is the purpose of `base_url`?
7. What does `params=` do?
8. Why is a descriptive User-Agent useful?
9. Why should an HTTP client be closed?
10. What is the difference between `response.text` and `response.content`?

## Intermediate

1. Explain connect vs read timeout.
2. Why should large downloads be streamed?
3. Why use temporary files?
4. What does `httpx.Limits` control?
5. Why should response content type be checked?
6. What is pool timeout?
7. Why can an API return HTML even when the application expects JSON?
8. Why is `requests.get(url)` without an explicit timeout risky?
9. Why should API configuration be centralized in a client class?
10. What does `httpx.MockTransport` allow you to test?

## Advanced

1. Explain transport-level vs application-level retries.
2. Design an API client for 100,000 requests/day.
3. How would you debug connection pool exhaustion?
4. How would you instrument an HTTP client?
5. How would TLS verification interact with an enterprise proxy?
6. When would HTTP/2 materially matter?
7. How would you test an API client without network access?
8. How would you prevent a failed 10 GB download from appearing as a completed file?
9. How would you distinguish an API failure from a proxy failure?
10. What evidence would you collect before increasing connection-pool limits?

---

# 56. Knowledge Check — Concise Solutions

## Basic

1. `httpx.get()` performs a one-off request; `httpx.Client()` provides a reusable client with persistent configuration and connection-pool behavior.
2. Reuse can avoid repeated connection-establishment work and improve efficiency for repeated requests.
3. A timeout bounds how long the client is willing to wait for a particular network operation.
4. `raise_for_status()` raises an HTTP-related exception when the response indicates an error status.
5. `response.json()` parses the response body as JSON.
6. `base_url` centralizes the common API host/prefix.
7. `params=` constructs query parameters without manual URL-string concatenation.
8. It identifies the application to the upstream service and can help operators understand traffic.
9. The client owns resources such as network connections that must be released.
10. `text` is decoded textual content; `content` is the complete body as bytes.

## Intermediate

1. Connect timeout bounds connection establishment; read timeout bounds waiting for response data.
2. Streaming prevents the complete response from being held in memory.
3. Temporary files prevent incomplete output from being exposed under the final filename.
4. `httpx.Limits` controls connection-pool capacity and keep-alive capacity.
5. A successful status does not guarantee that the body matches the expected format.
6. Pool timeout bounds how long a request waits for an available connection.
7. A gateway, proxy, server, or authentication layer can return HTML instead of the expected API payload.
8. Without an explicit timeout, the request does not have the bounded waiting behavior expected in production.
9. Centralization prevents every caller from reimplementing HTTP configuration and error handling.
10. It lets tests replace real network transport with deterministic fake responses.

## Advanced

1. Transport retries concern lower-level connection failures; application retries reason about HTTP responses and API semantics such as `429` or `503`.
2. Define a reusable client, explicit timeouts, controlled pool limits, response validation, observability, authentication boundaries, testing, and an explicit failure/retry strategy.
3. Measure concurrency, pool limits, pool wait behavior, latency, and upstream capacity before changing configuration.
4. Record request count, status codes, latency, timeout/error counts, and safe endpoint identifiers while redacting secrets.
5. A proxy may legitimately terminate/re-establish TLS, so the client may need the enterprise CA bundle rather than disabled certificate verification.
6. HTTP/2 can matter when the server supports it and the workload benefits from multiplexed concurrent streams.
7. Use `MockTransport`, `respx`, `responses`, or sanitized recorded fixtures.
8. Stream into a temporary file and atomically publish the final filename only after successful completion.
9. Compare client-side connection/TLS behavior, proxy configuration, logs, and direct-vs-proxied connectivity where permitted.
10. Collect pool wait time, active concurrency, request latency, error rates, source-system limits, and resource utilization.

---

# 57. Interview Questions

Use these as architecture-level interview practice.

1. Why is a persistent HTTP client often more efficient than one-off requests?
2. What happens if you do not configure timeouts?
3. What are the four HTTPX timeout categories?
4. How would you download a 10 GB file safely?
5. What is a connection pool?
6. What causes pool timeout?
7. How would you design a reusable API client?
8. How would you test HTTP code without a real API?
9. What should never be logged?
10. What is the difference between transport and application retries?
11. How would you debug TLS failures?
12. What does HTTP/2 change for API clients?
13. How would you distinguish a slow API from pool contention?
14. Why is `response.raise_for_status()` not enough to validate an API response?
15. Why is atomic file publication useful in ingestion systems?
16. How would you benchmark a reused HTTP client against one-off requests fairly?
17. How would you design a client for a multi-worker containerized ingestion service?
18. When would you use a custom CA bundle?
19. What risks exist in recorded HTTP fixtures?
20. What evidence would justify changing connection limits?

For advanced questions, answer in this structure:

```text
Requirements
    ↓
Workload characteristics
    ↓
Failure modes
    ↓
Candidate design
    ↓
Measurements
    ↓
Operational constraints
    ↓
Trade-offs
    ↓
Decision
```

Do not answer only with library definitions.

---

# 58. Mini Production Design Exercise

Design:

> A Python ingestion service that calls an external SaaS API 100,000 times per day.

## Constraints

- API occasionally hangs;
- responses can be large;
- API uses JSON;
- network is unreliable;
- API requires authentication;
- production runs inside containers;
- multiple workers may execute;
- logs are centralized;
- failures must be observable.

## Decide

### Client architecture

Would you use:

```text
one client per request
```

or:

```text
one reusable client per appropriate worker/job lifecycle
```

Explain the lifecycle and why.

### Timeout configuration

Decide:

- connect timeout;
- read timeout;
- write timeout;
- pool timeout.

Do not choose numbers without explaining the workload assumptions.

### Connection pool

Decide:

- maximum connections;
- keep-alive connections;
- expected concurrency;
- interaction with multiple workers.

### Streaming

Determine which responses should be streamed and how large files should be published safely.

### Logging

Specify:

- what gets logged;
- what is redacted;
- how URLs are sanitized;
- how request identifiers are handled.

### Metrics

At minimum consider:

- request count;
- latency;
- status codes;
- timeout count;
- error count.

### Testing

Design tests for:

- success;
- 500;
- timeout;
- invalid JSON;
- wrong content type;
- truncated download;
- secret redaction.

### TLS

Decide how certificate verification is managed in the production environment.

### Retry boundary

Describe:

```text
transport failure
       ↓
transport/client handling
       ↓
application retry policy
       ↓
ingestion workflow
```

Do not prescribe a single perfect architecture. The correct design depends on the endpoint, workload, infrastructure, source-system behavior, and operational requirements.

---

# 59. Final Mental Model

```text
Production HTTP Client
        │
        ├── Reuse connections
        ├── Configure explicit timeouts
        ├── Control connection pools
        ├── Stream large payloads
        ├── Validate responses
        ├── Write files atomically
        ├── Keep secrets out of logs
        ├── Instrument requests
        ├── Test without the network
        ├── Separate transport from application retries
        ├── Verify TLS
        └── Understand HTTP/2 and proxies
```

A production HTTP client is not merely a function that sends a request.

It is a **controlled boundary between your data pipeline and an unreliable external system**.

That boundary should make uncertainty explicit:

```text
external network
      ↓
bounded waiting
      ↓
controlled connections
      ↓
validated response
      ↓
safe parsing/storage
      ↓
observable outcome
```

---

# 60. Completion Checklist

Before considering this topic complete:

- [ ] I can explain why reusable clients are preferable to one-off requests.
- [ ] I can use both `httpx` and `requests`.
- [ ] I can configure `base_url`, headers, parameters, and JSON bodies.
- [ ] I understand `raise_for_status()`.
- [ ] I understand all four HTTPX timeout categories.
- [ ] I know why Requests requires explicit timeout configuration.
- [ ] I can stream large downloads without loading them into memory.
- [ ] I can safely write downloads using temporary files and atomic rename.
- [ ] I can handle invalid JSON and unexpected response bodies.
- [ ] I understand connection-pool limits.
- [ ] I can design a reusable API client class.
- [ ] I can test HTTPX without real network calls.
- [ ] I understand `MockTransport`, `respx`, and `responses`.
- [ ] I can instrument request count, latency, and status codes.
- [ ] I understand secret redaction.
- [ ] I can distinguish transport-level and application-level retries.
- [ ] I understand `urllib3.Retry` and Requests adapters.
- [ ] I understand TLS verification and custom CA bundles.
- [ ] I understand proxy configuration.
- [ ] I understand HTTP/2 at a practical level.
- [ ] I can benchmark one-off requests against a reused client.
- [ ] I can explain how I would productionize an HTTP ingestion client.

---

# Appendix A — Compact Reference

## HTTPX reusable client

```python
import httpx

timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=5.0,
)

limits = httpx.Limits(
    max_connections=20,
    max_keepalive_connections=10,
)

with httpx.Client(
    base_url="https://api.example.com",
    headers={
        "Accept": "application/json",
        "User-Agent": "my-ingestion-client/1.0",
    },
    timeout=timeout,
    limits=limits,
) as client:
    response = client.get(
        "/customers",
        params={"limit": 100},
    )

    response.raise_for_status()
    data = response.json()
```

## Requests reusable session

```python
import requests

with requests.Session() as session:
    response = session.get(
        "https://api.example.com/customers",
        timeout=(5, 30),
        params={"limit": 100},
        headers={
            "Accept": "application/json",
            "User-Agent": "my-ingestion-client/1.0",
        },
    )

    response.raise_for_status()
    data = response.json()
```

## HTTPX streaming

```python
with client.stream("GET", url) as response:
    response.raise_for_status()

    for chunk in response.iter_bytes():
        destination.write(chunk)
```

## HTTPX HTTP/2

```python
client = httpx.Client(http2=True)
```

## HTTPX custom CA bundle

```python
client = httpx.Client(
    verify="/path/to/ca-bundle.pem",
)
```

---

# Appendix B — Failure-Handling Matrix

| Failure | Layer | Typical diagnostic | Design concern |
|---|---|---|---|
| Connection refused | Transport | Connection exception | Connectivity/service availability |
| DNS failure | Transport/network | Name-resolution failure | DNS/network configuration |
| TLS verification failure | TLS | Certificate/verification exception | CA trust, hostname, proxy |
| Read timeout | Transport/client | Read timeout exception | Endpoint responsiveness |
| Pool timeout | Client resource | Pool timeout exception | Concurrency/pool sizing |
| HTTP 429 | Application/API | Status code + headers | API quota/rate policy |
| HTTP 500 | Application/API | Status code | Server failure |
| HTML instead of JSON | Payload | Content type/body | Gateway/proxy/API behavior |
| Invalid JSON | Payload | JSON parse exception | Malformed response |
| Truncated file | Payload/storage | Stream failure/incomplete transfer | Temporary-file publication |
| Secret in logs | Security | Log inspection | Redaction design |

---

# Appendix C — Engineering Review Questions

When reviewing an HTTP ingestion client, ask:

### Lifecycle

- Is the client reused?
- Is the lifecycle explicit?
- Is it closed correctly?

### Timeouts

- Are all relevant timeout dimensions bounded?
- Are values justified by endpoint behavior?
- Could a timeout be too short for legitimate large responses?
- Could a timeout be so long that failures consume workers unnecessarily?

### Memory

- Are large responses streamed?
- Could a response unexpectedly become multi-GB?
- Is the download path bounded in memory?

### Files

- Is the final filename protected from partial writes?
- Is publication atomic?
- Are failed temporary files cleaned up?

### Validation

- Are HTTP errors detected?
- Is content type validated?
- Is JSON parsing protected?
- Is the expected response structure checked?

### Pooling

- Is connection capacity aligned with worker concurrency?
- Could too many connections overload the source?
- Is pool waiting observable?

### Security

- Are TLS certificates verified?
- Are custom CA bundles handled correctly?
- Are secrets absent from logs?
- Are proxy credentials protected?

### Observability

- Can operators see request latency?
- Can they distinguish timeout from HTTP error?
- Are status-code distributions measurable?
- Can a failing endpoint be identified without exposing secrets?

### Testing

- Can the client be tested without the network?
- Are timeout and 500 cases tested?
- Are malformed responses tested?
- Are downloads tested for failure and atomicity?

### Reliability boundaries

- Is transport failure separated from application retry policy?
- Are retries bounded?
- Are retryable conditions explicit?
- Is the upstream API's behavior respected?

---

# Closing Principle

The HTTP client is one of the first reliability boundaries in an ingestion system.

A strong data engineer does not stop at:

```python
response = requests.get(url)
```

or:

```python
response = client.get(url)
```

The production question is:

```text
How will this client behave when the network is slow,
the server hangs, the response is malformed, the payload is huge,
the pool is exhausted, the certificate is unexpected,
the proxy changes behavior, or the API returns an error?
```

Design the client so those conditions are bounded, observable, testable, and recoverable.
