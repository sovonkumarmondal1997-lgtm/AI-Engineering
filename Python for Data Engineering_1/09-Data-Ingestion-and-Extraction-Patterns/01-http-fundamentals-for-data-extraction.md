# HTTP Fundamentals for Data Extraction

> **Module 2.9 — Data Ingestion and Extraction Patterns**  
> **Topic 01 — HTTP Fundamentals for Data Extraction**

This chapter builds the HTTP mental model required for production data extraction. It starts with the simplest question—"How does a program get data from another system?"—and progressively reaches connection reuse, conditional requests, streaming, asynchronous exports, HTTP/2, proxies, TLS inspection, and production debugging.

The goal is **not** to memorize HTTP trivia. The goal is to understand what your extraction program is asking a remote system to do, what the remote system actually returned, and what that means for correctness, reliability, performance, and operations.

---

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain the HTTP request/response model in your own words.
- Read and construct a basic HTTP request and response.
- Decompose a URL into scheme, host, port, path, query string, and fragment.
- Explain GET, POST, PUT, PATCH, DELETE, and HEAD without confusing protocol semantics with API-specific behavior.
- Explain important HTTP headers from a data-engineering perspective.
- Distinguish `Accept` from `Content-Type`.
- Inspect response status codes and choose an appropriate general pipeline action.
- Explain why `200 OK` does not necessarily mean "usable data".
- Explain DNS, TCP, TLS, and HTTPS at an operational level.
- Explain why connection reuse and connection pooling matter for extraction jobs.
- Explain HTTP compression and its CPU/network trade-off.
- Explain streaming and why it protects memory when downloading large responses.
- Explain caching, ETags, `If-None-Match`, `Last-Modified`, and `If-Modified-Since`.
- Explain HTTP idempotency and why it matters when retrying requests.
- Recognize REST, GraphQL, gRPC, and SOAP/XML interfaces.
- Read a basic OpenAPI document before implementing an extractor.
- Design the mental model for an asynchronous export workflow.
- Explain the practical differences between HTTP/1.1 and HTTP/2.
- Explain forward proxies and corporate TLS inspection.
- Debug an HTTP extraction failure systematically.
- Use `curl` to inspect an API.
- Build and exercise a small local FastAPI mock API.
- Explain how HTTP concerns map into a production ingestion architecture.

## Prerequisites

This chapter assumes that you are comfortable with:

- Python basics.
- The command line.
- JSON at a basic level.
- Basic networking vocabulary such as "server", "client", and "internet".

It does **not** assume that you already understand HTTP deeply.

Later topics in this module will build on this chapter:

- Topic 02: `httpx` and `requests`, sessions, and timeouts.
- Topic 03: API authentication, keys, OAuth2, and token refresh.
- Topic 04: pagination.
- Topic 05: rate limits, `429`, retries, and `Retry-After`.
- Topic 06: full vs incremental extraction and watermarks.
- Topic 07: CDC.
- Topic 08: webhooks.
- Topic 09: HTML parsing and responsible scraping.
- Topic 10: SFTP and file-drop ingestion.
- Topic 11: ingestion frameworks and managed connectors.

Those topics may be mentioned here when necessary, but they are not re-taught here.

---

# 1. Why HTTP Matters in Data Engineering

A data pipeline frequently needs data that lives somewhere else:

```text
SaaS application
       |
       | HTTPS
       v
HTTP API
       |
       | response
       v
Extraction process
       |
       v
Raw / Bronze landing
       |
       v
Transformation
       |
       v
Warehouse / Lakehouse
```

The HTTP layer is therefore often the boundary between your pipeline and an external source.

Examples include:

- extracting customers from a CRM;
- downloading orders from an e-commerce platform;
- requesting an export from an analytics SaaS;
- retrieving a JSON configuration;
- downloading CSV files exposed through HTTP;
- fetching a large JSONL export;
- checking whether a remote resource changed before downloading it.

A useful production mental model is:

```text
Data Engineer's Pipeline
        |
        v
   HTTP Client
        |
        v
      DNS
        |
        v
   TCP + TLS
        |
        v
 HTTP Request
        |
        v
 API / Server
        |
        v
 HTTP Response
        |
        v
 Response Validation
        |
        v
 Raw / Bronze Landing
```

Every layer can fail independently.

For example:

- DNS can fail before an HTTP request exists.
- TLS verification can fail before application data is exchanged.
- The server can return `401`.
- The server can return `200` with an HTML error page.
- A huge response can exhaust container memory.
- A retry can duplicate a remote operation.

That is why HTTP is not merely "how Python downloads JSON". It is part of the reliability boundary of an ingestion system.

---

# 2. HTTP Mental Model

## 2.1 What is HTTP?

HTTP—**Hypertext Transfer Protocol**—is an application-layer protocol used for communication between clients and servers.

A simple mental model is:

> A client asks a server to perform an operation, and the server sends back a response.

```text
Client
  |
  | "Please give me these customers."
  |
  v
Server
  |
  | "Here are the customers."
  |
  v
Client
```

The real protocol is more precise. The request contains structured information such as:

- method;
- target URL/path;
- headers;
- optionally a body.

The response contains:

- status;
- headers;
- optionally a body.

## 2.2 Why does HTTP exist?

Distributed systems need a common language.

Without a protocol, every application would have to invent its own rules for:

- addressing a resource;
- asking for data;
- sending data;
- indicating success;
- reporting errors;
- describing content;
- negotiating representations.

HTTP provides standardized semantics for these concerns.

## 2.3 A data-engineering analogy

Imagine a warehouse receiving shipments.

The request is the order form:

```text
Method: GET
Resource: /customers
Filters: status=active
```

The response is the shipment:

```text
Status: 200
Contents: customer records
Metadata: format, size, caching information
```

The analogy is useful, but HTTP is more precise than a physical shipment: status codes, headers, methods, and caching have defined protocol semantics.

---

# 3. The HTTP Request/Response Cycle

A simplified extraction lifecycle is:

```text
Extractor
   |
   | 1. Resolve hostname
   v
 DNS
   |
   | 2. Establish network connection
   v
 TCP
   |
   | 3. Establish encrypted session
   v
 TLS
   |
   | 4. Send HTTP request
   v
 API Server
   |
   | 5. Send HTTP response
   v
 Extractor
   |
   | 6. Validate and process
   v
 Raw / Bronze Landing
```

Not every connection follows exactly this sequence—for example, an existing connection can be reused—but it is a useful first model.

## 3.1 Client

The **client** initiates the HTTP exchange.

For data engineering, the client may be:

- a Python process;
- an ingestion service;
- a command-line program such as `curl`;
- an orchestration worker.

## 3.2 Server

The **server** receives the request and produces a response.

For an extractor, this might be:

- a SaaS API;
- an internal service;
- an object-download endpoint;
- a gateway in front of an API.

## 3.3 Request

A simplified request looks like:

```http
GET /v1/customers?status=active HTTP/1.1
Host: api.example.com
Accept: application/json
User-Agent: my-ingestor/1.0
```

The request tells the server what the client wants and supplies metadata needed to interpret the request.

## 3.4 Response

A simplified response looks like:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "customers": [
    {"id": 1, "name": "Asha"},
    {"id": 2, "name": "Ravi"}
  ]
}
```

The response tells the client whether the request succeeded and, when appropriate, returns data.

## 3.5 Production extraction lifecycle

A robust extractor should conceptually do:

```text
Build request
     |
Send request
     |
Receive response
     |
Inspect status
     |
Inspect headers
     |
Validate Content-Type
     |
Validate body structure
     |
Write raw data
     |
Record metadata
```

Do not jump directly from "HTTP response received" to "load JSON into the warehouse".

---

# 4. URLs

Consider:

```text
https://api.example.com:443/v1/customers?status=active&page=2#section
```

A URL can be decomposed as:

```text
https://api.example.com:443/v1/customers?status=active&page=2#section
 \__/   \________________\_/ \______________/\________________/\_______/
 scheme       host         port      path          query       fragment
```

## 4.1 Scheme

```text
https
```

The scheme identifies the protocol being used.

For production APIs, HTTPS is normally expected.

## 4.2 Host

```text
api.example.com
```

The hostname identifies the destination.

DNS translates a hostname into network address information.

## 4.3 Port

```text
443
```

The default port for HTTPS is 443.

The port may be omitted when the default is used.

## 4.4 Path

```text
/v1/customers
```

The path identifies the requested resource or route.

APIs frequently use paths such as:

```text
/customers
/customers/123
/orders
/orders/2026
```

## 4.5 Query string

```text
?status=active&page=2
```

The query string contains query parameters.

Here:

```text
status=active
page=2
```

Query parameters commonly control:

- filters;
- sorting;
- page selection;
- field selection;
- date ranges;
- limits.

Later, pagination will be studied in detail.

## 4.6 Fragment

```text
#section
```

Fragments are generally client-side identifiers and are not normally sent to the server as part of an HTTP request target.

For API extraction, fragments are usually irrelevant.

## 4.7 Path parameters vs query parameters

Compare:

```text
/customers/123
```

with:

```text
/customers?id=123
```

These are different API designs.

The first commonly expresses:

> Resource `123` under `/customers`.

The second commonly expresses:

> Query `/customers` using a filter named `id`.

Do not assume that one is universally correct. Follow the API contract.

## 4.8 URL encoding

URLs have reserved characters.

For example, a search value containing spaces may be encoded:

```text
?q=customer%20support
```

Python can safely construct query parameters rather than manually concatenating strings:

```python
from urllib.parse import urlencode

