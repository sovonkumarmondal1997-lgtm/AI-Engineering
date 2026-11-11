# Roadmap — Module 2.9: Data Ingestion and Extraction Patterns

This is the learning roadmap for the ninth module of Stage 2, **Python for
Data Engineering**. It tells you **what** to learn about getting data out
of source systems and into your platform, **in what order**, **how** to
learn each topic, and **how to prove to yourself** that you have learned
it before you move on.

Ingestion is the first hop of every pipeline (the "generation → ingestion"
step of the lifecycle in Module 2.1), and it is where most pipelines break.
Sources are owned by other teams and other companies. APIs time out,
change their pagination, throttle you, expire your tokens, and return
duplicates. Databases update rows without touching `updated_at` and delete
rows without telling you. Partners drop half-written files on SFTP servers
at random times. A senior data engineer designs ingestion that is
**complete, correct, idempotent, resumable, polite to the source, and
observable** — and knows when to buy a connector instead of building one.

You already know how to extract from databases with bounded memory (Module
2.7). This module covers every other way data arrives: HTTP APIs, change
data capture, webhooks, web pages, and file drops — plus the strategies
(full, incremental, CDC) that apply to all of them.

---

## 1. Module outcome

By the end of this module you will be able to:

- Explain HTTP well enough to debug any API extraction: methods, status
  codes, headers, content types, compression, caching, and streaming.
- Build robust API clients with **httpx** (and read **requests**-based
  code) using sessions, connection reuse, and explicit timeouts.
- Authenticate with API keys, bearer tokens, and **OAuth 2.0** flows, and
  refresh tokens automatically and safely.
- Paginate any API — offset, cursor, keyset, and link-header styles —
  completely and without duplicates or gaps.
- Respect **rate limits**: handle HTTP 429 and `Retry-After`, throttle
  proactively, and retry only what is safe to retry.
- Choose between **full and incremental** extraction, manage
  **watermarks** and state, and handle late commits, deletes, and
  backfills.
- Explain **change data capture** approaches and read changes from
  PostgreSQL's write-ahead log.
- Receive **webhooks** securely (signature verification, replay
  protection, deduplication) and reconcile them with pulls.
- Scrape web pages **responsibly and legally** when no API exists.
- Ingest **SFTP and file drops** reliably: completeness detection,
  checksums, file registries, and idempotency.
- Evaluate and use **ingestion frameworks** (dlt) and **managed
  connectors**, and make a build-vs-buy decision.

---

## 2. Prerequisites

This module builds on earlier stages and Modules 2.1–2.8. It does **not**
re-teach them.

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Local networking, ports, environment variables | Stage 0 — OS Fundamentals | Running local APIs, SFTP servers, and webhook receivers |
| Secrets and local security hygiene | Stage 0 — Developer Environment | API keys, client secrets, and SSH keys never enter code or logs |
| JSON, JSON Lines, CLI programs, exit codes | Stage 1 — Module 1.5 | Raw payloads are landed as JSON Lines; ingestion jobs are CLIs |
| Mocking and test doubles | Stage 1 — Module 1.7 | Testing API clients without calling real APIs |
| Decorators (retry), generators, context managers, datetime and time zones | Stage 1 — Module 1.9 | Generic retry and backoff are **not** re-taught; this module adds HTTP-specific rules |
| Safe logging, idempotency, safe file writes | Stage 1 — Module 1.10 | Every ingestion job must be re-runnable and must not log secrets |
| Lifecycle, bronze layer, freshness SLAs | Stage 2 — Module 2.1 | Ingestion writes bronze and is measured by freshness |
| Nested JSON flattening | Stage 2 — Module 2.5 | API responses are nested |
| SQL `MERGE`, keyset pagination, transactions | Stage 2 — Module 2.6 | Applying incremental and CDC changes to targets |
| Streaming extraction, metadata tables (`pipeline_runs`, `watermarks`) | Stage 2 — Module 2.7 | Database extraction is **not** re-taught; its state tables are reused |
| Source schemas, soft deletes, event data | Stage 2 — Module 2.8 | Knowing what you extract and how it changes |

**Tools needed:**

- Python 3.12+ in a `uv` project: `uv add httpx requests tenacity respx
  fastapi uvicorn beautifulsoup4 lxml paramiko "dlt[duckdb]" pyarrow duckdb
  psycopg[binary]`.
- Docker services: PostgreSQL with `wal_level=logical` (Topic 07), an SFTP
  server image (Topic 10), and MinIO (from Module 2.4) for landing data.
- A **mock API you build yourself** with FastAPI (Topic 01 onwards) that
  simulates pagination, authentication, rate limits, failures, and data
  changes — so every failure mode can be tested deterministically.
- Public APIs for real-world practice (for example the GitHub REST API or
  an open weather API) — always within their terms of use and limits.
- `curl` for exploring endpoints by hand.

---

## 3. How the module is organised

The eleven topics are grouped into five phases. Work through them **in
order**.

```text
Phase A — HTTP Foundations                        (Basics)
  01 HTTP fundamentals for data extraction
  02 httpx and requests: sessions and timeouts

Phase B — Extracting from APIs Correctly          (Intermediate)
  03 API authentication: keys, OAuth2, and token refresh
  04 Pagination: offset, cursor, and keyset
  05 Rate limits, HTTP 429, and Retry-After

Phase C — Extraction Strategies                   (Intermediate → Advanced)
  06 Full vs incremental extraction and watermarks
  07 Change data capture concepts

Phase D — Other Ingestion Channels                (Intermediate → Advanced)
  08 Webhooks and push-based ingestion
  09 HTML parsing and responsible scraping
  10 SFTP and file-drop ingestion

Phase E — Build vs Buy                            (Advanced)
  11 Ingestion frameworks: dlt and managed connectors

Consolidate
  practice-questions.md
  Module mini-project: a multi-source ingestion platform
```

The dependency chain:

```text
01 ► 02 ► 03 ► 04 ► 05 ► 06 ► 07 ► 08 ► 09 ► 10 ► 11
HTTP client auth  pages polite  what   every   push   pages files  frameworks
                  of    access  to     change  data   without       that do
                  data          pull                  APIs          01–10 for you
```

Why this order:

- You cannot debug an API client (02) without understanding HTTP (01).
- Authentication (03) comes before pagination (04) because you need access
  before you can page through data, and tokens often expire mid-pagination.
- Rate limits (05) come after pagination because paging through large
  datasets is what triggers them.
