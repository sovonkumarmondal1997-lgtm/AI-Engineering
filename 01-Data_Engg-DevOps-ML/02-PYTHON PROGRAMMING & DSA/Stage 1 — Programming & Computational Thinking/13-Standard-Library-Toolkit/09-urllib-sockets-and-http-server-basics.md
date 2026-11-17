# Lesson 09 — `urllib`, Sockets, and HTTP Server Basics

**Target runtime:** Python 3.12+ (examples use APIs available in supported modern Python releases).  
**Module:** Stage 1 — Programming & Computational Thinking → Module 13 — Standard Library Toolkit → Phase D — Config, Network and Runtime Utilities.

## Learning objectives

By the end of this lesson, you can:

- Explain the HTTP request/response model, URL components, TCP, ports, DNS, and TLS at a practical level.
- Construct URLs and query strings with `urllib.parse`, and make bounded HTTP requests with `urllib.request`.
- Distinguish `HTTPError` from `URLError`, decode response bytes intentionally, and avoid unbounded waits.
- Build a small TCP client/server protocol with explicit message framing and correct partial-read handling.
- Use `socket.getaddrinfo()` and `ipaddress` to reason about addresses without confusing parsing with reachability or authorization.
- Run a loopback-only `http.server` fake API with predictable startup, shutdown, and pytest coverage.
- Troubleshoot DNS, connect, TLS, HTTP, and application-level failures with useful but safe diagnostics.
- Recognize the limits of standard-library networking tools and when a higher-level client or production server is warranted.

## Prerequisites and roadmap boundaries

The Module 13 roadmap places this lesson after file/process operations, SQLite, security primitives, randomness/statistics, and TOML/INI configuration. Relevant earlier skills include bytes versus text, exception handling, `pathlib`, environment variables, CLI parsing, test fixtures, and safe subprocess use. Review those if byte/text conversions, context managers, or pytest fixtures are unfamiliar.

The roadmap explains that even if `httpx` (covered later) is used day to day, understanding the lower layer helps debug timeouts, DNS failures, proxy issues, and TLS errors. This lesson focuses on **Python standard-library foundations**: `urllib.request`, `urllib.parse`, `socket`, `ipaddress`, `ssl`, `http.client`, and `http.server`. It is not a comprehensive HTTP-client, async networking, SSRF-defense, or production web-server course. Retry/backoff policies and higher-level client ergonomics belong to the next level; SSRF has a separate security lesson elsewhere in the roadmap.

## 1. HTTP and network foundations

### 1.1 The request/response model

HTTP is an application protocol. A client sends a request consisting conceptually of a method, target URL/path, headers, and sometimes a body. A server responds with a status code, headers, and sometimes a body.

| Part | Purpose | Example |
|---|---|---|
| Method | Intended operation | `GET`, `POST`, `PUT`, `DELETE` |
| URL | Identifies a resource and endpoint | `https://api.example.test/v1/items?q=tea` |
| Headers | Metadata about request/response | `Accept: application/json` |
| Body | Data sent or returned | JSON bytes in a `POST` request |
| Status | Outcome category | `200`, `201`, `404`, `500` |

Common status families: `2xx` success, `3xx` redirection, `4xx` client/request problem, and `5xx` server-side failure. A status code alone does not explain the business meaning; inspect documented response headers and body while keeping response sizes bounded.

`GET` is conventionally safe to retry because it should not change server state; `POST` may create or trigger work. Do not automatically retry non-idempotent operations without an application-level idempotency design. This lesson demonstrates requests, not a general retry framework.

### 1.2 URL anatomy and network layers

For `https://api.example.test:8443/v1/items?q=tea#details`:

- Scheme: `https`
- Host: `api.example.test`
- Port: `8443`
- Path: `/v1/items`
- Query: `q=tea`
- Fragment: `details` (client-side identifier; not sent as part of an HTTP request target)

DNS maps hostnames to address records. An IP address identifies a network interface/address; a port identifies a transport endpoint on that host. TCP provides a reliable ordered **byte stream**, not application messages. TLS adds confidentiality, integrity, and peer authentication when configured correctly and certificate validation succeeds.

`urllib.parse.urlsplit()` parses a URL; it does **not** prove the URL is safe, reachable, or authorized. `socket.getaddrinfo()` resolves names; it does not establish that a connection will succeed or that an address should be trusted.

### 1.3 A layered troubleshooting model

Diagnose the stage that failed rather than treating every failure as “the network”:

1. **Configuration:** wrong URL, proxy variables, timeout value, or CA bundle.
2. **Name resolution:** hostname cannot resolve (`socket.gaierror`).
3. **Connection:** refused, route failure, or timeout.
4. **TLS:** certificate, hostname, protocol, or trust-chain failure.
5. **HTTP:** redirect, `4xx`, or `5xx` status.
6. **Application:** invalid JSON, schema mismatch, or unexpected payload.

A timeout limits waiting at a particular operation; it does not automatically create one total deadline for DNS + connect + TLS + response body. Use a higher-level client with explicit total-timeout semantics when the application needs a strict end-to-end deadline.

