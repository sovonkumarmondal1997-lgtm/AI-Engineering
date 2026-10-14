# Pagination: Offset, Cursor, and Keyset

Pagination is one of the most important reliability concepts in API data extraction. An API may expose a logical dataset containing thousands, millions, or more records, while returning only a manageable subset in each HTTP response.

A production extractor therefore has to solve more than “how do I get the next page?” It must answer:

- How do I know which records belong to the extraction?
- How do I know when the extraction is complete?
- What happens if records are inserted, deleted, or updated while I am reading?
- How do I avoid duplicates and gaps?
- What happens if the process crashes after page 37?
- Can the extraction resume safely?
- What happens if the cursor expires?
- How do I detect an API that accidentally returns the same page forever?
- How can I demonstrate that the extracted dataset is complete?

The central idea of this chapter is:

> **Pagination is a data correctness and reliability problem, not merely an API convenience.**

There is no universally correct pagination strategy. The appropriate strategy depends on the source API contract, dataset behavior, ordering guarantees, workload, operational constraints, and recovery requirements.

---

## 1. Learning Objectives

By the end of this chapter, you should be able to:

1. Explain why APIs paginate large result sets.
2. Distinguish requested page size from the actual number of records returned.
3. Implement offset/page-number pagination with `httpx`.
4. Explain why offset pagination can produce duplicates and skipped records when the source changes.
5. Implement cursor/token pagination.
6. Treat opaque cursors as API-managed state rather than values to decode or construct.
7. Explain keyset pagination and its relationship to deterministic ordering.
8. Use composite `(timestamp, id)` boundaries when a timestamp alone is not unique.
9. Follow HTTP `Link` headers when the API supplies the next URL.
10. Understand GraphQL connection pagination using `edges`, `node`, and `pageInfo`.
11. Identify reliable stopping conditions from an API contract.
12. Build generator-based paginators that avoid loading the entire result set into memory.
13. Separate an API client, paginator, business processing, and writer/landing layer.
14. Reason about inserts, deletes, updates, and unstable ordering during extraction.
15. Checkpoint pagination progress safely.
16. Resume extraction after a process crash.
17. Understand cursor expiration and recovery strategies.
18. Design bounded parallel extraction using independent date windows when the API contract permits it.
19. Implement maximum-page, maximum-record, request-budget, time-budget, and repeated-cursor guards.
20. Validate completeness without treating record count alone as proof.
21. Combine an incremental watermark with pagination using patterns such as `updated_since + cursor`.
22. Design and test a production-oriented paginator.
23. Debug silent gaps, duplicates, early termination, infinite loops, cursor failures, and boundary errors.
24. Defend pagination decisions during an architecture review.

---

## 2. Prerequisites

This chapter assumes completion of the earlier API extraction topics in this module, especially:

- HTTP fundamentals.
- HTTP methods, status codes, headers, and response bodies.
- `httpx` basics.
- Sessions and connection reuse.
- Timeouts.
- API authentication and token handling.
- JSON response handling.
- Basic Python functions, iterators, generators, exceptions, and type hints.

This chapter intentionally does **not** re-teach authentication or HTTP fundamentals in depth.

---

# Part I — Understand the Problem

## 3. What Problem Does Pagination Solve?

Imagine an API endpoint:

```http
GET /customers
```

Suppose the logical result contains 10 million customers.

Returning all 10 million records in one response creates several problems:

- enormous response size,
- high network transfer,
- large server-side work,
- large client memory requirements,
- long latency,
- higher probability of timeout,
- expensive retries,
- difficult failure recovery,
- expensive serialization and deserialization,
- increased load on the API,
- increased impact when a client makes a mistake.

Instead, an API can expose a smaller response:

```http
GET /customers?limit=100
```

The logical result is divided into smaller responses:

```text
10,000 records
      |
      v
+----------------+
| Page 1: 1-100  |
+----------------+
| Page 2: 101-200|
+----------------+
| Page 3: 201-300|
+----------------+
       ...
```

The client repeatedly requests portions of the logical result.

### A useful mental model

Think of pagination as walking through a long book using bookmarks.

The page is not merely a transport detail. The pagination mechanism determines where the reader continues from.

If the book is changing while you read it, a simple “page number” may no longer identify the same content.

That is why pagination becomes a data correctness problem.

---

## 4. Why APIs Cannot Always Return Everything

A production API may impose pagination because of:

### 4.1 Response-size constraints

Large responses consume bandwidth and processing resources.

### 4.2 Server memory and CPU

The server may need to query, serialize, and buffer a large result.

### 4.3 Network latency

A huge response takes longer to transfer.

### 4.4 Timeouts

Long-running requests have more opportunities to hit client, proxy, load-balancer, or server timeouts.

### 4.5 Failure cost

If a 500 MB response fails near completion, the client may have to repeat the entire request.

With pagination, failure can be isolated to a smaller unit.

### 4.6 API protection

Pagination prevents a single request from accidentally consuming an unreasonable amount of server capacity.

### 4.7 Client processing

A data pipeline may want to process records incrementally rather than load the entire dataset into memory.

---

## 5. Page Size and API Limits

Most paginated APIs expose some variation of:

- `limit`
- `page_size`
- `per_page`
- `first`

For example:

```http
GET /customers?limit=100
```

The client is requesting up to 100 records.

That does **not** necessarily mean the server will return exactly 100.

Suppose the client asks:

```http
GET /customers?limit=5000
```

but the API contract says:

```text
maximum page size = 100
```

The server might return only 100.

Therefore:

> **Never assume requested page size equals actual records returned.**

A robust extractor distinguishes:

```text
requested page size
        !=
actual number of records returned
```

### Why might the actual count be smaller?

Possible reasons include:

- the server caps the page size,
- fewer records remain,
- filtering changes the result set,
- the API deliberately returns smaller pages,
- a backend implementation has a smaller effective limit,
- the response represents a logical page whose size is not guaranteed.

The API contract determines what a short page means.

### Example

```python
requested_page_size = 500

response = client.get(
    "/customers",
    params={"limit": requested_page_size},
)

records = response.json()["data"]

print(len(records))
```

Do not write logic such as:

```python
if len(records) < requested_page_size:
    break
```

unless the API documentation explicitly guarantees that a short page means no further records exist.

---

# Part II — The Main Pagination Styles

## 6. The Four Main Pagination Styles

The most common patterns covered in this chapter are:

1. Offset/page-number pagination.
2. Cursor/token pagination.
3. Keyset pagination.
4. Link-header pagination.

GraphQL APIs commonly expose cursor pagination through a connection model.

A useful progression is:

```text
What is pagination?
        |
        v
Offset / page number
        |
        v
Cursor / token
        |
        v
Keyset
        |
        v
Link headers
        |
        v
GraphQL connections
        |
        v
Reliability and consistency
```

---

# Part III — Offset / Page-Number Pagination

## 7. Offset / Page-Number Pagination

Offset pagination tells the server:

> “Skip this many records, then return the next group.”

A page-number API may look like:

```http
GET /customers?page=1&per_page=100
GET /customers?page=2&per_page=100
GET /customers?page=3&per_page=100
```

An offset API may instead look like:

```http
GET /customers?offset=0&limit=100
GET /customers?offset=100&limit=100
GET /customers?offset=200&limit=100
```

Conceptually:

```text
offset = page_number × page_size
```

when the API uses zero-based page numbering.

For a one-based page API:

```text
offset = (page_number - 1) × page_size
```

The exact formula depends on the API contract.

---

## 8. Minimal Offset Example

Suppose the API returns:

```json
{
  "data": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ]
}
```

A basic paginator can be:

```python
from collections.abc import Iterator
from typing import Any

import httpx


def paginate_offset(
    client: httpx.Client,
    endpoint: str,
    page_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """Yield records from an offset-paginated API."""
    offset = 0

    while True:
        response = client.get(
            endpoint,
            params={
                "offset": offset,
                "limit": page_size,
            },
        )
        response.raise_for_status()

        payload = response.json()
        records = payload["data"]

        if not records:
            break

        yield from records

        offset += len(records)
```

### How it works

1. Start at offset `0`.
2. Request a page.
3. Parse the records.
4. Stop if the response contains no records.
5. Yield records to the caller.
6. Advance the offset.
7. Repeat.

Notice that the example uses:

```python
offset += len(records)
```

rather than:

```python
offset += page_size
```

This can be appropriate when the API defines `offset` relative to the number of records in the result sequence and the response can contain fewer records than requested.

However, the exact offset semantics must come from the API contract.

### Why it works

The next request begins after the records already consumed.

### What can go wrong?

If the source changes between requests, the records occupying later offsets may move.

This is the major correctness weakness of naïve offset pagination.

### Production consideration

A production implementation should usually add:

- explicit timeout,
- bounded page count,
- response validation,
- logging,
- error handling,
- completeness checks,
- a source-defined stopping condition,
- stable ordering if supported.

---

## 9. A Complete Offset Paginator

```python
from collections.abc import Iterator
from typing import Any

import httpx


def paginate_offset(
    client: httpx.Client,
    endpoint: str,
    *,
    page_size: int = 100,
    max_pages: int = 100_000,
) -> Iterator[dict[str, Any]]:
    """Yield records from a generic offset-based API."""
    if page_size <= 0:
        raise ValueError("page_size must be positive")

    offset = 0

    for page_number in range(1, max_pages + 1):
        response = client.get(
            endpoint,
            params={
                "offset": offset,
                "limit": page_size,
            },
        )
        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("API response must be a JSON object")

        records = payload.get("data")

        if not isinstance(records, list):
            raise ValueError("API response field 'data' must be a list")

        if not records:
            return

        for record in records:
            yield record

        offset += len(records)

    raise RuntimeError(
        f"Pagination exceeded maximum page count: {max_pages}"
    )
```

### Important engineering point

`max_pages` is not merely a performance setting.

It is a correctness guard.

If an API accidentally keeps returning non-empty pages forever, the extractor should fail rather than consume resources indefinitely.

---

# Part IV — Why Offset Pagination Can Fail

## 10. Offset Pagination Under Inserts

This is one of the most important examples in the chapter.

Assume records are ordered:

```text
A
B
C
D
E
F
```

Page size:

```text
3
```

### Page 1

```text
A
B
C
```

The extractor now requests:

```text
offset = 3
```

Before page 2 is evaluated, a new record `X` is inserted before `D`.

The dataset becomes:

```text
A
B
C
X
D
E
F
```

Now:

```text
offset = 3
```

returns:

```text
X
D
E
```

Depending on the exact source ordering and semantics, the extractor can encounter records twice or alter the intended extraction boundary.

For example, if the insertion occurs at a different position after page 1, a previously consumed record can move into the next offset range.

The key problem is:

> **Offset identifies a position, not a record.**

When the dataset changes, positions can change.

### Visual model

```text
Before page 1:

0   1   2   3   4   5
A   B   C   D   E   F
        ^
      page 1


After insertion:

0   1   2   3   4   5   6
A   B   C   X   D   E   F
                ^
            old offset boundary
```

The boundary moved relative to the records.

---

## 11. Offset Pagination Under Deletes

Start with:

```text
A
B
C
D
E
F
```

Page size:

```text
3
```

Page 1:

```text
A B C
```

Now `B` is deleted.

The dataset becomes:

```text
A
C
D
E
F
```

If page 2 uses:

```text
offset = 3
```

the server may return:

```text
E
F
```

Record `D` can be skipped because the dataset became shorter before the requested offset.

Again:

> Offset tracks a position in a changing sequence, not a durable record boundary.

---

## 12. Why This Matters

Offset pagination can still be perfectly appropriate when:

- the dataset is stable,
- the API defines suitable ordering semantics,
- the result is small,
- consistency requirements are modest,
- the API only exposes offset pagination,
- the extraction is intentionally a snapshot-like operation supported by the source.

The important engineering skill is not memorizing “offset is bad.”

It is understanding the source contract and recognizing the failure modes.

---

# Part V — Cursor / Token Pagination

## 13. Cursor / Token Pagination

Cursor pagination tells the API:

> “Continue from the position represented by this cursor.”

Example response:

```json
{
  "data": [
    {"id": "1"},
    {"id": "2"}
  ],
  "next_cursor": "eyJwYWdlIjoyfQ..."
}
```

The next request might be:

```http
GET /customers?cursor=eyJwYWdlIjoyfQ...
```

The cursor is often opaque.

That means the client should treat it as an API-issued token:

```text
receive cursor
      |
      v
store cursor
      |
      v
send cursor back
```

Do not decode, modify, or construct an opaque cursor unless the API explicitly documents that behavior.

---

## 14. Minimal Cursor Paginator

```python
from collections.abc import Iterator
from typing import Any

import httpx


def paginate_cursor(
    client: httpx.Client,
    endpoint: str,
    *,
    page_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """Yield records from a cursor-paginated API."""
    cursor: str | None = None

    while True:
        params: dict[str, Any] = {"limit": page_size}

        if cursor is not None:
            params["cursor"] = cursor

        response = client.get(endpoint, params=params)
        response.raise_for_status()

        payload = response.json()
        records = payload["data"]

        for record in records:
            yield record

        next_cursor = payload.get("next_cursor")

        if next_cursor is None:
            return

        cursor = next_cursor
```

### How it works

The first request does not contain a cursor.

```text
GET /customers?limit=100
```

The response provides:

```text
next_cursor = "abc"
```

The next request uses:

```text
GET /customers?limit=100&cursor=abc
```

The process repeats until the API's documented continuation signal says there is no next page.

### What can go wrong?

- missing cursor field,
- malformed response,
- cursor repeated,
- cursor expires,
- cursor refers to an invalid or unavailable server-side state,
- the API changes its semantics,
- client checkpoints the cursor before the corresponding data is durable.

### Production consideration

Cursor pagination often provides a better continuation model for APIs that explicitly support it, but it is not universally superior. Its behavior depends on the source contract.

---

## 15. Common Cursor Response Shapes

Different APIs may use different field names.

### Shape A

```json
{
  "data": [...],
  "next_cursor": "abc"
}
```

### Shape B

```json
{
  "items": [...],
  "next_page_token": "xyz"
}
```

### Shape C

```json
{
  "data": [...],
  "pagination": {
    "next": "https://api.example.com/customers?cursor=abc"
  }
}
```

The client must follow the documented response structure.

Do not assume every API calls the value `next_cursor`.

---

## 16. Cursor Versus Next-Page URL

These are related but distinct concepts.

A response may return:

```text
next_cursor = "abc"
```

The client constructs the next documented request using that cursor.

Another API may return:

```text
next = "https://api.example.com/customers?cursor=abc"
```

The server has supplied the complete next request URL.

The second approach can reduce client-side pagination reconstruction.

Do not turn a `next` URL into an inferred cursor algorithm unless the API documentation says to do so.

---

## 17. Cursor Expiration

Some cursor mechanisms are temporary.

Suppose:

```text
10:00  page 1
10:01  page 2
10:02  page 3
10:03  checkpoint cursor
...
15:00  process resumes
```

The API may reject the old cursor if the cursor has expired.

Possible outcomes include:

```text
HTTP 400
HTTP 404
HTTP 410
provider-specific error
```

The exact behavior is API-specific.

### Production recovery strategies

Depending on the source contract, recovery may include:

1. restart from a known safe boundary,
2. restart the extraction from the beginning,
3. re-establish an incremental boundary,
4. create a fresh cursor,
5. reprocess a bounded overlap and deduplicate.

Do not invent cursor-expiration semantics.

The source documentation determines the correct recovery method.

---

# Part VI — Keyset Pagination

## 18. Keyset Pagination

Keyset pagination replaces:

```text
skip N records
```

with:

```text
continue after the last known ordered key
```

Offset:

```text
offset = 500000
```

Keyset:

```text
id > 500000
```

A database-style example:

```sql
SELECT *
FROM customers
WHERE id > 5000
ORDER BY id
LIMIT 100;
```

An API might expose something conceptually similar:

```http
GET /customers?starting_after=5000&limit=100
```

or:

```http
GET /customers?since_id=5000&limit=100
```

These parameter names are illustrative. A real API must document the semantics.

---

## 19. Why Keyset Can Be More Stable

Offset says:

```text
start at position 500001
```

Keyset says:

```text
start after record/key 500000
```

The second statement is tied to an ordered value rather than a position.

This can be valuable when:

- the key is stable,
- ordering is deterministic,
- the source supports a suitable boundary filter,
- the dataset is large,
- deep offsets become expensive,
- records can change while extraction runs.

Again, this does not mean keyset is universally appropriate.

---

## 20. Deterministic Ordering

Keyset pagination depends on a meaningful ordering boundary.

Good candidates can include:

- unique IDs,
- timestamps combined with unique IDs,
- another immutable monotonic sequence.

A timestamp alone may not be unique.

Suppose:

```text
created_at        id
---------------------
10:00:00          101
10:00:00          102
10:00:00          103
10:00:01          104
```

If the last processed timestamp is:

```text
10:00:00
```

and the next query uses:

```text
created_at > '10:00:00'
```

then IDs `102` and `103` could be skipped if only ID `101` was processed at that boundary.

---

# Part VII — Composite Keyset Pagination

## 21. `(timestamp, id)` as a Composite Boundary

A more precise boundary is:

```text
(created_at, id)
```

The continuation rule becomes lexicographic:

```text
(created_at, id) > (last_created_at, last_id)
```

Conceptually:

```text
WHERE
    created_at > :last_created_at
    OR (
        created_at = :last_created_at
        AND id > :last_id
    )
ORDER BY created_at, id
LIMIT 100
```

For the example:

```text
10:00:00  101
10:00:00  102
10:00:00  103
10:00:01  104
```

If the last processed record is:

```text
(10:00:00, 102)
```

the next boundary includes:

```text
(10:00:00, 103)
(10:00:01, 104)
```

This avoids treating the timestamp as unique when it is not.

### API representation

An API could expose:

```http
GET /customers?after_created_at=2026-10-01T10:00:00Z&after_id=102
```

or it could encode the boundary into an opaque cursor.

The actual API contract determines the representation.

---

# Part VIII — Link-Header Pagination

## 22. HTTP `Link` Header Pagination

Some APIs return pagination links in HTTP headers.

Example:

```http
Link: <https://api.example.com/customers?page=2>; rel="next"
```

The important component is:

```text
rel="next"
```

The server is effectively telling the client:

> “Here is the URL I want you to use for the next page.”

This can be safer than reconstructing page parameters yourself.

---

## 23. Link-Header Implementation

```python
from collections.abc import Iterator
from typing import Any

import httpx


def extract_next_link(link_header: str | None) -> str | None:
    """Extract a rel=next URL from a simple Link header."""
    if not link_header:
        return None

    for part in link_header.split(","):
        part = part.strip()

        if 'rel="next"' not in part:
            continue

        if not part.startswith("<"):
            continue

        end = part.find(">")
        if end == -1:
            continue

        return part[1:end]

    return None


def paginate_link_header(
    client: httpx.Client,
    initial_url: str,
) -> Iterator[dict[str, Any]]:
    """Yield records by following server-provided next links."""
    next_url: str | None = initial_url

    while next_url is not None:
        response = client.get(next_url)
        response.raise_for_status()

        payload = response.json()

        for record in payload["data"]:
            yield record

        next_url = extract_next_link(
            response.headers.get("Link")
        )
```

### How it works

The first URL is known by the client.

After each response:

```text
HTTP response
      |
      v
Link header
      |
      v
rel="next"
      |
      v
next request
```

### Production consideration

The parser above is intentionally educational. Production systems should use a robust parser when the API can emit complex RFC-compliant link headers.

The key architectural principle is more important than the parser:

> When the API supplies the next request URL, use the documented continuation mechanism instead of reconstructing pagination state unnecessarily.

---

# Part IX — GraphQL Connection Pagination

## 24. GraphQL Connections

GraphQL APIs frequently expose cursor pagination through a connection structure.

Typical concepts include:

- `edges`
- `node`
- `pageInfo`
- `hasNextPage`
- `endCursor`

Example response:

```json
{
  "data": {
    "customers": {
      "edges": [
        {"node": {"id": "1"}},
        {"node": {"id": "2"}}
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "abc123"
      }
    }
  }
}
```

The next query commonly uses:

```text
after: endCursor
```

A generic query can look like:

```graphql
query {
  customers(first: 100, after: "abc123") {
    edges {
      node {
        id
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

### Relationship to cursor pagination

The conceptual flow is:

```text
first request
    |
    v
edges + pageInfo
    |
    +--> hasNextPage
    |
    +--> endCursor
             |
             v
        next request
```

GraphQL connection pagination is therefore closely related to cursor/token pagination, although the response and query structure are defined by the GraphQL schema.

---

# Part X — Comparing Pagination Strategies

## 25. Comparison Table

| Feature | Offset | Cursor | Keyset | Link Header | GraphQL Connection |
|---|---|---|---|---|---|
| Mechanism | Position/page | API-issued continuation token | Ordered boundary | Server-provided next URL | Cursor through connection |
| Implementation complexity | Low to moderate | Moderate | Moderate | Moderate | Moderate |
| Changing-data behavior | Can be sensitive to inserts/deletes | Depends on API contract | Can be stable with deterministic ordering | Depends on linked API semantics | Depends on GraphQL/API contract |
| Deep-page behavior | Can become expensive depending on backend | API-dependent | Often avoids deep offset traversal | API-dependent | API-dependent |
| Resumability | Usually position-based | Cursor can be checkpointed | Boundary can be checkpointed | Next URL can be checkpointed | End cursor can be checkpointed |
| API dependence | Parameter conventions | Strong | Strong | Strong | Strong |
| Ordering requirements | Depends on API | API-specific | Fundamental | API-specific | Schema/API-specific |
| Typical use | Simple paginated listings | Large API result sets with tokens | Ordered large datasets | APIs exposing continuation URLs | GraphQL APIs |
| Major risks | Gaps/duplicates under changes | Expiration, opaque state | Incorrect boundary/order | Incorrect link parsing or stale links | Incorrect `pageInfo` handling |
| Universal winner? | No | No | No | No | No |

The correct strategy depends on the source API contract and workload.

---

# Part XI — Reliable Stopping Conditions

## 26. Stopping Conditions

A paginator must know when to stop.

Possible signals include:

```text
no next cursor
has_more == false
no next Link header
empty page
short page
total count reached
```

But these signals are not equally reliable.

### Example

An API might return:

```json
{
  "data": [ ... ],
  "has_more": false
}
```

If the API contract explicitly defines `has_more`, that is strong evidence for termination.

A short page:

```text
requested = 100
returned = 37
```

is not automatically proof of completion.

The API might deliberately return fewer than 100 records.

### Stopping-condition table

| Signal | Reliable? | Depends on |
|---|---|---|
| `has_more=false` | Usually | API contract |
| Missing next cursor | Usually | API contract |
| No `rel="next"` link | Usually | API contract |
| Empty page | Sometimes | API semantics |
| Short page | Not always | API semantics |
| Total count reached | Sometimes | Count consistency |

The key principle is:

> **The API's documented contract determines the reliable stopping condition.**

---

# Part XII — Generator-Based Paginators

## 27. Why Generators Matter

Compare:

```python
records = fetch_everything()
```

with:

```python
for record in paginate(...):
    process(record)
```

The generator version can provide:

- lazy evaluation,
- bounded memory,
- separation between retrieval and consumption,
- composability,
- incremental processing.

Instead of materializing:

```text
page 1
page 2
page 3
...
page N
```

all at once, the application can process records as they arrive.

---

## 28. Yield Records Versus Yield Pages

### Record-oriented generator

```python
def paginate_records(...) -> Iterator[dict[str, Any]]:
    ...
    yield record
```

Useful when the downstream consumer processes one record at a time.

### Page-oriented generator

```python
def paginate_pages(...) -> Iterator[list[dict[str, Any]]]:
    ...
    yield records
```

Useful when the downstream operation is naturally page/batch oriented.

For example:

```python
for page in paginate_pages(client):
    write_batch(page)
```

The choice should follow the downstream processing boundary.

---

# Part XIII — Separate the Client From the Paginator

## 29. Clean Architecture

Avoid putting HTTP communication, pagination state, business logic, and writing into one giant function.

A useful conceptual architecture is:

```text
+-------------------+
|     API Client    |
| HTTP + validation |
+---------+---------+
          |
          v
+-------------------+
|     Paginator     |
| continuation     |
| stopping rules   |
| safety guards    |
+---------+---------+
          |
          v
+-------------------+
| Business Process  |
| transform/filter  |
+---------+---------+
          |
          v
+-------------------+
| Writer / Bronze   |
| durable landing   |
+-------------------+
```

This separation improves:

- testing,
- reuse,
- debugging,
- observability,
- maintainability.

---

## 30. Simple Separation Example

```python
from collections.abc import Iterator
from typing import Any

import httpx


class CustomersClient:
    """Small HTTP client for the customers endpoint."""

    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def fetch_page(
        self,
        *,
        cursor: str | None,
        limit: int,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}

        if cursor is not None:
            params["cursor"] = cursor

        response = self.client.get("/customers", params=params)
        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("Expected JSON object")

        return payload