- Strategies (06–07) apply to every source type, so they come once you can
  extract from APIs; CDC (07) builds directly on incremental extraction.
- Webhooks (08), scraping (09), and file drops (10) reuse HTTP, state, and
  idempotency ideas from earlier topics.
- Frameworks (11) come last: you can only evaluate a tool that "handles
  pagination, state, and schema evolution for you" once you have built
  those things yourself.

---

## 4. Suggested schedule

About **5 weeks at 8–10 hours per week**.

| Week | Work |
| --- | --- |
| 1 | Topic 01 — HTTP · Topic 02 — httpx and requests · build the mock API |
| 2 | Topic 03 — authentication · Topic 04 — pagination · Topic 05 — rate limits |
| 3 | Topic 06 — full vs incremental · Topic 07 — CDC |
| 4 | Topic 08 — webhooks · Topic 09 — scraping · Topic 10 — SFTP and file drops |
| 5 | Topic 11 — dlt and managed connectors · practice questions · mini-project |

---

## 5. How to study every topic (the ingestion loop)

```text
Read → Explore the source by hand → Write the contract → Build the extractor
→ Land raw data first → Make it complete → Make it safe to re-run
→ Inject failures → Measure → Write it down → Explain aloud
```

1. **Read** the topic file once, fully.
2. **Explore the source by hand** with `curl`, a browser, `psql`, or an
   SFTP client. Read the source's documentation fully, especially the
   sections on limits, pagination, and changes.
3. **Write the source contract**: endpoint or location, authentication,
   format, pagination, rate limits, how changes and deletes appear,
   expected volume, and owner.
4. **Build the extractor** as small, tested functions (client, paginator,
   state store, writer).
5. **Land raw data first**: write exactly what the source returned
   (JSON Lines or files) to bronze with ingestion metadata (`_extracted_at`,
   `_source`, `_run_id`, request parameters) before any transformation.
6. **Make it complete**: prove with counts or checksums that you received
   everything the source has for the requested window.
7. **Make it safe to re-run**: running the same job twice, or after a
   crash, must produce the same bronze data without duplicates or gaps.
8. **Inject failures** using your mock API or services: timeouts, 5xx
   errors, 429s, expired tokens, schema changes, half-written files, and
   duplicate deliveries.
9. **Measure** records per second, requests made, retries, and freshness.
10. **Write down** the rule you learned in `module-2.9-notes.md`.
11. **Explain aloud** how your extractor behaves when each failure
    happens.

Keep one `ingestion_lab/` `uv` project:

```text
ingestion_lab/
├── docker-compose.yml     # PostgreSQL (logical WAL), SFTP, MinIO
├── mock_api/              # your FastAPI mock source with failure switches
├── src/ingestion_lab/     # clients, paginators, state, writers per topic
├── contracts/             # one source contract per source (Markdown/YAML)
├── landing/               # local bronze output (git-ignored)
└── tests/                 # unit tests with mocked transports + integration tests
```

---

## 6. Phase A — HTTP Foundations (Basics)

### Topic 01 — [HTTP fundamentals for data extraction](01-http-fundamentals-for-data-extraction.md)

**Why it comes first:** Most external data arrives over HTTP. When an
extraction fails, the answer is almost always in a status code or a header
you did not read.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | The request/response cycle: method, URL, query parameters, headers, body; response status, headers, body |
| Basics | Methods for data work: `GET` (read), `POST` (create, and often "search" or "start export"), `PUT` / `PATCH`, `DELETE`, `HEAD` |
| Basics | Status code families and what each means for a pipeline: `2xx` success, `3xx` redirect, `4xx` your request is wrong (do not blindly retry), `5xx` the server failed (maybe retry) |
| Basics | Important codes: `200`, `201`, `202`, `204`, `301/302/307/308`, `304`, `400`, `401`, `403`, `404`, `408`, `409`, `410`, `422`, `429`, `500`, `502`, `503`, `504` |
| Basics | Content types (`application/json`, `text/csv`, `application/x-ndjson`, `application/octet-stream`) and the `Accept` header |
| Intermediate | HTTPS and TLS certificates, DNS, and connection reuse (keep-alive) — why reusing connections speeds up extraction |
| Intermediate | Compression (`Accept-Encoding: gzip, br`) and large responses; chunked transfer and streaming downloads |
| Intermediate | Caching and conditional requests: `ETag` / `If-None-Match`, `Last-Modified` / `If-Modified-Since`, and `304 Not Modified` for cheap "has anything changed?" checks |
| Intermediate | Idempotent vs non-idempotent methods, and why that decides what is safe to retry |
| Intermediate | API styles: REST, GraphQL (single endpoint, query in the body), gRPC (awareness), SOAP/XML (legacy); reading **OpenAPI** specifications |
| Advanced | The **asynchronous export** pattern: request a bulk export (`202 Accepted`), poll a status URL, download result files — common in SaaS APIs for large volumes |
| Advanced | HTTP/1.1 vs HTTP/2 (multiplexing) at a practical level |
| Advanced | Proxies, corporate TLS inspection, and custom certificate authorities |

**How to learn it**

1. Read the topic file.
2. Use `curl -v` against a public API and your mock API; annotate every
   request and response header you see.
3. Build the **mock API** with FastAPI: `/customers` returning JSON with
   configurable latency, error rate, and ETags. You will extend it in every
   later topic.

**Hands-on exercise — `http_explorer/`**

1. With `curl`, fetch a resource, then repeat with `If-None-Match` using its
   `ETag` and observe `304`.
2. Download a large file with and without `Accept-Encoding: gzip` and
   compare bytes transferred.
3. In the mock API, implement `/exports` using the asynchronous export
   pattern (`202`, status polling, download URL).
4. Write a one-page "status code → pipeline action" table (succeed,
   retry, fail fast, alert) and keep it — you will implement it in Topics
   02 and 05.

**Checkpoint — you are ready to move on when you can:**

- [ ] Describe an HTTP request and response in full.
- [ ] Explain what a pipeline should do for `400`, `401`, `404`, `429`,
      `500`, and `503`.
- [ ] Explain conditional requests with ETags.
- [ ] Explain the asynchronous export pattern.
- [ ] Read an OpenAPI specification to find pagination and limits.

**Common mistakes:** treating every non-200 response the same; ignoring
response headers; assuming `200` means the body is valid (some APIs return
errors inside a `200`).

---

### Topic 02 — [httpx and requests: sessions and timeouts](02-httpx-and-requests-sessions-and-timeouts.md)

