# 01 --- FastAPI Data Services

**Stage:** Stage 2 --- Python for Data Engineering\
**Module:** 2.22 --- Serving Data for Analytics, ML, and AI\
**Topic:** 01 --- FastAPI Data Services

> Build secure, tested, observable, production-grade data APIs using
> FastAPI and PostgreSQL, progressing from first principles to
> production operations.

## Learning Objective

The objective is not merely to learn FastAPI syntax. It is to learn how
a Data Engineer creates a controlled **data-serving boundary** between
trusted platform data and real consumers.

``` text
Basic → Fundamental → Intermediate → Advanced → Production
```

The serving contract is explicit:

``` text
Consumer → Shape → Latency → Freshness → Availability → Access Rules → Cost
```

## Why Data Engineers Build Data APIs

A data API exposes governed data to applications without exposing the
underlying database directly.

``` text
Warehouse / Lakehouse → Gold / Trusted Data → FastAPI → Application / ML / AI
```

Direct database exposure creates coupling, uncontrolled queries, weak
authorization boundaries, PII leakage risk, unstable contracts, and poor
operational control. FastAPI is the first serving layer in this module's
dependency chain; later modules cover aggregates/caching, semantic
metrics, feature stores, and vector pipelines.

## Consumer Contract

Before implementing an endpoint, define:

-   **Consumer** --- who calls it?
-   **Response shape** --- what fields are returned?
-   **Latency** --- how quickly must it respond?
-   **Freshness** --- how current must data be?
-   **Availability** --- what reliability is expected?
-   **Access rules** --- which rows/columns are allowed?
-   **Cost constraints** --- how much database work is acceptable?

Use this template repeatedly:

``` markdown
## Consumer Contract
### Consumer
...
### Response Shape
...
### Latency Requirement
...
### Freshness Requirement
...
### Availability Requirement
...
### Access Rules
...
### Cost Constraints
...
```

## HTTP and API Fundamentals

An API is a defined interface through which systems communicate. For a
data service, understand requests, responses, HTTP methods, headers,
query parameters, path parameters, request/response bodies, JSON,
serialization, and status codes.

``` http
GET /orders?status=completed&limit=50
Authorization: Bearer <token>
Accept: application/json
```

Important status codes:

  Code   Meaning                 Example
  ------ ----------------------- --------------------------
  200    OK                      Successful read
  202    Accepted                Export job accepted
  304    Not Modified            ETag validated
  400    Bad Request             Invalid request
  401    Unauthorized            Missing/invalid identity
  403    Forbidden               Authenticated but denied
  404    Not Found               Resource absent
  409    Conflict                State conflict
  422    Validation failure      Invalid input schema
  429    Too Many Requests       Rate limit exceeded
  500    Internal Server Error   Unexpected failure

HTTP is the transport contract; the data contract must be designed
deliberately on top of it.

## FastAPI Fundamentals

FastAPI is a Python framework for HTTP APIs built around type hints,
validation, OpenAPI generation, and ASGI.

``` python
from fastapi import FastAPI

app = FastAPI(title="Data Service")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Run locally:

``` bash
uvicorn app.main:app --reload
```

A request flows through:

``` text
Client → HTTP → Uvicorn / ASGI → FastAPI → Application layers → PostgreSQL
```

## Pydantic and Data Contracts

Pydantic validates request data and defines response contracts.

``` python
from pydantic import BaseModel, Field

class CustomerResponse(BaseModel):
    customer_id: int
    name: str = Field(min_length=1, max_length=200)
    region: str

class PageRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=500)
```

The contract chain is:

``` text
Python type hints → Pydantic → Validation → API contract → OpenAPI
```

Use required fields, optional fields, defaults, nested models,
validation errors, response models, serialization, and generated
schemas. Response models are also security boundaries: database columns
should not automatically become public API fields.

## OpenAPI and Documentation

FastAPI generates OpenAPI from route definitions, Pydantic models, and
security metadata. Common endpoints are `/docs`, `/redoc`, and
`/openapi.json`.

Document request schemas, response schemas, parameters, status codes,
authentication, and errors. OpenAPI supports frontend consumers, data
applications, ML services, platform teams, testing, and API governance.
Treat it as a **consumer contract**, not merely a documentation page.

## Uvicorn and ASGI

Uvicorn is an ASGI server. ASGI provides the application/server
interface used by FastAPI.

``` text
Client
  ↓