params = {
    "q": "customer support",
    "status": "active",
}

query_string = urlencode(params)
print(query_string)
```

Output:

```text
q=customer+support&status=active
```

This prevents many mistakes involving escaping.

## 4.9 Why query parameters matter to extraction

A filter can dramatically change data volume:

```text
/customers
```

might return 10 million records, while:

```text
/customers?status=active
```

might return 2 million.

The extraction contract therefore affects:

- network transfer;
- source load;
- memory;
- runtime;
- downstream storage;
- correctness.

---

# 5. HTTP Methods

HTTP methods describe the intended semantics of a request.

| Method | Typical purpose | Request body | Idempotent by HTTP semantics? | Data-engineering example |
|---|---|---|---|---|
| GET | Retrieve a representation | Usually no | Yes | Extract customers |
| POST | Submit data / create / start an operation | Often yes | No, by default | Start an export |
| PUT | Replace a resource representation | Often yes | Yes | Replace configuration |
| PATCH | Partially modify a resource | Often yes | Not inherently | Update selected fields |
| DELETE | Delete a resource | Usually no | Yes | Delete a remote resource |
| HEAD | Retrieve headers without response body | No | Yes | Check metadata |

**Important:** HTTP semantics and application behavior are different things. An API can implement application-specific behavior that changes what repeated requests do in practice.

## 5.1 GET

Conceptually:

```http
GET /customers/123
```

The client is asking for a representation of a resource.

A common extraction use case:

```text
GET /customers
```

returns customer data.

GET requests should generally be safe for an extractor to repeat, assuming the API follows normal HTTP semantics.

## 5.2 POST

Example:

```http
POST /exports
Content-Type: application/json

{
  "resource": "orders",
  "format": "jsonl"
}
```

POST can create a resource or initiate an operation.

That is important for data extraction because "reading data" does not always mean the HTTP method must be GET.

A SaaS platform may need to:

1. accept an export request;
2. generate a large file asynchronously;
3. return an export identifier.

## 5.3 PUT

PUT commonly means replacing the representation at a target resource.

Repeated identical PUT operations are defined as idempotent by HTTP semantics, although application-specific side effects still matter.

## 5.4 PATCH

PATCH is commonly used for partial modification.

Do not assume that repeating the same PATCH is idempotent merely because the same JSON body is sent twice.

## 5.5 DELETE

DELETE is defined as idempotent in HTTP semantics: repeating the request has the same intended effect on the resource state once it is deleted.

That does **not** mean every response will be identical.

## 5.6 HEAD

HEAD asks for the headers associated with a resource without requesting the response body.

It can be useful for metadata checks:

```text
Does this resource exist?
What is its content type?
What is its reported size?
Has it changed?
```

Server implementations vary, so test important behavior against the actual API.

---

# 6. HTTP Headers

Headers are metadata associated with requests and responses.

A useful mental model:

```text
HTTP message
├── start line
├── headers
└── body
```

Headers communicate metadata without placing it in the primary data payload.

## 6.1 `Accept`

`Accept` tells the server which response media types the client can accept.

Example:

```http
Accept: application/json
```

Conceptually:

> "If possible, return JSON."

This is **not** the same as `Content-Type`.

## 6.2 `Content-Type`

`Content-Type` describes the media type of the message body.

Request:

```http
Content-Type: application/json
```

means the request body is JSON.

Response:

```http
Content-Type: application/json
```

means the response body is JSON.

## 6.3 `Authorization`

An `Authorization` header commonly carries authentication/authorization credentials.

Example shape:

```http
Authorization: Bearer <token>
```

Authentication is intentionally only introduced here. Detailed API keys, OAuth2, and token refresh belong to Topic 03.

Never print credentials into ordinary pipeline logs.

## 6.4 `User-Agent`

Example:

```http
User-Agent: customer-ingestor/1.0
```

A useful User-Agent identifies your client.

It can help API operators distinguish traffic and diagnose issues.

## 6.5 `Accept-Encoding`

Example:

```http
Accept-Encoding: gzip, br
```

This communicates supported response compression formats.

The server may then return a compressed representation.

## 6.6 `If-None-Match`

Used for conditional retrieval with an ETag:

```http
If-None-Match: "abc123"
```

If the resource has not changed, the server may return:

```http
304 Not Modified
```

## 6.7 `If-Modified-Since`

A time-based conditional request:

```http
If-Modified-Since: Wed, 01 Oct 2026 10:00:00 GMT
```

The server may return `304` when it considers the resource unchanged since that time.

## 6.8 `Host`

The `Host` header identifies the target host for HTTP/1.1 requests.

It is especially important when multiple virtual hosts share infrastructure.

## 6.9 `Content-Length`

Indicates the length of the message body when that framing mechanism is used.

It can help clients understand expected body size.

## 6.10 `Transfer-Encoding`

This can describe transfer coding such as chunked transfer in HTTP/1.1.

Do not confuse transfer framing with the logical content format.

For example:

```text
Transfer-Encoding: chunked
Content-Type: application/json
```

means the JSON representation is transported in chunks. It does not mean the JSON itself has been divided into separate JSON documents.

---

# 7. Request Bodies

Not every HTTP request has a body.

GET commonly does not. POST, PUT, and PATCH frequently do.

## 7.1 JSON body

```http
POST /exports HTTP/1.1
Content-Type: application/json

{
  "resource": "customers",
  "format": "jsonl"
}
```

The `Content-Type` tells the server how to interpret the body.

## 7.2 Form data

A form-encoded body can look like:

```text
resource=customers&format=jsonl
```

with an appropriate media type.

## 7.3 Multipart form data

`multipart/form-data` is useful when a request contains multiple parts, such as fields and uploaded files.

It is common in web applications and file-upload APIs.

## 7.4 Raw or binary bodies

A body may contain bytes rather than JSON or form fields.

For example:

```text
application/octet-stream
```

may be used for arbitrary binary data.

## 7.5 Why POST can be used for extraction

Suppose an API must generate a 500 GB export.

A request might be:

```http
POST /exports
Content-Type: application/json

{
  "resource": "transactions",
  "from": "2026-01-01",
  "to": "2026-09-30",
  "format": "jsonl"
}
```

The operation is logically about obtaining data, but POST is appropriate because the client is **submitting an export job request** rather than simply retrieving an already-defined representation.

---

# 8. HTTP Responses

A response consists conceptually of:

```text
HTTP Response
├── Status line
├── Headers
└── Body
```

Example:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 87

{
  "customers": [
    {"id": 1, "name": "Asha"}
  ]
}
```

## 8.1 Status line

```text
HTTP/1.1 200 OK
```

It communicates:

- HTTP version;
- status code;
- reason phrase.

The numeric status code is the important machine-readable part.

## 8.2 Response headers

Examples:

```http
Content-Type: application/json
ETag: "abc123"
Cache-Control: max-age=60
Content-Encoding: gzip
```

These can affect how an extractor should interpret the response.

## 8.3 Response body

The body can contain:

- JSON;
- CSV;
- NDJSON/JSON Lines;
- XML;
- binary data;
- an empty body.

Never assume the body is JSON merely because the endpoint is called an "API".

---

# 9. HTTP Status Codes

Status codes are grouped into five families:

```text
1xx  Informational
2xx  Success
3xx  Redirection / caching-related outcomes
4xx  Client/request-side issue
5xx  Server-side failure
```

A status code is evidence about what happened at the HTTP layer. It is not a complete explanation of the application's business state.

## 9.1 `200 OK`

The request succeeded.

Typical action:

```text
Inspect headers
     |
Validate body
     |
Process data
```

Do not stop at `200`.

A server can return `200` with:

```http
Content-Type: text/html
```

when your extractor expected JSON.

## 9.2 `201 Created`

The request succeeded and created a resource.

Common after POST.

For an extractor, this may appear when creating an export job or another remote resource.

Retrying POST based only on the absence of a response is dangerous because the server might already have created the resource.

## 9.3 `202 Accepted`

The server accepted the request for processing, but the operation is not necessarily complete.

Typical extraction interpretation:

```text
202
 |
 +--> operation started
 |
 +--> poll status
 |
 +--> wait for terminal state
```

It is central to asynchronous exports.

## 9.4 `204 No Content`

The operation succeeded and there is no response body.

Do not call a JSON parser simply because the HTTP request succeeded.

## 9.5 `301 Moved Permanently`

The resource has been permanently redirected.

For an extractor, investigate the `Location` header and whether following redirects is appropriate.

Do not blindly follow arbitrary redirects when security or data-integrity assumptions depend on the original host.

## 9.6 `302 Found`

A temporary redirect.

Historically, client behavior around POST redirects has varied, so do not assume all clients preserve method/body behavior identically.

## 9.7 `307 Temporary Redirect`

A temporary redirect that preserves the request method and request body semantics.

This distinction matters for non-GET requests.

## 9.8 `308 Permanent Redirect`

A permanent redirect with method/body preservation semantics similar to `307`.

## 9.9 `304 Not Modified`

This is a special response to a conditional request.

It means, in effect:

> The selected representation has not changed according to the validator used.

Typical action:

```text
Reuse existing representation
or
Skip downloading unchanged content
```

It is not an ordinary successful response containing a body.

