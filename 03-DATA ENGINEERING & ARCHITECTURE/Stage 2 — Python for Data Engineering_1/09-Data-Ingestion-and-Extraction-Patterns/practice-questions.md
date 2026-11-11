# Practice Questions — Data Ingestion and Extraction Patterns

This document contains exactly **40 practice questions** covering the progression of the Data Ingestion and Extraction Patterns module.

The practice set follows the supplied module specification and reinforces the production principles taught across HTTP extraction, reusable HTTP clients, authentication, pagination, rate limiting, incremental extraction, CDC, webhooks, HTML extraction, SFTP/file drops, and ingestion frameworks.

> **Source-of-truth note:** The supplied roadmap requires the existing learning files to be the authoritative source. In this workspace, the roadmap and the available completed pagination/webhook source material were inspectable; the remaining named module files were not mounted. Questions therefore stay within the concepts explicitly specified by the roadmap and available source material rather than inventing unrelated material.

## How to Use This Document

- There are exactly **40 questions**.
- Questions 1–10 are **Basic**.
- Questions 11–20 are **Moderate**.
- Questions 21–30 are **Hard**.
- Questions 31–40 are **Advanced**.
- Each problem is immediately followed by its solution.
- Try to solve the problem before reading the solution.
- Treat the solutions as engineering explanations, not merely answer keys.
- Pay particular attention to correctness, completeness, state, idempotency, resumability, security, observability, and recovery.

---

# Part I — Basic

## Question 1 — Build a Correct HTTP Extraction Request

### Problem

An API exposes customer records at:

```text
https://api.example.com/v1/customers
```

The endpoint expects:

- a `GET` request,
- a query parameter named `limit`,
- a query parameter named `status`,
- a bearer token in the `Authorization` header.

You need the first 100 active customers.

### What You Need to Do

Describe the request you would construct and identify the purpose of:

1. the URL,
2. query parameters,
3. the authentication header,
4. the response body,
5. the HTTP status code.

Do not put the token directly into source code.

### Solution

A request can conceptually be represented as:

```text
GET https://api.example.com/v1/customers?limit=100&status=active
Authorization: Bearer <ACCESS_TOKEN>
```

In Python with `httpx`:

```python
import os
import httpx

token = os.environ["API_ACCESS_TOKEN"]

response = httpx.get(
    "https://api.example.com/v1/customers",
    params={"limit": 100, "status": "active"},
    headers={"Authorization": f"Bearer {token}"},
    timeout=30.0,
)

response.raise_for_status()
data = response.json()
```

### How the Solution Works

The URL identifies the resource. Query parameters modify the extraction request without changing the resource path.

The `Authorization` header carries the bearer token. The token belongs in an environment variable or another secure secret mechanism rather than being hard-coded.

The response contains the returned records in its body. The HTTP status code describes the outcome of the request. Calling `raise_for_status()` prevents successful-looking code from silently processing an error response.

The important extraction pattern is:

```text
construct request
      ↓
send request
      ↓
inspect status
      ↓
interpret content type/body
      ↓
extract records
```

### Key Takeaways

- Query parameters belong in the request parameters rather than being manually concatenated when the client supports structured parameters.
- Authentication belongs in the appropriate header.
- Never hard-code credentials.
- Do not process the response body before establishing that the response is acceptable.
- HTTP status and response body are both important when debugging extraction failures.

---

## Question 2 — Choose a Reusable HTTP Client

### Problem

A pipeline makes 500 requests to the same API. A beginner implementation creates a completely independent HTTP request for every page.

The pipeline also needs explicit timeouts and consistent headers.

### What You Need to Do

Explain why a reusable `httpx.Client` or `requests.Session` is preferable to repeatedly creating one-off requests.

### Solution

Use a reusable client/session:

```python
import os
import httpx

token = os.environ["API_ACCESS_TOKEN"]

with httpx.Client(
    headers={"Authorization": f"Bearer {token}"},
    timeout=30.0,
) as client:
    for page in range(1, 501):
        response = client.get(
            "https://api.example.com/v1/customers",
            params={"page": page, "limit": 100},
        )
        response.raise_for_status()
        records = response.json()
        # Process records.
```

### How the Solution Works

A reusable client gives the extraction code one place to configure common behavior.

It can reuse connections through connection pooling instead of treating every request as a completely independent operation. It also gives the application an explicit client lifecycle.

The same principle applies to `requests.Session`:

```python
import requests

with requests.Session() as session:
    session.headers.update(
        {"Authorization": f"Bearer {token}"}
    )

    response = session.get(
        "https://api.example.com/v1/customers",
        timeout=30,
    )
```

The exact API differs between `httpx` and `requests`, but the production idea is the same: configure a reusable client and define explicit request behavior.

### Key Takeaways

- Reusable clients reduce repeated configuration.
- Connection reuse can make repeated extraction more efficient.
- Explicit timeouts prevent requests from waiting indefinitely.
- Client lifecycle should be deliberate rather than accidental.
- The choice between `httpx` and `requests` should follow the library and execution model taught for the application, not arbitrary preference.

---

## Question 3 — Diagnose an Authentication Failure

### Problem

An extraction job receives:

```text
401 Unauthorized
```

The developer says:

> "The API is down because the request failed."

The request uses a bearer token.

### What You Need to Do

Explain what you would check before concluding that the source is unavailable.

### Solution

First verify authentication-related causes:

1. Is the `Authorization` header present?
2. Is its format correct?
3. Is the token expired?
4. Is the token intended for this API?
5. Is the required authentication scheme actually bearer authentication?
6. Did the secret get truncated or changed?
7. Is the application accidentally logging or loading an old token?
8. If OAuth is used, can the access token be refreshed?

A generic bearer request should resemble:

```python
headers = {
    "Authorization": f"Bearer {access_token}",
}
```

Secrets should come from a secure source such as an environment variable:

```python
access_token = os.environ["API_ACCESS_TOKEN"]
```

### How the Solution Works

A `401` is not equivalent to "the source is down." Authentication failure is one possible interpretation and should be investigated before changing networking or retry behavior.

For OAuth, the access token may be short-lived while a refresh token can be used to obtain another access token. A production extractor therefore needs to understand token expiry and refresh behavior.

The key debugging sequence is:

```text
request failure
    ↓
inspect status code
    ↓
identify failure class
    ↓
check authentication state
    ↓
refresh/reconfigure only when appropriate
```

### Key Takeaways

- Status codes are diagnostic information.
- Authentication failures should not automatically be retried forever.
- Access-token expiry is different from permanent credential failure.
- Secrets must not be exposed in logs or source code.

---

## Question 4 — Distinguish Offset and Cursor Pagination

### Problem

API A returns:

```json
{
  "items": [...],
  "page": 1,
  "total_pages": 20
}
```

API B returns:

```json
{
  "items": [...],
  "next_cursor": "abc123"
}
```

### What You Need to Do

Identify the pagination style of each API and explain how the extraction loop differs.

### Solution

API A uses page-number pagination. The extractor can request:

```text
page=1
page=2
page=3
...
```

API B uses cursor/token pagination. The extractor must use the server-provided cursor:

```text
initial request
    ↓
receive next_cursor
    ↓
send cursor
    ↓
receive next_cursor
    ↓
repeat until no next cursor
```

A cursor-based loop conceptually looks like:

```python
cursor = None

while True:
    params = {"limit": 100}
    if cursor is not None:
        params["cursor"] = cursor

    response = client.get(url, params=params)
    response.raise_for_status()

    payload = response.json()
    process(payload["items"])

    cursor = payload.get("next_cursor")
    if not cursor:
        break
```

### How the Solution Works

Page-number pagination tells the client which page to request.

Cursor pagination tells the client how to continue from the current position according to server-managed pagination state.

These strategies should not be treated as interchangeable because their consistency and failure characteristics can differ.

### Key Takeaways

- Offset/page-number pagination uses a position such as page or offset.
- Cursor pagination uses a continuation token supplied by the source.
- Stopping conditions must be explicit.
- Cursor pagination should not invent its own cursor values.

