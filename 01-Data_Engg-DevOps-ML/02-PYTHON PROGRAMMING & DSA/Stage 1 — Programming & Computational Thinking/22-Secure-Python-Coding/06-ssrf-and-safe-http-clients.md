# Lesson 06 — SSRF and Safe HTTP Clients

> **Module 1.22: Secure Python Coding** · Intermediate security engineering · Python 3.11+
>
> Defensive work only. Every network exercise in this lesson uses loopback mock services or an in-memory HTTP transport. Never test SSRF against a host, cloud account, cluster, or network you do not own and are explicitly authorized to assess.

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain SSRF as a trust-boundary failure and map the app's network position, credentials, and reachable services.
- Parse URLs unambiguously; apply HTTPS, port, userinfo, hostname, IDNA, and IP-address policies.
- Explain why URL validation and a one-time DNS lookup do **not** prevent DNS rebinding or a validate-then-connect race.
- Design redirect handling that revalidates every hop, with bounded time, bytes, content types, and decompression.
- Configure HTTP clients to avoid ambient proxies/credentials, verify TLS, and produce safe audit logs.
- Reduce blast radius with egress controls, workload identity, metadata restrictions, and isolated fetcher services.
- Test a reusable `SafeFetcher` policy using local fake services, redirect fixtures, and a rebinding simulation.

## Prerequisites and setup

You should know Python exceptions, `urllib.parse`, `ipaddress`, sockets/DNS, HTTP status codes and headers, TLS certificates, unit tests, and basic threat modeling. Earlier module lessons cover secrets, path traversal, subprocesses, unsafe parsing, and test design.

Create a virtual environment and install the dependency used in the lab:

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install "httpx>=0.27,<1" "pytest>=8,<10"
```

The lesson's examples target Python 3.11+ and HTTPX 0.27/0.28 APIs. Pin tested versions in a real project's lockfile. Cloud-specific controls are conceptual checklists here; configure and verify them in your actual cloud/network environment.

## 1. Vocabulary

| Term | Meaning |
|---|---|
| SSRF | Server-side request forgery: an attacker influences a server-side request to a destination the attacker could not directly reach. |
| Trust boundary | A point where data or authority crosses from one trust domain to another. A URL from a user is untrusted even if it is syntactically valid. |
| Egress | Outbound network traffic from a process, pod, VM, or subnet. |
| DNS rebinding | A hostname's DNS answers change so validation sees one address while a later connection reaches another. |
| TOCTOU | Time-of-check to time-of-use race: a property changes between validation and use. |
| Connection pinning | Ensuring the actual socket connects to an address that was validated, while preserving the correct TLS SNI and HTTP Host semantics. |
| IMDS | Cloud instance metadata service, sometimes able to issue workload credentials. |
| Egress proxy | A controlled network intermediary that enforces destination policy at connection time and logs requests. |
| Ambient credentials | Credentials made available implicitly through environment variables, credential files, cookie jars, or client defaults. |
| RAG | Retrieval-augmented generation; content is fetched and supplied to a model as context. |

## 2. SSRF request flow and trust boundaries

SSRF is not limited to internet-facing web apps. Batch jobs, model ingestion, link previews, webhook testers, PDF renderers, RAG crawlers, and agents all fetch attacker-influenced URLs. The request originates from **your** network and may inherit **your** permissions.

```text
User / tenant / uploaded document / model output
                     |
                     v
           URL or resource reference
                     |
          [parse + policy validation]
                     |
                     v
       SafeFetcher / isolated fetch service
                     |
       [egress proxy / firewall policy]
                     |
                     v
    DNS -> destination IP -> TCP -> TLS -> HTTP
                     |
       Internet allow-list / approved API

Forbidden or tightly restricted destinations include:
  loopback, private networks, link-local, metadata endpoints,
  internal DNS/service names, admin planes, Docker sockets,
  cluster control planes, and unrelated tenant resources.
```

The diagram is a policy model, not a guarantee that application validation controls the socket. DNS and connection establishment are separate operations; the network layer must enforce the destination at connect time.

### Assets and possible impact

- Cloud credentials from metadata endpoints, then access to object storage, KMS, databases, or queues.
- Internal admin endpoints, service discovery, monitoring, orchestration APIs, and databases.
- Cross-tenant data, internal HTTP APIs, or local services listening on loopback.
- Data exfiltration through response bodies, status codes, timing, or a blind request side effect.
- Denial of service through slow responses, huge bodies, redirects, decompression bombs, or expensive parsers.

### Threat-model questions

1. Who controls the URL, redirect target, DNS record, or fetched document?
2. Which credentials, proxy settings, cookies, and network routes are available to the fetching process?
3. What destinations and schemes are genuinely required for the product feature?
4. What are the maximum connect/read/total time, redirect count, bytes, decompressed bytes, and concurrency?
5. Can a network proxy enforce the destination policy at connection time even if the Python validator is bypassed?

## 3. URL parsing and a layered safe-fetch design

### 3.1 Why a URL is not just a string

A URL can contain a scheme, userinfo, host, port, path, query, and fragment. Parsers and consumers may interpret ambiguous input differently. Validate a parsed, canonical representation and use that representation downstream. Reject ambiguity rather than trying to repair every malformed URL.

Examples that deserve rejection or careful handling include:

- `http://user:pass@example.test/` — userinfo can disguise the effective host and may leak credentials.
- `https://example.test@127.0.0.1/` — the host is loopback; the text before `@` is userinfo.
- `file:///etc/passwd`, `gopher://...`, `ftp://...`, and other non-HTTP schemes.
- `https://allowed.example:8443/` — non-default port unless explicitly allowed.
- URLs containing control characters, backslashes, malformed brackets, or invalid ports.
- Unicode hostnames and visually confusable IDNs. The sample rejects non-ASCII hostname input to avoid IDNA-profile differences between the validator and HTTP client. Configure allow-lists using explicitly reviewed ASCII DNS names or punycode A-labels; do not accept arbitrary IDNs just because they can be encoded.
- Alternate IPv4 representations such as integer, octal-like, or hexadecimal strings. Do not attempt to enumerate every encoding; require an exact hostname allow-list and let a strict parser reject IP literals unless a specific literal is intentionally allowed.

**Parsing is not authorization.** `urllib.parse.urlsplit()` is useful, but it does not establish that a URL is safe. Do not rely on a single parser's quirks as a security boundary.

### 3.2 VULNERABLE / LAB ONLY — naive fetcher

This example deliberately allows a caller to choose a destination. Use it only against the local mock service in Section 8.

```python
# VULNERABLE / LAB ONLY
import httpx

def naive_fetch(url: str) -> bytes:
    # A user can choose localhost, private IPs, metadata endpoints, etc.
    return httpx.get(url, timeout=5.0).content
```

**Why it is vulnerable:** it does not restrict scheme, host, resolved IP, port, redirects, response size, content type, or ambient client behavior. The default HTTPX client normally verifies TLS, but TLS verification does not prevent SSRF. Reading `.content` buffers the whole response.