## 9.10 `400 Bad Request`

The server could not process the request as sent.

Possible causes:

- malformed JSON;
- invalid query parameter;
- missing required field;
- invalid syntax.

Typical action:

```text
Do not blindly retry.
Inspect the request and API contract.
```

## 9.11 `401 Unauthorized`

The request lacks valid authentication credentials in the sense defined by the API.

Possible causes:

- missing credential;
- expired credential;
- invalid credential.

Authentication implementation belongs to Topic 03.

Typical action:

```text
Inspect authentication configuration.
```

## 9.12 `403 Forbidden`

The server understood the request but refuses to authorize it.

Possible causes:

- insufficient permissions;
- access policy;
- source IP restriction;
- account restriction.

A retry usually does not fix a permissions problem.

## 9.13 `404 Not Found`

The server could not find the requested resource.

Possible causes:

- wrong URL;
- wrong resource identifier;
- deleted resource;
- API version mismatch.

Do not blindly retry.

## 9.14 `408 Request Timeout`

The server timed out waiting for the request.

This may be transient, but retry policy should consider the operation and request safety.

## 9.15 `409 Conflict`

The request conflicts with the current state of the target resource.

For data pipelines this might indicate:

- duplicate creation;
- state conflict;
- concurrent operation.

Inspect the API's documented semantics.

## 9.16 `410 Gone`

The target resource is no longer available and the condition is considered permanent.

This is generally not a useful retry candidate.

## 9.17 `422 Unprocessable Content`

The server understands the request but cannot process its content according to the API's validation rules.

Examples:

- invalid field value;
- invalid date range;
- schema validation failure.

Do not blindly retry unchanged input.

## 9.18 `429 Too Many Requests`

The client is being rate limited.

A production extractor should inspect available rate-limit metadata and, when provided, `Retry-After`.

Detailed rate-limit and retry algorithms belong to Topic 05.

## 9.19 `500 Internal Server Error`

The server encountered an unexpected condition.

It can be transient or persistent.

A retry may be appropriate depending on the operation and the API's behavior.

## 9.20 `502 Bad Gateway`

A gateway or proxy received an invalid response from an upstream service.

This is often transient, but not always.

## 9.21 `503 Service Unavailable`

The service is temporarily unable or unwilling to handle the request.

Possible causes include:

- maintenance;
- overload;
- dependency failure.

A `Retry-After` header may provide guidance.

## 9.22 `504 Gateway Timeout`

A gateway did not receive a timely response from an upstream service.

It may be transient.

## 9.23 Production-oriented status table

| Status | Meaning | General pipeline action | Blind retry? |
|---|---|---|---|
| 200 | Success | Validate and process | No |
| 201 | Created | Record created resource/result | No |
| 202 | Accepted | Poll operation state | No |
| 204 | Success, no body | Treat as empty response | No |
| 301/302 | Redirect | Inspect destination/policy | Not automatically |
| 307/308 | Redirect preserving method | Inspect destination/policy | Not automatically |
| 304 | Not modified | Reuse/skip unchanged representation | No |
| 400 | Invalid request | Fix request | No |
| 401 | Authentication problem | Fix credentials/auth flow | No |
| 403 | Forbidden | Fix authorization/policy | No |
| 404 | Not found | Verify path/resource | Usually no |
| 408 | Request timeout | Investigate; possibly retry | Context-dependent |
| 409 | Conflict | Inspect resource state | Context-dependent |
| 410 | Gone | Update extraction state/configuration | Usually no |
| 422 | Validation failure | Fix input | No |
| 429 | Rate limited | Respect server guidance | Yes, with policy |
| 500 | Server error | Investigate; possibly retry | Context-dependent |
| 502 | Bad gateway | Investigate; possibly retry | Context-dependent |
| 503 | Unavailable | Respect `Retry-After`; possibly retry | Context-dependent |
| 504 | Gateway timeout | Investigate; possibly retry | Context-dependent |

**Important:** detailed retry strategy is a later topic. Status codes provide signals; they do not mechanically determine the correct retry action in every application.

---

# 10. Content Types and Content Negotiation

## 10.1 Common content types

### JSON

```http
Content-Type: application/json
```

### CSV

```http
Content-Type: text/csv
```

### NDJSON

```http
Content-Type: application/x-ndjson
```

NDJSON contains one JSON value per line and is often useful for streaming records.

### Binary

```http
Content-Type: application/octet-stream
```

This indicates generic binary data.

## 10.2 `Accept` versus `Content-Type`

A simple distinction:

```text
Accept
   |
   +--> What response representation can I accept?

Content-Type
   |
   +--> What representation is this body?
```

Request:

```http
Accept: application/json
Content-Type: application/json
```

can mean:

- the request body is JSON;
- the client prefers a JSON response.

But the two headers have different roles.

## 10.3 Never blindly call `response.json()`

This is fragile:

```python
data = response.json()
```

A safer conceptual pattern is:

```python
content_type = response.headers.get("content-type", "").lower()

if "application/json" in content_type:
    data = response.json()
elif "text/csv" in content_type:
    text = response.text
    # Parse CSV.
else:
    # Inspect the response before deciding how to process it.
    raise ValueError(f"Unexpected content type: {content_type!r}")
```

This is intentionally simplified. Production code should also handle malformed payloads and documented media-type variations.

## 10.4 `200 OK` with HTML

Consider:

```http
HTTP/1.1 200 OK
Content-Type: text/html
```

while your pipeline expects:

```text
application/json
```

Possible causes include:

- a reverse proxy error page;
- a login page;
- a misconfigured endpoint;
- a documentation page;
- an application-level error represented as HTML.

**Lesson:** HTTP status and payload semantics are separate validation dimensions.

---

# 11. DNS, TCP, TLS, and HTTPS

HTTP operates above lower network layers.

A simplified model is:

```text
Application
    |
   HTTP
    |
   TLS
    |
   TCP
    |
   IP
    |
 Network
```

DNS is used to discover address information for a hostname.

## 11.1 DNS

Suppose the URL is:

```text
https://api.example.com/customers
```

The hostname:

```text
api.example.com
```

must be resolved through DNS.

Conceptually:

```text
api.example.com
       |
       v
      DNS
       |
       v
IP address information
```

If DNS fails, the HTTP server may never receive a request.

### Data-engineering debugging implication

If your extractor reports:

```text
Name or service not known
```

or a similar resolution failure, do not start debugging JSON parsing. The request may never have reached the API.

## 11.2 TCP

TCP provides a transport connection for many HTTP/1.1 and HTTP/2 deployments.

Connection establishment has a cost.

That cost becomes important when an extractor performs thousands of requests.

## 11.3 TLS

TLS provides encrypted communication and server authentication through certificates and trust relationships.

Important operational concepts:

- certificate;
- hostname verification;
- certificate authority (CA);
- trust chain;
- certificate expiration;
- trusted CA bundle.

You do not need to learn cryptography mathematics for this topic.

## 11.4 HTTPS

A useful simplification is:

```text
HTTP over TLS = HTTPS
```

HTTPS protects the communication channel against many forms of network eavesdropping and tampering.

It does **not** guarantee that:

- the API is logically correct;
- the response is truthful;
- the application has correct authorization;
- the returned data is complete;
- your pipeline validated the payload.

Encryption is not data-quality validation.

## 11.5 Practical connection flow

```text
1. DNS lookup
      |
2. TCP connection
      |
3. TLS handshake
      |
4. Certificate validation
      |
5. Encrypted HTTP request
      |
6. Encrypted HTTP response
```

Existing connections can skip some setup steps because they may be reused.

---

# 12. Connection Reuse and Keep-Alive

Opening a network connection repeatedly is expensive.

A simplified bad pattern:

```text
Request A
  |
  +--> connect
  +--> TLS handshake
  +--> request
  +--> response
  +--> close

Request B
  |
  +--> connect
  +--> TLS handshake
  +--> request
  +--> response
  +--> close
```

A reusable connection can conceptually behave like:

```text
connect
  |
TLS
  |
request A -> response A
  |
request B -> response B
  |
request C -> response C
  |
close
```

The exact behavior depends on the HTTP version and client/server implementation.

## 12.1 Why this matters for extraction

Suppose a job makes:

```text
100 requests
```

versus:

```text
100,000 requests
```

Connection setup overhead can become a significant fraction of runtime.

Connection reuse can reduce:

- TCP handshake overhead;
- TLS handshake overhead;
- latency;
- CPU work;
- connection pressure.

This is why later Topic 02 introduces reusable HTTP clients/sessions.

## 12.2 What not to learn yet

Do not memorize `httpx.Client` configuration here.

The conceptual requirement is:

> A production extractor should generally reuse connections rather than constructing a completely new network connection for every request.

Detailed client configuration belongs to Topic 02.

---

# 13. Compression

HTTP can compress response bodies.

A request may advertise support:

```http
Accept-Encoding: gzip, br
```

The server may return:

```http
Content-Encoding: gzip
```

Conceptually:

```text
Logical dataset
      |
      v
 compression
      |
      v
 fewer bytes over network
      |
      v
 decompression
      |
      v
 original representation
```

## 13.1 Why compression exists

For large payloads, network transfer can dominate runtime.

Compression can reduce:

- bytes transferred;
- bandwidth usage;
- transfer time;
- network cost.

## 13.2 The trade-off

Compression consumes CPU.