HTTP
  ↓
Uvicorn / ASGI
  ↓
FastAPI
  ↓
Application layers
  ↓
Database
```

Development commonly uses `--reload`; production requires deliberate
worker, resource, and lifecycle decisions. Multiple workers increase
process-level capacity but also increase memory and possible
database-pool demand.

## Layered Architecture

Use a clean boundary:

``` text
API / Router
    ↓
Service Layer
    ↓
Repository / Data Access Layer
    ↓
PostgreSQL
```

Responsibilities:

-   **Router:** HTTP concerns, parameters, dependencies, response
    mapping.
-   **Service:** serving/business orchestration.
-   **Repository:** SQL and database access.
-   **Schemas:** request/response contracts.
-   **Configuration:** environment-aware settings.
-   **Database layer:** pools, lifecycle, connection management.

Recommended structure:

``` text
serving/api/
├── app/
│   ├── main.py
│   ├── routers/
│   ├── services/
│   ├── repositories/
│   ├── schemas/
│   ├── dependencies/
│   ├── config/
│   └── database/
└── tests/
```

Putting SQL directly in route handlers mixes transport, persistence,
authorization, and business concerns and makes testing harder.

## Dependency Injection

FastAPI dependency injection uses `Depends` to supply reusable resources
and policies.

``` python
from fastapi import Depends

async def get_current_user() -> User:
    ...

@app.get("/customers")
async def customers(user: User = Depends(get_current_user)):
    ...
```

Use dependencies for settings, database pools, current users,
authentication, and authorization. Dependency injection improves
testability, reuse, separation of concerns, security, and
maintainability.

## PostgreSQL Connection Management

Use PostgreSQL as the primary example and the roadmap's pooled-driver
approach. Connections are expensive resources.

**Bad:**

``` text
Request → Create DB connection → Query → Close
```

**Good:**

``` text
Application startup → Create connection pool
Requests → Reuse pool connections
Application shutdown → Close pool
```

Pool sizing is capacity planning. If four workers each allow twenty
database connections, the application can potentially demand about
eighty connections. Compare this with PostgreSQL limits and other
clients. More connections do not automatically improve throughput.

Use FastAPI lifespan for application startup/shutdown and ensure
connections are acquired and released promptly.

## Sync vs Async

Synchronous code executes directly; asynchronous code can suspend while
waiting for I/O.

``` python
@app.get("/customers")
async def list_customers():
    rows = await async_database_call()
    return rows