**Why here:** Now you write the client. `requests` is everywhere in
existing code; `httpx` is the modern choice with a very similar API, HTTP/2,
and async support (used in Module 2.10).

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | `httpx.get` vs `httpx.Client`; `requests.get` vs `requests.Session` — and why one-off calls are wrong for extraction (no connection reuse) |
| Basics | `base_url`, default headers (including a descriptive `User-Agent`), query `params`, JSON bodies |
| Basics | `response.raise_for_status()`, `response.json()`, `response.status_code`, `response.headers` |
| Intermediate | **Timeouts**: connect, read, write, and pool timeouts; `requests` has **no default timeout** (a request can hang forever); `httpx` has a default but you should set it explicitly |
| Intermediate | Streaming large downloads to disk (`client.stream(...)`, `iter_bytes()`) with bounded memory and atomic file writes |
| Intermediate | Handling bad bodies: invalid JSON, HTML error pages, truncated responses, unexpected content types |
| Intermediate | Connection pool limits (`httpx.Limits`) and closing clients with context managers |
| Intermediate | Designing an **API client class**: one place for base URL, auth, timeouts, retries, and logging; methods returning parsed records |
| Advanced | Testing without the network: `httpx.MockTransport`, `respx` (httpx), `responses` (requests), and recorded fixtures |
| Advanced | Event hooks for logging and metrics (request count, latency, status codes) — with secrets redacted |
| Advanced | Transport-level retries (connection failures only) vs application-level retries (Topic 05); `urllib3.Retry` with `requests` adapters in legacy code |
| Advanced | TLS verification (`verify=`), custom CA bundles, proxies, and HTTP/2 (`http2=True`) |

**How to learn it**

1. Read the topic file.
2. Make your mock API hang for 60 seconds on one endpoint; call it with
   `requests` without a timeout, then with timeouts in both libraries.
3. Port a small `requests`-based script to `httpx` and list every
   difference you hit.

**Hands-on exercise — `api_client.py`**

1. Build `CustomersClient` on `httpx.Client` with `base_url`, a
   `User-Agent`, explicit timeouts, connection limits, and an event hook
   that logs method, URL (without secrets), status, and duration.
2. Implement `download_export(url, path)` that streams a 2 GB file to a
   temporary path and renames it on success.
3. Handle invalid JSON and HTML error pages with clear exceptions.
4. Write unit tests with `respx` covering success, timeout, `500`, invalid
   JSON, and a truncated download.
5. Benchmark 1,000 requests with one-off calls vs a reused client.

**Checkpoint:**

- [ ] Explain why a reused client/session is faster.
- [ ] Set connect and read timeouts in both libraries.
- [ ] Stream a large download with bounded memory.
- [ ] Test an API client without real network calls.

**Common mistakes:** no timeouts; creating a new client per request;
logging full URLs or headers containing tokens; calling `.json()` without
handling errors.

---

## 7. Phase B — Extracting from APIs Correctly (Intermediate)

### Topic 03 — [API authentication: keys, OAuth2, and token refresh](03-api-authentication-keys-oauth2-and-token-refresh.md)

**Why here:** Nearly every useful API requires authentication, and expired
or leaked credentials are among the most common causes of failed or unsafe
pipelines.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Authentication (who you are) vs authorization (what you may do); scopes and permissions |
| Basics | API keys in headers (preferred) vs query strings (they leak into logs and proxies); HTTP Basic auth |
| Basics | Bearer tokens (`Authorization: Bearer ...`) |
| Intermediate | **OAuth 2.0** roles and flows: **client credentials** (machine-to-machine — most common for pipelines), **authorization code with PKCE** (acting on behalf of a user), refresh tokens; device code flow (awareness) |
| Intermediate | Token lifetimes, `expires_in`, **proactive refresh** before expiry, and reactive refresh on `401` — refreshing once, then failing loudly |
| Intermediate | Caching tokens across requests and runs; thread-safe refresh; rotating refresh tokens that must be saved every time |
| Intermediate | Custom auth in httpx (`httpx.Auth` subclasses with an auth flow) and in requests (`AuthBase`) |
| Advanced | JWTs: structure (header, payload, signature), reading `exp` and scopes — and never trusting a token's contents without verification when it matters |
| Advanced | Request signing (HMAC signatures, cloud signature schemes such as AWS SigV4 — awareness), mutual TLS, and service-account key files |
| Advanced | Credential hygiene for pipelines: least-privilege scopes, dedicated service accounts, rotation, revocation, and never printing tokens (cloud secret managers in Module 2.18) |
| Advanced | Tokens expiring during long paginations and exports — designing clients that survive it |

**How to learn it**

1. Read the topic file.
2. Add OAuth 2.0 client credentials to your mock API: a `/token` endpoint
   issuing tokens that expire after 60 seconds.
3. Draw the client credentials and authorization code flows as sequence
   diagrams.

**Hands-on exercise — `auth.py`**

1. Implement `ClientCredentialsAuth(httpx.Auth)` that fetches a token,
   caches it, refreshes it 30 seconds before expiry, and retries once on
   `401` after forcing a refresh.
2. Run a 5-minute paginated extraction against tokens that expire every 60
   seconds; prove the extraction completes without failures.
3. Store a rotating refresh token safely between runs (in a local file
   with restricted permissions for now) and show what breaks if you do not
   save the new one.
4. Add a log filter that redacts `Authorization` headers and `token`
   fields; test it.
5. Decode a JWT's payload to read its expiry and scopes.

**Checkpoint:**

- [ ] Explain the OAuth 2.0 client credentials flow.
- [ ] Refresh tokens proactively and on `401` without loops.
- [ ] Explain why API keys should not go in query strings.
- [ ] Keep every credential out of code and logs.

**Common mistakes:** requesting a new token for every call; infinite
refresh loops on permanent `401`s; broad scopes "to be safe"; credentials
committed to Git.

---

### Topic 04 — [Pagination: offset, cursor, and keyset](04-pagination-offset-cursor-and-keyset.md)