```text
Compression
   |
   +--> lower network bytes
   |
   +--> more CPU work
```

The right balance depends on workload and infrastructure.

## 13.3 Compression is not encryption

These solve different problems:

```text
Compression -> reduce representation size

Encryption  -> protect confidentiality/integrity/authentication
```

A compressed response is not automatically secure.

---

# 14. Streaming and Chunked Transfer

Large API responses can be dangerous if the client loads the entire response into memory.

Conceptually:

```python
body = response.read()
```

means:

```text
Server
  |
  | huge response
  v
Client memory
  |
  v
Process everything
```

For a sufficiently large response, this can produce:

```text
Memory pressure
     |
     v
Container OOM
     |
     v
Pipeline failure
```

Streaming changes the model:

```text
Server
  |
  +--> chunk 1 --> process/write
  |
  +--> chunk 2 --> process/write
  |
  +--> chunk 3 --> process/write
  |
  +--> chunk 4 --> process/write
```

A conceptual Python example using `httpx`:

```python
import httpx

with httpx.stream("GET", "http://localhost:8000/large-export") as response:
    response.raise_for_status()

    for chunk in response.iter_bytes():
        if chunk:
            # In production, write the chunk to a raw destination.
            print(f"Received {len(chunk)} bytes")
```

This is intentionally conceptual. Detailed `httpx` streaming configuration belongs to Topic 02.

## 14.1 Chunked transfer versus application streaming

Do not treat these as identical terms.

- **Streaming** describes how the client/server progressively handle a response.
- **Chunked transfer encoding** is one HTTP/1.1 transfer-framing mechanism.

A response can be large and streamed without implying a particular application-level record format.

## 14.2 Data-engineering connection

For large exports:

```text
HTTP response
     |
     v
stream
     |
     v
raw file/object
     |
     v
Bronze/raw landing
```

This gives you bounded memory behavior.

---

# 15. HTTP Caching

Caching exists to avoid unnecessary work.

A cache may allow a previously obtained representation to be reused when it is still fresh or validated as unchanged.

For ingestion, caching can reduce:

- network transfer;
- source load;
- latency;
- unnecessary processing.

The exact caching behavior depends on HTTP cache-control metadata and the architecture.

## 15.1 Freshness

A representation can be considered fresh for some period.

For example:

```http
Cache-Control: max-age=60
```

conceptually indicates that the representation can be considered fresh for 60 seconds under the relevant cache rules.

## 15.2 Validation

When freshness expires, a client/cache can sometimes ask:

> Has the representation changed?

This is where ETags and Last-Modified become important.

---

# 16. ETag and Conditional Requests

An **ETag** is a validator associated with a selected representation.

First request:

```text
Client
  |
  | GET /customers
  v
Server
  |
  | 200
  | ETag: "abc123"
  v
Client
```

The client can retain:

```text
"abc123"
```

Later:

```text
Client
  |
  | GET /customers
  | If-None-Match: "abc123"
  v
Server
  |
  | 304 Not Modified
  v
Client
```

The server is saying that the representation has not changed according to the validator.

## 16.1 Why this matters for ingestion

Suppose an extractor downloads a 500 MB resource every hour.

If the resource has not changed, downloading 500 MB repeatedly is wasteful.

Conditional retrieval can reduce:

```text
500 MB
500 MB
500 MB
...
```

to:

```text
initial 500 MB
small conditional request/response
small conditional request/response
...
```

The exact savings depend on the protocol and cache behavior.

## 16.2 `curl` example

First inspect the resource:

```bash
curl -i http://localhost:8000/cached-resource
```

Suppose the response contains:

```http
ETag: "abc123"
```

Then:

```bash
curl -i \
  -H 'If-None-Match: "abc123"' \
  http://localhost:8000/cached-resource
```

A correctly implemented mock may return:

```http
HTTP/1.1 304 Not Modified
```

## 16.3 Python conceptual example

```python
import httpx

etag = '"abc123"'

headers = {
    "If-None-Match": etag,
}

response = httpx.get(
    "http://localhost:8000/cached-resource",
    headers=headers,
)

if response.status_code == 304:
    print("Resource did not change.")
elif response.is_success:
    print("Resource changed; process the new body.")
else:
    print("Unexpected response:", response.status_code)
```

---

# 17. Last-Modified and Conditional Requests

Another validator is:

```http
Last-Modified: Wed, 01 Oct 2026 10:00:00 GMT
```

A client can later send:

```http
If-Modified-Since: Wed, 01 Oct 2026 10:00:00 GMT
```

The server may respond:

```http
304 Not Modified
```

## 17.1 ETag versus Last-Modified

| Mechanism | Validator | Main idea |
|---|---|---|
| ETag | Representation validator | "Does this representation match this validator?" |
| Last-Modified | Timestamp | "Has this resource changed since this time?" |

ETags are often stronger validators because timestamps can have precision and clock-related limitations.

For example:

- updates can occur within a timestamp resolution;
- clocks may differ;
- resource generation may not map cleanly to filesystem modification time.

Do not treat ETag and Last-Modified as perfectly interchangeable.

---

# 18. Idempotency and Retry Safety

Idempotency is critical for production ingestion.

A useful definition:

> An operation is idempotent when repeating the same request has the same intended effect on the resource state as making it once.

HTTP defines idempotency for certain methods, but **actual application behavior matters**.

## 18.1 GET

```http
GET /customers/123
```

Repeated GETs normally retrieve the same resource representation without creating another customer.

## 18.2 PUT

```http
PUT /customers/123
```

Replacing the same representation repeatedly is idempotent under HTTP semantics.

## 18.3 DELETE

```http
DELETE /customers/123
```

Repeated deletion has the same intended state effect: the resource is absent.

The second response may differ from the first.

## 18.4 POST

```http
POST /exports
```

POST is not idempotent by default.

A retry can potentially create:

```text
export_123
export_124
```

when the client intended one export.

## 18.5 PATCH

PATCH is not inherently idempotent.

An application may design a particular PATCH operation to behave idempotently, but the HTTP method alone does not guarantee that.

## 18.6 Idempotency keys

Some APIs support:

```http
Idempotency-Key: 7f3d...
```

The client supplies a unique key for an operation.

The server can use the key to recognize repeated submissions.

This is especially useful for operations where:

```text
request sent
   |
   v
network failure
   |
   v
client does not know whether server completed it
```

A retry without idempotency protection can create duplicates.

Detailed retry algorithms belong to Topic 05.

---

# 19. API Styles

Data engineers encounter multiple API styles.

## 19.1 REST

REST-style APIs commonly expose resources through URLs and use HTTP methods.

Example:

```text
GET    /customers
GET    /customers/123
POST   /customers
PATCH  /customers/123
DELETE /customers/123
```

A typical response might be JSON.

However:

> Do not assume every HTTP API is RESTful, or that every API follows textbook REST conventions.

### Extraction consideration

Read the actual API contract:

- endpoints;
- parameters;
- response schemas;
- status codes;
- pagination;
- rate limits;
- authentication.

## 19.2 GraphQL

GraphQL commonly uses one endpoint and puts a query in the request body.

Conceptually:

```text
POST /graphql
```

Body:

```graphql
{
  customers {
    id
    name
    orders {
      id
      total
    }
  }
}
```

Advantages for extraction can include explicit field selection and nested retrieval.

Considerations include:

- query complexity;
- nested response structures;
- server-specific limits;
- pagination.

Detailed pagination belongs to Topic 04.

## 19.3 gRPC

gRPC uses an RPC model and commonly uses Protocol Buffers.

Characteristics include:

- strongly defined service contracts;
- binary serialization;
- efficient service-to-service communication;
- streaming support.

It is common in internal service-to-service systems and less common as a general public data extraction interface.

## 19.4 SOAP/XML

SOAP is a protocol/style used heavily in enterprise and legacy systems.

You may encounter:

- XML;
- envelopes;
- WSDL;
- enterprise service contracts.

A data engineer may need to extract from such a system even when a modern JSON REST API is unavailable.

## 19.5 Comparison

| Style | Typical format | Typical use | Extraction consideration |
|---|---|---|---|
| REST-style HTTP API | JSON, CSV, etc. | Public/internal resources | Understand HTTP semantics and API contract |
| GraphQL | JSON request/response | Flexible application data access | Query fields explicitly; understand server limits |
| gRPC | Protobuf/binary | Service-to-service | Client tooling and protobuf contract required |
| SOAP/XML | XML | Enterprise/legacy integration | Schema-heavy; WSDL and XML handling matter |

---

# 20. OpenAPI

OpenAPI is a machine-readable specification format for describing HTTP APIs.

A data engineer can use it to understand an unfamiliar API before writing extraction code.

It can describe:

- paths;
- HTTP methods;
- parameters;
- request bodies;
- response schemas;
- status codes;
- security metadata;
- examples.

A small example:

```yaml
openapi: 3.0.3
info:
  title: Customer API
  version: 1.0.0

paths:
  /customers:
    get:
      parameters:
        - name: page
          in: query
          schema:
            type: integer
        - name: limit
          in: query
          schema:
            type: integer
      responses:
        "200":
          description: Successful response
          content:
            application/json:
              schema:
                type: object
```

## 20.1 How to read an unfamiliar API

Before writing code, inspect:

```text
1. Base URL
2. Endpoint path
3. HTTP method
4. Required parameters
5. Optional parameters
6. Request body schema
7. Response schema
8. Status codes
9. Authentication requirements
10. Pagination clues
11. Rate-limit documentation
12. Error response format
```

This can prevent building an extractor based on guesses.

---

# 21. Asynchronous Export Pattern

Large SaaS APIs often cannot efficiently return millions of rows in one synchronous response.

Instead, they may expose an asynchronous export workflow.

The common conceptual sequence is:

```text
1. POST /exports
       |
       v
2. 202 Accepted
       |
       v
3. export_id
       |
       v
4. Poll status endpoint
       |
       v
5. Export becomes complete
       |
       v
6. Receive download URL
       |
       v
7. Stream result
       |
       v
8. Land raw data
```

## 21.1 Starting an export

```http
POST /exports
Content-Type: application/json

{
  "resource": "orders",
  "format": "jsonl"
}
```

Response:

```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "export_id": "exp_123"
}
```

`202` means:

> The server accepted the request, but completion is not represented by this response.

## 21.2 Polling

```http
GET /exports/exp_123
```

Possible response:

```json
{
  "status": "running"
}
```

Later:

```json
{
  "status": "completed",
  "download_url": "/downloads/exp_123.jsonl"
}
```

Possible terminal failure:

```json
{
  "status": "failed",
  "error": "Export generation failed"
}
```

## 21.3 Production concerns

A production workflow must define:

- valid states;
- polling interval;
- maximum polling duration;
- timeout behavior;
- terminal success states;
- terminal failure states;
- cleanup;
- download validation;
- streaming;
- idempotency for export creation.

Do not poll every millisecond. Do not poll forever.

Detailed rate-limit algorithms are a later topic, but asynchronous workflows must still be respectful of the source.

---

# 22. HTTP/1.1 vs HTTP/2

## 22.1 HTTP/1.1

HTTP/1.1 supports persistent connections.

Conceptually:

```text
Connection 1
   |
   +--> Request A
   +--> Response A
   +--> Request B
   +--> Response B
```

Multiple connections may be used to achieve concurrency.

## 22.2 HTTP/2

HTTP/2 introduces multiplexed streams over a connection.

Conceptually:

```text
One connection
  |
  +--> Stream A
  +--> Stream B
  +--> Stream C
```

HTTP/2 also uses binary framing and header compression mechanisms.

## 22.3 Why this can matter for extraction

Suppose an extractor needs many independent API requests.

With HTTP/2, a compatible client/server pair can multiplex requests over fewer connections.

Potential benefits include:

- reduced connection-management overhead;
- better utilization of one connection;
- lower latency for concurrent request workloads.

Actual performance depends on:

- server implementation;
- network latency;
- request sizes;
- concurrency;
- client implementation;
- source-side limits.

Do not assume "HTTP/2 is always faster".

Detailed Python concurrency is intentionally outside this chapter.

---

# 23. Proxies

Many production environments do not allow application servers to connect directly to the public internet.

A common architecture is:

```text
Data Pipeline
     |
     v
Corporate Forward Proxy
     |
     v
Internet
     |
     v
External API
```

A proxy can:

- control outbound traffic;
- log traffic metadata;
- enforce security policy;
- provide network routing;
- require authentication.

## 23.1 Debugging symptoms

An API may work:

```text
developer laptop
```

but fail:

```text
production container
```

because the network paths differ.

Possible causes:

- proxy required;
- DNS differences;
- outbound firewall;
- proxy authentication;
- CA configuration;
- blocked destination.

The first debugging question should not automatically be "Is the API broken?"

---

# 24. Corporate TLS Inspection

Some enterprise environments perform TLS inspection.

Conceptually:

```text
Client
   |
   | TLS connection
   v
Corporate proxy
   |
   | separate TLS connection
   v
Internet/API
```

The corporate proxy can terminate and re-establish TLS so it can inspect traffic according to organizational policy.

This usually requires a corporate CA certificate to be trusted by the client.

## 24.1 Why certificates can fail

Your laptop may trust:

```text
Corporate Root CA
```

while your minimal production container does not.

Then:

```text
Python client
    |
    v
certificate verification
    |
    v
unknown/untrusted issuer
```

The result can be a TLS certificate error.

## 24.2 Correct conceptual fix

Configure the environment with the organization's approved CA bundle:

```text
Corporate CA
      |
      v
Trusted CA bundle
      |
      v
HTTP client
```

Follow your organization's security process for distributing and trusting that CA.

## 24.3 Do not use `verify=False` as a production fix

This is unsafe:

```python
import httpx

httpx.get(
    "https://api.example.com",
    verify=False,
)
```

It disables certificate verification.

That removes an important security control.

The correct question is:

> Why is the expected certificate chain not trusted in this environment?

Then fix the trust configuration.

---

# 25. HTTP Debugging Methodology

When an extraction fails, work from the bottom of the stack upward.

## 25.1 Systematic workflow

```text
1. Can DNS resolve?
       |
2. Can TCP/TLS connection be established?
       |
3. Did the server respond?
       |
4. What is the HTTP status?
       |
5. What do response headers say?
       |
6. What is Content-Type?
       |
7. Is the body valid?
       |
8. Is the request malformed?
       |
9. Is authentication involved?
       |
10. Is the client rate limited?
       |
11. Is a proxy involved?
       |
12. Is the response cached?
       |
13. Is there an application-level error inside HTTP 200?
```

## 25.2 Decision tree

```text
Request failed
     |
     +-- No HTTP response?
     |      |
     |      +-- DNS?
     |      +-- network route?
     |      +-- TCP?
     |      +-- TLS/certificate?
     |      +-- timeout?
     |
     +-- HTTP response received?
            |
            +-- 2xx --> inspect headers and body
            |
            +-- 3xx --> inspect Location / redirect policy
            |
            +-- 4xx --> inspect request, credentials, permissions, resource
            |
            +-- 5xx --> inspect server/gateway and retry policy
```

## 25.3 Think in layers

Do not say:

> "The API is broken."

Instead ask:

```text
Network?
TLS?
HTTP?
Application?
Payload?
Pipeline?
```

That makes debugging evidence-driven.

---

# 26. curl Laboratory

`curl` is one of the best tools for learning HTTP because it exposes the protocol without requiring Python abstractions.

All examples below use the local mock API introduced later.

## 26.1 Basic GET

```bash
curl -i http://localhost:8000/customers
```

`-i` includes response headers.

Inspect:

- status;
- Content-Type;
- body.

## 26.2 Verbose mode

```bash
curl -v http://localhost:8000/customers
```

`-v` provides verbose connection/request/response information.

Use it when diagnosing:

- redirects;
- TLS;
- connection behavior;
- headers.

Do not paste secrets from verbose output into tickets or logs.

## 26.3 Query parameters

```bash
curl -G \
  --data-urlencode "status=active" \
  http://localhost:8000/customers
```

`-G` tells curl to append the supplied data to the query string.

`--data-urlencode` safely encodes the value.

## 26.4 Request headers

```bash
curl -H "Accept: application/json" \
  http://localhost:8000/customers
```

This demonstrates content negotiation.

## 26.5 POST JSON

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"resource":"customers"}' \
  http://localhost:8000/exports
```

This sends a JSON request body.

## 26.6 Conditional request

First:

```bash
curl -i http://localhost:8000/cached-resource
```

Copy the ETag.

Then:

```bash
curl -i \
  -H 'If-None-Match: "abc123"' \
  http://localhost:8000/cached-resource
```

A matching validator should produce:

```text
304 Not Modified
```

## 26.7 What to record during the lab

For every request, record:

```text
Method:
URL:
Request headers:
Request body:
Status:
Response headers:
Content-Type:
Response body:
Interpretation:
Pipeline action:
```

This habit is more valuable than memorizing curl flags.

---

# 27. Building the FastAPI Mock API

The mock API provides a safe local environment for learning.

> **Teaching note:** The following is intentionally contained in this Markdown file so the chapter remains self-contained. In a real project, application code would normally live in source files.

## 27.1 Setup

Create an isolated environment in your working project if needed and install:

```bash
python -m pip install fastapi uvicorn
```

Run the code below from the Markdown chapter by copying it into a temporary local file for the exercise. The exercise itself does not require adding that file to your curriculum repository.

## 27.2 Complete mock API

```python
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel


app = FastAPI(title="HTTP Fundamentals Mock API")


# Teaching/demo configuration.
# Environment variables let the learner change behavior without changing code.
LATENCY_SECONDS = float(os.getenv("MOCK_API_LATENCY_SECONDS", "0"))
ERROR_MODE = os.getenv("MOCK_API_ERROR_MODE", "none")


CUSTOMERS = [
    {"id": 1, "name": "Asha", "status": "active"},
    {"id": 2, "name": "Ravi", "status": "inactive"},
    {"id": 3, "name": "Mina", "status": "active"},
    {"id": 4, "name": "Omar", "status": "active"},
]


class ExportRequest(BaseModel):
    resource: str
    format: str = "jsonl"


exports: dict[str, dict[str, Any]] = {}


async def apply_demo_behavior() -> None:
    """Add optional latency or an intentional demo error."""
    if LATENCY_SECONDS > 0:
        await asyncio.sleep(LATENCY_SECONDS)

    if ERROR_MODE == "503":
        raise HTTPException(
            status_code=503,
            detail="Demo service unavailable",
            headers={"Retry-After": "5"},
        )