## 2. URL construction with `urllib.parse`

### 2.1 Parse, encode, join

```python
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

parts = urlsplit("https://example.test/search?q=green%20tea&page=2")
print(parts.scheme, parts.netloc, parts.path)
print(parse_qs(parts.query))
print(urlencode({"q": "green tea", "page": 2}))
print(quote("folder name/a.csv", safe="/"))
print(urljoin("https://example.test/v1/", "items/7"))
```

Expected output:

```text
https example.test /search
{'q': ['green tea'], 'page': ['2']}
q=green+tea&page=2
folder%20name/a.csv
https://example.test/v1/items/7
```

Notes:

- `urlencode()` is generally appropriate for query parameters and uses form-style encoding (spaces become `+`).
- `quote()` encodes a path or component; choose `safe` based on whether separators are structural. `quote_plus()` uses form-style space encoding.
- `parse_qs()` maps each key to a list because query keys can repeat.
- `urljoin()` resolves relative references; a fully qualified second argument can replace the original host. Do not use it with untrusted references without validating the result.
- Parsing and quoting are syntax operations, not a security policy.

### 2.2 Construct URLs instead of concatenating strings

```python
from urllib.parse import urlencode, urlsplit, urlunsplit

base = urlsplit("https://api.example.test/v1/items")
query = urlencode({"q": "tea & honey", "limit": 20})
url = urlunsplit((base.scheme, base.netloc, base.path, query, ""))
print(url)
```

Expected output:

```text
https://api.example.test/v1/items?q=tea+%26+honey&limit=20
```

In application code, validate the scheme and host against the application's policy before making a request. Avoid embedding user input directly into URL syntax. For sensitive values, avoid placing them in URLs because URLs commonly appear in logs, browser history, proxies, and monitoring systems.

## 3. HTTP requests with `urllib.request`

### 3.1 A bounded GET request

This example uses a reserved `.test` domain to show construction only. It will not succeed unless you replace the endpoint with a service you are authorized to call. Core tests later use loopback and do not require internet access.

```python
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

params = urlencode({"q": "python networking", "limit": 5})
url = f"https://api.example.test/search?{params}"
request = Request(url, headers={"Accept": "application/json", "User-Agent": "lesson-demo/1.0"})

try:
    with urlopen(request, timeout=5.0) as response:
        status = response.status
        content_type = response.headers.get("Content-Type", "")
        body = response.read(1_000_001)  # example cap: detect a body larger than 1 MB
        if len(body) > 1_000_000:
            raise ValueError("response body exceeds 1 MB limit")
        charset = response.headers.get_content_charset() or "utf-8"
        text = body.decode(charset, errors="strict")
        print(status, content_type, text[:200])
except HTTPError as exc:
    # HTTPError is also a file-like response; avoid dumping arbitrary body data to logs.
    print("HTTP status:", exc.code)
    exc.close()
except URLError as exc:
    # reason can contain useful OS/TLS detail; avoid logging secrets or full credentialed URLs.
    print("URL/network failure:", type(exc.reason).__name__)
except TimeoutError:
    print("Request timed out")
```

The snippet is a teaching example: the response is deliberately capped, but `urlopen()` may have received bytes before `read()` returns. For robust large-body handling, read in bounded chunks and enforce a total byte limit. A socket/URL timeout is not necessarily a total request deadline. Do not catch every exception and pretend the request succeeded.

`urlopen()` uses the standard library's configured TLS context for HTTPS by default, which verifies certificates and hostnames. Do not pass an unverified context to “fix” TLS errors. If a corporate CA is required, configure a trusted CA bundle/context deliberately.

### 3.2 POST with a URL-encoded body

`urllib.request.Request(data=...)` sends a request body; for a conventional form POST, provide bytes and the appropriate content type.

```python
from urllib.parse import urlencode
from urllib.request import Request, urlopen

form_bytes = urlencode({"name": "Ada Lovelace", "role": "data engineer"}).encode("ascii")
request = Request(
    "https://api.example.test/submit",
    data=form_bytes,
    headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
             "Accept": "application/json"},
    method="POST",
)
# Use urlopen(request, timeout=5) inside a context manager when calling a real approved endpoint.
print(request.get_method(), request.get_header("Content-type"), len(form_bytes) > 0)
```

Expected output:

```text
POST application/x-www-form-urlencoded; charset=UTF-8 True
```

For JSON POST bodies, serialize with `json.dumps(payload).encode("utf-8")` and set `Content-Type: application/json`. Do not assume JSON or form encoding merely because a request has a body.

### 3.3 Response lifetime, decoding, and size limits

- Use `with urlopen(...) as response:` so the response is closed even if parsing fails.
- HTTP bodies are bytes. Decode using a known protocol/declared charset; do not blindly assume every response is UTF-8.
- `response.headers.get_content_charset()` can be `None`; choose a documented fallback only when appropriate.
- A JSON response should be parsed with `json.loads(text)` or `json.load(response)` only if you have a deliberate size and encoding strategy.
- For untrusted/large responses, enforce a byte limit. Calling `read()` without a limit can consume unbounded memory.
- Avoid logging response bodies by default: they can contain personal information, tokens, or server diagnostics.