---

## Question 5 — Handle HTTP 429 Correctly

### Problem

An API extraction receives:

```text
429 Too Many Requests
Retry-After: 20
```

The developer immediately retries the request in a tight loop.

### What You Need to Do

Explain why this is incorrect and describe the safer behavior.

### Solution

A `429` indicates that the source is applying rate limiting. If `Retry-After` is supplied, the extractor should respect it rather than immediately retrying.

Conceptually:

```text
receive 429
    ↓
read Retry-After
    ↓
wait
    ↓
retry if the operation is retryable
```

The extractor should also avoid creating a retry storm across concurrent workers.

### How the Solution Works

Immediate retries increase request pressure precisely when the source is asking the client to reduce pressure.

A production extractor should distinguish retryable failures from non-retryable failures and use controlled backoff. It should also measure retry counts and throttling behavior so operators can understand whether the extraction is operating too aggressively.

### Key Takeaways

- `429` is a rate-limit signal.
- `Retry-After` is actionable information.
- Backoff protects both the source and the extractor.
- Pagination can amplify rate-limit pressure because every page becomes another request.
- Retry behavior must be bounded and observable.

---

## Question 6 — Select Full or Incremental Extraction

### Problem

A source contains 50 million customer records. The source exposes a reliable `updated_at` field and supports filtering records by update time.

A job needs to run every hour.

### What You Need to Do

Choose between full and incremental extraction and explain why.

### Solution

Use incremental extraction based on a durable watermark such as `updated_at`.

The conceptual state is:

```text
last_successful_watermark
        ↓
extract records after/bounded around watermark
        ↓
process and validate
        ↓
advance watermark only after successful processing
```

For example:

```text
previous watermark = 2026-10-01T10:00:00Z

extract:
updated_at >= 2026-10-01T10:00:00Z
and
updated_at <  2026-10-01T11:00:00Z
```

A small boundary overlap may be used when the source can have late commits or timestamp precision limitations, with downstream idempotency handling duplicates.

### How the Solution Works

A full extraction repeatedly scans the entire dataset. That can be unnecessarily expensive when the source provides a reliable incremental contract.

Incremental extraction reduces the amount of data that must be read, but it introduces state-management responsibilities. The watermark must not advance merely because the request succeeded; the extracted interval must be successfully handled according to the pipeline's correctness contract.

### Key Takeaways

- Incremental extraction is a stateful process.
- A watermark represents progress, not merely a filter value.
- Late-arriving records can make a naïve `>` watermark unsafe.
- Boundary overlap and idempotency can protect against timestamp-boundary gaps.

---

## Question 7 — Identify a CDC Change Event

### Problem

A database change stream produces:

```text
operation = UPDATE
key = 42
old_value = {"status": "pending"}
new_value = {"status": "paid"}
position = 918273
```

### What You Need to Do

Explain what this event represents and why the position is important for restartability.

### Solution

The event represents an update to the record identified by key `42`.

The change position, represented here as `918273`, gives the consumer a durable location in the source change stream. After a crash, the consumer can resume from an appropriate position rather than beginning from the beginning of the stream.

### How the Solution Works

CDC captures changes rather than repeatedly asking the source:

> "Which rows look different now?"

A production CDC process typically has:

```text
initial snapshot
      ↓
ongoing change stream
      ↓
persisted position/state
      ↓
restart from durable position
```

The exact position terminology depends on the source. For PostgreSQL logical replication, WAL/LSN concepts can provide this position.

### Key Takeaways

- CDC represents changes such as inserts, updates, and deletes.
- A durable position supports restart/resume.
- Initial snapshot and ongoing CDC solve different phases of ingestion.
- Replay is a normal recovery mechanism, not necessarily a failure of the architecture.

---

## Question 8 — Make a Webhook Receiver Reliable

### Problem

A webhook provider sends an HTTP `POST` containing an event.

The receiver currently:

1. receives the request,
2. performs a database update,
3. calls another API,
4. writes an audit record,
5. finally returns `200`.

Sometimes the provider sends the same event twice.

### What You Need to Do

Explain how to redesign the receiver's basic flow.

### Solution

The receiver should acknowledge quickly after validating what must be validated synchronously, persist the event or otherwise establish durable receipt, and perform expensive processing asynchronously.

A production-oriented flow is:

```text
Webhook POST
    ↓
authenticate / verify signature
    ↓
check basic validity
    ↓
durably land event
    ↓
return 2xx quickly
    ↓
asynchronous processing
    ↓
idempotent application
```

The event should have a stable event ID or equivalent deduplication key.

### How the Solution Works

Webhook providers commonly retry when they do not receive an acceptable response quickly. If the receiver spends too long processing the event, a retry can create duplicate delivery.

At-least-once delivery means duplicate events must be expected. The downstream processing therefore needs idempotency rather than assuming each event arrives exactly once.

### Key Takeaways

- Fast acknowledgement reduces unnecessary provider retries.
- Webhooks should be treated as at-least-once delivery unless the source contract guarantees otherwise.
- Durable event landing creates a recovery point.
- Event IDs are useful for deduplication.

---

## Question 9 — Detect an Incomplete SFTP File

### Problem

An SFTP directory contains:

```text
customers_2026-10-01.csv
```

A job sees the filename and immediately begins processing it. The producer is still uploading the file.

### What You Need to Do

Explain why this is dangerous and name two completeness mechanisms from the module scope.

### Solution

The job can read a partially written file and ingest incomplete data.

Two appropriate completeness mechanisms are:

1. a `.done` marker,
2. a manifest/checksum-based contract.

For example:

```text
customers_2026-10-01.csv
customers_2026-10-01.csv.done
```

The consumer processes the data only after the expected completion signal appears.

A manifest can additionally describe expected files and their checksums.

### How the Solution Works

The presence of a filename does not necessarily mean the producer has finished writing the bytes.

The ingestion contract should define how a consumer determines that a file is complete. This is part of the source contract, not something the consumer should guess.

### Key Takeaways

- A visible file is not automatically a complete file.
- Completion markers and manifests provide explicit state.
- Checksums can validate content integrity.
- File ingestion should be idempotent and restartable.

---

## Question 10 — Recognize the Role of an Ingestion Framework

### Problem

A team has several ordinary API sources. Each source requires authentication, pagination, state management, schema handling, retries, and operational monitoring.

The team is considering `dlt` or a managed connector.

### What You Need to Do

Explain what an ingestion framework can provide and one reason custom extraction code may still be necessary.

### Solution

A framework can provide reusable abstractions for common ingestion concerns such as:

- pagination,
- state,
- schema handling,
- loading,
- operational patterns.

A managed connector can reduce the amount of infrastructure and maintenance the team must own when the source is well supported.

Custom code may still be necessary when a source has unusual behavior, source-specific transformation requirements, unsupported authentication, special pagination, or a requirement the framework cannot express cleanly.

### How the Solution Works

The decision is not simply:

```text
framework = good
custom code = bad
```

Instead:

```text
source requirements
      ↓
connector/framework coverage
      ↓
customization required?
      ↓
operational burden
      ↓
total engineering cost
```

### Key Takeaways

- Frameworks reduce repeated engineering work.
- Managed connectors can reduce operational burden.
- Source coverage and customization requirements matter.
- Build-vs-buy decisions should consider reliability, maintenance, observability, and total engineering cost.

---

# Part II — Moderate

## Question 11 — Combine Authentication, Pagination, and Timeouts

### Problem

An API uses bearer authentication and cursor pagination. Your current code makes requests without a timeout and stops after the first page.

### What You Need to Do

Complete the extraction pattern so that it:

1. uses a reusable client,
2. sends the bearer token,
3. uses an explicit timeout,
4. follows cursors,
5. stops when no cursor remains.

### Solution