**Why here:** APIs return data in pages. An extractor that stops one page
early, or repeats a page, silently produces incomplete or duplicated data.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why APIs paginate; page size limits |
| Basics | **Offset / page-number pagination** (`?page=3&per_page=100`, `?offset=200&limit=100`) |
| Basics | **Cursor / token pagination** (an opaque `next_cursor` or `next_page_token` returned with each page) |
| Intermediate | **Keyset pagination** in APIs (`?since_id=...`, `?created_after=...`, `starting_after=...`) — the API version of Module 2.6's keyset idea |
| Intermediate | **Link-header pagination** (`Link: <...>; rel="next"`) and GraphQL connections (`edges`, `pageInfo`, `endCursor`, `hasNextPage`) |
| Intermediate | Stopping conditions: no next link, `has_more = false`, empty page, fewer items than the page size — and which ones are reliable for a given API |
| Intermediate | Writing paginators as **generators** that yield records or pages, separate from the HTTP client |
| Intermediate | **Consistency problems**: with offset pagination, inserts and deletes during extraction cause skipped or duplicated records; ordering that is not stable |
| Advanced | Checkpointing the cursor after each page so a crashed extraction resumes, and knowing when a saved cursor expires |
| Advanced | Parallel extraction by splitting a date range into windows, each paginated independently (a preview of concurrency in Module 2.10) |
| Advanced | Guards: maximum page count, loop detection (the same cursor twice), and completeness checks against a total count when the API provides one |
| Advanced | Combining pagination with incremental filters (Topic 06): `updated_since` + cursor |

**How to learn it**

1. Read the topic file.
2. Add all four pagination styles to your mock API, plus a switch that
   inserts and deletes records while you paginate.
3. For each style, predict whether records can be skipped or duplicated
   under concurrent changes, then test it.

**Hands-on exercise — `paginators.py`**

1. Implement one generator per style (offset, cursor, keyset, link header)
   sharing the same client.
2. Extract 100,000 records from the mock API while it inserts and deletes
   records; measure missing and duplicate records per style.
3. Add checkpointing: save the cursor after every page; kill the process
   and resume; prove the final output is complete and duplicate-free.
4. Add guards for repeated cursors and a maximum page count.
5. Paginate a real public API (for example, GitHub's link-header
   pagination) within its limits.
6. Unit-test every paginator with mocked pages, including an empty first
   page.

**Checkpoint:**

- [ ] Implement offset, cursor, keyset, and link-header pagination.
- [ ] Explain why offset pagination can skip or duplicate records.
- [ ] Resume a paginated extraction from a checkpoint.
- [ ] Detect pagination loops and incomplete extractions.

**Common mistakes:** stopping on the first short page when the API returns
variable page sizes; offset pagination on changing data; paginators mixed
into business logic; no guard against infinite loops.

---

### Topic 05 — [Rate limits, HTTP 429, and Retry-After](05-rate-limits-http-429-and-retry-after.md)

**Why here:** Paging through large datasets quickly hits rate limits. A
good extractor is fast **and** polite; a bad one gets throttled, banned, or
breaks the provider's service.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Why APIs limit: protecting shared infrastructure; limits per second, minute, day, and per concurrent request |
| Basics | `429 Too Many Requests` and the `Retry-After` header (seconds or an HTTP date); `503 Service Unavailable` with `Retry-After` |
| Basics | Rate-limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (and the newer standard `RateLimit` header fields) |
| Intermediate | **What to retry** (connection errors, timeouts, `408`, `429`, `500`, `502`, `503`, `504`) vs **what not to retry** (`400`, `401` after refresh, `403`, `404`, `422`) — turning your Topic 01 table into code |
| Intermediate | HTTP-specific retry rules on top of your Stage 1 retry decorator: **honour `Retry-After`** before any backoff formula; cap total retry time; add jitter |
| Intermediate | Retry libraries: `tenacity` (and awareness of `stamina`) — configuring stop, wait, and retry conditions |
| Intermediate | **Proactive throttling**: token-bucket and sliding-window limiters that stay under the limit instead of reacting to 429s |
| Advanced | Retrying non-idempotent requests safely with **idempotency keys** |
| Advanced | Sharing one API quota across several jobs or workers (a central limiter — e.g. a database or Redis-backed counter, awareness level) |
| Advanced | Circuit breakers: stop calling a failing source for a cooldown period instead of hammering it |
| Advanced | Daily quotas and budgeting: estimating requests per run, choosing page sizes and filters that minimise requests, and scheduling heavy extractions off-peak |
| Advanced | Observability: counting requests, retries, 429s, and time spent waiting per run |

**How to learn it**

1. Read the topic file.
2. Add a token-bucket limiter to your mock API that returns `429` with
   `Retry-After` and rate-limit headers.
3. Compare three clients on the same extraction: no handling, reactive
   (retry on 429), and proactive (throttle + reactive).

**Hands-on exercise — `polite_client.py`**

1. Implement a retry policy with `tenacity` that retries only retryable
   errors, honours `Retry-After` (both formats), uses exponential backoff
   with jitter otherwise, and gives up after a maximum total time.
2. Implement a token-bucket limiter driven by `X-RateLimit-Remaining` and
   `X-RateLimit-Reset`.
3. Extract 200,000 records from the throttled mock API with each client;
   record total time, 429 count, and retries.
4. Add a circuit breaker that pauses after five consecutive `5xx` errors.
5. Implement idempotency keys for a `POST /exports` call and show a safe
   retry.
6. Test: `404` is not retried; `503` with `Retry-After: 2` waits two
   seconds; a permanent outage fails within the time budget.

**Checkpoint:**

- [ ] Decide which HTTP failures to retry.
- [ ] Honour `Retry-After` and rate-limit headers.
- [ ] Throttle proactively with a token bucket.
- [ ] Explain idempotency keys and circuit breakers.

**Common mistakes:** retrying `4xx` errors; retries without jitter
(synchronised retry storms); ignoring `Retry-After`; unlimited retries that
hide outages; several jobs sharing one API key without coordination.

---

## 8. Phase C — Extraction Strategies (Intermediate → Advanced)

### Topic 06 — [Full vs incremental extraction and watermarks](06-full-vs-incremental-extraction-and-watermarks.md)