### 3.4 `HTTPError` versus `URLError`

`HTTPError` represents an HTTP response status that `urllib` treats as an error (for example, `404`); it includes `.code`, headers, and a readable response body. `URLError` represents a URL-opening/network-level problem and exposes `.reason`. `HTTPError` is a subclass of `URLError`, so catch it **first** if you need to distinguish status failures.

```python
from urllib.error import HTTPError, URLError

try:
    ...  # urlopen(...)
except HTTPError as exc:
    print("server replied with status", exc.code)
    exc.close()
except URLError as exc:
    print("could not complete URL request:", type(exc.reason).__name__)
```

Use a narrow exception policy: catch expected network and HTTP failures at the boundary where you can add context or decide whether to continue. Unexpected programming errors should generally remain visible.

### 3.5 Redirects, authentication, proxies, and TLS

- `urllib` follows common redirects through its default opener behavior. If redirects change the security meaning of a request, use a deliberate redirect policy and validate the final destination. Never forward credentials to an unexpected host.
- Basic authentication is Base64 encoding, **not encryption**. Use it only over correctly verified HTTPS and follow the service's credential policy. Do not hardcode credentials in examples or logs. If the service explicitly requires Basic authentication, build the header from secret values supplied at runtime and never log it:

```python
import base64
import os
from urllib.request import Request

username = os.environ["API_USERNAME"]
password = os.environ["API_PASSWORD"]
if ":" in username:
    raise ValueError("Basic-auth usernames cannot contain a colon")
# This example uses UTF-8; follow the server's documented Basic-auth charset policy.
credential = f"{username}:{password}".encode("utf-8")
authorization = "Basic " + base64.b64encode(credential).decode("ascii")
request = Request(
    "https://api.example.test/private",
    headers={"Authorization": authorization},
)
# Send with urlopen(request, timeout=3.0); never print `authorization`.
```

- `urllib.request` can honor proxy configuration from environment/system settings. Variables commonly include `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` (exact behavior can vary by platform and opener configuration). Debug unexpected routing by inspecting configuration without printing embedded credentials.
- HTTPS verification uses certificates and hostnames. Certificate failures are meaningful security signals; do not disable verification in production or tests just to make a connection pass. If a corporate CA is required, configure a trusted CA bundle/context deliberately:

```python
import ssl
from urllib.request import urlopen

context = ssl.create_default_context(cafile="/etc/ssl/certs/approved-corporate-ca.pem")
with urlopen("https://service.example.test/health", timeout=3.0, context=context) as response:
    print(response.status)
```

The CA path is deployment-specific; this example is not executed and the `.test` host is reserved. Keep normal hostname and certificate verification enabled.
- Server Name Indication (SNI) allows TLS servers to select certificates by hostname. The default HTTPS context handles standard client configuration.

### 3.6 `http.client` for lower-level HTTP control

`http.client` exposes the HTTP connection/request/response steps more directly than `urllib.request`. Use it when you need lower-level control over connection objects or response handling. It still requires explicit timeouts, correct cleanup, and careful body reading. For general application clients with pooling, richer timeout controls, connection reuse, and ergonomic APIs, consider the later-stage `httpx` client rather than building a large framework around the standard library.

## 4. TCP sockets: bytes, not messages

### 4.1 Basic lifecycle

A TCP server commonly:

1. Creates a stream socket (`socket.socket(AF_INET, SOCK_STREAM)`).
2. Binds to a local address and port.
3. Listens for incoming connections.
4. Accepts a connection, creating a new connected socket.
5. Receives/sends bytes.
6. Closes the connected socket and listening socket.

A client creates a socket, connects, exchanges bytes, and closes it. Use context managers or `try/finally` to ensure cleanup. Bind test servers to `127.0.0.1` unless remote access is explicitly needed.

### 4.2 TCP is a byte stream

TCP preserves byte order but does not preserve application write boundaries. One `sendall()` can be observed by the peer through multiple `recv()` calls; multiple sends can arrive together. `recv(n)` returns **up to** `n` bytes, not necessarily exactly `n` bytes. A return value of `b""` indicates orderly peer shutdown/EOF.

Protocols must define message framing. Common strategies:

- **Delimiter-based:** read until a delimiter such as newline, while enforcing a maximum length and defining escaping rules.
- **Fixed-size:** each message has a known fixed byte length.
- **Length-prefixed:** a header declares the number of body bytes; validate the length before allocating or reading.

For general-purpose protocols, length-prefixing is explicit and handles arbitrary body bytes well, but both sides must agree on byte order, header size, maximum message size, and error behavior.

### 4.3 A framed protocol with exact reads

This protocol sends a 4-byte unsigned big-endian length followed by UTF-8 payload bytes. The receiver caps the payload at 1 MiB. This is a teaching protocol, not an authenticated production protocol.