```

Critical rule:

> `async def` does not automatically make blocking code asynchronous.

Blocking database calls, filesystem calls, synchronous HTTP clients, or
CPU-heavy transformations inside async endpoints can block the event
loop. Async is primarily valuable for I/O-bound workloads; CPU-bound
work needs an appropriate compute boundary.

## Core Data API

Build a realistic data product rather than a meaningless toy API. Use:

``` text
Customers
Orders
Products
Regions
```

Representative endpoints:

``` text
GET /customers
GET /customers/{customer_id}
GET /orders
GET /orders/{order_id}
GET /products
```

For every endpoint explicitly state consumer, contract, request,
response, latency, freshness, access rules, and cost implications.

## Pagination and Keyset Cursors

Returning millions of rows is dangerous. Bound page size.

Large `OFFSET` queries can require the database to walk past many rows
before returning the desired page. Prefer keyset/cursor pagination for
large ordered datasets.

``` sql
SELECT order_id, created_at, amount
FROM gold_orders
WHERE (created_at, order_id) < (%s, %s)
ORDER BY created_at DESC, order_id DESC
LIMIT %s;
```

A cursor should represent the last ordering keys. Use stable,
deterministic ordering; timestamps alone may collide, so a unique ID is
a useful tie-breaker. The cursor must match the selected sort order.
Avoid materializing huge result sets in application memory.

## Filtering

Examples:

``` text
GET /orders?status=completed
GET /orders?region=APAC
GET /orders?customer_id=123
```

Validate allowed filters and compose parameterized predicates.

**Bad:**

``` python
query = f"SELECT ... WHERE region = '{region}'"
```

**Good:**

``` python
query = "SELECT ... WHERE region = %s"
params = (region,)
```

Never blindly concatenate user input into SQL. SQL injection prevention
is a data-service responsibility.

## Sorting

Clients should not inject arbitrary SQL expressions as sort fields. Use
an allowlist:

``` python
ALLOWED_SORT_FIELDS = {
    "created_at": "created_at",
    "order_id": "order_id",
    "amount": "amount",
}
```

Control direction explicitly. Sorting and pagination are coupled:
changing the ordering changes cursor semantics and usually the
supporting index strategy.

## Authentication

Authentication answers **who are you?** Cover API keys, bearer tokens,
OAuth2, JWT validation awareness, current-user dependencies, credential
handling, and secrets.

API keys can suit controlled integrations; stronger identity systems are
appropriate when user identity, delegated access, scopes, or enterprise
identity are required. A token must be validated according to the
identity system; syntactic validity is not enough.

## Authorization

Authorization answers **what are you allowed to access?** Cover roles,
permissions, resource access, regional access, tenant boundaries,
row-level access, and column-level access.

Example:

``` text
User region = APAC
Allowed = APAC customer/order data
Denied = EU customer/order data
```

Derive authorization from trusted identity context. Never rely on a
client-supplied region or tenant ID as proof of permission.

## Row-Level and Column-Level Data Protection

The database may contain more data than an API consumer needs. Use
row-level filtering, database-level row security awareness, column-level
protection, least privilege, and PII masking.

``` text
Database contains more data
        ↓
Authorization + projection
        ↓
API exposes only allowed data
```

For example, the API may return `customer_id`, `name`, and `region`
while withholding email, phone, or address. Use explicit response models
rather than returning every selected database column.

## Consistent Error Handling

Use a stable error body:

``` json
{
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "Order was not found",
    "request_id": "..."
  }
}
```

Cover validation, authentication, authorization, not-found, conflict,
rate-limit, and internal failures. Do not expose SQL, credentials, stack
traces, internal table names, or implementation details.

## Streaming Large Responses

A huge JSON response can exhaust memory:

``` text
Load all rows → Serialize all rows → Return
```

Prefer:

``` text
Read chunk → Serialize chunk → Send → Read next chunk
```

Use NDJSON or CSV when appropriate. Consider chunk size, cursor
lifetime, backpressure, timeouts, client disconnects, and cancellation.
Streaming controls memory behavior but does not make resource usage
free.

## Arrow and Parquet Downloads

JSON is not always the right format for analytical data. Arrow provides
a columnar in-memory representation; Parquet is a columnar analytical
file format. A large export can follow:

``` text
Gold data → Arrow/table representation → Parquet → Object storage → Download URL
```

This is appropriate for large analytical transfers where JSON
serialization is inefficient.

## Asynchronous Export Jobs

Use an asynchronous pattern for long-running exports:

``` text
Client
  ↓
POST /exports
  ↓
202 Accepted + job_id
  ↓
Background/worker processing
  ↓
Generate Parquet
  ↓
Object storage
  ↓
GET /exports/{job_id}
  ↓