@app.get("/customers")
async def get_customers(
    status: str | None = Query(default=None),
) -> dict[str, Any]:
    await apply_demo_behavior()

    customers = CUSTOMERS

    if status is not None:
        customers = [
            customer
            for customer in CUSTOMERS
            if customer["status"] == status
        ]

    return {"customers": customers}


@app.get("/customers/{customer_id}")
async def get_customer(customer_id: int) -> dict[str, Any]:
    await apply_demo_behavior()

    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer

    raise HTTPException(status_code=404, detail="Customer not found")


@app.get("/cached-resource")
async def cached_resource(
    if_none_match: str | None = Header(default=None),
) -> Response:
    await apply_demo_behavior()

    body = json.dumps(
        {
            "resource": "cached-resource",
            "version": 1,
            "message": "This representation can be conditionally requested.",
        },
        separators=(",", ":"),
    )

    etag_value = hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
    etag = f'"{etag_value}"'

    if if_none_match == etag:
        return Response(status_code=304, headers={"ETag": etag})

    return Response(
        content=body,
        media_type="application/json",
        headers={
            "ETag": etag,
            "Cache-Control": "max-age=60",
        },
    )


def generate_lines(number_of_records: int):
    for record_id in range(1, number_of_records + 1):
        record = {
            "id": record_id,
            "value": f"record-{record_id}",
        }
        yield (json.dumps(record) + "\n").encode("utf-8")


@app.get("/large-export")
async def large_export(
    records: int = Query(default=1000, ge=1, le=1_000_000),
):
    await apply_demo_behavior()

    return StreamingResponse(
        generate_lines(records),
        media_type="application/x-ndjson",
    )


@app.post("/exports", status_code=202)
async def create_export(request: ExportRequest) -> JSONResponse:
    await apply_demo_behavior()

    export_id = f"exp_{len(exports) + 1}"

    exports[export_id] = {
        "resource": request.resource,
        "format": request.format,
        "status": "running",
        "created_at": time.time(),
    }

    return JSONResponse(
        status_code=202,
        content={"export_id": export_id},
    )


@app.get("/exports/{export_id}")
async def get_export(export_id: str) -> dict[str, Any]:
    await apply_demo_behavior()

    export = exports.get(export_id)

    if export is None:
        raise HTTPException(status_code=404, detail="Export not found")

    # Teaching simplification: complete after two seconds.
    if time.time() - export["created_at"] >= 2:
        export["status"] = "completed"
        export["download_url"] = (
            f"/large-export?records=10000"
        )

    return export
```

## 27.3 Run the server

Save the code temporarily as `mock_api.py` for the lab, then:

```bash
uvicorn mock_api:app --host 127.0.0.1 --port 8000
```

You should see the server listening on:

```text
http://127.0.0.1:8000
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## 27.4 Explore the endpoints

### Customers

```bash
curl -i http://localhost:8000/customers
```

### Filter

```bash
curl -G \
  --data-urlencode "status=active" \
  http://localhost:8000/customers
```

### One customer

```bash
curl -i http://localhost:8000/customers/1
```

### Missing customer

```bash
curl -i http://localhost:8000/customers/999
```

Observe `404`.

### Cached resource

```bash
curl -i http://localhost:8000/cached-resource
```

Copy the ETag and repeat:

```bash
curl -i \
  -H 'If-None-Match: "PUT-THE-ETAG-HERE"' \
  http://localhost:8000/cached-resource
```

### Large export

```bash
curl -i \
  "http://localhost:8000/large-export?records=10000"
```

### Start export

```bash
curl -i -X POST \
  -H "Content-Type: application/json" \
  -d '{"resource":"customers","format":"jsonl"}' \
  http://localhost:8000/exports
```

Then query:

```bash
curl -i http://localhost:8000/exports/exp_1
```

Repeat after a few seconds.

## 27.5 Configurable latency

Start:

```bash
MOCK_API_LATENCY_SECONDS=1 \
uvicorn mock_api:app --host 127.0.0.1 --port 8000
```

This helps demonstrate that network latency is part of extraction performance.

## 27.6 Configurable error behavior

Start:

```bash
MOCK_API_ERROR_MODE=503 \
uvicorn mock_api:app --host 127.0.0.1 --port 8000
```

Then:

```bash
curl -i http://localhost:8000/customers
```

Observe:

```http
503 Service Unavailable
Retry-After: 5
```

This gives you a controlled environment for later retry lessons.

---

# 28. Hands-On Exercise — HTTP Explorer

## Objective

Build the HTTP mental model by observing actual requests and responses.

You must complete the exercise **before reading the solution**.

## Part A — Basic request

Run:

```bash
curl -i http://localhost:8000/customers
```

Answer:

1. What HTTP method was used?
2. What URL was requested?
3. What status code was returned?
4. What is the response Content-Type?
5. What is the response body?

### Expected observation

You should see a `200` response with JSON.

---

## Part B — Capture an ETag

Run:

```bash
curl -i http://localhost:8000/cached-resource
```

Find:

```http
ETag: "..."
```

Write down the exact value.

Then send:

```bash
curl -i \
  -H 'If-None-Match: "YOUR-ETAG"' \
  http://localhost:8000/cached-resource
```

### Expected result

You should receive:

```text
304 Not Modified
```

### Questions

1. Did the server send the original representation again?
2. Why can this save bandwidth?
3. Why can this reduce source load?
4. What state would your extractor need to retain to perform this optimization across runs?

---

## Part C — Large response

Request:

```bash
curl -i \
  "http://localhost:8000/large-export?records=10000"
```

Then increase the size:

```bash
curl -i \
  "http://localhost:8000/large-export?records=100000"
```

Think about the difference between:

```text
Read entire body into memory
```

and:

```text
Stream progressively to raw storage
```

### Questions

1. Why does response size matter even when the API itself is healthy?
2. What happens if the container has a 512 MB memory limit?
3. Why might JSON Lines/NDJSON be useful for streaming?

---

## Part D — Asynchronous export

Start:

```bash
curl -i -X POST \
  -H "Content-Type: application/json" \
  -d '{"resource":"customers","format":"jsonl"}' \
  http://localhost:8000/exports
```

Record the `export_id`.

Then:

```bash
curl -i http://localhost:8000/exports/exp_1
```

Repeat after a few seconds.

### Questions

1. Why did the initial request return `202` rather than `200`?
2. Why is polling required?
3. What is the terminal success state?
4. What would a terminal failure state look like?
5. Why should the client have a maximum polling duration?

---

## Part E — Status-code → pipeline-action table

Create your own one-page table:

| Status | Meaning | Pipeline action |
|---|---|---|
| 200 | ? | ? |
| 202 | ? | ? |
| 304 | ? | ? |
| 400 | ? | ? |
| 401 | ? | ? |
| 403 | ? | ? |
| 404 | ? | ? |
| 409 | ? | ? |
| 422 | ? | ? |
| 429 | ? | ? |
| 500 | ? | ? |
| 503 | ? | ? |
| 504 | ? | ? |

Do this from your own understanding first.

---

## Part F — Compression investigation

Compression behavior depends on the client and server implementation.

Use verbose curl output to inspect request/response headers:

```bash
curl -v \
  -H "Accept-Encoding: gzip" \
  http://localhost:8000/customers
```

The local FastAPI demonstration does not automatically provide production-grade compression middleware, so this part is primarily about learning to inspect negotiation headers.

For a real compressed API, compare:

```text
Content-Length
Content-Encoding
network transfer size
```

Do not confuse:

```text
Content-Encoding: gzip
```

with:

```text
Content-Type: application/json
```

The first describes transfer representation encoding; the second describes the logical media type.

---

## Exercise Debugging Hints

### If curl cannot connect

Check:

```bash
curl -v http://localhost:8000/customers
```

Then verify the server is running.

### If you get `404`

Check the path:

```text
/customers
/customers/1
/cached-resource
/large-export
/exports
```

### If the conditional request does not return `304`

Make sure you copied the ETag exactly, including quotes if the server supplied them.

### If the export does not become complete

Remember that the mock implementation uses a short time delay.

### If you receive an HTML page

Inspect:

```text
Content-Type
```

and verify that you are talking to the expected service.

---

# 29. Exercise Solution

## Part A

A typical response is:

```text
Method: GET
Status: 200
Content-Type: application/json
Body: JSON object containing customers
```

The important reasoning is:

```text
GET
 |
 v
resource requested
 |
 v
200
 |
 v
inspect Content-Type
 |
 v
parse JSON
```

## Part B

The first response provides an ETag.

The second request supplies:

```http
If-None-Match: <same-etag>
```

If unchanged:

```http
304 Not Modified
```

The server can avoid retransmitting the representation.

A production extractor might store the validator in pipeline state associated with the resource.

## Part C

A large response can exceed available process/container memory.

Streaming changes:

```text
entire response
     |
     v
memory
```

to:

```text
chunk
  |
  v
write/process
  |
  v
next chunk
```

This provides bounded-memory behavior when implemented correctly.

## Part D

The initial request starts work.

Therefore:

```text
POST /exports
      |
      v
202 Accepted
      |
      v
export_id
```

The export is not immediately complete.

The client polls:

```text
GET /exports/{export_id}
```

until it reaches a terminal state.

A production implementation should also handle timeout and failure states.

## Part E — Example answer