```python
import socket
import struct

MAX_MESSAGE = 1_048_576
HEADER = struct.Struct("!I")  # network byte order, unsigned 32-bit length


def recv_exact(sock: socket.socket, size: int) -> bytes:
    """Read exactly size bytes or raise EOFError if the peer closes early."""
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise EOFError(f"peer closed after {len(chunks)} of {size} bytes")
        chunks.extend(chunk)
    return bytes(chunks)


def send_frame(sock: socket.socket, payload: bytes) -> None:
    if len(payload) > MAX_MESSAGE:
        raise ValueError("message too large")
    sock.sendall(HEADER.pack(len(payload)) + payload)


def recv_frame(sock: socket.socket) -> bytes:
    (length,) = HEADER.unpack(recv_exact(sock, HEADER.size))
    if length > MAX_MESSAGE:
        raise ValueError("peer announced message larger than allowed limit")
    return recv_exact(sock, length)
```

The functions use `sendall()` because `send()` may write only part of the supplied bytes. `recv_exact()` loops because `recv()` may return fewer bytes than requested. The length cap prevents a peer from declaring an arbitrarily large allocation/read. In production, also consider an overall deadline, authentication, encryption, and rate/connection limits.

### 4.4 Small local TCP client/server

This example demonstrates framing over a loopback connection. It uses port `0`, letting the OS select an available port, and a thread to keep the server responsive while the client connects.

```python
import socket
import threading


def serve_one(listener: socket.socket) -> None:
    conn, _address = listener.accept()
    with conn:
        conn.settimeout(2.0)
        request = recv_frame(conn)
        send_frame(conn, b"ACK:" + request)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    listener.settimeout(2.0)
    host, port = listener.getsockname()
    thread = threading.Thread(target=serve_one, args=(listener,), daemon=True)
    thread.start()
    with socket.create_connection((host, port), timeout=2.0) as client:
        client.settimeout(2.0)
        send_frame(client, b"hello")
        print(recv_frame(client))
    thread.join(timeout=2.0)
    if thread.is_alive():
        raise RuntimeError("server thread did not stop")
```

Expected output:

```text
b'ACK:hello'
```

The listener remains open until after the client/server thread finishes. A daemon thread is not a substitute for lifecycle management; the explicit `join()` and timeout make a stuck server visible. A robust reusable server would need to handle repeated clients and expected exceptions deliberately.

### 4.5 Timeouts and cleanup

- `socket.create_connection((host, port), timeout=...)` applies a timeout to connection attempts; DNS resolution may not be bounded in the same way on every platform.
- `sock.settimeout(seconds)` controls blocking operations on that socket. `None` means blocking mode; `0.0` means non-blocking mode.
- `socket.setdefaulttimeout()` changes a process-wide default for newly created sockets. Avoid it in libraries because it affects unrelated code and creates hidden global behavior.
- Always close accepted sockets and listeners. A `with socket.socket(...)` block closes the socket on exit.
- On Python 3.10 and later, `socket.timeout` is an alias of `TimeoutError`; for this lesson's Python 3.12+ target, catch `TimeoutError` at the appropriate boundary. Also distinguish `ConnectionResetError`, `ConnectionRefusedError`, and other `OSError` subclasses where recovery differs.

## 5. Addressing and DNS

### 5.1 `getaddrinfo()` and IPv4/IPv6

```python
import socket

for family, socktype, proto, canonname, sockaddr in socket.getaddrinfo(
    "localhost", 80, type=socket.SOCK_STREAM
):
    print(family, socktype, sockaddr)
```

Exact rows vary by operating system and hosts configuration, so do not assert a single output in cross-platform tests. `getaddrinfo()` can return IPv4 and IPv6 addresses. Prefer it over manually assuming IPv4 when writing portable connection code.

The `ipaddress` module can parse and classify address literals:

```python
import ipaddress

address = ipaddress.ip_address("127.0.0.1")
print(address.is_loopback)
print(ipaddress.ip_network("192.0.2.0/24").num_addresses)
```

Expected output:

```text
True
256
```

Address classification alone is not a full authorization or SSRF defense. DNS can change, hostnames can resolve to multiple addresses, and redirects can change destinations. If an application fetches user-controlled URLs, use the dedicated SSRF/security guidance from the roadmap, validate schemes and destinations at each redirect/connection, and account for DNS rebinding and private/link-local ranges.

## 6. A local fake HTTP API with `http.server`

### 6.1 Custom request handler

`http.server` is useful for local demonstrations and deterministic integration tests. It is **not intended as a production public-facing server**: it lacks the hardening, deployment controls, robust concurrency model, and operational safeguards expected of a production service.

The following handler exposes a tiny `/health` endpoint and a controlled `/echo` POST endpoint. It binds only to loopback, limits the request body, validates the path, and returns explicit content lengths.

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

MAX_BODY = 4096


CLIENT_IO_TIMEOUT = 2.0  # short, explicit timeout for this local teaching server


class FakeAPIHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self) -> None:
        super().setup()
        # Prevent a client from holding a handler forever while sending a body.
        self.connection.settimeout(CLIENT_IO_TIMEOUT)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            # A test client may time out and disconnect before the response arrives.
            pass
        self.close_connection = True

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(404, {"error": "not_found"})
            return
        self._send_json(200, {"ok": True})

    def do_POST(self) -> None:
        if self.path != "/echo":
            self._send_json(404, {"error": "not_found"})
            return
        # This demonstration does not implement chunked request bodies.
        if self.headers.get("Transfer-Encoding") is not None:
            self._send_json(400, {"error": "transfer_encoding_not_supported"})
            return
        lengths = self.headers.get_all("Content-Length", [])
        if (len(lengths) != 1 or not lengths[0].isascii()
                or not lengths[0].isdecimal()):
            self._send_json(400, {"error": "invalid_content_length"})
            return
        length = int(lengths[0])
        if length > MAX_BODY:
            self._send_json(413, {"error": "body_too_large"})
            return
        try:
            body = self.rfile.read(length)
        except TimeoutError:
            self._send_json(408, {"error": "request_body_timeout"})
            return
        if len(body) != length:
            self._send_json(400, {"error": "incomplete_body"})
            return
        try:
            value = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not isinstance(value, dict):
            self._send_json(400, {"error": "expected_json_object"})
            return
        self._send_json(200, {"received": value})

    def log_message(self, format: str, *args: object) -> None:
        # Keep test output deterministic and avoid logging request content.
        return
```

This is still a test server, not a hardened parser. The handler sets a short per-connection I/O timeout, rejects missing/duplicate/non-decimal `Content-Length`, refuses transfer encodings it does not implement, caps body bytes, and handles a stalled body. Those are teaching safeguards, not a complete HTTP hardening strategy. A real public service also needs stricter total request deadlines, robust malformed-request handling, TLS termination, authentication/authorization, concurrency controls, observability, and deployment hardening. Never translate a request path directly into a filesystem path without a safe allow-list and containment check.

### 6.2 Controlled startup and shutdown

```python
import threading
from contextlib import contextmanager
from collections.abc import Iterator

@contextmanager
def running_fake_api() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAPIHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    started = False
    try:
        thread.start()
        started = True
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        try:
            if started:
                server.shutdown()  # call from outside the serve_forever thread
        finally:
            server.server_close()
            if started:
                thread.join(timeout=2.0)
                if thread.is_alive():
                    raise RuntimeError("HTTP server thread did not stop")
```

Port `0` asks the OS to choose an ephemeral port; the actual port is read from `server.server_address` after binding. Do not “check that a port is free” by opening and closing a temporary socket and then assume it will remain free: that creates a race. Binding the actual server to port `0` is the correct pattern.

`shutdown()` stops `serve_forever()` and should be called from a thread other than the one running `serve_forever()`. `server_close()` closes the listening socket. Joining the thread confirms it has stopped rather than leaving background work silently running.

### 6.3 Local client calls

```python
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