### 3.3 Defence: define a narrow product policy

Prefer an exact host allow-list over a deny-list. A deny-list has to anticipate every address encoding, internal hostname, newly introduced service, and redirect path. A host allow-list should match the actual business use case: e.g. a fixed set of partner APIs, not “any public URL”.

Policy decisions should include:

- Scheme: normally `https` only.
- Port: normally `443` only unless the integration explicitly requires another port.
- Host: exact normalized DNS names, or an explicitly documented subdomain rule. `host.endswith("example.com")` is unsafe because `notexample.com` also ends with that string; use exact matching or `host == suffix or host.endswith("." + suffix)` after canonicalization.
- Userinfo and fragments: reject userinfo; fragments are not sent in HTTP requests and can be rejected to avoid ambiguity.
- DNS: resolve all A/AAAA results and reject the host if any answer violates the policy. This is defense-in-depth, not connect-time enforcement.
- Network: force traffic through an egress proxy/firewall that independently enforces destination policy at the actual connection.
- Redirects: disable automatic redirects and revalidate each new URL under the same policy.
- Response: stream; cap bytes, time, redirects, and accepted media types; never echo raw response bodies or exception details to the caller.

### 3.4 A conservative URL and IP policy helper

This helper is intentionally only the **application-side validation layer**. It is not a complete SSRF boundary without connection-time enforcement by an egress proxy or a transport that pins the validated address.

```python
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import SplitResult, urlsplit

class FetchPolicyError(ValueError):
    """The requested resource violates the fetch policy."""


def canonical_host(host: str) -> str:
    """Return a normalized ASCII hostname; reject ambiguous forms."""
    if not host or "%" in host or not host.isascii():
        # Reject Unicode here: the validator and HTTP client may use different IDNA profiles.
        # Configure the allow-list with explicitly reviewed ASCII names / A-labels.
        raise FetchPolicyError("hostname must be an ASCII DNS name")
    if host.endswith("."):
        host = host[:-1]  # canonicalize one DNS root dot
    host = host.lower()
    labels = host.split(".")
    if (len(host) > 253 or any(
        not label or len(label) > 63
        or label.startswith("-") or label.endswith("-")
        or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in label)
        for label in labels
    )):
        raise FetchPolicyError("invalid hostname")
    return host


def parse_allowed_url(raw_url: str, allowed_hosts: set[str]) -> SplitResult:
    if not raw_url or len(raw_url) > 4096:
        raise FetchPolicyError("invalid URL length")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in raw_url):
        raise FetchPolicyError("control character in URL")
    if "\\" in raw_url:
        raise FetchPolicyError("backslashes are not accepted in URLs")

    try:
        parts = urlsplit(raw_url)
        # Accessing .port can raise ValueError for malformed ports/brackets.
        port = parts.port
        username, password = parts.username, parts.password
    except ValueError as exc:
        raise FetchPolicyError("malformed URL") from exc

    if parts.scheme.lower() != "https":
        raise FetchPolicyError("HTTPS is required")
    if not parts.netloc or not parts.hostname:
        raise FetchPolicyError("hostname is required")
    if username is not None or password is not None:
        raise FetchPolicyError("userinfo is not allowed")
    if parts.fragment:
        raise FetchPolicyError("fragments are not accepted")
    if port not in (None, 443):
        raise FetchPolicyError("port is not allowed")

    host = canonical_host(parts.hostname)
    # Configure allowed_hosts using canonical ASCII A-labels.
    canonical_allowed = {canonical_host(item) for item in allowed_hosts}
    if host not in canonical_allowed:
        raise FetchPolicyError("host is not allow-listed")
    return parts


def resolve_and_reject_non_global(host: str, port: int = 443) -> set[str]:
    """Defense-in-depth DNS check; not a defense against DNS rebinding alone."""
    try:
        answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise FetchPolicyError("DNS resolution failed") from exc
    addresses = {item[4][0].split("%", 1)[0] for item in answers}
    if not addresses:
        raise FetchPolicyError("no address records")

    for value in addresses:
        try:
            ip = ipaddress.ip_address(value)
        except ValueError as exc:
            raise FetchPolicyError("invalid DNS address") from exc
        # Normalize IPv4-mapped IPv6 before policy evaluation.
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        # is_global is useful, but behavior for special ranges has changed across
        # Python releases. Explicitly reject important classes too.
        if (
            not ip.is_global
            or ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
            or ip in ipaddress.ip_network("100.64.0.0/10")
            or ip in ipaddress.ip_network("169.254.0.0/16")
        ):
            raise FetchPolicyError("host resolves to a prohibited address")
    return addresses
```

**Important limitations:** `ipaddress.is_global` classifications are Python-version-sensitive, especially for special-purpose ranges; test the supported versions and keep an explicit policy. The example uses a host allow-list, so arbitrary IP literals are not accepted unless they are explicitly put in that allow-list. If your product truly needs an IP literal, parse it with `ipaddress` and authorize it as a distinct policy type. Do not assume IDNA conversion prevents homograph attacks. For IDNs, allow only the exact A-labels your integration expects.

This helper resolves the hostname, but a later HTTP client may resolve it again. Therefore it must not be presented as a complete defense against rebinding. Section 6 explains how to enforce policy at connection time.

## 4. DNS/IP validation and redirect handling

### 4.1 Address classes to consider

Reject destinations that are not explicitly allowed, including:

- Loopback: `127.0.0.0/8`, `::1`.
- RFC 1918 private IPv4: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`; IPv6 unique-local `fc00::/7`.
- Link-local: `169.254.0.0/16`, `fe80::/10`, which includes common metadata addresses.
- Unspecified, multicast, reserved, and non-global ranges.
- IPv4-mapped IPv6 values such as `::ffff:127.0.0.1`.
- Carrier-grade NAT `100.64.0.0/10`; do not assume it is public just because `is_private` may not classify it as private.
- Organization-specific internal ranges and metadata endpoints, even if a library classification changes.

Cloud metadata hostnames and addresses are examples of **destinations to block**, not destinations to probe. Never make a real metadata request during this lesson.

### 4.2 Redirects are new untrusted input

A redirect can turn an initially allowed URL into a forbidden destination. Disable automatic redirects. If redirects are required:

1. Enforce a small hop limit (for example, 3).
2. Resolve `Location` relative to the current URL with `urljoin`.
3. Parse and validate the new URL from scratch.
4. Re-check scheme, port, host allow-list, DNS policy, and connection-time policy.
5. Never forward credentials, cookies, or sensitive headers to a new origin.
6. Reject loops and malformed `Location` values.

HTTPX's `follow_redirects=False` prevents automatic following; it does not implement your policy for you. Redirect status handling should include 301, 302, 303, 307, and 308. Be especially cautious with method changes and credential forwarding if you support methods other than GET.

### 4.3 Host allow-lists must match the feature

For a partner integration, use exact hostnames such as `api.partner.example`. If subdomains are necessary, specify that rule deliberately and ensure the parent domain cannot delegate an untrusted subdomain. Avoid wildcarding an entire cloud provider domain or allowing all of `*.example` when tenants can control DNS for some names. Allow-lists should be paired with TLS verification and connection-time destination enforcement.

## 5. Timeouts, TLS, streaming, and response safety

### 5.1 HTTP client defaults

- Use TLS certificate and hostname verification; never set `verify=False`.
- Configure connect, read, write, and pool timeouts. A read timeout is generally an inactivity timeout, not a total wall-clock deadline.
- Enforce an overall deadline in application logic and at the egress proxy. DNS resolution may block outside HTTPX's normal connect timeout; use a resolver/proxy with bounded resolution if that is in scope.
- Disable automatic redirects; do not send ambient credentials.
- Set `trust_env=False` unless you intentionally require environment proxy settings. When proxies are required, configure the approved proxy explicitly.
- Do not let `.netrc`, inherited cookies, global authentication, `Authorization`, or custom headers silently expand the trust boundary.
- Set a descriptive User-Agent and request only the HTTP methods and media types required by the feature.

### 5.2 Bounded response streaming

Do not use `.content` or `.read()` on untrusted response bodies before checking size. Check `Content-Length` as an early rejection hint, but do not trust it as the only limit: it may be missing or false. Count bytes while streaming and stop immediately after the limit. Keep the connection open only while reading; close responses on all paths.

Compression needs a separate budget. HTTP libraries may automatically decompress responses; a limit on compressed bytes alone does not prevent a decompression bomb. For high-risk ingestion, either request identity encoding and reject compressed content, or use a pipeline that independently caps compressed and decompressed bytes and CPU time. Also bound parser complexity and depth after download.

Content-Type is not proof of content. Enforce an allow-list for the product (e.g. JSON only for an API client), then parse with a bounded parser and validate the resulting schema. Treat `Content-Disposition` filenames as untrusted metadata; do not use them as filesystem paths. The lab rejects non-identity `Content-Encoding` and reads raw response bytes so HTTPX cannot transparently decompress an attacker-controlled body before the byte limit is checked. If compressed content is a product requirement, use a separately reviewed decoder with independent compressed-byte, decompressed-byte, and CPU/time budgets.

### 5.3 Safe user-facing errors and logs

Return generic messages such as “The remote resource could not be fetched.” Internally, record a correlation ID, normalized hostname, policy decision, resolved addresses, redirect count, response byte count, status, elapsed time, and error category. Avoid logging full URLs when query strings can contain credentials or signed tokens. Never log response bodies by default. Sanitize control characters and cap log-field lengths to avoid log injection.

## 6. DNS rebinding and connection-time enforcement

### 6.1 Why validate-then-connect is insufficient

A vulnerable sequence is:

```text
T0: resolver says allowed.example -> public address 203.0.113.x
T1: application checks the answer and approves the hostname
T2: HTTP client resolves allowed.example again
T3: DNS answer has changed to 127.0.0.1 or another prohibited address
T4: socket connects to the new answer
```

The address above is illustrative documentation space, not a destination to connect to. The point is that the application validated one DNS answer but did not bind that answer to the socket. DNS TTLs, multiple A/AAAA answers, resolver caches, and proxy-side resolution complicate the situation. Checking the DNS answer once is valuable defense-in-depth, not a guarantee.

### 6.2 Stronger approaches

**Preferred for production:** route requests through a dedicated egress proxy that enforces destination policy at connection time. The proxy must resolve the hostname, reject forbidden IP ranges, validate every redirect if it follows redirects, prevent access to metadata/internal networks, and apply byte/time/concurrency limits. Configure workers so they cannot bypass the proxy with direct egress.

**Pinned connection design:** if implementing a custom connector, connect the socket to the exact validated IP while retaining the original hostname for TLS SNI, certificate hostname verification, and the HTTP `Host` header. The TLS server name must remain the DNS hostname; simply replacing the URL hostname with an IP can break TLS or silently weaken verification. Pin all permitted answers or select one according to policy; reject if the actual peer address does not match. Redirects require a fresh validation and new pinned connection.

Do not implement this by monkey-patching private HTTPX/httpcore internals without version-pinned tests. A custom transport is security-critical code. If you cannot prove the transport binds validation to the actual socket, use a policy-enforcing proxy or isolate the fetcher at the network layer.

### 6.3 Proxy and ambient client behavior

- `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY` can change the route. Use `trust_env=False` and explicitly configure the approved proxy.
- A proxy that resolves the destination itself must enforce the destination policy itself; local DNS validation cannot constrain a different resolver at the proxy.
- `requests`/`httpx` behavior around environment variables, `.netrc`, cookies, and redirect credential stripping differs by library/version. Do not rely on a client to strip `Authorization` or cookies correctly on every cross-origin redirect; this sample sends no ambient credentials and does not support custom auth headers. Audit the exact client and version you ship.
- Python `urllib` supports non-HTTP URL handlers such as `file:` in some APIs. Do not pass arbitrary schemes to `urlopen`; explicitly constrain to HTTP(S) and still apply host/IP/egress policy.

## 7. Network, identity, and cloud blast-radius controls

Application checks are one layer. Design for a validator bug.

### Network controls

- Dedicated fetcher workers have no route to internal service networks, control planes, databases, node ports, Docker sockets, or metadata endpoints unless a narrowly justified exception exists.
- Use outbound firewall rules or a dedicated egress proxy with hostname/IP policy, connection-time resolution checks, TLS requirements, request logs, and rate limits.
- Deny direct egress from workers so they cannot bypass the proxy.
- Segment workloads by trust level and tenant. Use Kubernetes `NetworkPolicy` where supported by the CNI; remember policy semantics and enforcement vary by cluster/CNI, and policies must be tested in the deployed environment.
- Do not expose container runtime sockets to the fetcher. A Docker socket or orchestration API can be equivalent to host/cluster control.

### Cloud identity and metadata

- Disable instance metadata access when not needed.
- Where supported, require AWS IMDSv2, set the hop limit conservatively (commonly 1 for workloads that do not need multi-hop access), and block metadata endpoints at the workload/network layer. IMDSv2 reduces some attack paths but is not a substitute for egress controls.
- Use workload identity and least-privilege roles rather than static cloud keys. Scope access to only required buckets, objects, keys, queues, and APIs.
- For AWS data access, VPC endpoint policies and resource policies such as `aws:SourceVpce` can restrict access paths where applicable; confirm service-specific semantics before relying on them.
- Enable and review cloud audit events (for example CloudTrail and relevant GuardDuty findings), alert on unusual metadata credential use and unexpected API calls, and preserve evidence during response.
- Never assume a private IP is unreachable merely because it is not internet-routable. Internal routes, peering, VPNs, service meshes, and container networks may expose it.

### Cloud SSRF kill chain (conceptual)

```text
Attacker-controlled URL
  -> vulnerable fetcher reaches metadata service
  -> workload credential is exposed
  -> credential accesses an over-permissioned data store or KMS key
  -> data exfiltration or further compromise