| Status | Meaning | Pipeline action |
|---|---|---|
| 200 | Success | Validate and process |
| 202 | Accepted | Poll operation |
| 304 | Unchanged | Reuse/skip representation |
| 400 | Invalid request | Inspect/fix request |
| 401 | Authentication issue | Fix authentication |
| 403 | Forbidden | Fix permissions/policy |
| 404 | Resource not found | Verify path/resource |
| 409 | State conflict | Inspect remote state |
| 422 | Validation error | Fix input |
| 429 | Rate limited | Respect server guidance |
| 500 | Server error | Investigate/retry according to policy |
| 503 | Service unavailable | Respect server guidance |
| 504 | Gateway timeout | Investigate/retry according to policy |

The table is not a substitute for API-specific documentation.

---

# 30. Production Failure Scenarios

## Scenario 1 — `200 OK`, but HTML instead of JSON

### Symptoms

```http
200 OK
Content-Type: text/html
```

The extractor expects JSON.

### Possible cause

- proxy login page;
- reverse proxy error page;
- wrong endpoint;
- application returned HTML.

### Investigation

Check:

```text
URL
Content-Type
response body
redirect history
proxy configuration
```

### Correct solution

Do not blindly parse JSON.

Validate the response before parsing.

### Production lesson

```text
HTTP success != application-data success
```

---

## Scenario 2 — `503` with `Retry-After`

### Symptoms

```http
503 Service Unavailable
Retry-After: 30
```

### Possible cause

The service is temporarily unavailable.

### Investigation

Inspect:

- status;
- headers;
- source documentation;
- current pipeline load.

### Correct solution

A retry may be appropriate. Respect server-provided guidance.

Detailed retry algorithms belong to Topic 05.

### Production lesson

The response itself may provide operational instructions.

---

## Scenario 3 — 100 requests are fine, 100,000 are slow

### Symptoms

The extraction scales poorly.

### Possible cause

Repeated connection establishment.

### Investigation

Compare:

```text
new connection per request
```

against:

```text
reused connections
```

Also measure:

- latency;
- server response time;
- client processing;
- network transfer.

### Correct solution

Use a reusable client/session with connection pooling. Topic 02 covers the implementation.

### Production lesson

Protocol-level overhead matters at scale.

---

## Scenario 4 — Large export causes OOM

### Symptoms

The container terminates due to memory exhaustion.

### Possible cause

The entire response was loaded into memory.

### Investigation

Measure:

```text
response size
process RSS
container memory limit
```

### Correct solution

Stream the response and write/process incrementally.

### Production lesson

Data volume is not only a storage concern. It is an HTTP client memory concern.

---

## Scenario 5 — API returns `304`

### Symptoms

The extractor expects a body but receives:

```http
304 Not Modified
```

### Possible cause

A conditional request was used and the resource has not changed.

### Investigation

Inspect:

```http
If-None-Match
ETag
If-Modified-Since
Last-Modified
```

### Correct solution

Reuse the previously stored representation or skip processing, depending on pipeline design.

### Production lesson

A `304` is an optimization signal, not a broken `200`.

---

## Scenario 6 — API returns `202`

### Symptoms

The extractor receives:

```http
202 Accepted
```

but no dataset.

### Possible cause

The API is asynchronous.

### Investigation

Inspect the response body for:

```text
export_id
job_id
status URL
```

### Correct solution

Poll the operation according to documented rules and retrieve the completed artifact.

### Production lesson

"Request accepted" and "data ready" are different states.

---

## Scenario 7 — Works locally, fails in corporate network

### Symptoms

TLS certificate verification fails only in the corporate environment.

### Possible cause

Corporate TLS inspection with a custom CA.

### Investigation

Compare:

```text
local trust store
production/container trust store
corporate CA requirements
proxy configuration
```

### Correct solution

Install/configure the approved CA bundle according to organizational policy.

### Production lesson

Never make certificate verification disappear simply to make the pipeline run.

---

## Scenario 8 — Retried POST creates duplicate exports

### Symptoms

A pipeline intended to create one export creates several.

### Possible cause

The initial POST succeeded but the response was lost. The client retried.

```text
POST
 |
 v
server creates export
 |
 X response lost
 |
 v
client thinks it failed
 |
 v
POST again
 |
 v
second export
```

### Investigation

Inspect:

- export history;
- request IDs;
- operation identifiers;
- API idempotency support.

### Correct solution

Where supported, use an idempotency key or another application-specific deduplication mechanism.

### Production lesson

Retry safety depends on operation semantics, not merely on whether a network call failed.

---

# 31. Real-World Data Engineering Architecture

A production HTTP extraction system can look conceptually like:

```text
                 SaaS API
                    |
                  HTTPS
                    |
                    v
          +-------------------+
          | HTTP Extractor    |
          +-------------------+
             |      |      |
             |      |      +--> Request metadata
             |      |
             |      +---------> Failure/status handling
             |
             +---------------> Response validation
                    |
                    +---------> Streaming
                    |
                    v
             Raw / Bronze Landing
                    |
                    v
             Pipeline Metadata
                    |
                    v
             Downstream Transform
```

## 31.1 HTTP concepts in the architecture

### DNS/TLS

Allows the extractor to reach and securely communicate with the source.

### Methods

Determine what operation is requested.

### Query parameters

Control extraction scope and filtering.

### Headers

Communicate content negotiation, caching, compression, and other metadata.

### Status codes

Tell the pipeline what happened at the HTTP layer.

### Content-Type

Helps select the correct parser.

### Connection reuse

Controls network efficiency.

### Compression

Controls the network/CPU trade-off.

### Streaming

Controls memory behavior.

### Conditional requests

Reduce unnecessary downloads.

### Idempotency

Controls retry safety.

### Asynchronous exports

Allow large datasets to be generated outside a single synchronous HTTP response.

---

# 32. Common Mistakes

## Mistake 1 — Treating HTTP as "just JSON"

HTTP is independent of JSON.

The response could be:

```text
JSON
CSV
NDJSON
XML
binary
HTML
empty
```

## Mistake 2 — Treating `200` as proof of valid data

Always inspect:

```text
status
Content-Type
body structure
```

## Mistake 3 — Assuming every POST is unsafe to retry in exactly the same way

POST is not idempotent by default, but application-level behavior and idempotency keys can change practical retry semantics.

## Mistake 4 — Retrying every 4xx

Most request errors require changing the request, not repeating it.

## Mistake 5 — Loading giant responses into memory

Large data should often be streamed.

## Mistake 6 — Opening a new connection for every request

Connection reuse can dramatically matter at scale.

## Mistake 7 — Disabling TLS verification

Never use:

```python
verify=False
```

as a production certificate fix.

## Mistake 8 — Assuming API documentation is optional

OpenAPI and API documentation are part of the extraction contract.

## Mistake 9 — Confusing `Accept` and `Content-Type`

Remember:

```text
Accept       = what representation I want/can accept
Content-Type = what representation this body is
```

## Mistake 10 — Assuming asynchronous means "keep polling forever"

A production poller needs:

- interval;
- timeout;
- terminal states;
- failure handling.

---

# 33. Production Checklist

## HTTP correctness

- [ ] Understand request/response structure.
- [ ] Use the correct HTTP method.
- [ ] Use the correct URL and query parameters.
- [ ] Send appropriate headers.
- [ ] Understand `Content-Type` and `Accept`.
- [ ] Validate response content.

## Reliability

- [ ] Understand status-code semantics.
- [ ] Do not blindly retry.
- [ ] Understand idempotency.
- [ ] Handle timeouts.
- [ ] Handle redirects deliberately.
- [ ] Distinguish transport failure from application failure.
- [ ] Handle asynchronous operations with explicit state.

## Performance

- [ ] Reuse connections.
- [ ] Use compression where appropriate.
- [ ] Stream large responses.
- [ ] Avoid unnecessary downloads.
- [ ] Use conditional requests where appropriate.
- [ ] Measure before optimizing.

## Security

- [ ] Use HTTPS for sensitive communication.
- [ ] Validate certificates.
- [ ] Configure approved CA bundles.
- [ ] Never put credentials in logs.
- [ ] Never use `verify=False` as a production workaround.
- [ ] Understand proxy/TLS-inspection requirements.

## Data engineering

- [ ] Validate response Content-Type.
- [ ] Validate response schema/content.
- [ ] Land raw data appropriately.
- [ ] Capture extraction metadata.
- [ ] Record relevant request/response metadata without secrets.
- [ ] Make failure behavior explicit.
- [ ] Preserve enough state for conditional retrieval where appropriate.

---

# 34. Knowledge Check

## Basic

### 1. What is HTTP?

**Answer:** HTTP is an application-layer protocol that defines standardized semantics for communication between clients and servers, including requests, responses, methods, headers, status codes, and message bodies.

### 2. What is a request?

**Answer:** A request is a client-to-server HTTP message containing a method, request target, headers, and optionally a body.

### 3. What is a response?

**Answer:** A response is a server-to-client HTTP message containing a status, headers, and optionally a body.

### 4. What is a URL?

**Answer:** A URL identifies the destination/resource being accessed and can contain a scheme, host, port, path, query parameters, and fragment.

### 5. What is a header?

**Answer:** A header is HTTP metadata associated with a request or response.

### 6. What is a status code?

**Answer:** A numeric code indicating the general result of an HTTP request, such as `200`, `404`, or `503`.

### 7. What is Content-Type?