with running_fake_api() as base_url:
    with urlopen(base_url + "/health", timeout=2.0) as response:
        print(response.status, json.loads(response.read().decode("utf-8")))

    request = Request(
        base_url + "/echo",
        data=json.dumps({"batch_id": "batch-7"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=2.0) as response:
        print(response.status, json.loads(response.read().decode("utf-8")))

    try:
        with urlopen(base_url + "/missing", timeout=2.0) as response:
            pass
    except HTTPError as exc:
        print("missing:", exc.code)
        exc.close()
```

Expected output:

```text
200 {'ok': True}
200 {'received': {'batch_id': 'batch-7'}}
missing: 404
```

## 7. Pytest integration tests using only loopback

These tests use a fixture that starts a server on an ephemeral port and always shuts it down. They require no external internet access.

```python
# test_fake_api.py
import json
import socket
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

# The lesson's implementation module contains these helpers and handler.
from network_demo import (
    FakeAPIHandler, HEADER, MAX_MESSAGE, recv_exact, recv_frame,
    running_fake_api, send_frame,
)


@pytest.fixture
def api_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAPIHandler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
    started = False
    try:
        thread.start()
        started = True
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        try:
            if started:
                server.shutdown()
        finally:
            server.server_close()
            if started:
                thread.join(timeout=2)
                assert not thread.is_alive(), "test HTTP server did not stop"


def test_health_success(api_url):
    with urlopen(api_url + "/health", timeout=2) as response:
        assert response.status == 200
        assert json.loads(response.read().decode("utf-8")) == {"ok": True}


def test_unknown_path_returns_404(api_url):
    with pytest.raises(HTTPError) as caught:
        urlopen(api_url + "/not-found", timeout=2)
    try:
        assert caught.value.code == 404
        assert json.loads(caught.value.read().decode("utf-8")) == {"error": "not_found"}
    finally:
        caught.value.close()


def test_post_echo(api_url):
    request = Request(
        api_url + "/echo",
        data=b'{"job":"daily"}',
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=2) as response:
        assert json.loads(response.read().decode("utf-8")) == {"received": {"job": "daily"}}


def test_invalid_json_returns_400(api_url):
    request = Request(api_url + "/echo", data=b"not-json", method="POST")
    with pytest.raises(HTTPError) as caught:
        urlopen(request, timeout=2)
    try:
        assert caught.value.code == 400
    finally:
        caught.value.close()


def test_oversized_body_returns_413(api_url):
    request = Request(
        api_url + "/echo", data=b"x" * 4097,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with pytest.raises(HTTPError) as caught:
        urlopen(request, timeout=2)
    try:
        assert caught.value.code == 413
    finally:
        caught.value.close()


def test_malformed_content_length_returns_400(api_url):
    # Raw HTTP is used because urllib correctly supplies Content-Length for data=.
    host, port = api_url.removeprefix("http://").split(":")
    with socket.create_connection((host, int(port)), timeout=1) as sock:
        sock.sendall(
            b"POST /echo HTTP/1.1\r\nHost: localhost\r\n"
            b"Content-Length: nope\r\nConnection: close\r\n\r\n"
        )
        with sock.makefile("rb") as response_stream:
            status_line = response_stream.readline()
    assert b"400 Bad Request" in status_line


def test_incomplete_request_body_times_out(monkeypatch):
    import network_demo
    monkeypatch.setattr(network_demo, "CLIENT_IO_TIMEOUT", 0.05)
    with running_fake_api() as api_url:
        host, port = api_url.removeprefix("http://").split(":")
        with socket.create_connection((host, int(port)), timeout=1) as sock:
            sock.settimeout(1)
            sock.sendall(
                b"POST /echo HTTP/1.1\r\nHost: localhost\r\n"
                b"Content-Length: 10\r\nConnection: close\r\n\r\nxy"
            )
            response = bytearray()
            while True:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                response.extend(chunk)
        assert b"408 Request Timeout" in response


def test_socket_read_timeout_is_bounded():
    left, right = socket.socketpair()
    try:
        right.settimeout(0.05)
        with pytest.raises(TimeoutError):
            right.recv(1)  # peer sends no bytes
    finally:
        left.close()
        right.close()


def test_framed_message_round_trip_and_zero_length():
    left, right = socket.socketpair()
    try:
        send_frame(left, b"hello")
        assert recv_frame(right) == b"hello"
        send_frame(left, b"")
        assert recv_frame(right) == b""
    finally:
        left.close()
        right.close()


def test_frame_reader_detects_early_eof():
    left, right = socket.socketpair()
    try:
        left.sendall(b"\x00\x00")  # incomplete four-byte header
        left.close()
        with pytest.raises(EOFError):
            recv_frame(right)
    finally:
        right.close()


def test_oversized_frame_rejected_before_reading_body():
    left, right = socket.socketpair()
    try:
        left.sendall(HEADER.pack(MAX_MESSAGE + 1))
        with pytest.raises(ValueError, match="larger than allowed"):
            recv_frame(right)
    finally:
        left.close()
        right.close()


def test_context_manager_closes_server_port():
    with running_fake_api() as url:
        host, port = url.removeprefix("http://").split(":")
        with urlopen(url + "/health", timeout=1) as response:
            assert response.status == 200
    with pytest.raises(OSError):
        socket.create_connection((host, int(port)), timeout=0.2)
```

**Why this test design is reliable:** it binds the server itself to port `0`, uses loopback only, sets client timeouts, reads bounded small responses, checks exact status/payload behavior, and tears down the serving thread. The suite also tests a deliberately incomplete request body against a short handler timeout. Keep all such tests on loopback with explicit client and server timeouts so a failed test cannot hang the suite.

## 8. Timeout behavior and deterministic timeout testing

Timeout tests can be flaky if they rely on a public internet host or a hard-coded network condition. Test against a local server with an intentionally delayed handler instead. Example pattern:

```python
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from urllib.error import URLError
from urllib.request import urlopen

class SlowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(0.3)
        body = b"late"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            # The client is expected to time out before this response is written.
            pass
        self.close_connection = True
    def log_message(self, format, *args):
        return

server = ThreadingHTTPServer(("127.0.0.1", 0), SlowHandler)
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02})
started = False
try:
    thread.start()
    started = True
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    try:
        with urlopen(url, timeout=0.05) as response:
            response.read()
    except (TimeoutError, URLError) as exc:
        print("timeout or URL-level failure:", type(exc).__name__)
finally:
    try:
        if started:
            server.shutdown()
    finally:
        server.server_close()
        if started:
            thread.join(timeout=2)
            if thread.is_alive():
                raise RuntimeError("slow test server did not stop")
```

The precise exception wrapping can depend on which stage timed out; test the behavior relevant to your Python/runtime and avoid asserting an overly specific wrapper exception unless the contract guarantees it. This demonstrates a timeout, not a universal total-deadline guarantee.

## 9. Advanced reliability and security

### 9.1 Timeouts at each stage

Distinguish connection timeout, socket read timeout, and total deadline. `urlopen(timeout=...)` applies to blocking operations involved in opening/using the request, but it is not a robust total wall-clock budget across name resolution, redirects, and repeated reads. For a long response, each successful read may make progress and extend elapsed time. Higher-level clients often provide clearer connect/read/write/pool/total timeout configuration.

Never use an infinite timeout for an unattended pipeline. A timeout should be selected from the workload's service-level objective and downstream latency, not copied blindly. Retries need bounded attempts, backoff/jitter, an overall deadline, and idempotency awareness; these belong to the higher-level HTTP-client lesson.

### 9.2 URL validation and SSRF boundary

If a URL comes from a user, job config, database row, or remote API, do not treat parsing as validation. A defensive policy commonly restricts schemes (usually `https`, sometimes `http` for local/test), validates host/port, rejects credentials and unexpected fragments, and checks resolved destinations against allowed ranges. Redirects must be revalidated, and DNS rebinding/private-address cases require care. This lesson only introduces the issue; follow the roadmap's dedicated SSRF lesson before implementing a URL-fetching feature exposed to untrusted input.

### 9.3 Request sizes and untrusted input

- Cap response bytes before parsing; validate content types where relevant.
- Cap server request body sizes before reading them.
- Treat `Content-Length` as untrusted and validate parse/range before reading.
- Never map a URL path to a local filesystem path without an allow-list and robust path containment.
- Do not echo arbitrary request data into logs or error bodies.
- Bind test servers to `127.0.0.1`; binding `0.0.0.0` exposes the service on all IPv4 interfaces and is unnecessary for local tests.

### 9.4 TLS and proxies

Use the default verified TLS configuration. A custom CA should be an explicit trusted configuration, not a blanket verification bypass. Proxy variables can affect routing and may embed credentials; avoid printing full proxy URLs. For debugging, log the destination hostname, stage, elapsed time, exception class, and request correlation ID, while redacting authorization headers, cookies, query secrets, and bodies.

### 9.5 Partial reads, non-blocking I/O, `selectors`, and `asyncio`

The framing code above uses blocking sockets with timeouts. For many simultaneous connections, non-blocking sockets and `selectors` can multiplex readiness; `asyncio` builds a higher-level asynchronous model on event loops. These approaches add lifecycle, cancellation, and backpressure concerns. Choose them when measured concurrency/latency needs justify the complexity; do not mix blocking socket calls into an event loop's hot path.

### 9.6 Troubleshooting and observability

| Symptom | Likely layer | Checks |
|---|---|---|
| `socket.gaierror` | DNS | Host spelling, resolver, VPN/corporate DNS, `getaddrinfo()` |
| `ConnectionRefusedError` | TCP connect | Is service listening on that address/port? Is bind address correct? |
| `TimeoutError` | DNS/connect/read/peer | Identify operation, inspect latency and timeout policy |
| `ConnectionResetError` | TCP peer closed/reset | Server logs, protocol mismatch, intermediary reset |
| `ssl.SSLError` / certificate error | TLS | Hostname, system clock, CA chain, proxy interception |
| `HTTPError` | HTTP response | Status code, safe error payload, endpoint and auth policy |
| `JSONDecodeError` | Application payload | Content-Type, body truncation, schema and upstream behavior |

Useful tools include `curl -v` for request/response diagnostics, `ss` or `lsof` for local listening sockets, and Wireshark/tcpdump for packet-level inspection where authorized. Packet captures can contain sensitive data; handle them as confidential artifacts. Never scan or capture networks without permission.

## 10. Common mistakes

- No timeout: an unattended job can hang indefinitely.
- Treating `recv(n)` as “read exactly n bytes.”
- Using `send()` once and assuming every byte was transmitted.
- Assuming each TCP write maps to one read.
- Concatenating query parameters without encoding reserved characters.
- Confusing URL parsing with validation or SSRF protection.
- Decoding response bytes using an arbitrary encoding.
- Reading unbounded request/response bodies into memory.
- Catching `URLError` before `HTTPError` and losing status-specific handling.
- Disabling TLS verification to suppress certificate errors.
- Binding a test server to every interface or leaving it running after a test.
- Testing against external public endpoints in the core test suite.
- Treating `http.server` as production-ready.
- Logging full URLs with sensitive query values or logging authorization headers.

## 11. Mini-project: a local pipeline health probe

Build a small command that calls a configured health endpoint and reports a bounded result. Requirements:

1. Parse the URL with `urlsplit()` and reject schemes other than the explicitly allowed set.
2. Use a configurable finite timeout.
3. Send an `Accept: application/json` header and a descriptive `User-Agent`.
4. Limit the body size and decode according to response metadata with a documented fallback.
5. Distinguish HTTP status failures from network failures.
6. Parse JSON and validate the expected response shape.
7. Log status, elapsed time, and error class, but not credentials, secret query values, or response bodies by default.
8. Test it against the local fake API, including a 404 and a slow endpoint.

Do not use this mini-project as an arbitrary URL fetcher. If the endpoint is not controlled by your application, implement the roadmap's SSRF requirements before making network calls.

## 12. Hands-on exercises

1. Change the GET example to send repeated query parameters such as `tag=python&tag=networking`. Use `parse_qs()` to verify both values are retained.
2. Extend the local API with `GET /items?id=7`; validate query structure with `urlsplit()` and `parse_qs()` rather than splitting strings manually.
3. Add a `Content-Length` limit and malformed JSON test to the POST handler.
4. Change the TCP protocol to newline-delimited UTF-8. Define what happens if a peer never sends a newline and enforce a maximum line length.
5. Write a test that closes a TCP peer midway through a length-prefixed frame and asserts `EOFError`.
6. Add timing to the health probe using `time.monotonic()` and avoid logging the complete URL.
7. Explain why a free-port “check then bind” is racy and demonstrate port `0` instead.
8. Document which failures are retryable for an idempotent `GET` and which must not be blindly retried for a `POST`.

## 13. Self-check with answers

### 1. What is the difference between `HTTPError` and `URLError`?

`HTTPError` means the server returned an HTTP status treated as an error and carries a status code/response; `URLError` covers failures opening/accessing the URL. Since `HTTPError` subclasses `URLError`, catch it first when status-specific handling matters.

### 2. Why must a TCP protocol define framing?

TCP is an ordered byte stream. The receiver cannot infer application message boundaries from individual `send()` calls. Delimiters, fixed sizes, or explicit length prefixes tell the receiver when one message ends; the implementation must also handle partial reads/writes and limits.

### 3. How do you start a test server on a free port and clean it up?

Bind the server directly to `("127.0.0.1", 0)`, read the assigned port from `server.server_address`, run `serve_forever()` in a thread, then call `shutdown()`, `server_close()`, and `join()` in a `finally` block or fixture teardown.

### 4. Does `urlsplit()` make a URL safe?

No. It parses structure. A security policy must separately decide allowed schemes, hosts, ports, addresses, credentials, redirects, and access to local/private networks.

### 5. Why use `sendall()` but still loop around `recv()`?

`sendall()` keeps sending until all supplied bytes are sent or an error occurs. `recv()` returns up to the requested number of bytes and can return early, so an exact-length protocol must accumulate data until the required byte count is reached or EOF occurs.

### 6. Does `urlopen(timeout=5)` guarantee the whole request finishes within five seconds?

No. It is not a universal end-to-end deadline across DNS, redirects, and a sequence of body reads. Use explicit total-deadline logic or a client that provides it when strict elapsed-time bounds are required.

## 14. Final reference checklist

| Need | Standard-library tool | Important caveat |
|---|---|---|
| Parse URL components | `urllib.parse.urlsplit` | Parsing is not validation |
| Encode query parameters | `urllib.parse.urlencode` | Handles query syntax; don't concatenate raw values |
| Encode URL components | `quote`, `quote_plus` | Choose the correct component and safe characters |
| Make HTTP request | `urllib.request.urlopen`, `Request` | Always set timeouts and cap body sizes |
| Handle HTTP status errors | `urllib.error.HTTPError` | Catch before `URLError` |
| Handle URL/network failures | `urllib.error.URLError` | `.reason` may reveal useful diagnostics; redact carefully |
| Lower-level HTTP | `http.client` | More manual connection and response lifecycle |
| TCP client/server | `socket` | TCP is a byte stream; implement framing |
| Resolve hostnames | `socket.getaddrinfo` | Resolution is not authorization or reachability proof |
| Parse IP literals/networks | `ipaddress` | Classification alone is not SSRF defense |
| Verified TLS client context | `ssl.create_default_context` | Never disable verification as a workaround |
| Local fake API | `http.server.ThreadingHTTPServer` | Development/testing only; bind loopback |
| Multiplex socket readiness | `selectors` | Adds non-blocking lifecycle complexity |
| Debug request | `curl -v` | Redact secrets; use only authorized endpoints |
| Inspect local listeners | `ss`, `lsof` | Platform-specific and permission-dependent |

Before shipping a small network utility, confirm: finite timeouts; correct URL encoding; TLS verification enabled; bounded request/response sizes; byte/text conversion explicit; errors classified; resources closed; sensitive data redacted; URL/redirect policy appropriate; and tests use loopback fixtures rather than public internet dependencies.


## 15. Further reading and verification boundaries

The roadmap-derived lesson scope is `urllib`, `socket`, `ipaddress`, `ssl`, `http.client`, a local `http.server` fake API, timeouts, proxies, TLS, framing, and network troubleshooting. The following official references were used to cross-check API and security claims; they supplement rather than replace the roadmap:

- [Python 3.13 `urllib.request`](https://docs.python.org/3.13/library/urllib.request.html) — request construction, response objects, timeout argument, and opener behavior.
- [Python 3.13 `urllib.parse`](https://docs.python.org/3.13/library/urllib.parse.html) — URL parsing, quoting, query encoding, and joining.
- [Python 3.13 `socket`](https://docs.python.org/3.13/library/socket.html) — socket lifecycle, `sendall`, `recv`, timeouts, and `getaddrinfo`.
- [Python 3.12 `http.server`](https://docs.python.org/3.12/library/http.server.html) — handler/server behavior and production/security warning.
- [Python 3.13 `ssl`](https://docs.python.org/3.13/library/ssl.html) — verified TLS contexts and certificate configuration.

**Verification boundary:** local examples and tests validate the demonstrated behavior on the tested runtime; they do not establish production security, prove every operating-system behavior, or test external DNS/proxy/certificate infrastructure. Before deploying a network utility, run integration tests in the target network environment and apply the application's threat model.