```

Break the chain at multiple points: no metadata route, workload identity with minimal scope, storage policies requiring expected network paths, short-lived credentials, audit detections, and an isolated fetch service. Do not test this chain against a real cloud account as part of this lesson.

## 8. Webhooks, renderers, and AI ingestion

### 8.1 Webhooks you send versus receive

**Sending to a customer-provided webhook URL is an SSRF problem.** Apply the same URL policy, DNS/connection enforcement, redirects, timeouts, size limits, and egress controls. Sign outbound payloads with a documented scheme, such as HMAC-SHA-256, and define retry/backoff and idempotency semantics.

**Receiving webhooks is a different problem.** Verify the provider's signature over the exact raw request bytes using the provider's documented algorithm; compare MACs with a constant-time function where applicable. Validate timestamps within a bounded skew, track replay identifiers, cap request body size, and make handlers idempotent. Source-IP allow-lists are an additional control, not a replacement for signatures. Never invent your own signing protocol if the provider specifies one.

### 8.2 Non-obvious SSRF entry points

The same destination policy applies when a URL reaches:

- PDF/HTML renderers and headless browsers (`wkhtmltopdf`, Chromium): subresources, redirects, CSS imports, and JavaScript may fetch more URLs.
- Image/SVG processors and external delegates.
- XML parsers with external entity resolution (XXE), or parsers that load remote schemas.
- `git clone`, package installers, model downloaders, notebook conversion/execution, OAuth/OIDC discovery, link-unfurling bots, webhook testers, crawlers, and URL-preview services.
- LLM agent browsing tools, tool calls, and RAG ingestion crawlers.

Do not pass user URLs to shell commands or generic protocol handlers. Prefer purpose-built libraries and disable external resource loading in parsers/renderers. If a renderer needs network access, run it in an isolated sandbox with no internal network and a tightly constrained egress path.

### 8.3 Safe crawling and RAG ingestion

- Enforce host/domain policy, per-domain rate limits, concurrency caps, total time and byte budgets, and accepted content types. Respect `robots.txt` where applicable as a crawler conduct policy, but never treat it as an authorization or SSRF security boundary.
- Fetch in a separate low-privilege service with no cloud credentials and no route to internal networks.
- Record provenance (source URL after redaction, fetch time, content hash, MIME/type decision, parser version) without retaining secrets in query strings.
- Strip active content and sandbox document parsing; do not execute scripts, notebooks, macros, or downloaded code.
- Treat fetched text as **untrusted data**. It can contain prompt injection instructions that attempt to redirect an agent, exfiltrate secrets, or invoke tools. Keep tool authorization separate from document text, and never let retrieved content override system policy.

### 8.4 Prefer designs that avoid arbitrary server-side fetching

Before building a general-purpose URL fetcher, consider whether the feature can avoid SSRF exposure entirely:

- Let the user's browser or client retrieve public content when that fits the product and does not expose privileged credentials.
- Accept a file upload instead of fetching an arbitrary user-supplied URL; scan and parse it in an isolated, resource-limited worker.
- Use a narrowly scoped pre-signed object URL or a fixed partner API endpoint rather than a general URL parameter.
- If server-side fetching is necessary, queue it to a dedicated fetcher with no cloud credentials, no internal routes, strict egress policy, and bounded resource budgets.

These alternatives reduce attack surface; any URL fetch that remains server-side still needs the same policy and connection-time enforcement.

## 9. Reusable `SafeFetcher` design and lab

The example below implements application-side policy, manual redirects, time/byte limits, and safe response handling. **Production requirement:** use `SafeFetcher.production()` with an egress proxy that enforces destination policy at connection time. The constructor requires an explicit HTTP(S) proxy URL and rejects proxy URL userinfo; `SafeFetcher.for_test()` is an explicit test-only injection point. The Python-side DNS check is not a substitute for the proxy. The lab uses an injected in-memory HTTPX transport for deterministic redirects, plus a local mock HTTP server to demonstrate why the naive fetcher is unsafe.

### 9.1 `safe_fetcher.py`

```python
from __future__ import annotations

import ipaddress
import socket
import time
from dataclasses import dataclass
from urllib.parse import SplitResult, urljoin, urlsplit

import httpx


class FetchError(RuntimeError):
    """Safe, user-facing fetch failure; does not include raw remote content."""


@dataclass(frozen=True)
class FetchPolicy:
    allowed_hosts: frozenset[str]
    allowed_ports: frozenset[int] = frozenset({443})
    max_bytes: int = 1_000_000
    max_redirects: int = 3
    total_timeout_seconds: float = 10.0
    allowed_content_types: frozenset[str] = frozenset({
        "application/json", "text/plain"
    })

    def __post_init__(self) -> None:
        if not self.allowed_hosts:
            raise ValueError("allowed_hosts must not be empty")
        if self.max_bytes <= 0 or self.max_redirects < 0:
            raise ValueError("invalid size or redirect limit")
        if self.total_timeout_seconds <= 0:
            raise ValueError("timeout must be positive")