Status + expiring/presigned URL
```

`202 Accepted` means the request has been accepted but the work is not
complete. This topic teaches the serving architecture, not a full
distributed task-processing system.

## Timeouts and Resource Protection

Protect the API and PostgreSQL from accidental or malicious expensive
work. Cover request timeouts, database query timeouts, connection
timeouts, request-size limits, query-cost limits, cancellation, bounded
page sizes, and database protection.

A data API can become a denial-of-service vector without an attacker: an
unbounded export or expensive query can consume shared capacity.

## Rate Limiting

Rate limiting controls request volume. Define limits per user, API key,
tenant, or service identity where appropriate. Exceeding a limit
commonly returns `429 Too Many Requests`.

Think about the combined model:

``` text
Authentication + Authorization + Rate Limiting + Query Cost Limits
```

Authentication identifies the caller; authorization controls access;
rate limiting controls frequency; query-cost limits control expensive
work. Distributed deployments need shared or infrastructure-aware state
rather than only process-local counters.

## ETag and Cache-Control

HTTP conditional requests can prevent retransmission of unchanged data:

``` text
Underlying data version → ETag → If-None-Match → 304 Not Modified
```

Use `Cache-Control` to communicate freshness. Derive ETags from a
trustworthy data/representation version. This is HTTP caching; the full
Redis/cache-layer topic belongs to Topic 02.

## API Versioning and Deprecation

Example:

``` text
/v1/orders
/v2/orders
```

Distinguish additive from breaking changes. Version when a stable
consumer contract needs explicit compatibility management. Define
deprecation communication, migration strategy, and retirement. Do not
version every trivial internal change automatically.

## OpenAPI as a Data Product Contract

OpenAPI should describe stable expectations between provider and
consumer: paths, parameters, schemas, status codes, authentication, and
error structures. Use contract testing to prevent accidental
incompatible changes. Treat data APIs as **data products**, not HTTP
wrappers around database tables.

## Observability with OpenTelemetry

Measure logs, metrics, and traces. At minimum capture:

-   p50, p95, p99 latency;
-   throughput;
-   error rate;
-   timeouts;
-   database latency;
-   query duration;
-   freshness.

Trace the request path:

``` text
Client → FastAPI span → Service span → Database span
```

Use request IDs for correlation. If p95 suddenly increases, traces
should help distinguish application latency from database latency,
connection-pool contention, serialization, or downstream waits.

## Testing FastAPI Data Services

### Unit tests

Test validation, business/service logic, and repository behavior where
appropriate.

### API tests

Use FastAPI/httpx test patterns to verify status codes, response bodies,
validation, errors, pagination, filtering, and sorting.

### Async tests

Use an async-capable client/test strategy for async endpoints.

### Integration tests

Test the real boundary:

``` text
FastAPI → PostgreSQL
```

Unit tests alone can miss SQL mistakes, schema mismatches, transaction
behavior, indexes, and database-specific semantics. Disposable
PostgreSQL environments such as Testcontainers are appropriate when
adopted by the project.

### Contract tests

Validate API schemas, status codes, parameters, and compatibility with
OpenAPI.

### Security tests

Test unauthenticated access, unauthorized access, regional access, PII
exposure, invalid filters, and SQL injection attempts.

## Load Testing

Use Locust or k6. Model realistic traffic:

``` text
GET /orders
GET /orders/{id}
GET /customers
filtered order queries
paginated queries
```

Measure concurrency, throughput, p50, p95, p99, error rate, and database
load. Average latency is insufficient because tail latency can be
dramatically worse.

## Production Deployment Awareness

Understand:

``` text
Load Balancer
      ↓
FastAPI containers
      ↓
Connection pools
      ↓