**Why here:** You can now extract anything from an API. The next question
is **what** to extract on each run: everything, or only what changed. This
applies equally to APIs, databases (Module 2.7), and files.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Full extraction** (snapshot of everything each run): simple, catches deletes, expensive at scale |
| Basics | **Incremental extraction**: only new or changed records since the last run |
| Basics | **Watermarks**: the value (e.g. `updated_at`, an increasing id, a sequence number) that marks how far you have extracted; the high-water mark stored in a state table |
| Intermediate | Incremental patterns: append-only (events, logs) vs changed-records (upsert downstream with `MERGE`, Module 2.6) |
| Intermediate | Choosing a watermark column: must be reliably updated on every change, indexed on the source, and monotonic enough |
| Intermediate | Boundary rules: inclusive vs exclusive comparisons, records with identical timestamps, and **deduplicating** the overlap |
| Intermediate | **Lookback windows**: re-reading a safety overlap (e.g. the last 30 minutes) to catch late commits, clock skew, and long-running source transactions that commit with earlier timestamps |
| Intermediate | Storing and advancing state safely: update the watermark **only after** data is durably landed (reusing the `watermarks` table from Module 2.7) |
| Advanced | **Deletes are invisible** to timestamp-based incremental extraction: soft-delete flags, periodic full key reconciliation, or CDC (Topic 07) |
| Advanced | **Backfills**: re-extracting a historical range in windows without disturbing normal runs; idempotent writes per window (transformation-side backfills are in Module 2.12) |
| Advanced | Hybrid strategies: frequent incremental runs + a weekly full reconciliation; full extraction for small tables and incremental for large ones |
| Advanced | Time zones and precision in watermarks (UTC, microseconds vs seconds, APIs that truncate filters) |
| Advanced | Choosing a strategy from volume, change rate, source capabilities, and freshness SLAs (Module 2.1) |

**How to learn it**

1. Read the topic file.
2. Add `updated_since` filtering to your mock API, plus switches for late
   commits (records appearing with past timestamps) and hard deletes.
3. For five sources (a small reference table, a 500-million-row orders
   table, an append-only event log, a SaaS contacts API with no delete
   signal, a daily file drop), choose a strategy and justify it.

**Hands-on exercise — `incremental_extractor.py`**

1. Extract customers from the mock API incrementally with an `updated_at`
   watermark stored in the `watermarks` table; land raw pages to bronze as
   JSON Lines partitioned by run date.
2. Inject late commits and show records being missed; fix it with a
   lookback window and deduplication by `(id, updated_at)`.
3. Inject hard deletes and show they are missed; add a weekly full-key
   reconciliation that detects deleted ids and emits delete markers.
4. Implement `backfill(start, end, window="1d")` that re-extracts history
   in windows idempotently.
5. Crash the job after landing data but before saving the watermark; show
   the next run produces no gaps and no duplicates downstream.
6. Test boundary conditions: identical timestamps at the boundary, empty
   windows, and the first-ever run with no state.

**Checkpoint:**

- [ ] Choose full vs incremental extraction for a source and justify it.
- [ ] Manage a watermark safely (advance only after landing).
- [ ] Explain and fix the late-commit problem with a lookback window.
- [ ] Explain why deletes are missed and three ways to capture them.
- [ ] Run an idempotent backfill.

**Common mistakes:** using a watermark column that is not updated on every
change; advancing the watermark before data is saved; strict `>` boundaries
that lose same-timestamp records; forgetting deletes.

---

### Topic 07 — [Change data capture concepts](07-change-data-capture-concepts.md)