class SafeFetcher:
    """A policy-enforcing application layer; production transport must enforce egress."""

    REDIRECT_STATUSES = {301, 302, 303, 307, 308}

    def __init__(self, policy: FetchPolicy, *, egress_proxy: str):
        """Create the production client with an explicit proxy; proxy policy is external.

        This proves only that a proxy is configured, not that it enforces SSRF policy.
        Operators must verify connection-time IP enforcement and block direct egress.
        """
        try:
            proxy_parts = urlsplit(egress_proxy)
            proxy_port = proxy_parts.port
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid egress proxy URL") from None
        if (
            proxy_parts.scheme.lower() not in ("http", "https")
            or not proxy_parts.hostname
            or proxy_parts.username is not None
            or proxy_parts.password is not None
            or proxy_parts.fragment
            or (proxy_port is not None and not 1 <= proxy_port <= 65535)
        ):
            raise ValueError("an explicit HTTP(S) proxy URL without userinfo is required")
        self.policy = policy
        self.client = httpx.Client(
            proxy=egress_proxy,
            trust_env=False,
            follow_redirects=False,
            verify=True,
            timeout=httpx.Timeout(5.0, connect=2.0, read=3.0, write=3.0, pool=2.0),
            headers={"User-Agent": "ExampleSafeFetcher/1.0", "Accept-Encoding": "identity"},
        )

    @classmethod
    def production(cls, policy: FetchPolicy, *, egress_proxy: str) -> "SafeFetcher":
        """Create a client routed through a separately policy-enforcing egress proxy."""
        return cls(policy, egress_proxy=egress_proxy)

    @classmethod
    def for_test(cls, policy: FetchPolicy, client: httpx.Client) -> "SafeFetcher":
        """Inject an in-memory/mock client for tests only; never use for production fetches."""
        instance = cls.__new__(cls)
        instance.policy = policy
        instance.client = client
        return instance

    @staticmethod
    def _canonical_host(host: str) -> str:
        if not host or "%" in host or not host.isascii():
            # Require ASCII DNS names / explicit punycode A-labels so the policy
            # parser and HTTP client's IDNA handling cannot disagree.
            raise FetchError("invalid destination")
        if host.endswith("."):
            host = host[:-1]
        host = host.lower()
        labels = host.split(".")
        if (len(host) > 253 or any(
            not label or len(label) > 63
            or label.startswith("-") or label.endswith("-")
            or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in label)
            for label in labels
        )):
            raise FetchError("invalid destination")
        return host

    def _parse(self, raw: str) -> tuple[SplitResult, str, int]:
        if not raw or len(raw) > 4096:
            raise FetchError("invalid destination")
        if "\\" in raw or any(ord(c) < 0x20 or ord(c) == 0x7f for c in raw):
            raise FetchError("invalid destination")
        try:
            parts = urlsplit(raw)
            port = parts.port
            user, password = parts.username, parts.password
        except ValueError as exc:
            raise FetchError("invalid destination") from exc
        if parts.scheme.lower() != "https" or not parts.hostname:
            raise FetchError("only allow-listed HTTPS destinations are supported")
        if user is not None or password is not None or parts.fragment:
            raise FetchError("invalid destination")
        host = self._canonical_host(parts.hostname)
        allowed = {self._canonical_host(h) for h in self.policy.allowed_hosts}
        effective_port = 443 if port is None else port
        if host not in allowed or effective_port not in self.policy.allowed_ports:
            raise FetchError("destination is not allowed")
        return parts, host, effective_port

    @staticmethod
    def _resolve_public(host: str, port: int) -> set[str]:
        try:
            rows = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise FetchError("destination could not be resolved") from exc
        addresses = {row[4][0].split("%", 1)[0] for row in rows}
        if not addresses:
            raise FetchError("destination could not be resolved")
        for value in addresses:
            try:
                ip = ipaddress.ip_address(value)
            except ValueError as exc:
                raise FetchError("invalid destination address") from exc
            if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
                ip = ip.ipv4_mapped
            if (
                not ip.is_global or ip.is_loopback or ip.is_private
                or ip.is_link_local or ip.is_multicast or ip.is_reserved
                or ip.is_unspecified
                or ip in ipaddress.ip_network("100.64.0.0/10")
                or ip in ipaddress.ip_network("169.254.0.0/16")
            ):
                raise FetchError("destination address is not allowed")
        return addresses

    def fetch(self, raw_url: str) -> tuple[bytes, str, int]:
        """Return (body, media_type, status); no unbounded body buffering."""
        deadline = time.monotonic() + self.policy.total_timeout_seconds
        current = raw_url
        for hop in range(self.policy.max_redirects + 1):
            parts, host, port = self._parse(current)
            # Defense in depth only. The production proxy must repeat policy at connect time.
            self._resolve_public(host, port)
            if time.monotonic() >= deadline:
                raise FetchError("fetch deadline exceeded")

            try:
                with self.client.stream("GET", current, follow_redirects=False) as response:
                    if response.status_code in self.REDIRECT_STATUSES:
                        location = response.headers.get("location")
                        if not location or hop >= self.policy.max_redirects:
                            raise FetchError("redirect limit exceeded")
                        if len(location) > 4096 or "\\" in location or any(
                            ord(char) < 0x20 or ord(char) == 0x7F for char in location
                        ):
                            raise FetchError("invalid redirect destination")
                        next_url = urljoin(current, location)
                        # Next loop parses, resolves, and applies policy from scratch.
                        current = next_url
                        continue
                    if not 200 <= response.status_code < 300:
                        raise FetchError("remote service returned an unsuccessful status")
                    media_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                    if media_type not in self.policy.allowed_content_types:
                        raise FetchError("remote content type is not allowed")
                    content_encoding = response.headers.get("content-encoding", "identity").strip().lower()
                    if content_encoding not in ("", "identity"):
                        # Reject before HTTPX can decompress attacker-controlled bytes.
                        raise FetchError("compressed responses are not supported")
                    length = response.headers.get("content-length")
                    if length is not None:
                        try:
                            declared_length = int(length)
                            if declared_length < 0:
                                raise ValueError("negative content length")
                            if declared_length > self.policy.max_bytes:
                                raise FetchError("remote response is too large")
                        except ValueError:
                            raise FetchError("invalid response length") from None
                    chunks: list[bytes] = []
                    total = 0
                    # iter_raw() avoids automatic decompression. Since non-identity
                    # encodings were rejected above, byte count is the body byte count.
                    for chunk in response.iter_raw(chunk_size=64 * 1024):
                        if time.monotonic() >= deadline:
                            raise FetchError("fetch deadline exceeded")
                        total += len(chunk)
                        if total > self.policy.max_bytes:
                            raise FetchError("remote response is too large")
                        chunks.append(chunk)
                    return b"".join(chunks), media_type, response.status_code
            except httpx.HTTPError:
                # Suppress exception chaining: transport exceptions may embed URLs.
                raise FetchError("remote resource could not be fetched") from None
        raise FetchError("redirect limit exceeded")

    def close(self) -> None:
        self.client.close()
```

### 9.2 Review the implementation honestly

This is a teaching implementation of application policy, not a drop-in universal production security boundary.

- The production constructor requires an explicit HTTP(S) proxy URL, rejects URL userinfo, and disables ambient environment configuration, but **the proxy itself must enforce destination policy at connection time**. Merely configuring a proxy is not sufficient if it allows arbitrary CONNECT destinations or resolves untrusted names without checks. The `for_test()` factory deliberately bypasses production client construction and must remain test-only.
- The application resolves the host before sending the request, but HTTPX through a proxy may cause the proxy to resolve it independently. The DNS check is therefore defense-in-depth only.
- `Accept-Encoding: identity` asks the server not to compress. The fetcher also rejects any non-identity `Content-Encoding` before reading and uses `iter_raw()` to avoid automatic decompression. If compressed content is required, this implementation is insufficient; add a separately reviewed decoder with compressed/decompressed byte and CPU/time budgets. Enforce network/proxy limits too.
- The `deadline` is checked between operations/chunks; it cannot preempt a blocked system DNS resolver or every blocking transport operation. Proxy DNS/connect/read deadlines and worker-level cancellation are also required for a hard wall-clock budget.
- This implementation accepts only `GET`, has no cookies or auth headers, and does not return raw response headers. Keep those restrictions unless the use case requires a reviewed extension.
- The sample rejects Unicode hostname input and requires the allow-list to use ASCII DNS names or reviewed punycode A-labels, avoiding reliance on different IDNA profiles in the validator and HTTP client. DNS/IP classification varies by Python version; maintain tests for supported versions and explicit organization-specific ranges.
- The code does not implement a custom pinned-IP transport. Use an egress proxy that enforces policy at connect time, or add a separately reviewed, version-pinned transport that binds the socket to the validated address while preserving TLS SNI/hostname verification.

### 9.3 Local fake service

Save as `lab_server.py`. This binds only to loopback. It does not contact cloud metadata or any external host.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
            return
        body = b'{"message":"local lab only"}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Avoid noisy request logging during the exercise.
        return

if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
```