```python
import os
import httpx

url = "https://api.example.com/v1/orders"
token = os.environ["API_ACCESS_TOKEN"]

with httpx.Client(
    headers={"Authorization": f"Bearer {token}"},
    timeout=30.0,
) as client:
    cursor = None

    while True:
        params = {"limit": 100}

        if cursor:
            params["cursor"] = cursor

        response = client.get(url, params=params)
        response.raise_for_status()

        payload = response.json()

        for record in payload["items"]:
            process(record)

        next_cursor = payload.get("next_cursor")
        if not next_cursor:
            break

        cursor = next_cursor
```

### How the Solution Works

The reusable client centralizes authentication and timeout configuration.

The cursor is initially absent. After each successful page, the source supplies the continuation cursor. The extractor uses that cursor for the next request.

The stopping condition is based on the source's pagination contract rather than an arbitrary page count.

### Key Takeaways

The important combined pattern is:

```text
client lifecycle
+ authentication
+ explicit timeout
+ source-provided cursor
+ explicit stopping condition
```

The code is still incomplete as a production extractor because rate limiting, checkpointing, deduplication, observability, and recovery may also be required.

---

## Question 12 — Fix a Cursor Pagination Loop

### Problem

The following extractor sometimes loops forever:

```python
cursor = None

while cursor != "":
    response = client.get(url, params={"cursor": cursor})
    payload = response.json()

    process(payload["items"])
    cursor = payload.get("next_cursor", "")
```

The source occasionally returns the same cursor twice.

### What You Need to Do

Diagnose the problem and provide a guard.

### Solution

Track previously seen cursors:

```python
cursor = None
seen_cursors = set()

while True:
    if cursor is not None:
        if cursor in seen_cursors:
            raise RuntimeError(
                f"Cursor loop detected: {cursor!r}"
            )
        seen_cursors.add(cursor)

    params = {"limit": 100}
    if cursor is not None:
        params["cursor"] = cursor

    response = client.get(url, params=params)
    response.raise_for_status()

    payload = response.json()
    process(payload["items"])

    next_cursor = payload.get("next_cursor")

    if not next_cursor:
        break

    cursor = next_cursor
```

### How the Solution Works

The original loop assumes that every returned cursor moves progress forward.

That assumption is unsafe. A buggy or unstable source can return the same continuation token repeatedly.

Loop detection converts silent infinite execution into an explicit failure that can be investigated.

A production implementation should also checkpoint progress where appropriate so that a crash does not require restarting from the beginning.

### Key Takeaways

- Pagination guards protect the extractor from source anomalies.
- A cursor is not automatically proof of forward progress.
- Loop detection is different from the normal stopping condition.
- Explicit failure is safer than an infinite extraction loop.

---

## Question 13 — Handle Pagination Plus Rate Limiting

### Problem

A 100-page extraction repeatedly receives `429` responses around page 60. The current retry logic performs five immediate retries.

### What You Need to Do

Redesign the behavior so that the extractor respects the source and still resumes pagination correctly.

### Solution

The extractor should:

1. identify `429` as retryable,
2. inspect `Retry-After` when provided,
3. wait before retrying,
4. use controlled backoff where appropriate,
5. avoid restarting the entire extraction,
6. keep the current page/cursor state,
7. record retry metrics,
8. stop after a bounded retry policy if the source remains unavailable.

Conceptually:

```python
for attempt in range(max_attempts):
    response = client.get(url, params=params)

    if response.status_code != 429:
        response.raise_for_status()
        break

    retry_after = response.headers.get("Retry-After")
    wait_seconds = parse_retry_after(retry_after, attempt)
    time.sleep(wait_seconds)
else:
    raise RuntimeError("Retry budget exhausted")
```

### How the Solution Works

The page or cursor represents extraction progress. A temporary throttling response should not erase that state.

The extractor should retry the failed request, not restart from page one.

Retry behavior must also avoid synchronized retry storms. Measuring retries allows operators to detect whether the configured extraction rate is consistently too aggressive.

### Key Takeaways

- Rate limiting and pagination interact.
- Preserve progress while retrying a throttled request.
- Respect `Retry-After`.
- Bound retries.
- Observe retry behavior rather than hiding it.

---

## Question 14 — Protect a Watermark From a Failed Run

### Problem

A job extracts records from:

```text
10:00:00 <= updated_at < 11:00:00
```

It successfully downloads the records, but crashes while loading them downstream.

The implementation had already changed the stored watermark to `11:00:00`.

### What You Need to Do

Explain the correctness problem and redesign the state transition.

### Solution

The watermark was advanced too early.

The safer sequence is:

```text
read previous watermark
      ↓
extract bounded interval
      ↓
land/process data
      ↓
validate successful completion
      ↓
commit/record successful state
      ↓
advance watermark
```

If the load fails, the watermark should remain at the previous safe point so the interval can be rerun.

Idempotent downstream processing or raw landing makes the rerun safe.

### How the Solution Works

A watermark is a statement of durable progress. If the state says that an interval was successfully processed when it was not, the next run can skip data permanently.

This is a classic failure between data processing and state update.

### Key Takeaways

- Watermark advancement is part of the correctness protocol.
- "Request succeeded" is not the same as "ingestion succeeded."
- Rerunnable windows require idempotency.
- Durable state should represent confirmed progress.

---

## Question 15 — OAuth Token Expiration During Pagination

### Problem

A cursor-based extraction has processed 40 pages. The access token expires while requesting page 41.

### What You Need to Do

Explain how the extractor should respond without losing its position or exposing credentials.

### Solution

The extractor should:

1. detect the authentication failure,
2. determine whether the access token is expired,
3. use the refresh-token flow if the source contract supports it,
4. obtain a new access token,
5. retry the failed page/cursor,
6. keep the existing cursor/checkpoint,
7. avoid logging the access or refresh token.

The state should remain conceptually:

```text
last successful cursor = cursor_for_page_40
```

The token changes; extraction progress does not.

### How the Solution Works

Authentication state and extraction state are separate concerns.

Refreshing a token should not reset pagination. The failed request can be retried using the same cursor after successful authentication refresh.

A production implementation should also avoid multiple workers independently refreshing the same credential without coordination when that can create token-refresh races.

### Key Takeaways

- Token refresh should preserve extraction progress.
- Authentication state and pagination state should be modeled separately.
- Never log token values.
- A token-expiry failure is not a reason to restart the whole extraction.

---

## Question 16 — Scrape Only What You Need

### Problem

A public page contains product names, prices, images, advertisements, navigation, reviews, and unrelated content.

Your ingestion requirement is only:

```text
product_name
price
```

### What You Need to Do

Describe a responsible extraction approach using an HTML parser.

### Solution

Use an HTML parser such as BeautifulSoup to select only the required structured elements.

Conceptually:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")

for card in soup.select(".product-card"):
    name = card.select_one(".product-name")
    price = card.select_one(".price")

    if name and price:
        emit({
            "product_name": name.get_text(strip=True),
            "price": price.get_text(strip=True),
        })
```

The exact selectors must match the source HTML.

### How the Solution Works

The parser converts the HTML document into a structure that can be queried.

A responsible scraper should minimize unnecessary work and unnecessary source load. It should respect applicable source rules such as terms of use and robots guidance where relevant, apply rate limiting, and validate extracted values.

### Key Takeaways

- Extract only the required information.
- HTML selectors are source-dependent.
- Source changes can break selectors.
- Responsible scraping includes source politeness and validation.
- This is an extraction problem, not a generic web-development problem.

---

## Question 17 — Detect an Incomplete File With a Manifest

### Problem

A vendor sends:

```text
orders_2026-10-01.csv
orders_2026-10-01.sha256
```

The checksum does not match the downloaded file.

### What You Need to Do

Explain whether the ingestion should continue and what recovery steps should occur.

### Solution

Do not process the file as trusted input.

The checksum mismatch indicates that the bytes received do not match the expected artifact.

The ingestion process should:

1. record the mismatch,
2. quarantine or otherwise avoid processing the invalid file,
3. retry/retrieve again according to the source contract,
4. escalate if repeated retrievals fail,
5. preserve enough metadata to diagnose the event.

### How the Solution Works

A checksum provides a content-integrity check.

It does not by itself prove that the file contains semantically correct data, but a mismatch means the expected byte-level artifact was not received.

The source contract should define whether the file can be safely re-downloaded or whether the producer must resend it.

### Key Takeaways

- Do not ingest a file that fails its integrity contract.
- Checksums support safe file-drop ingestion.
- Recovery should be explicit and observable.
- File identity and processing state should be tracked.

---

## Question 18 — Duplicate Webhook Events

### Problem

The same event arrives twice:

```text
event_id = evt_123
```

The first copy successfully updates an order to `paid`. The second copy arrives five seconds later.

### What You Need to Do

Design an idempotency strategy.

### Solution

Use the event ID as a durable deduplication key.

Conceptually:

```text
receive evt_123
    ↓