**Why here:** Timestamp-based incremental extraction misses deletes,
intermediate changes, and badly behaved `updated_at` columns. Change data
capture reads **every change** from the database itself.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | What CDC is: capturing inserts, updates, and deletes as a stream of change events |
| Basics | Why CDC: deletes captured, every intermediate change, low latency, and low load on the source compared with repeated queries |
| Basics | Approaches: query-based (timestamps — Topic 06), **trigger-based** (audit tables), **log-based** (reading the database's transaction log), snapshot comparison |
| Intermediate | Log-based CDC in PostgreSQL: the write-ahead log (WAL), `wal_level = logical`, **logical decoding**, output plugins (`test_decoding`, `pgoutput`, `wal2json`), **replication slots**, and publications |
| Intermediate | The equivalents in other databases (MySQL binlog in row format, SQL Server CDC tables, Oracle redo logs, MongoDB change streams) — awareness |
| Intermediate | The **change event**: operation (create, update, delete, snapshot read), `before` and `after` images, primary key, commit timestamp, and log position (e.g. LSN) |
| Intermediate | **Initial snapshot + streaming**: taking a consistent snapshot and then applying changes from exactly the right log position — no gaps, no double-apply |
| Advanced | Applying changes to a target: ordering per key, keeping the latest change per key, and `MERGE` with deletes (SQL from Module 2.6) |
| Advanced | Replica identity and `before` images for updates and deletes; tables without primary keys |
| Advanced | Operational risks: an abandoned replication slot keeps WAL and can fill the source's disk; monitoring slot lag; permissions for a CDC user |
| Advanced | Schema changes during CDC (columns added, types changed) and how they appear in the stream |
| Advanced | The **transactional outbox** pattern: applications write events to an outbox table that CDC publishes |
| Advanced | Where CDC tools fit: Debezium streaming into Kafka (built in Module 2.16) and managed CDC services (Module 2.17) |

**How to learn it**

1. Read the topic file.
2. Enable logical decoding in your Docker PostgreSQL, create a slot with
   `test_decoding`, make changes, and read them with
   `pg_logical_slot_peek_changes` / `pg_logical_slot_get_changes`.
3. Draw the timeline of an initial snapshot followed by streaming, marking
   the log position where streaming must begin.

**Hands-on exercise — `cdc_lab/`**

1. Create a trigger-based audit table on `customers` and compare its
   output with logical decoding for the same changes.
2. Write a Python reader that polls a logical replication slot (using the
   SQL functions above), parses changes into change events (op, key,
   before/after, LSN, commit time), and lands them as JSON Lines.
3. Take an initial snapshot in a `REPEATABLE READ` transaction, record the
   slot's starting position, and apply streamed changes to a target table
   with `MERGE` (including deletes); prove the target equals the source.
4. Show a delete that timestamp-based extraction missed in Topic 06 being
   captured by CDC.
5. Stop reading the slot, generate heavy writes, and watch WAL retention
   grow; write a check that alerts on slot lag.
6. Add a column to the source table mid-stream and observe the events.

**Checkpoint:**

- [ ] Compare query-based, trigger-based, and log-based CDC.
- [ ] Explain logical decoding and replication slots.
- [ ] Describe the snapshot + streaming handoff.
- [ ] Apply change events to a target correctly, including deletes.
- [ ] Explain the risk of abandoned replication slots.

**Common mistakes:** leaving replication slots unmonitored; applying
changes out of order; treating CDC as "just faster incremental" without
handling schema changes and deletes.

---

## 9. Phase D — Other Ingestion Channels (Intermediate → Advanced)

### Topic 08 — [Webhooks and push-based ingestion](08-webhooks-and-push-based-ingestion.md)

**Why here:** Some sources push data to you instead of waiting to be
polled. Push delivers data fast, but brings its own reliability and
security problems.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Pull vs push ingestion; webhooks as HTTP `POST` requests sent by the source when something happens |
| Basics | A minimal webhook receiver (a small FastAPI endpoint — full API design is in Module 2.22) |
| Basics | Responding fast: acknowledge with `2xx` quickly, then process asynchronously; providers retry on timeouts or errors |
| Intermediate | **Signature verification**: HMAC signatures over the raw request body with a shared secret, compared in constant time (`hmac.compare_digest`) |
| Intermediate | **Replay protection**: signed timestamps and a tolerance window |
| Intermediate | **At-least-once delivery**: duplicates are normal — deduplicate by event id |
| Intermediate | **No ordering guarantees**: use event timestamps or version numbers; fetch the latest state from the API when order matters |
| Intermediate | Land first, process later: write the raw, verified payload to bronze (or a queue) before any parsing |
| Advanced | **Webhooks lose events** (outages, misconfiguration, provider bugs): periodic reconciliation pulls via the API (Topics 04–06) |
| Advanced | Security: HTTPS only, secret rotation, IP allowlists where offered, payload size limits, and never trusting payload content without verification |
| Advanced | Dead-letter handling for payloads that fail parsing; replaying stored payloads after a bug fix |
| Advanced | Local development: exposing a local receiver with a tunnel service (awareness) and replaying recorded payloads in tests |
| Advanced | Other push channels: object-storage event notifications (e.g. "a file was created in this bucket"), message queues, and event streams (Module 2.16) |

**How to learn it**

1. Read the topic file.
2. Read the webhook documentation of two real providers (for example a
   payments provider and a code-hosting provider) and compare how they
   sign payloads, retry, and order events.
3. Add a "webhook sender" to your mock API that signs payloads, retries on
   failure, sends duplicates, and sends events out of order.

**Hands-on exercise — `webhook_receiver/`**

1. Build a FastAPI receiver that verifies the HMAC signature and timestamp,
   rejects invalid requests with `401`, writes the raw payload to a
   landing folder (one JSON Lines file per minute), and returns `200`
   within 100 ms.
2. Deduplicate by event id in a separate processing step and apply events
   in version order to a target table.
3. Stop the receiver for five minutes while the sender keeps sending;
   restart it and show which events arrived via provider retries.
4. Implement a nightly reconciliation job that pulls recent changes from
   the mock API and repairs anything webhooks missed.
5. Test: bad signature, expired timestamp, duplicate event, out-of-order
   events, malformed JSON (sent to a dead-letter folder).

**Checkpoint:**

- [ ] Verify webhook signatures and prevent replays.
- [ ] Explain at-least-once delivery and deduplicate events.
- [ ] Explain why webhooks need reconciliation pulls.
- [ ] Design a receiver that acknowledges fast and processes later.

**Common mistakes:** heavy processing before responding (causing provider
retries and duplicates); verifying signatures on re-serialised JSON instead
of the raw body; trusting webhooks as the only source of truth.

---

### Topic 09 — [HTML parsing and responsible scraping](09-html-parsing-and-responsible-scraping.md)

**Why here:** Sometimes the only source is a web page. Scraping is the
most fragile and most legally sensitive ingestion method, so it comes after
you know every better alternative.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | **Responsibility first**: check for an official API, data export, or open dataset before scraping; read the site's terms of service; respect `robots.txt` (`urllib.robotparser`); consider copyright and personal-data laws; when in doubt, ask the site owner or your legal team |
| Basics | HTML structure: elements, attributes, the DOM tree |
| Basics | Parsing with **BeautifulSoup** (with the `lxml` parser) and CSS selectors; `lxml` with XPath |
| Intermediate | Extracting tables, lists, links, and detail pages; following pagination links politely |
| Intermediate | Structured data hidden in pages: JSON-LD (`<script type="application/ld+json">`), embedded JSON state, and the site's own JSON endpoints — often more stable than HTML |
| Intermediate | Politeness: low request rates, delays, caching, identifying yourself with a descriptive `User-Agent` and contact, and scraping off-peak |
| Intermediate | Encodings, relative URLs (`urljoin`), and whitespace cleanup |
| Advanced | JavaScript-rendered pages: headless browsers (e.g. Playwright) — their cost and fragility, and why a JSON endpoint is usually better |
| Advanced | Brittleness management: saving raw HTML to bronze, selector tests on saved pages, detecting layout changes (e.g. required fields suddenly missing) and alerting |
| Advanced | Boundaries you must not cross: bypassing authentication, paywalls, CAPTCHAs, or anti-bot protections; collecting personal data without a lawful basis; ignoring a site's explicit refusal |

**How to learn it**

1. Read the topic file.
2. Write a scraping decision checklist (API available? terms allow it?
   `robots.txt`? personal data? rate?) and apply it to three websites.
3. Practise on sites built for scraping practice or on pages you host
   yourself.

**Hands-on exercise — `scraper/`**

1. Serve a small static "product catalogue" website locally (paginated
   listing pages and detail pages, some with JSON-LD).
2. Build a scraper that checks `robots.txt`, rate-limits itself, sets a
   descriptive `User-Agent`, and caches pages.
3. Extract products from JSON-LD when present and from HTML otherwise;
   save raw HTML and parsed JSON Lines to bronze.
4. Change the site's HTML layout and show your validation detecting
   missing fields instead of silently producing empty values.
5. Write selector unit tests against saved HTML fixtures.

**Checkpoint:**

- [ ] Decide whether scraping is appropriate and legal for a source.
- [ ] Parse HTML with CSS selectors and XPath.
- [ ] Prefer structured data (JSON-LD, JSON endpoints) over HTML.
- [ ] Detect layout changes before they corrupt data.

**Common mistakes:** scraping when an API exists; aggressive request rates;
no raw-HTML retention (so bugs cannot be reprocessed); silently accepting
empty fields after a site redesign.

---

### Topic 10 — [SFTP and file-drop ingestion](10-sftp-and-file-drop-ingestion.md)

**Why here:** Banks, retailers, logistics firms, and government partners
still exchange data as files on SFTP servers and shared storage. File
ingestion looks simple and fails in subtle ways.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | SFTP (over SSH) vs FTP and FTPS; why plain FTP is unacceptable for sensitive data |
| Basics | Connecting with `paramiko`: key-based authentication, listing directories, downloading files, closing connections |
| Basics | **Host key verification** with `known_hosts` — never auto-accepting unknown host keys in production |
| Intermediate | **Completeness detection**: is the partner still uploading? Stable size over time, `.done` / `.ok` marker files, upload-then-rename conventions, and control (manifest) files listing expected files and row counts |
| Intermediate | **Checksums** (SHA-256) for integrity, and trailer/control totals inside files (Module 2.5) |
| Intermediate | **File registry**: recording every processed file (path, size, modification time, checksum, status) so each file is processed exactly once, even across re-runs |
| Intermediate | Post-processing: archiving or moving processed files (if permitted), or leaving them and relying on the registry |
| Intermediate | Filename conventions with dates and sequence numbers; detecting missing or out-of-sequence files |
| Advanced | Redelivered and corrected files: the same name with different content, `_v2` files, and replacement rules agreed with the partner |
| Advanced | Encrypted and compressed deliveries: PGP-encrypted files (`gpg`), ZIP archives with several files, and nested archives |
| Advanced | Object-storage drop zones (a partner writes to a bucket prefix) and event-driven processing via storage notifications (Module 2.17) |
| Advanced | Freshness monitoring: alerting when an expected daily file has not arrived by its agreed time (freshness SLAs from Module 2.1) |
| Advanced | Operational hygiene: dedicated partner accounts, restricted directories, key rotation, and connection retries with limits |

**How to learn it**

1. Read the topic file.
2. Run an SFTP server in Docker with key-based authentication and a
   partner "upload" script that writes files slowly, sometimes twice, and
   sometimes with bad checksums.
3. Write a file-exchange agreement for a fictional partner: naming, timing,
   completeness signal, checksums, encryption, and corrections.

**Hands-on exercise — `sftp_ingestion.py`**

1. Connect with `paramiko` using a private key and a pinned host key.
2. Poll a directory; process only files with a matching `.done` marker;
   verify SHA-256 checksums from a manifest file.
3. Record every file in a registry table and skip already-processed files
   on re-runs; handle a corrected file re-sent under the same name
   according to your agreement.
4. Decrypt a PGP-encrypted file and extract a ZIP archive into bronze,
   keeping the original file.
5. Detect a missing daily file by 07:00 and exit with a non-zero code and a
   clear message.
6. Test: half-uploaded file, duplicate delivery, bad checksum, missing
   file, and an unknown host key (must fail).

**Checkpoint:**

- [ ] Connect to SFTP securely with key and host-key verification.
- [ ] Detect when a file is completely delivered.
- [ ] Process each file exactly once with a registry.
- [ ] Verify integrity with checksums and control totals.
- [ ] Alert on missing files.

**Common mistakes:** processing files that are still uploading;
`AutoAddPolicy` for host keys; relying only on file names to detect
duplicates; deleting partner files you were not allowed to delete.

---

## 10. Phase E — Build vs Buy (Advanced)

### Topic 11 — [Ingestion frameworks: dlt and managed connectors](11-ingestion-frameworks-dlt-and-managed-connectors.md)

**Why last:** You have now built authentication, pagination, rate
limiting, incremental state, schema handling, and idempotent loading by
hand. Frameworks and managed services do much of this for you — and you
can finally judge them properly.

**What to learn**

| Level | Concepts |
| --- | --- |
| Basics | Build vs buy: the long-term cost of maintaining custom connectors (API changes, auth changes, schema drift) vs licence and usage costs |
| Basics | **dlt (data load tool)**: pipelines, sources, and resources (`@dlt.resource`, `@dlt.source`); destinations such as DuckDB, PostgreSQL, filesystem, and cloud warehouses |
| Basics | dlt write dispositions: `append`, `replace`, `merge` (with primary and merge keys) |
| Intermediate | dlt **incremental loading** (`dlt.sources.incremental`) and pipeline state — compared with your Topic 06 implementation |
| Intermediate | dlt **schema inference and evolution**: nested JSON normalised into child tables, new columns added automatically, and schema contracts to freeze or restrict changes |
| Intermediate | The declarative REST API source: configuring auth, pagination, and incremental parameters instead of writing code |
| Intermediate | Protocols and ecosystems: **Singer** taps and targets (and Meltano), **Airbyte** connectors (open source and cloud) — awareness and when you meet them |
| Advanced | **Managed connectors** (e.g. Fivetran and similar SaaS tools) and cloud-native services (database migration and CDC services on major clouds — Module 2.17): what they automate, pricing models (often per active row), and limits |
| Advanced | **Evaluation criteria**: connector coverage and quality, incremental and CDC support, delete handling, schema-drift behaviour, backfills, observability, security and data residency, cost at your volume, and lock-in |
| Advanced | Wrapping any tool with your own controls: source contracts, completeness checks, data-quality checks (Module 2.11), and freshness monitoring (Module 2.20) |
| Advanced | When custom code still wins: unusual sources, strict cost or latency needs, complex auth, or sources no vendor supports |

**How to learn it**

1. Read the topic file.
2. Re-implement your Topic 06 incremental API extraction with dlt and
   compare lines of code, behaviour on failures, and handling of schema
   changes.
3. Read the documentation of two managed connector products for the same
   source and compare their incremental, delete, and pricing behaviour.

**Hands-on exercise — `dlt_pipelines/`**

1. Build a dlt pipeline for your mock API customers with `merge`
   disposition, `dlt.sources.incremental` on `updated_at`, and a DuckDB
   destination.
2. Rebuild it with dlt's declarative REST API source configuration.
3. Add a nested field and a new column to the mock API; observe how dlt
   evolves the schema, then enable a schema contract that rejects new
   columns and observe the failure.
4. Load the same data with your hand-written extractor and prove both
   produce identical row sets.
5. Write a build-vs-buy decision record for five sources (a popular CRM, a
   payments API, an internal PostgreSQL database, a partner SFTP drop, a
   niche industry API) using the evaluation criteria.

**Checkpoint:**

- [ ] Build an incremental pipeline with dlt.
- [ ] Explain how dlt handles state, schema evolution, and merges.
- [ ] Compare Singer, Airbyte, and managed connectors at a high level.
- [ ] Make a build-vs-buy decision with written criteria.

**Common mistakes:** assuming a connector handles deletes or late data
without checking; letting automatic schema evolution add columns nobody
reviews; ignoring per-row pricing at scale; buying a tool and dropping your
own completeness and quality checks.

---

## 11. Consolidate — practice questions

When all eleven topics are done, open
[`practice-questions.md`](practice-questions.md). For every question:

1. Write the **source contract**: access method, authentication,
   pagination, limits, change and delete behaviour, volume, and owner.
2. Choose the strategy (full, incremental, CDC, push, file) and justify it
   against the freshness requirement.
3. Design state: what is stored, where, and when it advances.
4. List failure modes and how your design handles each.
5. Implement it against the mock source and prove completeness and
   idempotency with tests.
6. Estimate requests, run time, and cost per day.

---

## 12. Module mini-project — a multi-source ingestion platform

This is the proof that you have finished the module.

**Scenario:** A retail company needs its bronze layer fed from five
sources, all landing into a lake (MinIO or local Parquet/JSON Lines) with
consistent metadata:

1. **SaaS CRM API** (your mock API): OAuth 2.0 client credentials with
   60-second tokens, cursor pagination, strict rate limits, `updated_since`
   filtering, late commits, and hard deletes.
2. **Orders database** (PostgreSQL): log-based CDC via logical decoding
   with an initial snapshot.
3. **Payments provider**: signed webhooks with duplicates and out-of-order
   delivery, plus a reconciliation API.
4. **Logistics partner**: daily PGP-encrypted CSV files on SFTP with `.done`
   markers, manifests, and occasional corrected re-sends.
5. **Marketing platform**: loaded with **dlt** using its REST API source.

Build `ingestion_platform/`, a `uv` project with:

- **Source contracts** for all five sources.
- **Extractors** for sources 1–4 built on your own client, auth, paginator,
  rate-limiter, and registry components; source 5 via dlt.
- **A common landing format**: raw payloads plus `_source`, `_run_id`,
  `_extracted_at`, and request/file metadata, partitioned by source and
  date.
- **State management**: watermarks, cursors, replication positions, and a
  file registry in a metadata database, advanced only after data is
  durably landed.
- **Reliability**: timeouts everywhere, retries only for retryable errors,
  honouring `Retry-After`, circuit breakers, resumable runs, and
  reconciliation jobs for webhooks and deletes.
- **Observability**: a `pipeline_runs` record per run (records landed,
  requests, retries, 429s, duration) and a freshness check per source that
  exits non-zero when a source is late.
- **Security**: credentials from environment variables only, redacted
  logs, verified webhook signatures, pinned SFTP host keys.
- **Tests**: unit tests with mocked transports for every failure mode, and
  integration tests against the Docker services, including kill-and-resume
  runs.
- **A build-vs-buy note** explaining why source 5 used dlt and sources 1–4
  did not (or would not in a real company).

**Grading yourself:** killing any extractor at any moment and re-running
it produces bronze data with no gaps and no duplicates; deletes from the
CRM and the orders database are captured; no secret appears anywhere in
logs or code; and every source's freshness is visible after each run.

---

## 13. Module self-assessment — exit criteria

Only move to Module 2.10 when you can tick every box without looking at your
notes:

- [ ] I can debug API extractions using status codes and headers.
- [ ] I can build tested API clients with sessions and explicit timeouts.
- [ ] I can authenticate with keys and OAuth 2.0, and refresh tokens
      safely.
- [ ] I can paginate completely with every common pagination style and
      resume from checkpoints.
- [ ] I can handle rate limits proactively and retry only safe failures.
- [ ] I can design full, incremental, and backfill extractions with safe
      watermarks, lookbacks, and delete handling.
- [ ] I can explain log-based CDC and apply change events correctly.
- [ ] I can receive webhooks securely and reconcile them.
- [ ] I can decide when scraping is appropriate and do it responsibly.
- [ ] I can ingest SFTP file drops exactly once with integrity checks.
- [ ] I can use dlt and make a build-vs-buy decision.
- [ ] I have finished all practice questions and the mini-project.

---

## 14. Recommended reading and references

| Resource | Relevant topics |
| --- | --- |
| MDN Web Docs — HTTP overview, status codes, headers, conditional requests, caching | 01, 05 |
| httpx documentation (clients, timeouts, streaming, authentication, transports) and requests documentation | 02, 03 |
| RFC 6749 (OAuth 2.0) and the OAuth 2.0 Security Best Current Practice; oauth.net guides | 03 |
| Public API design guides from major providers (e.g. GitHub, Stripe, Google) — pagination, rate limits, idempotency, webhooks | 04, 05, 08 |
| `tenacity` documentation | 05 |
| PostgreSQL documentation — logical decoding, replication slots, and logical replication | 07 |
| Debezium documentation — CDC concepts, snapshots, and event structure | 07 |
| *Designing Data-Intensive Applications* — Martin Kleppmann, chapters on replication and change data capture | 06, 07 |
| Beautiful Soup and lxml documentation; Python `urllib.robotparser` | 09 |
| Paramiko documentation | 10 |
| dlt documentation — sources, incremental loading, schema evolution and contracts, REST API source | 11 |
| *Fundamentals of Data Engineering* — Joe Reis and Matt Housley, chapter on ingestion | All topics |

---

## 15. Where this module leads

| This module's idea | Where it goes deeper |
| --- | --- |
| Many API requests in parallel; async clients | 2.10 Concurrency and Parallelism in Practice |
| Validating raw payloads and source contracts | 2.11 Data Validation, Contracts, and Quality |
| Incremental processing, backfills, and checkpoints on the transformation side | 2.12 Transformation Patterns and Pipeline Design |
| Scheduling extractions, sensors for file arrival, retries and SLAs | 2.13 Orchestration and Workflow Management |
| Debezium, Kafka, and streaming CDC | 2.16 Streaming and Event-Driven Data |
| Object-storage drop zones, event notifications, managed CDC services | 2.17 Cloud Storage and Cloud Data Platforms |
| Cloud secrets managers for API keys and SSH keys | 2.18 Containers, Infrastructure, and CI/CD |
| Testing extractors with containers and recorded fixtures | 2.19 Testing Data Pipelines |
| Freshness alerts, lineage, and PII in ingested data | 2.20 Observability, Lineage, Governance, and Security |
| Webhook receivers as production APIs | 2.22 Serving Data for Analytics, ML, and AI |

Every downstream table is only as good as the data that entered the
platform. The habits you build here — write the source contract, land raw
data first, advance state only after saving, retry only what is safe, and
reconcile against the source — are what make a data platform trustworthy
from its very first hop.