Start it in one terminal with `python lab_server.py`, then stop it with Ctrl+C when done. It is intentionally HTTP on loopback for the lab; production `SafeFetcher` policy rejects HTTP and loopback.

### 9.4 Safe local test strategy

Because the safe production policy must reject loopback, use two separate test methods:

1. Prove the naive function can reach the loopback fake service.
2. Prove `SafeFetcher` rejects loopback and HTTP before making a request.
3. Use HTTPX `MockTransport` and a fake resolver in unit tests for deterministic allowed-host redirect behavior without DNS or external network access. Keep the fake resolver and mocked transport strictly in tests; do not add a production “allow localhost” bypass.

The following `test_safe_fetcher.py` uses HTTPX's in-memory transport for deterministic unit tests. The only socket test binds an ephemeral port on `127.0.0.1`; no test makes a network request to an external host. The resolver is stubbed in tests that exercise redirect/body behavior; a separate test feeds mixed DNS answers to the real IP-policy function.

```python
# test_safe_fetcher.py
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
import pytest

import safe_fetcher
from safe_fetcher import FetchError, FetchPolicy, SafeFetcher


def build_fetcher(handler, *, max_bytes=100, max_redirects=2):
    policy = FetchPolicy(
        allowed_hosts=frozenset({"api.partner.example"}),
        max_bytes=max_bytes,
        max_redirects=max_redirects,
    )
    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        trust_env=False,
        follow_redirects=False,
    )
    return SafeFetcher.for_test(policy, client)


def stub_public_dns(monkeypatch):
    monkeypatch.setattr(
        SafeFetcher,
        "_resolve_public",
        staticmethod(lambda host, port: {"8.8.8.8"}),
    )


def test_naive_fetcher_reaches_owned_loopback_fixture_only():
    # VULNERABLE / LAB ONLY: target is an ephemeral loopback server created here.
    class LocalHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"local fake metadata service"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):
            return

    server = HTTPServer(("127.0.0.1", 0), LocalHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        # This is intentionally unsafe and exists only to demonstrate the lab flaw.
        with httpx.Client(trust_env=False, timeout=2.0, follow_redirects=False) as client:
            body = client.get(f"http://127.0.0.1:{server.server_port}/").content
        assert body == b"local fake metadata service"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2.0)


def test_rejects_http_userinfo_and_unapproved_host_before_request():
    called = []
    fetcher = build_fetcher(lambda request: called.append(request) or httpx.Response(200))
    try:
        for url in (
            "http://api.partner.example/",
            "https://api.partner.example@blocked.example/",
            "https://blocked.example/",
            "https://api.partner.example:444/",
        ):
            with pytest.raises(FetchError):
                fetcher.fetch(url)
        assert called == []
    finally:
        fetcher.close()


def test_allowed_host_success(monkeypatch):
    stub_public_dns(monkeypatch)
    fetcher = build_fetcher(
        lambda request: httpx.Response(
            200,
            headers={"content-type": "application/json", "content-length": "8"},
            stream=httpx.ByteStream(b'{"ok":1}'),
        )
    )
    try:
        body, media_type, status = fetcher.fetch("https://api.partner.example/data")
        assert (body, media_type, status) == (b'{"ok":1}', "application/json", 200)
    finally:
        fetcher.close()


def test_redirect_to_blocked_host_is_rejected_before_second_request(monkeypatch):
    stub_public_dns(monkeypatch)
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://blocked.example/next"})

    fetcher = build_fetcher(handler)
    try:
        with pytest.raises(FetchError):
            fetcher.fetch("https://api.partner.example/start")
        assert len(seen) == 1
    finally:
        fetcher.close()


def test_allowed_relative_redirect_is_revalidated_and_followed(monkeypatch):
    stub_public_dns(monkeypatch)
    seen = []

    def handler(request):
        seen.append(request.url.path)
        if request.url.path == "/start":
            return httpx.Response(302, headers={"location": "/end"})
        return httpx.Response(200, headers={"content-type": "text/plain"}, stream=httpx.ByteStream(b"done"))

    fetcher = build_fetcher(handler)
    try:
        body, media_type, status = fetcher.fetch("https://api.partner.example/start")
        assert (body, media_type, status) == (b"done", "text/plain", 200)
        assert seen == ["/start", "/end"]
    finally:
        fetcher.close()


def test_redirect_cap_is_enforced(monkeypatch):
    stub_public_dns(monkeypatch)
    fetcher = build_fetcher(
        lambda request: httpx.Response(302, headers={"location": "/again"}),
        max_redirects=1,
    )
    try:
        with pytest.raises(FetchError, match="redirect limit"):
            fetcher.fetch("https://api.partner.example/start")
    finally:
        fetcher.close()


def test_declared_and_streamed_size_limits(monkeypatch):
    stub_public_dns(monkeypatch)
    for headers in (
        {"content-type": "text/plain", "content-length": "101"},
        {"content-type": "text/plain"},
    ):
        fetcher = build_fetcher(
            lambda request, h=headers: httpx.Response(200, headers=h, stream=httpx.ByteStream(b"x" * 101)),
            max_bytes=100,
        )
        try:
            with pytest.raises(FetchError, match="too large"):
                fetcher.fetch("https://api.partner.example/data")
        finally:
            fetcher.close()


def test_wrong_content_type_is_rejected(monkeypatch):
    stub_public_dns(monkeypatch)
    fetcher = build_fetcher(
        lambda request: httpx.Response(200, headers={"content-type": "text/html"}, content=b"<html>")
    )
    try:
        with pytest.raises(FetchError, match="content type"):
            fetcher.fetch("https://api.partner.example/data")
    finally:
        fetcher.close()


def test_unicode_hostname_is_rejected_to_avoid_idna_parser_differentials():
    called = []
    fetcher = build_fetcher(lambda request: called.append(request) or httpx.Response(200))
    try:
        with pytest.raises(FetchError):
            fetcher.fetch("https://faß.de/")
        assert called == []
    finally:
        fetcher.close()


def test_compressed_response_is_rejected_before_body_read(monkeypatch):
    stub_public_dns(monkeypatch)
    fetcher = build_fetcher(
        lambda request: httpx.Response(
            200,
            headers={"content-type": "text/plain", "content-encoding": "gzip"},
            stream=httpx.ByteStream(b"not-decompressed-by-the-fetcher"),
        )
    )
    try:
        with pytest.raises(FetchError, match="compressed responses"):
            fetcher.fetch("https://api.partner.example/data")
    finally:
        fetcher.close()


def test_redirect_location_with_control_characters_is_rejected(monkeypatch):
    stub_public_dns(monkeypatch)
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://api.partner.example/\nnext"})

    fetcher = build_fetcher(handler)
    try:
        with pytest.raises(FetchError):
            fetcher.fetch("https://api.partner.example/start")
        assert len(seen) == 1
    finally:
        fetcher.close()


def test_negative_content_length_is_rejected(monkeypatch):
    stub_public_dns(monkeypatch)
    fetcher = build_fetcher(
        lambda request: httpx.Response(
            200, headers={"content-type": "text/plain", "content-length": "-1"}, content=b"x"
        )
    )
    try:
        with pytest.raises(FetchError, match="response length"):
            fetcher.fetch("https://api.partner.example/data")
    finally:
        fetcher.close()


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1", "10.0.0.1", "172.16.0.1", "192.168.1.1",
        "169.254.169.254", "100.64.0.1", "224.0.0.1", "240.0.0.1",
        "192.0.2.1", "198.18.0.1", "203.0.113.1", "0.0.0.0",
        "::", "::1", "::ffff:127.0.0.1", "fc00::1", "fe80::1",
        "ff02::1", "2001:db8::1",
    ],
)
def test_special_use_and_non_public_addresses_are_rejected(monkeypatch, address):
    parsed = __import__("ipaddress").ip_address(address)
    family = socket.AF_INET6 if parsed.version == 6 else socket.AF_INET
    sockaddr = (address, 443, 0, 0) if parsed.version == 6 else (address, 443)
    monkeypatch.setattr(
        safe_fetcher.socket,
        "getaddrinfo",
        lambda host, port, *, type: [(family, socket.SOCK_STREAM, 6, "", sockaddr)],
    )
    with pytest.raises(FetchError, match="not allowed"):
        SafeFetcher._resolve_public("api.partner.example", 443)


@pytest.mark.parametrize(
    "proxy_url",
    [
        "file:///tmp/proxy", "http://user:secret@proxy.example:3128/",
        "http://proxy.example:0/", "http://proxy.example:bad/",
    ],
)
def test_production_constructor_rejects_unsafe_proxy_url(proxy_url):
    policy = FetchPolicy(allowed_hosts=frozenset({"api.partner.example"}))
    with pytest.raises(ValueError):
        SafeFetcher(policy, egress_proxy=proxy_url)


def test_100_plus_url_attack_corpus_is_rejected_before_transport(monkeypatch):
    # Deterministic offline corpus: no real resolver or external network is used.
    payloads = [
        "http://api.partner.example/", "file:///etc/passwd", "gopher://127.0.0.1/",
        "ftp://127.0.0.1/", "dict://127.0.0.1/", "https://user:pass@api.partner.example/",
        "https://api.partner.example@127.0.0.1/", "https://api.partner.example:444/",
        "https://faß.de/", "https://%65xample.com/", "https://api.partner.example\\@127.0.0.1/",
        "https://api.partner.example/\tpath", "https://[::1]/", "https://[::ffff:127.0.0.1]/",
        "https://2130706433/", "https://0177.0.0.1/", "https://0x7f000001/",
        "https://169.254.169.254/", "https://100.100.100.200/",
    ]
    for index in range(60):
        payloads.append(f"https://blocked-{index}.example/")
        payloads.append(f"https://blocked-{index}.example:444/path")
    payloads = list(dict.fromkeys(payloads))
    assert len(payloads) >= 100

    called = []
    fetcher = build_fetcher(lambda request: called.append(request) or httpx.Response(200))
    monkeypatch.setattr(
        SafeFetcher,
        "_resolve_public",
        staticmethod(lambda *args: pytest.fail("invalid corpus URL reached DNS validation")),
    )
    try:
        for url in payloads:
            with pytest.raises(FetchError):
                fetcher.fetch(url)
        assert called == []
    finally:
        fetcher.close()


def test_dns_answer_change_between_redirect_hops_is_rejected(monkeypatch):
    # Simulate a changing answer set entirely in-process; no DNS or socket access occurs.
    answers = []

    def fake_getaddrinfo(host, port, *, type):
        address = "8.8.8.8" if not answers else "127.0.0.1"
        answers.append(address)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, port))]

    monkeypatch.setattr(safe_fetcher.socket, "getaddrinfo", fake_getaddrinfo)
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(302, headers={"location": "/next"})

    fetcher = build_fetcher(handler)
    try:
        with pytest.raises(FetchError, match="not allowed"):
            fetcher.fetch("https://api.partner.example/start")
        assert answers == ["8.8.8.8", "127.0.0.1"]
        assert seen == ["/start"]
    finally:
        fetcher.close()


def test_mixed_public_and_loopback_dns_answers_are_rejected(monkeypatch):
    def fake_getaddrinfo(host, port, *, type):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port)),
        ]

    monkeypatch.setattr(safe_fetcher.socket, "getaddrinfo", fake_getaddrinfo)
    with pytest.raises(FetchError, match="not allowed"):
        SafeFetcher._resolve_public("api.partner.example", 443)
```