verify event
    ↓
check event_id
    ↓
if already processed:
    acknowledge safely
else:
    record/process event
```

A durable event registry can contain:

```text
event_id
received_at
processing_status
processed_at
```

The important property is that the check and the state transition are safe against concurrent duplicate deliveries.

### How the Solution Works

At-least-once delivery means duplicate delivery is expected.

Without deduplication, a side effect could occur twice. The event ID gives the system an identity for the delivery.

For robust processing, deduplication state should survive process restarts.

### Key Takeaways

- Duplicate events are normal in reliable webhook systems.
- Event identity should be durable.
- Idempotency is a correctness mechanism.
- Acknowledgement should not imply that duplicate business effects are executed.

---

## Question 19 — Diagnose a Webhook Signature Mismatch

### Problem

A webhook provider signs the exact raw HTTP request body.

Your application does:

```python
payload = await request.json()
body = json.dumps(payload).encode()
signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
```

The provider's signature does not match.

### What You Need to Do

Identify the likely problem and explain the correct verification approach.

### Solution

The likely problem is that the application parsed and re-serialized the JSON before verifying the signature.

Signature verification should use the original raw request bytes:

```python
body = await request.body()

expected = hmac.new(
    secret,
    body,
    hashlib.sha256,
).hexdigest()

if not hmac.compare_digest(expected, received_signature):
    raise HTTPException(status_code=401)
```

The exact signature encoding must follow the provider's contract.

### How the Solution Works

Cryptographic signatures operate over bytes.

Even semantically equivalent JSON can have different byte representations due to whitespace, ordering, escaping, or serialization choices.

The safe sequence is:

```text
raw request body
      ↓
HMAC calculation
      ↓
constant-time comparison
      ↓
only then parse/process payload
```

### Key Takeaways

- Verify what the provider actually signed.
- Do not reconstruct signed bytes from parsed JSON.
- Use `hmac.compare_digest` for comparison.
- Authentication and payload parsing are separate steps.

---

## Question 20 — Decide Whether a Connector Fits

### Problem

A managed connector supports an API's normal authentication and pagination. However, your source has a special endpoint whose pagination state must combine:

```text
updated_since + cursor
```

The connector does not support that behavior.

### What You Need to Do

Explain the engineering decision you would evaluate.

### Solution

First determine whether the unsupported behavior is a hard requirement for correctness.

If the source requires `updated_since + cursor` to obtain a complete and reliable incremental extraction, a connector that cannot represent that behavior may not be sufficient by itself.

Possible approaches include:

1. configure the connector if an extension point exists,
2. use custom extraction for that source,
3. use the framework for common lifecycle/loading behavior while keeping source-specific extraction custom,
4. choose a different connector with the required source coverage.

### How the Solution Works

The decision should be based on source behavior rather than on whether a connector is generally convenient.

A framework is useful when its abstraction matches the source contract. If the abstraction hides a requirement that is essential for correctness, operational simplicity can become operational risk.

### Key Takeaways

- Source-specific behavior can determine build-vs-buy decisions.
- "Connector exists" does not mean "connector is sufficient."
- Hybrid architectures can be appropriate.
- Correctness requirements come before convenience.

---

# Part III — Hard

## Question 21 — Offset Pagination Loses Records

### Problem

An API uses:

```text
?page=1&limit=100
?page=2&limit=100
```

The dataset is changing while extraction runs.

After page 1 completes, 20 new records are inserted near the beginning of the result ordering. Page 2 is then requested.

The final dataset contains duplicates and missing records.

### What You Need to Do

Diagnose the problem and explain why offset pagination can be unsafe when the source changes during extraction.

### Solution

Offset/page-number pagination assumes that the position of records remains sufficiently stable while the extraction progresses.

If new records are inserted before the next offset, the contents of later pages can shift. Some records can be returned twice, while others can be skipped.

A safer approach depends on the source contract. Options can include:

- cursor pagination,
- keyset pagination with stable ordering,
- bounded incremental extraction using an appropriate timestamp plus pagination,
- another source-supported consistency mechanism.

### How the Solution Works

Suppose page size is 100.

Initially:

```text
records 1–100   → page 1
records 101–200 → page 2
```

If 20 records are inserted before the original page boundary:

```text
records 1–120   now occupy the earlier region
```

The second request can no longer represent the same logical slice of the dataset.

This is a source-consistency problem, not merely a coding bug.

### Key Takeaways

- Offset pagination is sensitive to changing datasets.
- Stable ordering is critical.
- Pagination strategy must be chosen according to source behavior.
- Completeness cannot be assumed merely because every page request returned `200`.

---

## Question 22 — A Cursor Expires After a Crash

### Problem

An extractor checkpoints its cursor after each page. It processes 30 pages and then crashes.

When it restarts, the stored cursor has expired.

### What You Need to Do

Design a recovery approach without assuming that the expired cursor can be reused forever.

### Solution

The recovery strategy must follow the source's pagination contract.

Possible recovery paths include:

1. restart from a valid source-supported checkpoint,
2. restart from a bounded window using an `updated_since + cursor` strategy if supported,
3. restart from an earlier safe checkpoint,
4. use a source-supported backfill or reconciliation mechanism,
5. deduplicate already landed records during replay.

The system should not blindly fabricate or mutate the cursor.

### How the Solution Works

A checkpoint is useful only while the source accepts the checkpoint state.

Cursor expiration means the checkpoint is no longer directly usable. The extractor therefore needs a recovery boundary.

If the source supports deterministic keyset-style or time-bounded progress, the system can recover from a broader state such as:

```text
last durable time boundary
+
pagination state within that boundary
```

Reprocessing overlap is acceptable when downstream processing is idempotent.

### Key Takeaways

- Checkpointing improves recovery but does not eliminate source-specific expiration.
- Recovery needs a source-supported strategy.
- Idempotency makes replay practical.
- Durable state should contain enough information to establish a safe recovery point.

---

## Question 23 — Prevent an Unsafe Watermark Advance

### Problem

An incremental source uses `updated_at`.

The job does:

```text
read max(updated_at) from source
extract records <= max(updated_at)
set watermark = max(updated_at)
```

A record commits just after the maximum was observed but before the extraction finishes.

### What You Need to Do

Explain the gap and propose a safer boundary strategy.

### Solution

The maximum timestamp observed at the start is not necessarily a stable representation of all changes that belong to the extraction window.

A safer strategy is to define an explicit extraction boundary and use a replay overlap.

For example:

```text
previous_safe_watermark = T0
run boundary = T1

extract:
    updated_at >= T0 - overlap
    updated_at <  T1
```

After successful processing, advance the durable watermark to the safe boundary `T1`.

The overlap protects against late commits and timestamp-boundary behavior, while idempotent processing prevents duplicate output from becoming a correctness problem.

### How the Solution Works

The core issue is confusing:

```text
current source state
```

with:

```text
stable extraction boundary
```

A timestamp can be useful as a watermark, but only if the source contract makes its semantics sufficiently reliable.

### Key Takeaways

- Watermarks need explicit boundaries.
- Late commits require defensive extraction windows.
- Overlap plus idempotency is often safer than an aggressive exact boundary.
- The source's timestamp semantics must be understood before relying on them.

---

## Question 24 — Recover From a Webhook Processing Failure

### Problem

A webhook event is received and signature verification succeeds.

The receiver stores the raw event, returns `200`, and later asynchronous processing fails because a downstream dependency is unavailable.

The provider will not resend the event because it already received `200`.

### What You Need to Do

Design the recovery mechanism.

### Solution

The durable raw event becomes the recovery source.

A production flow can be:

```text
webhook
  ↓