def cursor_pages(
    client: CustomersClient,
    *,
    page_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """Yield complete API payloads one page at a time."""
    cursor: str | None = None

    while True:
        payload = client.fetch_page(
            cursor=cursor,
            limit=page_size,
        )

        yield payload

        cursor = payload.get("next_cursor")

        if cursor is None:
            return


def records(
    client: CustomersClient,
    *,
    page_size: int = 100,
) -> Iterator[dict[str, Any]]:
    """Yield customer records from cursor-paginated pages."""
    for page in cursor_pages(client, page_size=page_size):
        for record in page["data"]:
            yield record
```

The layers now have distinct responsibilities.

---

# Part XIV — Consistency Problems

## 31. Pagination Is a Correctness Problem

Consider two datasets.

### Static dataset

```text
A
B
C
D
E
F
```

Nothing changes while the extraction runs.

### Changing dataset

```text
A
B
C
D
E
F
```

while records are:

```text
inserted
deleted
updated
reordered
```

The second case is much harder.

Potential symptoms include:

- duplicate records,
- missing records,
- records processed outside the intended boundary,
- inconsistent page membership,
- incomplete extraction.

---

## 32. Stable Ordering

A paginator needs to understand the source ordering.

A problematic conceptual ordering is:

```text
ORDER BY updated_at
```

if many records can have exactly the same timestamp and the API does not define a deterministic tie-breaker.

A stronger database-style ordering can be:

```text
ORDER BY updated_at, id
```

when the API supports deterministic composite ordering.

The important point is not that every API must expose these exact fields.

It is:

> **A pagination boundary must correspond to a stable and deterministic ordering defined by the source contract.**

---

## 33. Updates Can Change Position

Suppose records are ordered by:

```text
updated_at
```

and a record moves from:

```text
10:00
```

to:

```text
10:30
```

while the extraction is running.

If the pagination strategy assumes a fixed ordering but the record moves between pages, the same logical record may be encountered in an unexpected position.

Therefore, changing fields used for ordering require careful extraction design.

---

# Part XV — Checkpointing and Resuming

## 34. What Is a Checkpoint?

A checkpoint is durable state that records extraction progress.

For example:

```json
{
  "source": "customers",
  "cursor": "abc123",
  "updated_at": "2026-10-01T10:30:00Z",
  "last_successful_page": 42
}
```

The exact state should reflect the source pagination contract.

A checkpoint can protect against process failure.

---

## 35. The Correct Ordering of State Changes

A critical sequence is:

```text
request page
    |
    v
receive page
    |
    v
durably land/process page
    |
    v
checkpoint cursor
```

The order matters.

### Dangerous ordering

```text
receive page
    |
    v
checkpoint cursor
    |
    v
crash
    |
    v
page was never durably written
```

The checkpoint says:

```text
"I processed this page."
```

but the data says otherwise.

On restart, the paginator may skip the page.

### Safer conceptual ordering

```text
receive
  |
  v
durably land/process
  |
  v
checkpoint
```

This is a general data-engineering principle:

> **Durably land data before advancing extraction state.**

---

# Part XVI — Crash and Resume

## 36. Crash Scenario

Imagine:

```text
Page 1 ✓
Page 2 ✓
Page 3 ✓
Page 4 ✓
Page 5 ← process crashes
```

If the last durable checkpoint represents page 4, the restart can begin from the state associated with page 5.

```text
last checkpoint = page 4
          |
          v
       restart
          |
          v
       page 5
```

For cursor pagination, this might mean:

```text
last_checkpointed_cursor
```

For keyset pagination:

```text
last_checkpointed_key
```

For a date-window extraction:

```text
window + pagination state
```

The checkpoint format depends on the pagination strategy.

---

## 37. Exactly-Once Versus At-Least-Once Effects

A restart can create duplicate processing if the system lands a page successfully but crashes before checkpointing it.

Example:

```text
page received
    |
    v
page written ✓
    |
    v
CRASH
    |
    v
checkpoint not updated
```

On restart, the page may be written again.

This is not necessarily a defect if the landing or downstream operation is idempotent.

A robust ingestion architecture therefore often combines:

```text
durable checkpointing
+
idempotent landing/deduplication
```

rather than assuming a crash can never occur between two durable operations.

---

# Part XVII — Cursor Expiration and Recovery

## 38. Expired Cursor

Suppose:

```text
10:00  page 1
10:01  page 2
10:02  page 3
10:03  checkpoint
...
15:00  resume
```

The source may reject the old cursor.

The important questions are:

1. Is cursor expiration documented?
2. How does the API signal expiration?
3. Can a fresh cursor be created?
4. Can the extraction restart from a safe timestamp or key?
5. Is overlap and deduplication supported?
6. Is the source able to reproduce the same logical result set?

A production design must answer these before relying on long-lived cursors.

---

# Part XVIII — Parallel Extraction With Date Windows

## 39. Why Parallel Windows Exist

A large extraction can sometimes be divided into independent time windows:

```text
2026-01-01 → 2026-02-01
2026-02-01 → 2026-03-01
2026-03-01 → 2026-04-01
```

Conceptually:

```text
             API
              |
      +-------+-------+
      |       |       |
      v       v       v
    Jan     Feb     Mar
   window  window  window
      |       |       |
   cursor   cursor  cursor
      |       |       |
      +-------+-------+
              |
              v
          deduplicate
```

Each window has independent pagination state.

This can reduce elapsed time when the API supports filtering by the chosen time range.

---

## 40. Boundary Design

Suppose windows are:

```text
[Jan 1, Feb 1)
[Feb 1, Mar 1)
[Mar 1, Apr 1)
```

Using half-open intervals can make boundaries explicit:

```text
start <= timestamp < end
```

This avoids overlapping the exact boundary in the ideal case.

But source APIs vary.

If the API only supports inclusive filters, you may need:

```text
[Jan 1, Feb 1]
[Feb 1, Mar 1]
```

plus deduplication.

The source contract determines the safe representation.

---

## 41. Risks of Parallel Windows

Parallel date-window extraction should be treated as an advanced optimization.

Risks include:

- boundary duplicates,
- boundary gaps,
- records whose timestamps change during extraction,
- overlapping windows,
- insufficient API filtering guarantees,
- rate-limit pressure,
- excessive concurrency,
- inconsistent snapshots.

Do not introduce parallel windows merely because the dataset is large.

First establish that the source contract makes independent windows safe.

This chapter intentionally does not teach asynchronous programming in depth; concurrency internals belong to the later concurrency module.

---

# Part XIX — Pagination Safety Guards

## 42. Why Guards Are Necessary

Even a well-documented API can encounter:

- server bugs,
- client bugs,
- malformed responses,
- repeated cursors,
- incorrect termination metadata,
- unexpected data volume.

A production paginator should fail safely.

---

## 43. Maximum Page Count

Example:

```python
max_pages = 100_000
```

If the extractor exceeds the limit:

```python
raise RuntimeError(
    f"Pagination exceeded maximum page count: {max_pages}"
)
```

This protects against infinite or unexpectedly huge extraction.

---

## 44. Repeated Cursor Detection

Consider:

```text
cursor A
cursor B
cursor C
cursor C  <-- unexpected
```

A simple guard:

```python
seen_cursors: set[str] = set()

if cursor in seen_cursors:
    raise RuntimeError("Pagination loop detected")

seen_cursors.add(cursor)
```

A more precise implementation should decide whether to track the cursor before or after requesting the page based on the API's cursor semantics.

The key principle is:

> If pagination state repeats without a documented reason, fail rather than loop forever.

---

## 45. Maximum Records

A record budget can provide another protection:

```python
max_records = 10_000_000
```

After each page:

```python
total_records += len(records)

if total_records > max_records:
    raise RuntimeError("Record budget exceeded")
```

This can detect a source or filter behaving very differently from expectations.

---

## 46. Request and Time Budgets

You can also enforce:

```text
maximum HTTP requests
maximum elapsed time
```

These guards are particularly useful for scheduled production jobs.

They do not replace correctness checks.

They protect operational resources.

---

# Part XX — Completeness Validation

## 47. How Do You Know the Extraction Is Complete?

This is harder than it sounds.

Suppose your pipeline extracted:

```text
10,000 records
```

That does not prove that the correct 10,000 records were extracted.

You could have:

```text
9,500 correct records
+
500 duplicates
=
10,000 rows
```

Or:

```text
9,900 correct records
+
100 unrelated records
=
10,000 rows
```

Or:

```text
9,999 correct records
+
1 duplicate
=
10,000 rows
```

The count looks correct but the dataset is wrong.

---

## 48. Completeness Signals

Possible validation signals include:

- API-provided total count,
- expected page count,
- expected date range,
- source-side totals,
- extracted record count,
- unique key count,
- checksums where applicable,
- reconciliation queries.

### Example

If the source reports:

```text
expected = 100,000
```

and the extractor has:

```text
raw rows = 100,000
unique IDs = 100,000
```

that is stronger evidence than:

```text
raw rows = 100,000
```

alone.

Even then, completeness depends on what the source's total represents and whether the total is consistent with the extraction boundary.

---

# Part XXI — Combining Pagination With Incremental Extraction

## 49. `updated_since + cursor`

A common production pattern is:

```text
watermark
+
pagination cursor
```

For example:

```http
GET /customers?updated_since=2026-10-01T00:00:00Z&cursor=abc
```

Conceptually:

```text
updated_since
      +
   cursor
      |
      v
bounded incremental result
      |
      v
multiple pages
```

The watermark defines the logical extraction window.

The cursor moves through that window.

---

## 50. Two Pieces of State

A run may have:

```text
watermark = 2026-10-01T00:00:00Z
cursor = abc123
```

The cursor says:

```text
where I am inside this run
```

The watermark says:

```text
which logical source interval this run is extracting
```

These are different responsibilities.

---

## 51. When Should the Watermark Advance?

A common safe conceptual sequence is:

```text
choose extraction boundary
        |
        v
paginate all records in boundary
        |
        v
land/process data
        |
        v
validate completeness
        |
        v
advance durable watermark
```

Do not advance the run-level watermark merely because the first page succeeded.

Otherwise, a crash after page 1 could cause later records to fall outside the next extraction.

---

## 52. Lookback and Overlap

A changing source can benefit from a lookback window.

Instead of:

```text
updated_since = last_watermark
```

the next run might intentionally use:

```text
updated_since = last_watermark - overlap
```

The overlap creates a safety margin for:

- timestamp precision,
- late updates,
- clock differences,
- transaction timing,
- source-side ordering behavior.

But overlap creates duplicates by design.

Therefore:

```text
lookback
+
deduplication
```

must be designed together.

---

# Part XXII — Building a Production-Grade Paginator

## 53. Design Goals

A production paginator should make important behavior explicit:

- HTTP client,
- timeout,
- pagination state,
- stopping condition,
- checkpointing,
- loop detection,
- maximum page count,
- logging,
- error handling,
- completeness validation,
- safe restart.

The implementation should remain understandable.

---

## 54. Educational Production-Oriented Example

The following is intentionally framework-light. A real system would replace the in-memory checkpoint store with durable storage.

```python
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


class CheckpointStore(Protocol):
    """Interface for durable pagination state."""

    def load(self) -> str | None:
        ...

    def save(self, cursor: str) -> None:
        ...


@dataclass
class InMemoryCheckpointStore:
    """Educational checkpoint store.

    Replace with durable storage in production.
    """

    cursor: str | None = None

    def load(self) -> str | None:
        return self.cursor

    def save(self, cursor: str) -> None:
        self.cursor = cursor


class Paginator:
    """Cursor paginator with basic production safety guards."""

    def __init__(
        self,
        client: httpx.Client,
        endpoint: str,
        page_size: int,
        checkpoint_store: CheckpointStore,
        *,
        max_pages: int = 100_000,
        max_records: int = 10_000_000,
    ) -> None:
        if page_size <= 0:
            raise ValueError("page_size must be positive")

        self.client = client
        self.endpoint = endpoint
        self.page_size = page_size
        self.checkpoint_store = checkpoint_store
        self.max_pages = max_pages
        self.max_records = max_records

    def records(self) -> Iterator[dict[str, Any]]:
        """Yield records while checkpointing completed pages."""
        cursor = self.checkpoint_store.load()
        seen_cursors: set[str] = set()

        total_records = 0

        for page_number in range(1, self.max_pages + 1):
            if cursor is not None:
                if cursor in seen_cursors:
                    raise RuntimeError(
                        f"Pagination loop detected at cursor={cursor!r}"
                    )
                seen_cursors.add(cursor)

            params: dict[str, Any] = {
                "limit": self.page_size,
            }

            if cursor is not None:
                params["cursor"] = cursor

            response = self.client.get(
                self.endpoint,
                params=params,
            )
            response.raise_for_status()

            payload = response.json()

            if not isinstance(payload, dict):
                raise ValueError("Expected JSON object")

            records = payload.get("data")

            if not isinstance(records, list):
                raise ValueError(
                    "Expected 'data' to be a JSON list"
                )

            for record in records:
                if not isinstance(record, dict):
                    raise ValueError(
                        "Each record must be a JSON object"
                    )

                total_records += 1

                if total_records > self.max_records:
                    raise RuntimeError(
                        "Maximum record budget exceeded"
                    )

                yield record

            next_cursor = payload.get("next_cursor")

            if next_cursor is None:
                return

            if not isinstance(next_cursor, str):
                raise ValueError(
                    "'next_cursor' must be a string or null"
                )

            # In a real pipeline, the records from this page must
            # already be durably landed before this checkpoint advances.
            self.checkpoint_store.save(next_cursor)

            cursor = next_cursor

        raise RuntimeError(
            f"Maximum page count exceeded: {self.max_pages}"
        )
```

### Important limitation

The example's `yield` boundary is intentionally educational.

A production implementation must define precisely what “durably landed” means before advancing the checkpoint.

For example, the architecture might instead be:

```text
fetch page
   |
   v
validate page
   |
   v
write raw page durably
   |
   v
commit landing
   |
   v
checkpoint cursor
```

This makes the state transition explicit.

### How it works

The paginator:

1. loads the previous cursor,
2. sends it to the API,
3. validates the response,
4. yields records,
5. reads the next cursor,
6. checkpoints successful progress,
7. repeats,
8. stops when the API indicates completion.

### Why it works

Pagination state is explicit and guarded.

### What can go wrong?

- cursor expires,
- checkpoint store fails,
- API returns malformed JSON,
- API repeats a cursor,
- record volume exceeds the configured budget,
- the source changes during extraction.

### Production consideration

The checkpoint store should be durable and should participate in a clearly defined data-commit protocol.

---

# Part XXIII — Testing Pagination

## 55. Test Without Calling a Real API

Paginators should be testable without network access.

`httpx.MockTransport` is useful for creating deterministic HTTP responses.

The tests should prove both normal behavior and failure behavior.

---

## 56. Mock Transport Example

```python
import json

import httpx


def test_cursor_pagination() -> None:
    responses = {
        None: {
            "data": [{"id": 1}, {"id": 2}],
            "next_cursor": "abc",
        },
        "abc": {
            "data": [{"id": 3}],
            "next_cursor": None,
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        cursor = request.url.params.get("cursor")

        payload = responses[cursor]

        return httpx.Response(
            200,
            json=payload,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
        transport=transport,
        base_url="https://api.example.test",
    ) as client:
        records = list(
            paginate_cursor(
                client,
                "/customers",
                page_size=2,
            )
        )

    assert [record["id"] for record in records] == [1, 2, 3]
```

This proves:

- first request has no cursor,
- next request uses the returned cursor,
- multiple pages are consumed,
- the paginator stops correctly.

---

## 57. Required Test Matrix

A robust paginator should test at least:

1. single-page response,
2. multiple pages,
3. empty response,
4. missing next cursor,
5. repeated cursor,
6. malformed response,
7. HTTP error,
8. cursor expiration,
9. short page,
10. API returns more pages after a short page,
11. crash before checkpoint,
12. crash after landing but before checkpoint,
13. resumed extraction,
14. duplicate page,
15. inconsistent ordering.

### What each test proves

| Test | What it validates |
|---|---|
| Single page | Normal termination |
| Multiple pages | Continuation logic |
| Empty first page | Empty-result behavior |
| Missing cursor | Stopping/response contract |
| Repeated cursor | Loop protection |
| Malformed response | Schema validation |
| HTTP error | Error propagation/recovery boundary |
| Cursor expiration | Recovery design |
| Short page | Avoiding unsafe short-page termination |
| More pages after short page | Correct stopping semantics |
| Crash before checkpoint | Safe retry behavior |
| Crash after landing | Duplicate-safe design |
| Resume | Checkpoint correctness |
| Duplicate page | Idempotency/deduplication |
| Inconsistent ordering | Source consistency assumptions |

---

# Part XXIV — Debugging Pagination Failures

## 58. Debugging Method

Use a disciplined sequence:

```text
Symptom
   ↓
Possible causes
   ↓
Investigation
   ↓
Evidence
   ↓
Root cause
   ↓
Fix
   ↓
Prevention
```

Do not immediately rewrite the paginator.

First determine whether the problem is:

- source behavior,
- pagination logic,
- checkpoint state,
- response parsing,
- ordering,
- filtering,
- deduplication,
- validation.

---

## 59. Scenario 1 — Expected 100,000, Received 97,000

### Symptom

```text
expected = 100,000
received = 97,000
```

### Possible causes

- early stopping,
- skipped records,
- source-side filtering,
- expired/restarted pagination,
- incorrect page-size assumptions,
- unstable offset boundaries,
- API total count refers to a different snapshot.

### Investigation

Compare:

```text
raw record count
unique key count
page count
last pagination state
source-reported total
date/time boundary
```

For offset pagination, inspect whether the source changed during extraction.

### Evidence

If page 47 is missing from logs, the issue may be an early termination or failure.

If counts are:

```text
raw = 97,000
unique = 97,000
```

there may be actual missing records.

If:

```text
raw = 100,000
unique = 97,000
```

then duplicates explain part of the discrepancy.

### Prevention

Add completeness validation and durable page-level observability.

---

## 60. Scenario 2 — Records Duplicated Between Pages

### Symptom

The same IDs occur on consecutive pages.

### Possible causes

- changing dataset with offset pagination,
- repeated cursor,
- API defect,
- unstable ordering,
- retry that reprocessed a page,
- overlapping time windows.

### Investigation

Log:

```text
page number
cursor
first ID
last ID
record count
```

Compare the overlap.

### Root-cause example

An insert changed the offset position between page requests.

### Fix

Use a source-supported stable pagination mechanism or deduplicate at a safe boundary.

---

## 61. Scenario 3 — Paginator Runs Forever

### Symptom

The extraction never terminates.

### Possible causes

- repeated cursor,
- API always reports another page,
- client incorrectly reconstructs the next cursor,
- empty page is not handled,
- continuation state is not updated.

### Investigation

Log cursor transitions:

```text
A → B → C → C
```

### Fix

Implement:

```python
seen_cursors
```

and:

```python
max_pages
```

### Prevention

Treat loop protection as a production requirement.

---

## 62. Scenario 4 — Extraction Stops Early

### Symptom

The pipeline stops even though records remain.

### Possible causes

- short-page termination,
- missing cursor field interpreted as completion,
- malformed response,
- incorrect `has_more` parsing,
- transient source behavior.

### Key question

Does the API contract explicitly define the signal used by the paginator as terminal?

If not, the stopping logic is unsafe.

---

## 63. Scenario 5 — Crash Causes Missing Records

### Symptom

After restart, a gap appears.

### Possible cause

The checkpoint advanced before the page was durably landed.

Dangerous sequence:

```text
checkpoint
   ↓
crash
   ↓
data missing
```

### Fix

Use:

```text
durable landing
   ↓
checkpoint
```

---

## 64. Scenario 6 — Crash Causes Duplicate Records

### Symptom

A page appears twice after restart.

### Cause

The page was landed successfully, but the process crashed before the checkpoint advanced.

```text
land page ✓
checkpoint ✗
crash
```

### Response

Make the landing operation idempotent or deduplicate by a stable record identity.

This is often safer than trying to guarantee that no crash can occur between operations.

---

## 65. Scenario 7 — Cursor Suddenly Becomes Invalid

### Symptom

A previously valid cursor now fails.

### Possible causes

- cursor expiration,
- source-side state change,
- malformed checkpoint,
- cursor used outside its intended scope.

### Investigation

Check:

- documented cursor lifetime,
- error response,
- time since checkpoint,
- extraction boundary,
- whether the cursor is tied to a specific query.

### Fix

Follow the source's documented recovery mechanism.

Do not modify an opaque cursor to “repair” it.

---

## 66. Scenario 8 — Offset Pagination Produces Inconsistent Results

### Symptom

The same extraction produces different records across runs.

### Possible causes

- inserts,
- deletes,
- updates,
- unstable ordering,
- changing source state.

### Investigation

Compare source changes during the extraction interval.

### Root cause

The extractor assumed that:

```text
offset N
```

always referred to the same logical record boundary.

It does not necessarily do so on a changing dataset.

---

## 67. Scenario 9 — Short Page but More Records Exist

### Symptom

The API returns:

```text
requested = 100
returned = 37
```

but another page exists.

### Root cause

The paginator incorrectly assumed:

```text
short page = end
```

### Fix

Use the documented continuation signal.

---

## 68. Scenario 10 — Parallel Date Windows Create Boundary Duplicates

### Symptom

The same record appears in two windows.

### Possible cause

Both windows include the same timestamp boundary.

For example:

```text
window A: timestamp <= Feb 1
window B: timestamp >= Feb 1
```

Records exactly at Feb 1 appear in both.

### Fix

Use explicit non-overlapping intervals where supported:

```text
[Jan 1, Feb 1)
[Feb 1, Mar 1)
```

or intentionally overlap and deduplicate.

The source API determines which filter semantics are possible.

---

# Part XXV — Performance Considerations

## 69. Page Size

Page size affects the trade-off:

```text
larger pages
    ↓
fewer HTTP requests
but
larger responses
```

versus:

```text
smaller pages
    ↓
more HTTP requests
but
smaller individual responses
```

There is no universal ideal page size.

Measure it against:

- response latency,
- payload size,
- serialization cost,
- client memory,
- server behavior,
- API limits,
- rate limits.

---

## 70. Connection Reuse

Using one configured `httpx.Client` can allow connection reuse.

Example:

```python
timeout = httpx.Timeout(30.0)

with httpx.Client(
    base_url="https://api.example.com",
    timeout=timeout,
) as client:
    for record in paginate_cursor(client, "/customers"):
        process(record)
```

Creating a new client for every page can unnecessarily discard connection-management benefits.

---

## 71. Deep Offset Performance

Some database-backed APIs implement offset by scanning or skipping increasingly many rows.

Conceptually:

```text
offset 100
   ↓
small amount of skipping

offset 10,000,000
   ↓
potentially much more backend work
```

The actual behavior depends on the API implementation and database query plan.

Do not assume deep offsets are always slow, but recognize that offset depth can become a performance factor.

---

## 72. Cursor and Keyset Efficiency

Cursor and keyset mechanisms can avoid some forms of deep-position traversal because the continuation state can correspond to a backend-supported boundary.

However, the API implementation determines actual performance.

The correct approach is measurement, not assumption.

---

## 73. Server-Side Filtering

If the API supports:

```text
updated_since
date ranges
status filters
```

use them when they correctly define the intended extraction boundary.

Reducing unnecessary records at the source can reduce:

- requests,
- transfer,
- client processing,
- storage,
- validation workload.

---

## 74. Parallel Windows

Parallel date windows can reduce elapsed time, but they may increase:

- request concurrency,
- API load,
- rate-limit pressure,
- complexity,
- boundary risks.

Use bounded parallelism and only when the source contract makes the approach safe.

---

# Part XXVI — Realistic API Examples

## 75. Generic Examples

### Page number

```http
GET /customers?page=2&per_page=100
```

### Cursor

```http
GET /customers?cursor=abc
```

### Starting key

```http
GET /customers?starting_after=12345
```

### Link header

```http
Link: <https://api.example.com/customers?page=2>; rel="next"
```

### GraphQL

```graphql
query {
  customers(first: 100, after: "cursor") {
    edges {
      node {
        id
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

These are **generic educational examples**.

They do not claim that a particular provider implements these exact parameter names or semantics.

Provider-specific behavior must be verified against that provider's current documentation.

---

# Part XXVII — Hands-On Exercises

## 76. Exercise 1 — Four Paginators

Implement four paginators:

1. offset,
2. cursor,
3. keyset,
4. Link header.

Use the same mock API/client structure where practical.

### Requirements

Each paginator should:

- yield records,
- stop correctly,
- validate responses,
- handle empty results,
- include at least one safety guard.

### Expected result

You should be able to explain exactly what state identifies the next page in each strategy.

---

## 77. Exercise 2 — Changing Dataset

Create a mock source containing 100,000 logical records.

During extraction, simulate:

- inserts,
- deletes,
- updates.

Compare pagination strategies.

Measure:

```text
missing records
duplicate records
raw records
unique records
```

### Expected result

You should observe that pagination behavior depends strongly on how the source changes and what ordering guarantees exist.

Do not expect a universal winner.

---

## 78. Exercise 3 — Checkpointing

Implement checkpointing after every successfully landed page.

Then simulate:

```text
Page 1 ✓
Page 2 ✓
Page 3 ✓
Page 4 ← crash
```

Restart the process.

### Prove

- the extraction resumes from a safe boundary,
- no page is silently skipped,
- any intentional replay is handled safely,
- the final unique record set is complete.

---

## 79. Exercise 4 — Safety Guards

Implement:

```python
max_pages
```

and:

```python
seen_cursors
```

Then create a mock API that repeats a cursor.

Expected behavior:

```text
A → B → C → C
```

causes a controlled failure rather than an infinite loop.

---

## 80. Exercise 5 — Real API

Use a public API within its documented limits.

A public API exposing HTTP `Link`-header pagination may be used.

Document:

- pagination mechanism,
- page-size behavior,
- stopping condition,
- ordering behavior,
- rate-limit constraints,
- evidence that your implementation follows the API contract.

Do not assume undocumented provider behavior.

---

## 81. Exercise 6 — Unit Tests

Write tests for every paginator.

At minimum include:

```text
empty first page
```

This case is important because it distinguishes:

```text
valid empty result
```

from:

```text
parser or continuation bug
```

---

# Part XXVIII — Advanced Challenge

## 82. Production-Style Ingestion Problem

Design an ingestion pipeline for:

```text
API:
100,000+ customers

Pagination:
cursor

Filter:
updated_since

Rate limit:
documented API limit

Dataset:
changes while extraction runs

Failure:
process crashes after page N
```

Your design must specify:

- pagination state,
- checkpoint strategy,
- watermark strategy,
- deduplication,
- completeness validation,
- retry boundaries,
- loop protection,
- resume strategy,
- observability.

---

## 83. Reference Solution

### Step 1 — Establish the extraction boundary

Choose a run boundary:

```text
run_start_watermark = T0
```

If the source supports a bounded upper time condition, prefer an explicit interval.

If only `updated_since` is available, design a controlled watermark/lookback strategy.

---

### Step 2 — Maintain two kinds of state

```text
Run state:
    watermark boundary

Page state:
    cursor
```

Conceptually:

```text
watermark
   +
cursor
```

---

### Step 3 — Request pages

```http
GET /customers?updated_since=T0&cursor=abc
```

Use the documented parameter semantics.

---

### Step 4 — Validate each page

Validate:

- HTTP status,
- JSON structure,
- record structure,
- pagination metadata,
- record identities.

---

### Step 5 — Durably land data

For every successful page:

```text
receive
  ↓
validate
  ↓
durably land
```

The landing layer should support idempotent replay or deterministic deduplication.

---

### Step 6 — Advance the cursor checkpoint

Only after the corresponding page has been durably handled:

```text
land page
   ↓
checkpoint cursor
```

---

### Step 7 — Guard pagination

Maintain:

```text
max_pages
max_records
request budget
time budget
seen cursors
```

---

### Step 8 — Validate completeness

At the end, reconcile whatever source-side signals are available:

```text
source count
raw count
unique count
expected boundary
```

Do not rely on row count alone.

---

### Step 9 — Advance the watermark

Only after the extraction is successfully complete and validated should the durable run-level watermark move forward.

Conceptually:

```text
extract all pages
       ↓
land
       ↓
validate
       ↓
advance watermark
```

---

### Step 10 — Crash recovery

If the process crashes after page 25:

```text
last durable cursor = page 25 boundary
```

Restart from the checkpoint.

If the cursor has expired, follow the API's documented recovery path. If necessary, restart from a safe source boundary and deduplicate.

---

### Step 11 — Observability

Record at minimum:

```text
run_id
source
endpoint
start time
end time
watermark
page count
record count
unique record count
last cursor identifier/fingerprint if safe to log
request count
errors
termination reason
checkpoint status
```

Avoid logging secrets or sensitive opaque tokens if the API treats cursors as credentials or privileged state.

---

# Part XXIX — Production Design Checklist

## 84. Correctness

- [ ] Pagination style identified from source contract
- [ ] Stable ordering understood
- [ ] Reliable stopping condition identified
- [ ] Inserts considered
- [ ] Deletes considered
- [ ] Updates considered
- [ ] Completeness validation implemented
- [ ] Duplicate detection considered
- [ ] Boundary semantics documented

## Reliability

- [ ] Checkpointing implemented
- [ ] Resume capability defined
- [ ] Cursor expiration handling defined
- [ ] Loop detection implemented
- [ ] Maximum page guard implemented
- [ ] Record/request/time budgets considered
- [ ] Crash semantics tested

## Performance

- [ ] Page size measured
- [ ] Connection reuse enabled where appropriate
- [ ] Server-side filtering used when safe
- [ ] Request count measured
- [ ] Response size measured
- [ ] Deep-page behavior understood
- [ ] Parallel windows considered only when safe
- [ ] API rate limits respected

## Data Engineering

- [ ] Raw pages can be durably landed
- [ ] Pagination state is durable
- [ ] Incremental filters are handled correctly
- [ ] Duplicate detection exists
- [ ] Backfill implications are understood
- [ ] Replay behavior is defined
- [ ] Run-level and page-level state are distinguished

## Testing

- [ ] Mocked API tests
- [ ] Empty-page test
- [ ] Multiple-page test
- [ ] Cursor-loop test
- [ ] Malformed-response test
- [ ] Crash/resume test
- [ ] Changing-data test
- [ ] Short-page test
- [ ] Cursor-expiration test
- [ ] Boundary-window test

---

# Part XXX — Interview and Architecture Questions

## 85. Questions

1. Why can offset pagination produce duplicates?
2. Why can offset pagination skip records?
3. When would cursor pagination be appropriate?
4. What is keyset pagination?
5. Why is deterministic ordering important?
6. Why can `created_at > last_timestamp` lose records?
7. How does `(timestamp, id)` solve the boundary problem?
8. What makes a stopping condition reliable?
9. Why should a paginator be implemented as a generator?
10. What should be checkpointed?
11. When should the checkpoint advance?
12. What happens if the cursor expires?
13. How do you detect a pagination loop?
14. How would you prove extraction completeness?
15. How would you resume after a process crash?
16. How can inserts and deletes affect pagination?
17. When is parallel date-window extraction safe?
18. How would you combine `updated_since` with cursor pagination?
19. How would you design a production paginator for 500 million records?
20. How would you debug a pipeline that silently extracted 3% fewer records than expected?

---

# Part XXXI — Self-Review Answers

## 86. Why Can Offset Pagination Produce Duplicates?

Because offset identifies a position in the result sequence rather than a durable record boundary. If records are inserted or otherwise reordered between requests, a previously returned record can move into a later offset range.

---

## 87. Why Can Offset Pagination Skip Records?

Deletes or other changes can shift records toward earlier positions. When the client then skips the original offset, it can move past records that were not yet consumed.

---

## 88. When Would Cursor Pagination Be Appropriate?

When the source API explicitly provides cursor/token pagination and its semantics fit the extraction workload. The client should follow the documented cursor lifecycle and stopping rules.

---

## 89. What Is Keyset Pagination?

Keyset pagination continues after the last known ordered key instead of skipping a number of rows. A conceptual query is:

```sql
WHERE id > :last_id
ORDER BY id
LIMIT 100
```

---

## 90. Why Is Deterministic Ordering Important?

The continuation boundary must identify a stable position in the logical ordered result. If records can tie or reorder unpredictably, the extractor can skip or duplicate records.

---

## 91. Why Can `created_at > last_timestamp` Lose Records?

Multiple records can have the same timestamp. If only one of them has been processed, using a strict timestamp boundary can skip the remaining records with that timestamp.

---

## 92. How Does `(timestamp, id)` Help?

It creates a deterministic lexicographic boundary:

```text
(timestamp, id) > (last_timestamp, last_id)
```

The unique ID resolves timestamp ties.

---

## 93. What Makes a Stopping Condition Reliable?

It is defined by the API's documented semantics. Examples include an explicit `has_more=false`, absence of a documented next cursor, or absence of a documented `rel="next"` link.

A short page is not universally reliable.

---

## 94. Why Use a Generator?

A generator allows lazy consumption and can keep memory bounded. It also separates record retrieval from record processing.

---

## 95. What Should Be Checkpointed?

The state required to safely resume the extraction, such as:

- cursor,
- keyset boundary,
- page state,
- extraction window,
- relevant watermark,
- run identifier.

The exact state depends on the pagination strategy.

---

## 96. When Should the Checkpoint Advance?

After the corresponding page or unit of work has been durably handled according to the pipeline's commit semantics.

Conceptually:

```text
land
  ↓
checkpoint
```

not:

```text
checkpoint
  ↓
land
```

---

## 97. What Happens If the Cursor Expires?

The API may reject it. The pipeline should follow the documented recovery mechanism, which may involve restarting from a safe boundary, creating a fresh cursor, or reprocessing an overlap and deduplicating.

---

## 98. How Do You Detect a Pagination Loop?

Track pagination state and fail when an unexpected repeated cursor appears.

Also use a maximum page count.

---

## 99. How Would You Prove Completeness?

Use multiple independent signals where available:

- source totals,
- unique key counts,
- expected boundaries,
- page counts,
- reconciliation queries,
- checksums where appropriate.

Do not treat raw row count alone as proof.

---

## 100. How Would You Resume After a Crash?

Load the last durable checkpoint and continue from that state. If the state is no longer valid, use the source's documented recovery path.

The landing layer should tolerate safe replay.

---

## 101. How Can Inserts and Deletes Affect Pagination?

They can change the position of records in an offset-based sequence. This can cause duplicates and skipped records.

---

## 102. When Is Parallel Date-Window Extraction Safe?

When the source supports reliable date filtering, window boundaries are well-defined, pagination within each window is correct, and the resulting workload remains within operational constraints.

---

## 103. How Would You Combine `updated_since` With Cursor Pagination?

Use the watermark to define the logical incremental boundary and the cursor to traverse pages inside that boundary.

Maintain both as separate pieces of state.

---

## 104. How Would You Design a Production Paginator for 500 Million Records?

Start with source contract and workload requirements rather than choosing a pagination strategy by habit.

Then design:

```text
bounded extraction windows
+
appropriate pagination mechanism
+
server-side filtering
+
durable landing
+
checkpointing
+
idempotent replay
+
loop guards
+
completeness validation
+
observability
```

If the API contract supports safe date windows, parallel extraction may be considered with bounded concurrency and rate-limit awareness.

---

## 105. How Would You Debug a Pipeline That Extracted 3% Fewer Records?

First establish the extraction boundary and expected population.

Then compare:

```text
source totals
raw extracted rows
unique extracted keys
page count
termination reason
pagination state
window boundaries
```

Next inspect whether the issue is:

- early termination,
- skipped pages,
- offset movement,
- filter boundary,
- cursor expiration,
- failed page,
- duplicate/gap reconciliation.

Use evidence to isolate the root cause rather than changing the paginator blindly.

---

# Part XXXII — Core Engineering Principles

## 106. Principle 1

> **Pagination is a data correctness problem, not merely an API convenience.**

A paginator determines which records are included in the extraction.

---

## 107. Principle 2

> **Never assume the page size requested equals the number of records returned.**

The server may cap or otherwise vary the actual response size.

---

## 108. Principle 3

> **Never assume a short page means the extraction is complete unless the API contract says so.**

Stopping behavior must be based on documented semantics.

---

## 109. Principle 4

> **Changing source data can make offset pagination inconsistent.**

Positions can move when records are inserted or deleted.

---

## 110. Principle 5

> **Stable ordering is fundamental to reliable pagination.**

A continuation boundary needs deterministic semantics.

---

## 111. Principle 6

> **Persist progress so extraction can resume after failure.**

Long-running extraction should not depend on process memory alone.

---

## 112. Principle 7

> **Durably land data before advancing extraction state.**

This reduces the risk of creating gaps after a crash.

---

## 113. Principle 8

> **Protect against infinite pagination loops.**

Use repeated-state detection and bounded budgets.

---

## 114. Principle 9

> **Completeness must be demonstrated, not assumed.**

A record count is evidence, not automatically proof.

---

## 115. Principle 10

> **Pagination and incremental extraction often need to work together.**

A watermark defines the logical extraction boundary; pagination traverses that boundary.

---

# Part XXXIII — Final Challenge

## 116. Design Review Exercise

You are asked to ingest customer records from an API.

The API exposes:

```text
GET /customers
```

It supports:

```text
updated_since
limit
cursor
```

The API returns:

```json
{
  "data": [
    {
      "id": "c-001",
      "updated_at": "2026-10-01T10:00:00Z"
    }
  ],
  "next_cursor": "abc123",
  "has_more": true
}
```

Your ingestion system must handle:

```text
100,000+ records
changing source data
process crashes
cursor expiration
API rate limits
incremental extraction
```

### Design the system

Before looking at the reference answer, specify:

1. What is the extraction boundary?
2. What is the page state?
3. What gets checkpointed?
4. When does the checkpoint advance?
5. How do you resume?
6. How do you detect a loop?
7. What happens if the cursor expires?
8. How do you validate completeness?
9. How do you handle duplicates?
10. How do you prevent an infinite extraction?
11. How do you observe the run?
12. How do you safely advance the watermark?

---

# Part XXXIV — Reference Architecture

## 117. End-to-End Flow

```text
                 +----------------------+
                 | Extraction boundary |
                 | watermark / window   |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |     API Client       |
                 | timeout + HTTP       |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |      Paginator       |
                 | cursor + guards      |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   Page validation    |
                 | schema + identities  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |  Durable landing     |
                 | raw page / records   |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Cursor checkpoint    |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Completeness checks  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Advance watermark    |
                 +----------------------+
```

The architecture separates:

```text
logical extraction boundary
```

from:

```text
position inside that boundary
```

That distinction is fundamental.

---

# Part XXXV — Checkpoint / Self-Assessment

## 118. Beginner Checkpoint

Can you explain in your own words:

- why APIs paginate,
- what a page size is,
- what an offset is,
- what a cursor is,
- what keyset pagination means?

If not, review Parts I–III.

---

## 119. Intermediate Checkpoint

Can you implement:

- offset pagination,
- cursor pagination,
- keyset pagination,
- Link-header pagination?

Can you explain:

- why a short page is not automatically terminal,
- why stable ordering matters,
- why offset pagination can fail under inserts and deletes?

If not, review Parts III–IX.

---

## 120. Advanced Checkpoint

Can you design:

- durable checkpoints,
- crash recovery,
- cursor-expiration recovery,
- loop protection,
- completeness validation,
- date-window extraction,
- `updated_since + cursor`?

Can you explain why:

```text
land
  ↓
checkpoint
```

is safer than:

```text
checkpoint
  ↓
land
```

If not, review Parts XV–XXII.

---

## 121. Architecture Checkpoint

Given a new API, can you answer all of these before writing the paginator?

```text
1. What pagination mechanism does the API document?
2. What is the ordering?
3. Is the ordering deterministic?
4. What is the continuation state?
5. What is the reliable stopping condition?
6. Can the source change during extraction?
7. What happens if the process crashes?
8. How long are cursors valid?
9. What state must be checkpointed?
10. How will completeness be validated?
11. Can the extraction be safely partitioned?
12. What operational budgets are required?
```

If you cannot answer these, implementation should not begin yet.

---

# Part XXXVI — Production Readiness Checklist

Before putting a paginator into production, verify:

### Source contract

- [ ] Pagination mechanism is documented.
- [ ] Requested page size semantics are documented.
- [ ] Maximum page size is known.
- [ ] Ordering semantics are known.
- [ ] Continuation state semantics are known.
- [ ] Cursor expiration behavior is understood.
- [ ] Stopping condition is documented.
- [ ] Filtering semantics are documented.

### Correctness

- [ ] Stable ordering is understood.
- [ ] Changing-data behavior has been considered.
- [ ] Duplicate handling is defined.
- [ ] Missing-record detection is defined.
- [ ] Boundary behavior is tested.
- [ ] Completeness validation exists.

### Reliability

- [ ] Checkpoint state is durable.
- [ ] Checkpoint advancement follows data durability.
- [ ] Crash/restart behavior is tested.
- [ ] Cursor expiration recovery is defined.
- [ ] Repeated-cursor detection exists.
- [ ] Maximum page guard exists.
- [ ] Request/time/record budgets exist where appropriate.

### Performance

- [ ] Page size has been measured.
- [ ] Connection reuse is enabled where appropriate.
- [ ] Server-side filtering is used when appropriate.
- [ ] Request volume is understood.
- [ ] Response size is understood.
- [ ] Deep-page behavior is understood.
- [ ] Parallel windows are used only when safe.
- [ ] API rate limits are respected.

### Operations

- [ ] Run ID is logged.
- [ ] Page count is logged.
- [ ] Record count is logged.
- [ ] Unique key count is observable where appropriate.
- [ ] Termination reason is logged.
- [ ] Errors are observable.
- [ ] Checkpoint state is observable without exposing secrets.
- [ ] Alerts exist for abnormal completeness or runtime behavior.

---

# Part XXXVII — Final Takeaways

The progression through this chapter should now be:

```text
Beginner
   ↓
Understand why pagination exists
   ↓
Understand page size
   ↓
Implement offset pagination
   ↓
Understand offset correctness problems
   ↓
Implement cursor pagination
   ↓
Understand cursor expiration
   ↓
Understand keyset pagination
   ↓
Understand composite keyset boundaries
   ↓
Understand Link headers
   ↓
Understand GraphQL connections
   ↓
Choose reliable stopping conditions
   ↓
Build generator-based paginators
   ↓
Separate client and paginator responsibilities
   ↓
Handle changing datasets
   ↓
Implement checkpoints
   ↓
Recover from crashes
   ↓
Detect loops
   ↓
Validate completeness
   ↓
Combine pagination with incremental extraction
   ↓
Understand parallel date windows
   ↓
Build and test a production-grade paginator
   ↓
Defend the design in an architecture review
```

The most important lesson is not to memorize one pagination pattern.

Instead, develop the habit of asking:

```text
What does the API contract guarantee?
             +
What does the workload require?
             +
What happens when the source changes?
             +
How is progress made durable?
             +
How will completeness be demonstrated?
```

A reliable paginator is therefore not merely a loop around HTTP requests.

It is a small stateful data-ingestion component with:

```text
source-contract understanding
+
pagination state
+
ordering semantics
+
termination logic
+
durability
+
recovery
+
safety guards
+
validation
+
observability
```

Once these ideas are understood, pagination becomes an engineering design problem that can be reasoned about systematically rather than a collection of URL parameters to copy from an API tutorial.