Run unit tests with `pytest -q test_safe_fetcher.py`. For the naive reachability demonstration, start `lab_server.py` separately and use the loopback-only check below; do not use a real metadata endpoint.
### 9.5 Redirect and DNS-rebinding unit-test design

A deterministic redirect test should inject an `httpx.MockTransport` that returns a redirect from `https://api.partner.example/start` to `https://blocked.example/`, then assert the fetcher rejects the second host before issuing a second request. To test the policy path without DNS, inject a resolver function into a test-only version of the class; have it return an allowed global address for the first lookup and a loopback address on the second. Assert that the second result is rejected and that the HTTP transport is never called for the prohibited hop.

For a real connection-time guarantee, a mock cannot prove that the OS socket used a pinned address. Integration-test the deployed egress proxy with a local controlled DNS fixture that changes answers between lookups, and verify the proxy blocks the prohibited destination at connection time. Do not point the fixture at a real metadata address or external network. Use a disposable network namespace/container and a fake loopback “metadata” server you own.

A testable design improvement is to inject `resolver` and `transport_factory` interfaces into `SafeFetcher`; production implementations use the system resolver plus an enforcing egress proxy, while tests use deterministic fakes. Avoid exposing test-only policy bypasses in the production API.

### 9.6 Malicious URL regression matrix

Each case should be rejected before network access unless it exactly matches a deliberately approved product destination. Do not blindly treat every syntactic variation as the same outcome; assert the intended policy decision.