verify
  ↓
raw event landing
  ↓
200
  ↓
async processing
  ↓
failure
  ↓
retry / dead-letter state
  ↓
replay after recovery
```

The event should have processing state such as:

```text
received
processing
failed
retryable
dead-lettered
processed
```

### How the Solution Works

The `200` acknowledges receipt to the provider; it does not mean that every downstream side effect succeeded.

Because the event was durably landed before acknowledgement, the system does not depend on the provider sending it again.

A replay mechanism can retry the event after the downstream dependency recovers.

### Key Takeaways

- Fast acknowledgement changes the recovery responsibility.
- Raw event landing creates a durable recovery point.
- Dead-letter and replay patterns protect against downstream failures.
- The webhook provider is not necessarily the source of truth for recovery.

---

## Question 25 — Out-of-Order Webhook Events

### Problem

Two events for the same order arrive:

```text
event A: order.status = paid
event B: order.status = pending
```

The event timestamp shows that B occurred before A, but B arrives after A.

### What You Need to Do

Explain how the system should avoid incorrectly reverting the order.

### Solution

The processor should use event ordering information where the source provides it, such as:

- event sequence/version,
- source timestamp where appropriate,
- version number,
- another source-defined ordering field.

If event A represents a later source version than B, processing B after A should not overwrite the newer state.

If the event does not contain enough information to establish correct ordering, the processor may need to fetch the latest source state from the source system.

### How the Solution Works

Webhook arrival order is not automatically source-event order.

Therefore:

```text
arrival order != business order
```

When ordering cannot be trusted, blindly applying every event can create stale state.

Fetching current source state can be safer when the webhook acts as a notification that something changed rather than as the authoritative full state.

### Key Takeaways

- Delivery order and source order can differ.
- Versions are stronger than arrival time when the source provides them.
- A webhook is a delivery mechanism, not automatically the source of truth.
- Latest-state fetches can be a reconciliation mechanism.

---

## Question 26 — Protect Webhook Verification From Replay

### Problem

A valid webhook request was captured by an attacker and sent to your endpoint again two hours later. The signature remains valid because the signature covers only the body.

### What You Need to Do

Design replay protection using the mechanisms covered by the module.

### Solution

Use a signed timestamp in the verification scheme.

Conceptually:

```text
signed payload
+
signed timestamp
        ↓
verify signature
        ↓
check timestamp tolerance
        ↓
reject stale/replayed request
```

For example, the system may accept only requests whose signed timestamp falls within a configured tolerance.

An event ID can provide an additional duplicate-detection mechanism.

### How the Solution Works

A valid signature proves that the request was signed with the secret; it does not necessarily prove that the request is fresh.

Including a signed timestamp binds authenticity to a time window.

A production system should also avoid logging secrets and should support secret rotation.

### Key Takeaways

- Authentication and freshness are different properties.
- HMAC alone does not automatically prevent replay.
- Signed timestamps provide a freshness check.
- Event IDs provide another layer of idempotency.

---

## Question 27 — CDC Restart After Partial Application

### Problem

A CDC consumer receives changes:

```text
position 1001
position 1002
position 1003
position 1004
```

It applies 1001–1003, crashes before durably recording progress, and restarts from 1001.

### What You Need to Do

Explain why replay is expected and how the downstream application should remain correct.

### Solution

The consumer should replay from the last durable position.

If the last durable state was before 1001, events 1001–1003 may be delivered again.

The downstream application should therefore be designed for safe replay, using an idempotent application strategy or a transaction/state mechanism that makes repeated application harmless.

### How the Solution Works

CDC systems commonly favor durable positions and replay rather than pretending that every failure can be avoided.

The key distinction is:

```text
event delivery
```

versus:

```text
durable downstream effect
```

If the consumer cannot atomically prove that a change was both applied and its position recorded, replay is a normal recovery outcome.

### Key Takeaways

- Replay is a reliability mechanism.
- Durable positions define restart boundaries.
- Downstream application must tolerate replay.
- Exactly-once effects are a stronger requirement than exactly-once delivery.

---

## Question 28 — Diagnose an Incomplete SFTP File Incident

### Problem

A pipeline processed:

```text
sales_2026-10-01.csv
```

The file had no `.done` marker. The resulting row count was 40% lower than normal.

Later, the producer confirms the upload was still running when ingestion started.

### What You Need to Do

Identify:

1. the symptom,
2. the root cause,
3. how to verify it,
4. the fix,
5. how to prevent recurrence.

### Solution

**Symptom:** unusually low row count and incomplete ingestion.

**Likely root cause:** the consumer treated file appearance as proof of completion.

**Verification:** compare ingestion time with producer upload/completion state and inspect the file's final size/checksum.

**Fix:** obtain the complete file and reprocess it using an idempotent file-processing mechanism.

**Prevention:** require a completion marker, manifest, atomic handoff convention, or equivalent source contract.

### How the Solution Works

The key failure is a missing completeness boundary.

A file-drop ingestion system should define a state transition such as:

```text
visible
→ complete
→ validated
→ processing
→ processed
```

The consumer should not infer "complete" from visibility alone.

### Key Takeaways

- File presence is not file completeness.
- Validation should occur before business processing.
- Source contracts should define completion.
- Recovery should support safe reprocessing.

---

## Question 29 — Corrected Resend From a Vendor

### Problem

A vendor originally sends:

```text
orders_2026-09-30.csv
```

Your pipeline processes it successfully.

Two days later, the vendor sends a corrected version with the same logical business date but different contents.

### What You Need to Do

Design the file identity and processing strategy so the corrected file can be handled safely.

### Solution

Do not use only the business date as the file's identity.

Track file-level metadata such as:

```text
logical_date
filename
size
checksum
received_at
processing_status
version/correction indicator if supplied
```

If the checksum differs, treat the new file as a distinct artifact requiring the source-defined correction policy.

The downstream pipeline should be able to:

- detect that this is a new artifact,
- process the correction,
- avoid accidentally treating it as the same already-completed byte stream,
- reconcile downstream data if the correction changes previously loaded records.

### How the Solution Works

Idempotency means repeated processing of the same artifact should not duplicate effects. It does not mean every artifact with the same business date is identical.

A checksum is useful for distinguishing byte-identical retransmission from changed content.

### Key Takeaways

- File identity and business date are different concepts.
- Corrected files require an explicit source contract.
- Checksums help distinguish duplicates from corrections.
- Processing state must support correction/replay.

---

## Question 30 — Diagnose a Connector That Misses Changes

### Problem

A managed connector loads most records correctly but misses updates to a particular source table.

A manual extraction confirms that the source has changed rows.

### What You Need to Do

List the investigation path before deciding to replace the connector.

### Solution

Investigate in this order:

1. Determine which extraction mode the connector uses for that source.
2. Check whether the table supports the connector's expected incremental/CDC mechanism.
3. Inspect connector state/checkpoints.
4. Determine whether deletes or updates are represented correctly.
5. Check source-specific schema or key requirements.
6. Inspect connector logs and observability signals.
7. Compare connector-extracted state with a controlled source query.
8. Determine whether the missing behavior is a connector limitation or configuration/state problem.

Only after establishing the cause should the team decide whether to configure, extend, replace, or bypass the connector.

### How the Solution Works

A managed connector is an abstraction over ingestion behavior. A missing change can come from:

```text
source limitation
configuration
state/checkpoint issue
schema/key issue
connector behavior
```

Replacing the connector without identifying the failure can reproduce the same conceptual problem elsewhere.

### Key Takeaways

- Diagnose the source contract before changing tooling.
- Inspect state as well as current data.
- Connector observability matters.
- Build-vs-buy is an engineering decision, not a branding decision.

---

# Part IV — Advanced

## Question 31 — Design a Multi-Source Customer Ingestion Architecture

### Problem

A company has three customer sources:

1. a REST API supporting cursor pagination and OAuth,
2. a PostgreSQL database where changes can be captured from the database log,
3. a webhook provider that emits customer-change events.

Requirements:

- recover from failures,
- avoid duplicate business effects,
- support historical backfills,
- handle deletes,
- reconcile missing webhook events,
- keep credentials secure.

### What You Need to Do

Design an ingestion approach and justify the extraction strategy for each source.

### Solution

A reasonable architecture is:

```text
REST API
  ↓