PostgreSQL
```

Cover Docker, environment variables, secrets, configuration, multiple
workers, reverse-proxy awareness, health endpoints, readiness/liveness
concepts, graceful shutdown, and database pool sizing. This is
deployment awareness, not a Kubernetes course.

## End-to-End Production Project

Build one realistic PostgreSQL-backed service for **Orders + Customers +
Products + Regions**. Implement incrementally:

``` text
FastAPI
→ Pydantic
→ PostgreSQL
→ Repository/Service layers
→ Dependency injection
→ Pooling + async I/O
→ Pagination/filtering/sorting
→ Authentication/authorization
→ Regional access + PII protection
→ Errors
→ Streaming
→ Async Parquet export
→ ETag/Cache-Control
→ Rate limits/timeouts
→ OpenAPI/OpenTelemetry
→ Tests
→ Load tests
→ Docker/deployment awareness
```

## Practical Labs

### Lab 1 --- Basic FastAPI endpoint

Create `GET /health`; run locally and inspect OpenAPI.

### Lab 2 --- Pydantic validation

Create customer request/response models and test invalid fields.

### Lab 3 --- PostgreSQL integration

Create `GET /customers/{customer_id}` backed by PostgreSQL.

### Lab 4 --- Layered architecture

Separate router, service, and repository.

### Lab 5 --- Dependency injection

Inject settings, database resources, and current user.

### Lab 6 --- Connection pooling

Create a pool at startup and close it at shutdown.

### Lab 7 --- Keyset pagination

Implement deterministic cursor pagination for orders.

### Lab 8 --- Safe filtering/sorting

Add allowlisted filters and sort fields.

### Lab 9 --- Authentication

Protect endpoints and validate identity.

### Lab 10 --- Authorization/PII

Enforce regional access and explicit response projections.

### Lab 11 --- Streaming

Implement NDJSON or CSV streaming.

### Lab 12 --- Async Parquet export

Return `202`, track a job, create Parquet, and expose status/download.

### Lab 13 --- ETag/Cache-Control

Implement conditional requests using a data version.

### Lab 14 --- Rate limits/timeouts

Protect resources and expensive queries.

### Lab 15 --- OpenTelemetry

Instrument HTTP, service, and database spans.

### Lab 16 --- Comprehensive tests

Add unit, API, async, integration, contract, and security tests.

### Lab 17 --- Load testing

Use Locust or k6; measure p50/p95/p99, throughput, errors, and database
load.

### Lab 18 --- Containerization

Run the service in Docker and verify configuration and lifecycle
behavior.

For every lab document: objective, prerequisites, task, expected
behavior, implementation guidance, validation, common mistakes, and
production takeaway.

## Debugging Scenarios

### p95 latency suddenly increases

Investigate API latency, database latency, query plan, connection pool
exhaustion, large result sets, missing pagination, blocking code, and
concurrency. Do not add workers before locating the bottleneck.

### Connection pool exhaustion

Inspect worker count, pool size, PostgreSQL limits, connection leaks,
long-running queries, transactions, streaming requests, and connection
release.

### Export memory explosion

Look for giant Python lists, giant JSON serialization, and full
materialization. Prefer cursor/chunked reads and Parquet writing.

### Cross-region data exposure

Treat it as a security incident. Check identity, authorization
dependencies, service policy, repository filtering, database policy,
cache scope if applicable, and negative security tests.

### Async API still has poor concurrency

Look for blocking database drivers, synchronous third-party clients,
filesystem operations, CPU-heavy work, and expensive serialization.

## Bad vs Good Engineering

  -------------------------------------------------------------------------------
  Bad approach            Why it fails             Better approach
  ----------------------- ------------------------ ------------------------------
  Connection per request  Connection               Pooling
                          overhead/storms          

  SQL in route            Poor                     Repository
                          separation/testability   

  String-interpolated SQL Injection risk           Parameterized SQL

  Large OFFSET            Increasing skip work     Keyset pagination

  Arbitrary sort fields   SQL injection/invalid    Allowlists
                          SQL                      

  PII by default          Leakage                  Explicit response models

  Auth without            Identity is not          Authorization policy
  authorization           permission               

  Blocking async code     Blocks event loop        Async I/O/appropriate worker

  Giant JSON export       Memory/latency pressure  Streaming/async Parquet

  Exposed SQL errors      Internal leakage         Stable error contract

  No timeout              Unbounded resource use   Timeouts

  No rate limit           Overload                 Rate limits

  No observability        Hard diagnosis           Logs/metrics/traces

  Happy-path tests only   Production failures      Failure/security/integration
                          escape                   tests

  Average latency only    Hides tail               p50/p95/p99
  -------------------------------------------------------------------------------

## Architecture Diagrams

### Request lifecycle

``` mermaid
sequenceDiagram
    participant C as Client
    participant U as Uvicorn/ASGI
    participant F as FastAPI
    participant S as Service
    participant R as Repository
    participant DB as PostgreSQL
    C->>U: HTTP request
    U->>F: ASGI request
    F->>F: Validate
    F->>S: Service call
    S->>R: Data request
    R->>DB: Parameterized SQL
    DB-->>R: Rows
    R-->>S: Data
    S-->>F: Result
    F-->>U: Response
    U-->>C: HTTP response