| Input / condition | Expected policy outcome | Reason |
|---|---|---|
| `http://api.partner.example/` | Reject | HTTPS-only policy. |
| `https://api.partner.example:444/` | Reject | Port not allow-listed. |
| `https://user:pass@api.partner.example/` | Reject | Userinfo forbidden. |
| `https://api.partner.example@127.0.0.1/` | Reject | Effective host is loopback, not allow-listed. |
| `https://127.0.0.1/`, `https://[::1]/` | Reject | IP literal not allow-listed; loopback policy. |
| `https://169.254.169.254/` | Reject without requesting it | Link-local/metadata destination; never probe. |
| `https://100.100.100.200/` | Reject without requesting it | Example metadata IP used by some cloud platforms; never probe. |
| `https://2130706433/`, `https://0x7f000001/` | Reject | Noncanonical IP encodings are not in exact hostname allow-list. |
| `https://api.partner.example\\@127.0.0.1/` | Reject | Backslash ambiguity. |
| URL containing tabs, CR, LF, NUL, or DEL | Reject | Control characters and parser differential risk. |
| Invalid IPv6 brackets or port | Reject | Malformed URL. |
| Unicode confusable or unapproved IDN | Reject | Canonicalization is not authorization; exact A-label allow-list. |
| Allowed hostname resolves to any prohibited address | Reject | Mixed answer sets must not be accepted. |
| Allowed hostname resolves publicly at check time, then privately at connect time | Must be blocked by egress proxy/pinned transport | Validator alone cannot close rebinding race. |
| Redirect from allowed host to an unapproved host | Reject before second request | Every redirect is a new trust decision. |
| Redirect loop or too many hops | Reject | Bound redirects. |
| Missing/false `Content-Length` with body over cap | Abort while streaming | Header is only an early hint. |
| Wrong Content-Type | Reject before body processing where possible | Type policy. |
| Slow response or endless stream | Abort under deadline/worker controls | Resource exhaustion. |
| Compressed bomb | Reject or enforce decompressed-size/CPU limits | Compressed byte limit alone is insufficient. |
| Environment has hostile `HTTPS_PROXY` or `NO_PROXY` | Client route remains explicit | `trust_env=False` plus configured egress proxy. |

### 9.7 Fuzz and regression strategy

The roadmap calls for a corpus of 100+ URL cases. The lab includes a deterministic offline corpus of more than 100 hostile URL variants and address-class tests, covering scheme, userinfo, malformed port, IPv4/IPv6, alternate IP spellings, backslashes, controls, Unicode/IDNs, and unapproved hosts. Extend it with product-specific hosts, mixed-case/canonicalization cases, redirect fixtures, and unusual DNS answers; keep expected decisions in a golden test table. Extend the corpus with product-specific hosts and add property-based testing (for example Hypothesis) for parser robustness: arbitrary strings must either produce a normalized approved URL or a typed rejection, never an unhandled exception, crash, or network request before policy approval. Fuzzing must be offline. Run a separate controlled integration suite against your egress proxy to prove the connection-time policy; pure unit tests cannot prove the network route.

## 10. Common mistakes

- Checking only `url.startswith("https://")` or using a substring check on the hostname.
- Using a deny-list instead of a narrow allow-list.
- Checking DNS once and assuming the later socket must use that address.
- Validating the initial URL but following redirects automatically.
- Treating `ipaddress.is_global` as a permanent, complete security policy.
- Forgetting IPv4-mapped IPv6, CGNAT, metadata addresses, internal DNS, or organization-specific ranges.
- Assuming TLS verification prevents SSRF. TLS protects the connection to the named server; it does not authorize the destination.
- Setting only a read timeout and calling it a total deadline.
- Reading the entire body into memory or trusting `Content-Length` alone.
- Relying on `Accept-Encoding: identity` as proof the response cannot be compressed.
- Accidentally inheriting proxy variables, `.netrc`, cookies, or authentication headers.
- Believing a Kubernetes NetworkPolicy is active without confirming the CNI enforces it.
- Sending untrusted URLs to renderers, `git`, package installers, or LLM tools outside the same policy boundary.
- Treating fetched web text as trusted instructions for an AI agent.

## 11. Self-check with answers

### 1. Why is a hostname deny-list insufficient?

Because attackers can use alternate address encodings, internal DNS names, new internal services, redirects, IPv6 variants, and parser differentials. A narrow allow-list describes the destinations the feature actually needs. DNS/IP checks and network enforcement still matter.

### 2. Explain DNS rebinding and one strong mitigation.

A hostname resolves to an allowed address during validation but resolves to a prohibited address before the HTTP client connects. A one-time lookup does not bind the validated answer to the socket. Use a custom, reviewed transport that connects to the validated IP while retaining correct TLS SNI/hostname verification, or preferably route through an egress proxy that enforces the policy at connection time and cannot be bypassed.

### 3. Which cloud controls limit blast radius if the validator has a bug?

Block metadata access where not required; require IMDSv2 where applicable; use short-lived workload identity with least privilege; restrict storage/API access using resource and endpoint policies; isolate fetcher networks; block direct egress; audit credential and API use; alert on anomalous access.

### 4. Why does `shell=False` or HTTPS not solve SSRF?

Those controls address different boundaries. HTTPS provides transport security to the chosen host, not destination authorization. Avoiding a shell reduces command injection but does not prevent a URL fetcher from reaching an internal service.

### 5. What must happen after a redirect?

Resolve the new location relative to the previous URL, parse and validate it from scratch, enforce the same host/scheme/port/IP policy at connection time, avoid forwarding credentials, and stop after a small redirect limit.

### 6. How would you test a rebinding defense safely?

Use a controlled local DNS fixture and fake internal service in a disposable network environment. Simulate changing DNS answers, prove that the egress proxy or pinned connector checks the actual connection destination, and assert the prohibited connection never occurs. Do not contact real metadata endpoints or third-party networks.

## 12. Completion checklist

- [ ] I can draw the SSRF trust boundary and identify the credentials/network routes available to a fetcher.
- [ ] I parse URLs strictly and enforce HTTPS, allowed ports, exact host policy, no userinfo, and explicit IDN behavior.
- [ ] I validate all DNS answers, including IPv4-mapped IPv6 and CGNAT, while understanding that this is not connect-time enforcement.
- [ ] Redirects are disabled or manually revalidated at every hop with a cap.
- [ ] TLS verification is on; timeouts, total budget, concurrency, bytes, content types, and parser limits are explicit.
- [ ] Ambient proxy settings, `.netrc`, cookies, and credentials are controlled.
- [ ] The fetcher cannot bypass an egress proxy/firewall that enforces destination policy at connection time.
- [ ] Metadata access is blocked or tightly controlled; workload identity is least-privileged.
- [ ] Webhook sending and receiving have separate SSRF/signature/replay controls.
- [ ] Renderers, installers, crawlers, RAG ingestion, and agent tools share the same destination policy.
- [ ] Regression corpus, redirect tests, and DNS-rebinding tests run in CI; proxy integration tests validate the real network boundary.
- [ ] User-facing errors are generic and logs are structured, bounded, and free of secrets.

## Further reading

Use the official documentation for the versions you deploy: Python `urllib.parse`, `ipaddress`, and `ssl`; HTTPX client, timeout, proxy, and streaming documentation; OWASP SSRF Prevention Cheat Sheet; cloud provider metadata-service and workload-identity guidance; and the Kubernetes NetworkPolicy documentation for your CNI. Treat library behavior as versioned: lock dependencies and run security regression tests when upgrading.