OAuth client
  ↓
cursor/incremental extraction
  ↓
raw landing
  ↓
state + downstream processing

PostgreSQL
  ↓
initial snapshot
  ↓
log-based CDC
  ↓
durable position
  ↓
raw change events
  ↓
downstream application

Webhook provider
  ↓
signature verification
  ↓
fast acknowledgement
  ↓
raw event landing
  ↓
deduplication
  ↓
async processing
  ↓
reconciliation pull
```

The API should use cursor/incremental extraction according to its source contract.

PostgreSQL is appropriate for CDC when the source supports log-based change capture. The initial snapshot establishes the starting dataset; ongoing CDC captures later inserts, updates, and deletes.

The webhook should not be treated as the only source of truth. Its events can trigger timely processing while reconciliation through a pull mechanism protects against event loss.

### How the Solution Works

Each source has different semantics.

The central architecture principle is:

```text
source characteristics
      ↓
appropriate ingestion mechanism
      ↓
durable state
      ↓
idempotent downstream processing
      ↓
recovery/reconciliation
```

A single mechanism should not be forced onto every source.

### Key Takeaways

- API extraction, CDC, and webhooks solve different source problems.
- Raw landing provides a recovery boundary.
- Reconciliation is important when push delivery can be incomplete.
- Security and state management must be source-specific.

---

## Question 32 — Design for Correctness Under API Failure

### Problem

An API extraction has:

- cursor pagination,
- OAuth access tokens,
- HTTP 429 rate limits,
- occasional cursor expiration,
- records that can be updated while extraction is running.

The job must be resumable and complete.

### What You Need to Do

Design the state and failure-handling strategy.

### Solution

Maintain durable state containing enough information to identify the extraction boundary and pagination progress, for example:

```text
source
extraction_window
last_safe_boundary
current_cursor
last_successful_page/checkpoint
```

The extraction loop should:

1. authenticate using a secure token mechanism,
2. use an explicit timeout,
3. request pages using the source cursor,
4. respect `Retry-After` on `429`,
5. checkpoint successful progress,
6. detect cursor loops,
7. detect cursor expiration,
8. recover from an earlier safe boundary if the cursor expires,
9. use overlap where required by source timestamp semantics,
10. deduplicate replayed records,
11. advance durable progress only after successful processing.

### How the Solution Works

There are multiple independent failure dimensions:

```text
authentication failure
rate limiting
cursor failure
source mutation
process crash
downstream failure
```

A robust extractor does not solve these with one mechanism.

The architecture instead separates:

- authentication state,
- pagination state,
- extraction-window state,
- downstream processing state.

### Key Takeaways

- Resumability requires explicit state.
- A cursor checkpoint is not the same thing as a complete extraction checkpoint.
- Replay is expected when recovery uses an earlier safe boundary.
- Correctness requires completeness validation, not only successful HTTP requests.

---

## Question 33 — Webhook System With Loss Recovery

### Problem

A payment provider sends webhook events for:

```text
payment.created
payment.updated
payment.refunded
```

The provider can retry requests, but its delivery system occasionally loses events. The provider also exposes an API that can query payment state.

### What You Need to Do

Design a production ingestion strategy that is both event-driven and recoverable.

### Solution

Use the webhook as the low-latency notification path and the API as the reconciliation path.

Architecture:

```text
                 ┌───────────────┐
Webhook ────────→│ verify + land │
                 └───────┬───────┘
                         ↓
                    async process
                         ↓
                    payment state
                         ↑
                 reconciliation API
                         ↑
                 scheduled/recovery
```

The webhook receiver should:

1. verify the signature using the raw request body,
2. enforce replay protection,
3. enforce payload limits and HTTPS,
4. durably land the event,
5. acknowledge quickly,
6. process asynchronously,
7. deduplicate using event IDs,
8. handle out-of-order events using versions/timestamps where supported,
9. dead-letter events that cannot be processed,
10. replay failed events.

A reconciliation process should periodically compare source payment state with the ingested state and repair missing events.

### How the Solution Works

The webhook provides low latency but cannot necessarily guarantee completeness.

The API provides a pull-based recovery mechanism.

This produces a deliberate hybrid:

```text
push for timeliness
+
pull for completeness/reconciliation
```

### Key Takeaways

- Push and pull are complementary.
- A webhook is not automatically the source of truth.
- Reconciliation converts an unreliable delivery channel into a recoverable ingestion system.
- Raw event retention supports replay and diagnosis.

---

## Question 34 — Choose Full, Incremental, CDC, or Webhook

### Problem

Evaluate these four sources:

| Source | Characteristics |
|---|---|
| A | 20,000 records, no update timestamp, reliable full endpoint |
| B | 500 million records, reliable `updated_at`, hourly updates |
| C | PostgreSQL database with supported log-based change capture |
| D | SaaS system with signed webhook events and a query API |

### What You Need to Do

For each source, choose an appropriate primary ingestion approach and justify it.

### Solution

**Source A — Full extraction**

The dataset is small and lacks a reliable incremental signal. A full extraction can be operationally simple and sufficient.

**Source B — Incremental extraction**

The dataset is large and exposes a reliable update timestamp. Incremental extraction reduces repeated source scanning.

**Source C — CDC**

The database supports log-based change capture, so CDC can capture inserts, updates, and deletes while avoiding repeated polling.

**Source D — Webhook plus reconciliation**

Use webhooks for timely change notification, but retain a pull-based reconciliation mechanism because webhook delivery may be duplicated, delayed, out of order, or lost.

### How the Solution Works

The correct choice depends on source characteristics:

```text
small + no incremental contract → full
large + reliable change marker → incremental
database log available          → CDC
push events + query API         → webhook + reconciliation
```

There is no universal extraction strategy.

### Key Takeaways

- Source contracts determine extraction strategy.
- Full extraction is not inherently wrong when the dataset is small.
- Incremental extraction depends on reliable progress semantics.
- CDC is appropriate when supported source-log semantics provide the required correctness.
- Webhooks and reconciliation can complement each other.

---

## Question 35 — Build-vs-Buy Architecture Review

### Problem

Your organization needs 30 ingestion sources.

A managed connector platform supports 25 sources well. Five sources require unusual pagination and source-specific transformation.

The team has limited operational capacity but strong Python expertise.

### What You Need to Do

Design a build-vs-buy strategy rather than selecting one approach for all 30 sources.

### Solution

Use a deliberate hybrid evaluation.

For the 25 well-supported sources, managed connectors may reduce:

- implementation effort,
- maintenance,
- operational burden,
- recurring reliability work.

For the five unusual sources, custom extraction may be appropriate if the connector cannot express their source contracts correctly.

A shared internal ingestion pattern can still standardize:

```text
authentication
timeouts
logging
state
retry behavior
raw landing
validation
observability
```

The decision should compare total engineering cost, not only initial development time.

### How the Solution Works

The real architecture decision is:

```text
source coverage
+
correctness
+
customization
+
reliability
+
observability
+
maintenance
+
operational burden
```

A managed connector that cannot implement a required correctness property may cost less initially but create operational problems later.

Conversely, writing 30 bespoke extractors may create unnecessary maintenance.

### Key Takeaways

- Build-vs-buy can be source-specific.
- A hybrid model is often possible.
- Total engineering cost includes maintenance and operations.
- Correctness requirements are non-negotiable.

---

## Question 36 — Production Incident: Duplicate Data After Recovery

### Problem

An API extraction crashed after processing page 75.

The restart began at checkpoint page 70 because page 75 had not been durably checkpointed.

Pages 70–75 were therefore processed twice.

### What You Need to Do

Explain why this can be acceptable and what must be true downstream.

### Solution

Reprocessing pages 70–75 can be an intentional recovery strategy.

The key requirement is idempotent downstream processing.

For example, records should have stable source identities, allowing repeated delivery to be recognized as the same logical record rather than creating duplicate business rows.

The system should also make its checkpoint semantics explicit:

```text
checkpoint 70
→ replay 70–75
→ successful processing
→ advance checkpoint
```

### How the Solution Works

Checkpointing creates a recovery boundary. It does not necessarily mean that every record after the boundary can be processed exactly once.

The safer trade-off is often:

```text
possible duplicate processing
```

rather than:

```text
possible silent data loss
```

Idempotency makes that trade-off operationally safe.

### Key Takeaways

- Recovery may intentionally replay data.
- Exactly-once processing is often harder than at-least-once delivery.
- Durable checkpoints and idempotent sinks work together.
- A small amount of duplicate processing is preferable to silently skipping records when correctness requires completeness.

---

## Question 37 — Design a Secure Webhook Receiver

### Problem

A public webhook endpoint receives sensitive business events.

The security requirements are:

- verify authenticity,
- prevent replay,
- avoid secret leakage,
- reject oversized requests,
- acknowledge quickly,
- support secret rotation.

### What You Need to Do

Design the receiver's validation sequence.

### Solution

A suitable sequence is:

```text
HTTPS request
    ↓