```

### Layered architecture

``` mermaid
flowchart TD
    A[API / Router] --> B[Service Layer]
    B --> C[Repository / Data Access]
    C --> D[(PostgreSQL)]
```

### Connection pooling

``` mermaid
flowchart LR
    R1[Request 1] --> P[Connection Pool]
    R2[Request 2] --> P
    R3[Request 3] --> P
    P --> DB[(PostgreSQL)]
```

### Authentication/authorization

``` mermaid
flowchart TD
    Req[Request] --> Auth[Authenticate]
    Auth --> Identity[Identity / Claims]
    Identity --> Policy[Authorization Policy]
    Policy --> Data[Permitted Data]
    Policy --> Deny[403 / Restricted Result]
```

### Streaming

``` mermaid
flowchart LR
    DB[(PostgreSQL)] --> Cursor[Cursor / Chunks]
    Cursor --> Encode[NDJSON / CSV]
    Encode --> Client[Client]
```

### Async export

``` mermaid
flowchart LR
    C[Client] --> API[POST /exports]
    API --> Accepted[202 + job_id]
    API --> W[Worker]
    W --> DB[(PostgreSQL)]
    W --> P[Parquet]
    P --> S[Object Storage]
    C --> Status[GET /exports/{job_id}]
    Status --> S
```

### Observability

``` mermaid
flowchart LR
    C[Client] --> API[FastAPI]
    API --> S[Service]
    S --> DB[(PostgreSQL)]
    API --> O[OpenTelemetry]
    S --> O
    O --> T[Telemetry Backend]
```

### Production deployment

``` mermaid
flowchart TD
    LB[Load Balancer] --> C1[FastAPI Container]
    LB --> C2[FastAPI Container]
    C1 --> P1[Pool]
    C2 --> P2[Pool]
    P1 --> DB[(PostgreSQL)]
    P2 --> DB