**Answer:** `Content-Type` describes the media type of the message body, such as JSON or CSV.

### 8. What is HTTPS?

**Answer:** HTTPS is HTTP transported over TLS, providing encrypted communication and certificate-based authentication of the server endpoint.

---

## Intermediate

### 9. Why is connection reuse important?

**Answer:** Reusing connections avoids repeatedly paying connection-establishment and often TLS-handshake costs. This can substantially reduce latency and overhead for extraction jobs making many requests.

### 10. What is an ETag?

**Answer:** An ETag is a representation validator supplied by a server. A client can use it later in `If-None-Match` to ask whether the representation has changed.

### 11. What is `304`?

**Answer:** `304 Not Modified` is a response to a conditional request indicating that the selected representation has not changed according to the validator.

### 12. What is a conditional GET?

**Answer:** It is a GET request containing a validator such as `If-None-Match` or `If-Modified-Since`, allowing the server to avoid retransmitting an unchanged representation.

### 13. Why does compression matter?

**Answer:** Compression reduces network bytes and potentially transfer time, at the cost of CPU work for compression/decompression.

### 14. What is streaming?

**Answer:** Streaming means progressively receiving and processing/writing a response rather than requiring the entire response body to reside in memory at once.

### 15. Why is `202` different from `200`?

**Answer:** `200` indicates the request succeeded and the response represents the requested outcome. `202` indicates that the request was accepted for processing but the operation may not be complete yet.

### 16. Why does idempotency matter for retries?

**Answer:** If an operation is not safely repeatable, a retry after an ambiguous network failure can create duplicate resources or duplicate work.

---

## Advanced

### 17. How would you diagnose an HTTP extraction failure?

**Answer:** Start at the lowest relevant layer: DNS, network/TCP, TLS, HTTP response, status code, headers, Content-Type, body validity, application-level errors, authentication/authorization, proxy configuration, and rate limiting. Avoid assuming the API is at fault before collecting evidence.

### 18. Why might an API return `200` with unusable data?

**Answer:** HTTP status only describes the HTTP-level result. The body could be HTML, malformed JSON, an application-level error object, or otherwise violate the expected extraction contract.

### 19. How would you design an asynchronous export workflow?

**Answer:** Submit the export request, persist the returned operation identifier, poll a documented status endpoint at a controlled interval, enforce a maximum wait time, handle terminal failure states, retrieve the download URL when ready, stream the result, validate it, and record metadata/state for recovery.

### 20. Why might HTTP/2 improve extraction performance?

**Answer:** HTTP/2 can multiplex multiple streams over a connection and uses binary framing and header compression. For workloads involving many concurrent requests, this can reduce connection-management overhead and improve utilization. Actual performance depends on the client, server, network, and workload.

### 21. How can corporate TLS inspection break extraction?

**Answer:** A corporate proxy may terminate and re-establish TLS using an enterprise certificate chain. If the container does not trust the enterprise CA, certificate validation fails.

### 22. Why should `verify=False` not be used as a production fix?

**Answer:** It disables certificate verification and removes an important security control. The correct solution is to configure the appropriate trusted CA chain.

### 23. How does conditional retrieval reduce ingestion cost?

**Answer:** A validator such as an ETag can let the client receive `304` rather than retransmitting an unchanged large representation, reducing network transfer and source load.

### 24. How do HTTP semantics influence retry design?

**Answer:** Retry safety depends on whether repeating an operation can change remote state or create duplicate work. HTTP defines idempotency for certain methods, but application-specific behavior and mechanisms such as idempotency keys also matter.

---

# 35. Interview Preparation

## 1. Walk me through an HTTP request from a data engineer's perspective.

A strong answer:

```text
1. The extractor constructs the URL and request.
2. DNS resolves the hostname.
3. A network connection is established or reused.
4. TLS is negotiated for HTTPS when needed.
5. The client sends the HTTP request.
6. The server/gateway processes it.
7. The client receives status, headers, and possibly a body.
8. The extractor validates status and content type.
9. The payload is parsed or streamed.
10. Raw data and extraction metadata are persisted.
```

A senior answer also mentions that each stage can fail independently.

## 2. Explain 400, 401, 403, 404, 409, 422, and 429.

- `400`: request is malformed or invalid.
- `401`: authentication credentials are missing/invalid according to the API.
- `403`: request is understood but forbidden.
- `404`: resource is not found.
- `409`: request conflicts with resource state.
- `422`: request content fails application validation.
- `429`: client is being rate limited.

The correct pipeline action depends on the API and operation. Most should not be blindly retried unchanged.

## 3. Which status codes would you retry?

There is no universal "retry all 5xx" rule.

Potential retry candidates can include transient `408`, `429`, `500`, `502`, `503`, and `504`, but the operation, server guidance, idempotency, and failure context must be considered.

`429` and `503` may provide `Retry-After`.

Detailed retry strategy belongs to Topic 05.

## 4. What is the difference between ETag and Last-Modified?

ETag is a representation validator. Last-Modified is a timestamp-based validator.

ETags are often stronger because timestamps have precision and clock-related limitations.

## 5. Why is connection reuse important?

It avoids repeated TCP/TLS setup and reduces latency and resource consumption for workloads with many requests.

## 6. What is the difference between Content-Type and Accept?

`Content-Type` describes the body being sent or received.

`Accept` expresses the response media types the client can accept.

## 7. Explain HTTP streaming.

Streaming allows a client to process a response progressively rather than requiring the complete response to be loaded into memory.

This is especially important for large exports.

## 8. When would an API return 202?

When it has accepted a request for asynchronous processing but the requested operation is not complete.

A large export is a common example.

## 9. What is idempotency?

Idempotency means repeating the same request has the same intended effect on resource state as performing it once.

HTTP semantics define certain methods as idempotent, but application-specific behavior must also be considered.

## 10. Why is retrying POST potentially dangerous?

POST is not idempotent by default. A server may create a new resource each time.

If a client loses the response after the server succeeds, a blind retry can create duplicate resources.

## 11. Explain HTTP/1.1 vs HTTP/2.

HTTP/1.1 supports persistent connections but commonly uses multiple connections for concurrency. HTTP/2 supports multiplexed streams over a connection, binary framing, and header compression.

## 12. What happens during TLS verification?

The client verifies that the certificate presented by the server is trusted through an appropriate CA chain and that the certificate identity matches the requested hostname, along with other validity checks performed by the TLS implementation.

## 13. How would you diagnose a certificate failure in a corporate network?

Determine whether a corporate proxy performs TLS inspection, identify the enterprise CA, compare trust configuration between working and failing environments, inspect proxy settings, and configure the approved CA bundle.

## 14. Why should certificate verification not simply be disabled?

Because doing so removes server identity verification and makes the connection vulnerable to interception or impersonation.

## 15. How would you design an HTTP-based ingestion system for a large SaaS export?

A strong architecture answer would include:

```text
SaaS API
   |
   v
Authenticated HTTP client
   |
   v
Export submission
   |
   v
Persist operation ID
   |
   v
Controlled polling
   |
   v
Completed download
   |
   v
Streaming transfer
   |
   v
Raw/Bronze landing
   |
   v
Validation + metadata
   |
   v
Downstream processing
```

Then discuss:

- status handling;
- timeout;
- idempotency;
- connection reuse;
- compression;
- content validation;
- proxy/TLS requirements;
- observability;
- recovery after worker failure.

---

# 36. Final Checkpoint

Do not move to Topic 02 until you can answer **yes** to these statements:

```text
[ ] I can explain HTTP without memorizing terminology.
[ ] I understand the request/response lifecycle.
[ ] I understand HTTP methods and their semantics.
[ ] I can inspect URLs and query parameters.
[ ] I understand important HTTP headers.
[ ] I can interpret HTTP status codes.
[ ] I understand Content-Type and Accept.
[ ] I understand DNS/TLS/HTTPS at a practical level.
[ ] I understand connection reuse.
[ ] I understand compression.
[ ] I understand streaming.
[ ] I understand HTTP caching.
[ ] I can explain ETag/If-None-Match.
[ ] I can explain Last-Modified/If-Modified-Since.
[ ] I understand idempotency and retry safety.
[ ] I can distinguish REST, GraphQL, gRPC, and SOAP.
[ ] I can read a basic OpenAPI specification.
[ ] I can explain asynchronous exports.
[ ] I understand HTTP/1.1 vs HTTP/2.
[ ] I understand proxies.
[ ] I understand corporate TLS inspection.
[ ] I can debug an HTTP extraction failure systematically.
[ ] I completed the curl laboratory.
[ ] I built the FastAPI mock API.
[ ] I completed the HTTP Explorer exercise.
```

The real checkpoint is not whether you can repeat definitions. You should be able to explain **why** each concept matters to a data pipeline.

For example, you should be able to reason:

```text
Large response
    |
    +--> memory risk
    |
    +--> stream it
    |
    v
Raw landing
```

or:

```text
Conditional request
    |
    +--> unchanged
    |
    +--> 304
    |
    v
avoid unnecessary download
```

or:

```text
POST export
    |
    +--> network ambiguity
    |
    v
retry risk
    |
    v
idempotency / deduplication
```

Once these relationships are clear, the next topic can introduce the Python HTTP clients and production client configuration without treating them as magic.

> **Do not move to Topic 02 until you can explain these concepts and complete the hands-on work without blindly copying the solution.**