enforce request-size limit
    ↓
read raw body
    ↓
extract signature + signed timestamp
    ↓
verify HMAC over the raw body/signing input
    ↓
constant-time comparison
    ↓
validate timestamp tolerance
    ↓
record event identity
    ↓
durably land event
    ↓
return 2xx quickly
    ↓
asynchronous processing
```

Secret rotation can support overlapping old/new secrets for a controlled transition, depending on the provider contract.

Secrets must not be embedded in source code or logs.

### How the Solution Works

Each control addresses a different threat:

| Control | Purpose |
|---|---|
| HTTPS | Protect transport |
| HMAC | Authenticate the request |
| Raw-body verification | Verify exactly what was signed |
| Constant-time comparison | Avoid unsafe comparison behavior |
| Timestamp tolerance | Reduce replay window |
| Event ID | Support deduplication |
| Payload limit | Reduce oversized-request risk |
| Secret rotation | Allow credential lifecycle management |

### Key Takeaways

Security is layered. No single signature check solves authentication, replay, transport, resource exhaustion, and credential lifecycle simultaneously.

---

## Question 38 — Architecture Review: API + SFTP + Webhook

### Problem

A business receives:

- hourly customer updates through an API,
- daily financial files over SFTP,
- real-time order events through webhooks.

The organization requires:

- recoverability,
- auditability,
- duplicate-safe processing,
- late-arriving data handling,
- operational visibility.

### What You Need to Do

Propose a unified ingestion architecture and explain where the three source types should differ.

### Solution

Use a common reliability envelope but source-specific ingestion mechanisms.

```text
API
 ↓
HTTP client + auth + pagination + incremental state
 ↓
raw landing/state
 ↓

SFTP
 ↓
completeness marker/manifest/checksum
 ↓
file registry
 ↓
raw landing
 ↓

Webhook
 ↓
signature + replay validation
 ↓
fast acknowledgement
 ↓
raw event landing
 ↓
async processing
 ↓

              common downstream layer
                       ↓
              validation/idempotency
                       ↓
                curated state
                       ↓
                observability
```

The common layer can standardize:

- source identity,
- ingestion run/event identity,
- raw retention,
- processing state,
- error handling,
- observability,
- replay/recovery.

But the source-specific controls remain different.

### How the Solution Works

The API's main challenges are pagination, rate limits, authentication, and incremental state.

The SFTP source's main challenge is file completeness and identity.

The webhook's main challenges are authenticity, retries, duplicates, ordering, and fast acknowledgement.

Trying to make all three behave like a single generic extractor can hide important correctness properties.

### Key Takeaways

- Standardize operational patterns, not source semantics.
- Different ingestion mechanisms have different failure modes.
- Raw landing and explicit state improve recoverability.
- Unified observability does not require identical extraction logic.

---

## Question 39 — Production Incident Diagnosis Across the Module

### Problem

An ingestion platform reports:

- API row counts are lower than expected,
- some API requests show repeated 429s,
- one incremental job advanced its watermark,
- webhook events are duplicated,
- a daily SFTP file occasionally has too few rows,
- a managed connector reports successful runs but downstream changes are missing.

### What You Need to Do

Create a prioritized diagnostic plan. Do not immediately rewrite the platform.

### Solution

Investigate each symptom according to its source contract.

### 1. API row-count discrepancy

Check:

- pagination stopping conditions,
- cursor progression,
- stable ordering,
- cursor loops,
- source changes during pagination,
- completeness validation,
- checkpoint/restart behavior.

### 2. Repeated 429s

Check:

- request rate,
- pagination volume,
- proactive throttling,
- `Retry-After` handling,
- retry counts,
- whether concurrent workers create a retry storm.

### 3. Watermark advancement

Check whether the watermark was advanced before successful downstream processing.

If so, identify the affected interval and rerun it from a safe boundary.

### 4. Duplicate webhooks

Check:

- event IDs,
- durable deduplication state,
- acknowledgement timing,
- provider retry behavior,
- whether business effects are idempotent.

### 5. SFTP row-count issue

Check:

- completion markers,
- manifest/checksum,
- upload timing,
- duplicate/corrected files,
- source contract.

### 6. Managed connector missing changes

Check:

- source extraction mode,
- connector state/checkpoint,
- source-specific update/delete behavior,
- schema/key requirements,
- connector observability,
- whether the connector supports the required source behavior.

### How the Solution Works

The important principle is to diagnose by failure class rather than applying one generic retry or rewrite.

The platform contains several distinct state machines:

```text
HTTP request state
pagination state
authentication state
watermark state
CDC position
webhook processing state
file processing state
connector state
```

Each needs evidence from its own source contract.

### Key Takeaways

Production debugging starts with symptoms and evidence. Do not assume all ingestion failures are networking failures or that replacing tooling automatically fixes correctness.

---

## Question 40 — Design the Production Ingestion Strategy

### Problem

You are designing a production ingestion platform for a company with these requirements:

- 12 REST APIs,
- 2 PostgreSQL sources,
- 1 webhook provider,
- 1 public HTML source,
- 1 daily SFTP feed,
- several sources that could be handled by `dlt` or managed connectors.

Constraints:

- some APIs have strict rate limits,
- some APIs use OAuth,
- one API uses cursor pagination,
- one API has unstable offset pagination,
- PostgreSQL changes must include deletes,
- webhook delivery can be duplicated and out of order,
- the HTML source must be accessed responsibly,
- SFTP files can arrive late and may be corrected,
- the team wants low operational burden,
- every source must be recoverable,
- credentials must remain secure.

### What You Need to Do

Design a production ingestion strategy.

Your answer must explicitly address:

1. source-by-source extraction strategy,
2. authentication,
3. pagination,
4. rate limiting,
5. incremental state,
6. CDC,
7. webhook reliability,
8. HTML extraction,
9. SFTP completeness,
10. framework versus custom code,
11. idempotency,
12. replay/recovery,
13. observability,
14. security,
15. operational trade-offs.

### Solution

A suitable design is a **source-specific ingestion architecture with shared operational primitives**.

#### 1. REST APIs

For each API:

```text
secure client
    ↓