```

## Common Production Mistakes

1.  Treating FastAPI as only CRUD instead of a data-serving boundary.
2.  Exposing database tables directly.
3.  Putting SQL in route handlers.
4.  Skipping validation.
5.  No pagination or unbounded page sizes.
6.  Large OFFSET pagination.
7.  Unsafe dynamic SQL.
8.  Arbitrary sorting.
9.  Creating connections per request.
10. Blocking calls inside async endpoints.
11. Returning PII by default.
12. Authentication without authorization.
13. No rate limiting.
14. No query timeout.
15. No request-size limit.
16. Inconsistent error responses.
17. Huge JSON responses.
18. No API versioning strategy.
19. No observability.
20. Testing only individual functions.
21. No integration tests.
22. No load tests.
23. Ignoring database performance.

Each mistake matters because it creates a failure mode in correctness,
security, performance, reliability, or maintainability.

## Interview Preparation --- Questions and Answers

### Beginner

**What is FastAPI?** A Python framework for building HTTP APIs using
type hints, validation, OpenAPI, and ASGI.

**What is an API?** A defined interface through which systems
communicate; a data API exposes controlled data operations.

**What is Pydantic?** A typed data-modeling and validation library used
to define and enforce API contracts.

**What is Uvicorn?** An ASGI server commonly used to run FastAPI
applications.

**What is OpenAPI?** A machine-readable description of API operations,
schemas, parameters, responses, and security requirements.

### Intermediate

**Why dependency injection?** It makes resources and policies reusable,
replaceable, and testable.

**Why connection pooling?** It reuses expensive database connections and
controls database concurrency.

**Why keyset pagination?** It avoids the growing skip work of large
offsets when supported by appropriate ordering/indexes.

**What is async I/O?** The ability to suspend during I/O waits so other
work can proceed on the event loop.

**How prevent SQL injection?** Parameterize values and allowlist SQL
identifiers.

**Authentication vs authorization?** Authentication establishes
identity; authorization determines permitted access.

### Advanced / Senior

**How design a high-volume data API?** Start with the consumer contract,
bound work, use indexed access paths, pooling, keyset pagination, safe
filters/sorts, async I/O, timeouts, rate limits, observability, and load
testing.

**How protect PostgreSQL from expensive queries?** Use pagination,
allowlists, indexes, query timeouts, pool limits, rate limits, and
query-cost limits.

**How serve millions of rows?** Use pagination, streaming, or
asynchronous Parquet export rather than one giant JSON response.

**How implement row-level access?** Derive scope from trusted identity
and enforce it in the server-side data-access path, optionally with
database row-level security.

**How monitor p95/p99?** Instrument HTTP/application/database spans and
latency metrics, then correlate tail latency with the slow path.

**How design asynchronous exports?** Return `202` and a job ID, process
asynchronously, write the artifact to object storage, and return status
plus an expiring download URL.

**How design a multi-tenant API?** Treat tenant identity as trusted
authorization context, enforce tenant isolation at the data boundary,
optionally add database-level policies, and test cross-tenant access.

**How prevent PII leakage?** Use explicit response models, column
projection, least privilege, authorization, security tests, and safe
logging.

**How balance freshness, latency, correctness, and cost?** Make the
tradeoffs explicit in the consumer contract and choose the simplest
serving path that meets the required constraints.

## Final Assessment and Acceptance Checklist

You should be able to build a FastAPI data service; define Pydantic
contracts; structure router/service/repository layers; connect
PostgreSQL safely; use pooling and dependency injection; understand
async behavior; implement keyset pagination, safe filtering and sorting;
authenticate and authorize; enforce regional/row-level access; protect
PII; return consistent errors; stream large datasets; create
asynchronous exports; use ETag/Cache-Control; enforce timeouts and rate
limits; document with OpenAPI; instrument with OpenTelemetry; write
unit/integration/contract/security tests; load-test; reason about
deployment; and diagnose performance/security/reliability failures.

### Final challenge

> Design and implement a production-grade FastAPI Data Service for
> Orders and Customers backed by PostgreSQL, then secure, test, observe,
> and load-test it.

### Acceptance checklist

``` text
[ ] Consumer contract defined
[ ] Pydantic request/response contracts
[ ] Layered router/service/repository design
[ ] PostgreSQL + connection pool
[ ] Dependency injection
[ ] Async I/O without blocking calls
[ ] Keyset pagination
[ ] Safe filtering + allowlisted sorting
[ ] Parameterized SQL
[ ] Authentication + authorization
[ ] Regional/row-level access
[ ] PII protection
[ ] Consistent errors
[ ] NDJSON/CSV streaming
[ ] Parquet async export
[ ] ETag + Cache-Control
[ ] API versioning/deprecation strategy
[ ] Request/query timeouts and cost limits
[ ] Rate limiting
[ ] OpenAPI contract
[ ] OpenTelemetry
[ ] Unit/API/async tests
[ ] Integration tests
[ ] Contract tests
[ ] Security tests
[ ] Load tests with p50/p95/p99
[ ] Docker/deployment awareness
[ ] Operational debugging demonstrated
```

## Learning Loop and Scope Boundary

For every concept, use:

``` text
1. What is it?
2. Why does it exist?
3. Real-world analogy
4. Minimal Python example
5. FastAPI example
6. Data Engineering example
7. Production considerations
8. Common mistakes
9. Debugging example
10. Practice task
```

The operating habit is:

``` text
Read → Name the consumer and contract → Design the serving path → Build it → Secure it → Test it → Load it → Observe it → Change the data underneath → Write it down → Explain it aloud
```

**Scope boundary:** this file is focused on Topic 01. Detailed
aggregate/cache, semantic-layer, feature-store, and embedding/vector
implementation belongs to Topics 02--05 respectively.