authentication
    ↓
timeouts
    ↓
source-specific pagination
    ↓
rate-limit handling
    ↓
incremental state where supported
    ↓
raw landing
    ↓
idempotent processing
```

Use cursor or keyset-style mechanisms when the source supports them reliably. Treat unstable offset pagination carefully and validate completeness.

OAuth sources should maintain access-token and refresh-token handling separately from extraction state.

#### 2. Rate limits

Implement:

- `429` handling,
- `Retry-After`,
- controlled backoff,
- proactive throttling where required,
- bounded retries,
- retry metrics.

Do not allow retries to create a retry storm.

#### 3. Incremental state

Persist watermarks/checkpoints durably.

Advance state only after the corresponding extraction interval has been successfully handled.

Use overlap where source timestamp semantics make boundary loss possible, combined with idempotent processing.

#### 4. PostgreSQL CDC

For the PostgreSQL sources:

```text
initial snapshot
      ↓
ongoing log-based CDC
      ↓
durable position
      ↓
replay/restart
      ↓
downstream application
```

The CDC stream must preserve inserts, updates, and deletes according to the source contract.

#### 5. Webhook source

Use:

```text
HTTPS
 ↓
signature verification over raw body
 ↓
replay protection
 ↓
event-ID deduplication
 ↓
raw event landing
 ↓
fast 2xx
 ↓
async processing
 ↓
ordering/version handling
 ↓
dead-letter/replay
 ↓
reconciliation
```

Treat webhook delivery as a notification mechanism rather than automatically assuming it is the authoritative state.

#### 6. HTML source

Use an HTML parser such as BeautifulSoup, extracting only the required information.

Respect applicable:

- source terms,
- robots guidance,
- rate limits,
- reasonable request frequency.

Validate extracted fields because HTML structure can change.

#### 7. SFTP

Require an explicit completeness contract such as:

```text
data file
+
.done marker
```

or:

```text
manifest
+
checksums
```

Maintain file identity and processing state so that:

- duplicate transfers are harmless,
- corrected files are detectable,
- late files can be processed,
- failed processing can be retried.

#### 8. dlt / managed connectors

Use managed/framework-based ingestion where source behavior is well supported and the abstraction preserves correctness.

Use custom extraction where source-specific behavior cannot be represented safely.

A hybrid model can minimize operational burden while retaining control over unusual sources.

#### 9. Shared reliability primitives

Across all source types, standardize:

```text
source identity
run/event/file identity
durable state
raw landing
idempotent processing
validation
structured observability
failure classification
replay/recovery
```

Do not force identical extraction logic across sources.

#### 10. Security

Keep API keys, bearer tokens, OAuth credentials, webhook secrets, and other credentials outside source code.

For webhooks:

- verify signatures,
- use raw request bytes,
- use constant-time comparison,
- apply replay protection,
- rotate secrets,
- require HTTPS.

For SFTP, apply the security and encryption mechanism required by the source contract.

#### 11. Observability

Measure at least source-appropriate signals such as:

- request failures,
- retry counts,
- `429` frequency,
- pages/cursors processed,
- checkpoint progress,
- watermark progress,
- CDC positions,
- webhook duplicates,
- webhook failures,
- dead-letter counts,
- file validation failures,
- connector failures,
- extracted/processed record counts.

The exact metrics should reflect each source's state model.

#### 12. Recovery model

The central recovery principle is:

```text
durable state
+
raw/landing data
+
idempotent processing
+
replay
+
reconciliation
```

A crash should result in a controlled replay or restart, not silent data loss.

### How the Solution Works

This design deliberately avoids selecting one universal ingestion technology.

The platform is organized around the source contract:

| Source type | Primary mechanism | Main correctness concern |
|---|---|---|
| REST API | Pull + pagination/incremental extraction | completeness and resumability |
| OAuth API | Pull + token lifecycle | authentication continuity |
| PostgreSQL | Snapshot + CDC | durable position and deletes |
| Webhook | Push + reconciliation | duplicates, ordering, event loss |
| HTML | Responsible parsing | source changes and source politeness |
| SFTP | File-drop ingestion | completeness and file identity |
| dlt/managed source | Framework/connector | source coverage and operational fit |

The architecture therefore follows:

```text
Requirements
    ↓
Source contract
    ↓
Extraction mechanism
    ↓
Durable state
    ↓
Correctness controls
    ↓
Recovery strategy
    ↓
Observability
    ↓
Operational evaluation
```

The important production insight is that ingestion is not simply the act of moving bytes. It is a correctness and reliability system operating against external source behavior.

### Key Takeaways

- There is no single ingestion mechanism that fits every source.
- Pull, push, incremental extraction, CDC, file drops, scraping, and frameworks solve different problems.
- Correctness depends on explicit source contracts and durable state.
- Idempotency and replay are central to failure recovery.
- Security controls must match the authentication and delivery mechanism.
- Frameworks should reduce operational burden without hiding source-specific correctness requirements.
- A production ingestion architecture should be explainable in terms of source behavior, constraints, failure modes, and recovery.

---

# Module Coverage Map

| Topic | File | Questions | Major Concepts Tested |
|---|---|---:|---|
| 01 | `01-http-fundamentals-for-data-extraction.md` | 1, 3, 5, 11, 32, 40 | HTTP request/response, headers, query parameters, status codes, response handling, extraction failures |
| 02 | `02-httpx-and-requests-sessions-and-timeouts.md` | 2, 11, 13, 15, 32, 40 | clients/sessions, connection reuse, explicit timeouts, reusable clients, safe request patterns |
| 03 | `03-api-authentication-keys-oauth2-and-token-refresh.md` | 1, 3, 11, 15, 32, 37, 40 | API keys/bearer tokens, OAuth, access/refresh tokens, expiry, secret handling |
| 04 | `04-pagination-offset-cursor-and-keyset.md` | 4, 12, 13, 21, 22, 32, 36, 40 | offset, cursor, keyset reasoning, stopping conditions, stable ordering, loop detection, checkpointing, resumability |
| 05 | `05-rate-limits-http-429-and-retry-after.md` | 5, 13, 32, 40 | 429, Retry-After, backoff, throttling, retry storms, retry measurement |
| 06 | `06-full-vs-incremental-extraction-and-watermarks.md` | 6, 14, 23, 32, 34, 36, 40 | full vs incremental, watermarks, boundaries, overlap, late commits, state advancement, idempotency |
| 07 | `07-change-data-capture-concepts.md` | 7, 27, 31, 34, 40 | initial snapshot, inserts/updates/deletes, log-based CDC, positions, restart, replay |
| 08 | `08-webhooks-and-push-based-ingestion.md` | 8, 18, 19, 24, 25, 26, 31, 33, 37, 38, 40 | fast acknowledgement, retries, at-least-once delivery, deduplication, HMAC, replay protection, ordering, reconciliation, raw landing |
| 09 | `09-html-parsing-and-responsible-scraping.md` | 16, 34, 38, 40 | HTML parsing, structured extraction, responsible scraping, source changes, validation |
| 10 | `10-sftp-and-file-drop-ingestion.md` | 9, 17, 28, 29, 38, 40 | completeness, `.done` markers, manifests, checksums, file identity, corrected resends, late files, idempotency |
| 11 | `11-ingestion-frameworks-dlt-and-managed-connectors.md` | 10, 20, 30, 35, 39, 40 | dlt, managed connectors, framework abstractions, source coverage, build-vs-buy, operational burden, maintenance |

## Final Practice Progression

The 40 questions intentionally progress through four engineering levels:

```text
Questions 1–10
    ↓
Understand individual mechanisms

Questions 11–20
    ↓
Combine mechanisms

Questions 21–30
    ↓
Reason about failures and recovery

Questions 31–40
    ↓
Design production ingestion systems
```

The central principle across the entire practice set is:

> **Choose and operate an ingestion strategy according to the source contract, workload, correctness requirements, failure modes, and operational constraints—not according to a universal preference for one technology.**
