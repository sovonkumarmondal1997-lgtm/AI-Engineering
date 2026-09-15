# 16 — Local Networking for Development

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Computer, Linux, and Developer Foundations, Gap 0C — "Local
networking needed for development" (extends Module 0.2 — Operating System Fundamentals)
**Concept(s) covered:** client-server communication, `localhost`, `127.0.0.1`, private/public IP
addresses, ports, DNS, URLs, the one-process-per-port rule, "process running" vs. "service
reachable," `curl`, `ss -ltnp`, `Get-NetTCPConnection`
**Status:** Not Started

---

## Learning Goals

By the end of this lesson you will be able to:

- Explain, in plain language, what a client and a server are and how they talk to each other.
- Explain `localhost`, `127.0.0.1`, and the difference between a private and a public IP address.
- Explain what a port is, and why two programs cannot normally listen on the same one.
- Explain what DNS does and how a URL is built from its parts.
- Explain the difference between "a process is running" and "a service is reachable."
- Use `curl` to send a request to a local service and read the response.
- Use `ss -ltnp` (Linux/WSL2) or `Get-NetTCPConnection` (PowerShell) to find which process is
  listening on a port.
- Safely diagnose "connection refused," a wrong port, a process that isn't running, and a port
  already in use.
- Explain why this lesson matters for later API, FastAPI, Docker, model-serving, vector-database,
  and AI-agent work.

## Prerequisites

- **Module 0.2, Concepts 01–03** ([Kernel and User Space](01-kernel-and-user-space.md),
  [System Calls](02-system-calls.md), [Processes](03-processes.md)) — this lesson treats a
  "service" as just a process, and a network request as just another way a process talks to the
  outside world through the kernel.
- **Module 0.2, Concept 11** ([Standard Input/Output](11-standard-input-output.md)) — useful for
  contrasting how a process reads/writes text on a terminal versus over a network.
- Comfort in a terminal (Bash/WSL2 or PowerShell) from Module 0.3 — Command Line is helpful but not
  required; every command below is explained from scratch.
- No prior networking knowledge is assumed. This lesson deliberately teaches only what is needed to
  understand a *local* development service — not general networking, routing, or the internet at
  large.

---

## 1. What Is It?

**Connecting to what you already know.** Every process you've met so far in this module ran on its
own, read and wrote files (Concept 07 — [Filesystems](07-filesystems.md)), and printed to a
terminal (Concept 11 — [Standard Input/Output](11-standard-input-output.md)). This lesson
introduces a new way two *separate* processes — possibly on different machines, but often just two
programs on your own laptop — can talk to each other: over a network connection, using the
**client-server** pattern.

**Client.** Simple meaning: the program that starts a conversation by asking for something.
Technical meaning: a client is a process that initiates a network connection to a specific address
and port, sends a request, and waits for a response.

**Server.** Simple meaning: the program that waits, listens, and answers when asked. Technical
meaning: a server is a process that binds to a port, listens for incoming connections, and responds
to requests it receives.

**A simple conceptual example:**

```text
You run:  curl http://localhost:8000/
                ↓
Your terminal starts a CLIENT process (curl)
                ↓
The client sends a request to a SERVER process listening on port 8000
                ↓
The server reads the request, prepares a response
                ↓
The server sends the response back
                ↓
curl prints the response to your terminal
```

**Why this matters immediately:** almost everything you will build later in this roadmap — a
backend API, a FastAPI app, a model-serving endpoint, a vector database, an AI agent calling a
tool — is one of these two roles, usually a server, and debugging any of them starts with the same
question this lesson answers: *is the right process listening on the right port, and can a client
actually reach it?*

---

## 2. Why Does It Exist?

**The problem: two independent processes need a reliable way to exchange requests and responses.**
A process can talk to itself easily (function calls, in-memory variables) and can talk to the
filesystem easily (Concept 07). But two *separate* processes — even two processes on the very same
machine — have no shared memory and no direct way to reach each other, unless the operating system
gives them one. Networking, even purely local networking, is that mechanism.

**The specific problems local networking solves for a developer:**

- **Talking to a service you just started.** You start a small web server on your machine; you need
  a way to send it a request and see what it does — without leaving your machine at all.
- **Identifying *which* service to talk to.** One machine can run many services at once (a
  database, a backend API, a model server); ports (Section 5) exist so each can be reached
  separately.
- **Distinguishing "my code is broken" from "my code isn't reachable."** Section 5's core
  distinction — a process can be running perfectly and still be unreachable, for reasons that have
  nothing to do with its logic.
- **Preparing for real networked systems.** Every later stage that involves an API, a database
  connection, a Dockerized service, or a model-serving endpoint builds directly on the same
  client-server, address-and-port model this lesson introduces — just applied beyond your own
  machine.

**What this lesson deliberately does not cover.** Full networking (routing, subnets, firewalls,
TLS/HTTPS internals, load balancers) is a later, deeper topic. This lesson teaches only the small,
practical slice needed to run and debug a local development service — exactly the scope Stage 0's
roadmap (Gap 0C) calls for.

---

## 3. Why an AI Engineer Needs It

- **Every backend API and model-serving endpoint is a local server before it is anything else.**
  Long before a FastAPI app or a model server is deployed anywhere, you will run it on your own
  machine and need to confirm it's actually listening and reachable — this lesson is that skill.
- **"Connection refused" and "port already in use" are two of the most common early errors** in
  backend, database, and model-serving work. Without this lesson's mental model, both look like
  mysterious failures instead of two specific, diagnosable situations (Section 11).
- **Docker exposes and maps ports** using exactly the concepts in this lesson (a container process
  listens on a port; that port is mapped to one on your host machine) — you cannot reason about a
  Docker networking problem without first understanding ports and listeners on a single machine.
- **Vector databases and local model servers** (for example, a local embedding server or a locally
  hosted LLM) are, mechanically, just another process listening on a local port — the exact same
  diagnostic questions apply: is it running, and is it reachable?
- **AI agents that call tools or APIs** are, underneath, client processes making the same kind of
  request this lesson's `curl` examples make — understanding the client-server exchange here
  directly demystifies what an agent's "tool call" is actually doing at the network level.

**A production-style sequence, previewed here:**

```text
You start a local model-serving process
        ↓
It binds to a port (e.g., 8000) and starts listening
        ↓
Your application code (or an agent) acts as a CLIENT
        ↓
It sends a request to that port
        ↓
The model server responds with a result
```

This is the same shape you will use later for a FastAPI backend, a Dockerized service, or a
locally-served model — only the payload changes.

---

## 4. Beginner Explanation

**Analogy: apartments in a building.**

```text
Machine (your laptop)   = an apartment building
IP address              = the building's street address
Port                    = a specific apartment number in that building
Process listening       = someone home in that apartment, answering the door
```

If you want to visit a specific person, knowing the building's address isn't enough — you need
their apartment number too. If you knock on apartment 8000 and nobody is home, you get no answer
("connection refused," Section 11). If you knock on the wrong apartment number, you might reach the
wrong resident entirely, or nobody. And critically: **two different households can't both claim
the exact same apartment number in the same building at the same time** — this is the everyday feel
of Section 5's one-process-per-port rule.

**Where this analogy is useful:** it captures the core shape — an address gets you to the building
(the machine), a port gets you to the specific listener within it (the process).

**Where this analogy breaks down:** a building's apartment numbers rarely change, but a port is
just a number any listening program can choose (within rules explained in Section 5) — there's
nothing physically fixed about "port 8000 is a web server"; that's convention, not law. The rest of
this lesson moves from this everyday intuition into the precise, technical model.

---

## 5. Technical Explanation

### `localhost` and `127.0.0.1`

**IP address.** Simple meaning: a numeric address identifying a machine on a network. Technical
meaning: an Internet Protocol address, a number (commonly written in IPv4 as four dot-separated
numbers, e.g. `192.168.1.42`) that identifies a device on a network so other devices know where to
send data.

**`127.0.0.1`.** A special, reserved IP address that always means "this same machine" — no matter
which machine you're on. A request sent to `127.0.0.1` never leaves your computer; it's handled
entirely inside your own machine's networking stack.

**`localhost`.** A human-friendly name that means the same thing as `127.0.0.1`. Your computer
already knows, without asking any external service, that `localhost` means "me." `curl
http://localhost:8000/` and `curl http://127.0.0.1:8000/` reach the exact same place.

**Why this matters for development:** running a service on `localhost`/`127.0.0.1` means it's only
reachable from your own machine — nobody else on your network, let alone the internet, can reach
it. This is exactly what you want while developing and testing.

### Private and public IP addresses

**Private IP address.** An address only meaningful *within* a local network (like your home
Wi-Fi) — for example, `192.168.1.42`. Other devices on the same Wi-Fi can reach it; the wider
internet cannot, directly.

**Public IP address.** An address that identifies your network (often your home router) to the
wider internet.

**Why the distinction matters here:** `127.0.0.1` (this machine only) is the narrowest scope; a
private IP (this local network) is wider; a public IP (the internet) is widest. This lesson's
practical work stays entirely at the narrowest scope — you never need to expose a service beyond
your own machine to complete it.

### Ports, and why only one process normally listens on a port

**Port.** Simple meaning: a numbered "channel" on a machine that a specific program is listening
on. Technical meaning: a 16-bit number (0–65535) that, combined with an IP address, identifies a
specific communication endpoint on a machine, allowing the operating system to route incoming data
to the correct listening process.

**Why only one process can normally listen on a given port at a time:** when a process asks the
operating system to listen on a port, the OS reserves that exact (address, port) combination for
that process alone — this is precisely so that incoming data has one, unambiguous destination. If a
second process tries to listen on the same port, the OS refuses ("port already in use," Section
11) — not as an arbitrary restriction, but because allowing two listeners would make it impossible
to know which process should receive an incoming request.

**Common port numbers you'll see in development** (conventions, not hard rules): `8000` and `8080`
are common defaults for local development web servers; `5432` is PostgreSQL's conventional default;
`6379` is Redis's. None of these numbers are enforced by the operating system — they're just
widely-followed conventions so developers don't have to guess.

### DNS and URLs

**DNS (Domain Name System).** Simple meaning: the system that turns human-readable names (like
`example.com`) into IP addresses. Technical meaning: DNS is a distributed lookup system that
resolves a domain name to the IP address a client should actually connect to. **This lesson's
practical work never needs DNS** — `localhost` is resolved locally, without any lookup — but
understanding DNS's job matters because it's the same step every real networked request performs
before a client-server exchange (Section 1) can even begin.

**URL (Uniform Resource Locator).** A structured way of writing "how to reach a specific thing on a
specific server." Breaking down `http://localhost:8000/status`:

```text
http://        localhost      :8000      /status
   ↓                ↓            ↓           ↓
 scheme       host/address     port      path (which
(how to talk)  (which machine (which    resource on
               / DNS name)    listener)  that server)
```

- **scheme** — the protocol/rules the client and server will use to talk (`http` here).
- **host** — the machine to connect to; a DNS name (resolved via DNS) or a raw IP address, or
  `localhost` for "this machine."
- **port** — which listener on that machine (Section 5's port explanation).
- **path** — which specific resource or endpoint on the server you're asking for.

### "Process running" versus "service reachable"

This is the single most important distinction in this lesson, and the source of most local
networking confusion:

- **A process running** means the operating system has a live process for your program (Concept 03
  — [Processes](03-processes.md)) — you can see it with `ps` (Section 9).
- **A service being reachable** means that process has successfully bound to a port and is actively
  listening for connections on it — and nothing (a crash before it got that far, binding to the
  wrong port, a typo in the address) is preventing a client from reaching it.

A process can be running perfectly and still be unreachable — for example, if it crashed *after*
starting but *before* it finished setting up its listener, or if it's listening on a different port
than you're trying to reach. Section 11 walks through exactly how to tell these apart.

---

## 6. How It Works Internally

At a level appropriate for this lesson (full socket-programming detail is out of scope):

```text
1. A server process asks the operating system: "let me listen on port 8000."
2. The OS reserves that port for this process (Section 5's one-listener rule) and confirms.
3. The server process now waits, doing nothing, until a request arrives (Concept 05 — Scheduling
   — the OS doesn't waste CPU on a process that's just waiting for network input).
4. A client process asks the OS: "connect me to 127.0.0.1, port 8000."
5. The OS delivers that connection request to the listening server process.
6. The server reads the request, does its work, and sends a response back through the same
   connection.
7. The client receives the response and the connection is closed (or kept open, depending on the
   protocol).
```

**Why this matters:** every diagnostic question in Section 11 ("is it running," "is it listening,"
"is it reachable") maps directly onto one of these numbered steps — diagnosis is really just asking
"which of these steps actually happened?"

---

## 7. Real-World Example

**Scenario:** you start a tiny local web server, using nothing but Python's built-in tools (no
installation required), and talk to it with `curl`.

```bash
cd ~/practice-shell/networking-demo   # a dedicated practice folder — see Concept 08, Permissions,
                                        # and this module's Project 0.3 guide for why this matters
python3 -m http.server 8000
```

This starts a process that serves the files in the current directory over HTTP, listening on port
`8000`, on all local interfaces (including `127.0.0.1`). It will keep running, printing a line for
every request, until you stop it (Concept 10 — [Signals](10-signals.md) — Ctrl+C sends it
`SIGINT`).

In a **second** terminal window, while that's still running:

```bash
curl http://localhost:8000/
```

**Example output** (a typical response — the exact HTML will differ based on the files in your
folder):

```text
<!DOCTYPE HTML>
<html>
<head>
<title>Directory listing for /</title>
</head>
...
```

This confirms the full loop from Section 1: your `curl` client reached the server process, the
server responded, and you saw the response. Section 9 builds on this exact example to show how to
find the server's PID and its listening port independently of the server's own output.

---

## 8. Relationships to Other Concepts

```text
Processes (Concept 03)        ← a server is just a process
        ↓
Standard I/O (Concept 11)     ← contrast: printing to a terminal vs. responding over a network
        ↓
Signals (Concept 10)          ← how you stop a running server (Ctrl+C / SIGINT / SIGTERM)
        ↓
THIS LESSON: Local Networking  ← addresses, ports, client-server, reachability
        ↓
Process Lifecycle (Concept 14) ← a server's full run: start, listen, serve, stop, exit code
        ↓
Module 0.3 — Command Line       ← using curl and other CLI tools fluently
        ↓
Module 0.4 — Developer Environment → running a real local Python service
        ↓
Later roadmap stages:
  → Backend APIs and FastAPI        (a server you write, listening on a port, reached by curl or
                                      a browser exactly as in Section 7)
  → Docker                           (a container's process listens on a port *inside* the
                                      container; Docker maps that port to one on your host —
                                      the exact same "process + port + reachability" model,
                                      with one extra mapping step)
  → Model serving                    (a model-serving process is, mechanically, just another
                                      local server — the same PID/port/curl diagnostic steps apply)
  → Vector databases                 (commonly run as a local service on a fixed port, e.g. 6379-
                                      or 8000-style conventions, reached the same way)
  → AI agents calling tools/APIs     (a tool call is a client request to some server — local or
                                      remote — using this exact request/response shape)
```

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2, or in native Linux/macOS. No `sudo` is required anywhere in
this lesson, and every command below only inspects your own machine or talks to a process you
started yourself.

### Finding a listening port — Linux/WSL2

With the server from Section 7 still running in one terminal, run this in another:

```bash
ss -ltnp
```

- `ss` — a tool for inspecting sockets (network endpoints) on this machine.
- `-l` — show only **l**istening sockets (servers waiting for connections, not active connections).
- `-t` — show only **t**cp sockets (the connection type `curl`/HTTP use).
- `-n` — show **n**umeric addresses/ports (don't try to resolve names — faster, and avoids DNS,
  Section 5, entirely).
- `-p` — show the **p**rocess (PID and program name) that owns each listening socket. On some
  systems this flag requires elevated privileges to show the process name for sockets you don't
  own; for your own test server, it works without `sudo`.

**Example output:**

```text
State    Recv-Q   Send-Q     Local Address:Port      Peer Address:Port   Process
LISTEN   0        5              127.0.0.1:8000            0.0.0.0:*    users:(("python3",pid=4213,fd=3))
```

Reading this row: `LISTEN` confirms something is actively listening (not just running — Section
5's key distinction); `127.0.0.1:8000` is the address and port it's listening on; `pid=4213`
identifies the exact process — the same number `python3 -m http.server` would show if you checked
it with `ps` (Concept 03).

### Finding a listening port — PowerShell

```powershell
Get-NetTCPConnection -State Listen
```

- `Get-NetTCPConnection` — PowerShell's equivalent of inspecting network sockets on the machine.
- `-State Listen` — the equivalent of `ss`'s `-l` flag: show only listening sockets, not active
  connections.

**Example output (columns trimmed for readability):**

```text
LocalAddress   LocalPort  State    OwningProcess
127.0.0.1      8000       Listen   4213
```

`OwningProcess` here plays the same role as `ss -ltnp`'s `pid=` field — it's the process ID
actually holding that port. You can cross-reference it with `Get-Process -Id 4213` to see the
program name, the same way `ps -p 4213` would work on Linux.

### Verifying reachability with `curl`

```bash
curl -i http://localhost:8000/
```

- `curl` — a command-line tool that acts as a network client (Section 1): it sends a request and
  prints the response.
- `-i` — include the response's status line and headers in the output, not just the body — useful
  for seeing *whether* you got a real response, even before reading its content.

**Example output (headers shown, body truncated):**

```text
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/3.x
Date: ...
Content-type: text/html; charset=utf-8

<!DOCTYPE HTML>
...
```

`HTTP/1.0 200 OK` is the single most useful line here: it confirms the client reached a real,
responding server. Section 11 covers what you see instead when that's *not* true.

### Stopping the server safely

In the terminal running `python3 -m http.server 8000`, press **Ctrl+C**. This sends `SIGINT`
(Concept 10 — [Signals](10-signals.md)) to that process, and it exits. Confirm it's gone and the
port is free again:

```bash
ss -ltnp | grep 8000
```

No output means nothing is listening on port 8000 anymore — the port is free.

---

## 10. Common Misconceptions

- **"If my server process is running, it must be reachable."** False — see Section 5's core
  distinction. A process can be alive (visible in `ps`) while having crashed before binding its
  port, or while listening on a different port than you expect.
- **"`localhost` and my machine's real IP address are different things I need to manage
  separately."** For local development, they behave the same for reaching your own machine.
  `127.0.0.1`/`localhost` is simply the most restrictive, always-correct way to say "this machine."
- **"Any two programs can share a port if they're both mine."** No — see Section 5. Ownership
  doesn't matter; the operating system enforces one listener per (address, port) combination,
  regardless of who started which process.
- **"A port number tells you what kind of service is running."** No — port `8000` doesn't
  *require* an HTTP server; it's convention only. The only way to know what's really listening is
  to check, using Section 9's commands, not to assume from the number.
- **"DNS is required to reach `localhost`."** No — Section 5 explained `localhost` resolves locally,
  with no DNS lookup at all. DNS matters for real domain names, not for talking to your own
  machine.

---

## 11. Debugging and Troubleshooting

Each scenario follows this module's standard shape: symptom → what it actually means → how to
confirm → safe next step. Every command here only inspects state or stops a process you started and
identified yourself — never an arbitrary or unfamiliar PID.

### Scenario 1 — "Connection refused"

**Symptom:**

```bash
curl http://localhost:8000/
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**What it means:** your client reached your machine's networking stack just fine, but **nothing is
listening** on port 8000 right now. This is not a network problem — it's confirmation that step 3
in Section 6's internal flow never happened (or happened and then stopped).

**How to confirm:** run `ss -ltnp | grep 8000` (or `Get-NetTCPConnection -State Listen` and look
for port 8000). No matching row confirms nothing is listening.

**Safe next step:** start (or restart) the server you intended to reach, watch its own terminal
output for a startup error, and re-check with `ss -ltnp` before trying `curl` again.

### Scenario 2 — Wrong port

**Symptom:** `curl` to one port gives "connection refused," but the server is definitely running.

**What it means:** the server is listening on a *different* port than the one you're requesting —
for example, it started on `8080` while you're curling `8000`.

**How to confirm:** run `ss -ltnp` (no `grep` filter this time) and read every listening row to find
which port your process actually bound to. Cross-check the PID against the server's own process
(Concept 03's `ps` techniques).

**Safe next step:** update your `curl` command (or your client code) to use the port `ss -ltnp`
actually shows — never guess.

### Scenario 3 — Process not running at all

**Symptom:** "connection refused," and `ss -ltnp` shows nothing — *and* there's no server process
visible in `ps` either.

**What it means:** the server never started, or it started and crashed immediately (before or
during binding its port).

**How to confirm:** look at the terminal where you ran the server's start command — the error, if
any, will be printed there (a Python traceback, for example). This is exactly why Section 7's
example keeps the server's terminal visible in one window while you test from another.

**Safe next step:** read the error message from bottom to top (Module 0.4's traceback-reading
skill), fix the specific problem it names, and restart the server.

### Scenario 4 — "Port already in use"

**Symptom:**

```text
OSError: [Errno 98] Address already in use
```

**What it means:** exactly Section 5's one-listener rule — some process (possibly an earlier,
still-running copy of your own server) already holds that port.

**How to confirm:** run `ss -ltnp | grep <port>` and read the `pid=` value in the result — that is
the process currently holding the port.

**Safe next step:** confirm that PID is genuinely your own earlier test server (check the command
name shown by `ss -ltnp` or `ps -p <pid>`), then stop **that exact, confirmed PID** gracefully
(Concept 10 — send `SIGTERM`/Ctrl+C, not a forced kill, as a first attempt) before starting a new
one. **Never stop a PID you have not personally confirmed belongs to your own test process** — see
this module's Project 0.3 guide for the full safe procedure.

---

## 12. Exercises

Work through these in your dedicated practice directory (see Section 7 and this module's Project
0.3 guide). Use the workflow from Concept 14 and Stage 0 Gap 0F: state what you expect before you
run anything.

1. Start `python3 -m http.server 8000` in your practice folder. In a second terminal, use `curl -i`
   to confirm it's reachable, then use `ss -ltnp` (or `Get-NetTCPConnection`) to find its PID
   independently. Confirm both PIDs match.
2. Try starting a **second** `python3 -m http.server 8000` while the first is still running, in a
   third terminal. Read the exact error. Explain, in your own words, why it happened, using Section
   5's one-listener rule.
3. Stop the first server with Ctrl+C. Immediately try `curl` again and read the exact error message
   you get. Then run `ss -ltnp` again and confirm the port no longer appears.
4. Start the server on a different port, e.g. `python3 -m http.server 8080`, and deliberately
   `curl http://localhost:8000/` (the wrong port). Read the error, then fix your `curl` command
   using only what `ss -ltnp` tells you — not memory.
5. In one or two sentences each, write your own plain-language definitions of: client, server,
   port, `localhost`, and "reachable." Do not copy this lesson's wording — if you can't write it
   without looking, reread the relevant section first.

## 13. Expected Results

- **Exercise 1:** the PID printed by `ss -ltnp`/`Get-NetTCPConnection` matches the PID you'd find
  for the `python3 -m http.server` process via `ps`/`Get-Process`, confirming Section 5's technical
  explanation.
- **Exercise 2:** an `OSError: [Errno 98] Address already in use` (or the OS-equivalent message) —
  direct, hands-on evidence of Section 5's one-listener-per-port rule.
- **Exercise 3:** `curl` reports `Connection refused` — the port is confirmed genuinely free by
  `ss -ltnp` showing no matching row.
- **Exercise 4:** the first `curl` fails with `Connection refused` (Scenario 2); after correcting
  the port to `8080`, it succeeds.
- **Exercise 5:** your own explanations should closely match this lesson's Section 1 and Section 5
  content, but phrased in words you chose yourself.

## 14. Review Questions

1. What is the difference between a client and a server, in your own words?
2. Why does `curl http://localhost:8000/` never leave your own machine?
3. Why can't two processes both listen on port `8000` at the same time?
4. A process is visible in `ps`, but `curl` to its expected port says "connection refused." Give
   two different possible explanations, and how you'd tell them apart.
5. What does `ss -ltnp`'s `pid=` field (or `Get-NetTCPConnection`'s `OwningProcess`) actually tell
   you, and why is that more reliable than assuming from the port number alone?

## 15. Production Relevance

At this point, you understand the client-server model, addresses and ports, DNS and URLs at a basic
level, the crucial difference between a running process and a reachable service, and how to use
`curl` and `ss -ltnp`/`Get-NetTCPConnection` to diagnose a local service. You are **not** yet
expected to understand full networking (subnets, routing, firewalls, TLS/HTTPS internals) or
container networking in depth — those are later, more advanced topics.

For a production Applied AI Engineer, this lesson's mental model shows up constantly:

- **Local API development.** Every FastAPI or backend service you build starts exactly like Section
  7's example: a local process, a port, and `curl` (or a browser) as the client while you develop.
- **"Why can't my app reach the database/API/model server?"** is, overwhelmingly often in practice,
  answered by this lesson's Section 11 — process not running, wrong port, or port already in use —
  rather than by anything more exotic.
- **Docker port mapping** is this lesson's model plus one extra step: a container's internal port
  is mapped to a port on your host machine, but the underlying "is it listening, is it reachable"
  questions are identical.
- **Model-serving and vector-database processes** are, mechanically, ordinary local servers — the
  exact diagnostic steps in Section 9 and Section 11 apply directly, regardless of what the service
  actually does internally.
- **AI agents making tool or API calls** are client processes making requests in the same
  request/response shape this lesson's `curl` examples demonstrate — this lesson demystifies what a
  "tool call" or "API call" actually is at the network level.

**This lesson is one part of a much larger networking picture** — a foundational one, but not the
whole picture. **This lesson does not teach subnets, routing, firewalls, NAT, TLS/HTTPS internals,
load balancing, DNS server administration, IPv6 in depth, or container/cluster networking** — every
one of these is a genuinely important, more advanced topic, and every one of them is built directly
on top of the client-server, address, and port fundamentals this lesson just established.

**What comes next**, building directly on this lesson:

```text
Local Networking                 ← this lesson
  → Module 0.3 — Command Line       (fluency with curl and other CLI tools)
  → Module 0.4 — Developer Environment → running a real local Python service reproducibly
  → Backend APIs / FastAPI           (writing the server side of exactly this exchange)
  → Docker                            (the same model, plus port mapping between container
                                        and host)
  → Model serving / vector databases  (the same model, applied to AI-specific local services)
```

None of these are taught here — this section exists only to show where this lesson sits within the
larger roadmap you are building, one concept at a time.

---

## Key Terms

- **Client** — a process that initiates a request to a server and waits for a response.
- **Server** — a process that listens on a port and responds to incoming requests.
- **IP address** — a numeric address identifying a machine on a network.
- **`127.0.0.1`** — the reserved IP address that always means "this same machine."
- **`localhost`** — a human-friendly name for `127.0.0.1`.
- **Private IP address** — an address meaningful only within a local network (e.g., home Wi-Fi).
- **Public IP address** — an address that identifies a network to the wider internet.
- **Port** — a numbered endpoint (0–65535) that, with an IP address, identifies exactly which
  listening process on a machine should receive incoming data.
- **DNS (Domain Name System)** — the system that resolves human-readable domain names into IP
  addresses.
- **URL (Uniform Resource Locator)** — a structured address combining a scheme, host, port, and
  path to describe exactly how to reach a specific resource on a specific server.
- **Listening** — the state of a process that has successfully bound to a port and is waiting for
  incoming connections on it.
- **Reachable** — a service is reachable when a client can successfully connect to the port it is
  listening on; distinct from the underlying process simply being alive.
- **`curl`** — a command-line client tool used to send a network request and print the response.
- **`ss -ltnp`** — a Linux command that lists listening TCP sockets along with the PID of the
  process holding each one.
- **`Get-NetTCPConnection`** — the PowerShell equivalent for inspecting listening TCP connections
  and their owning process.

## Summary

A client sends a request; a server listens on a port and responds. `localhost`/`127.0.0.1` always
means "this machine," which is why local development never needs DNS or a public IP address. Only
one process can listen on a given port at a time — this is enforced by the operating system, not by
convention. A process being *alive* and a service being *reachable* are two different facts, and
almost every local networking problem you'll hit ("connection refused," a wrong port, a port
already in use) comes down to confusing the two. `curl` lets you act as a client to test
reachability directly; `ss -ltnp` (or `Get-NetTCPConnection` on PowerShell) lets you see, with
certainty, exactly which process is holding which port — replacing guesswork with evidence, exactly
as Stage 0's engineering-thinking practices require.

## Completion Checklist

- [ ] I can explain, without notes, what a client and a server are and how they exchange a request
      and a response.
- [ ] I can explain why `curl http://localhost:8000/` never leaves my own machine.
- [ ] I can explain, in my own words, why only one process can listen on a given port at a time.
- [ ] I can explain the difference between a process running and a service being reachable, with an
      example of each going wrong independently.
- [ ] I ran a local HTTP server, reached it with `curl`, and found its PID and port using
      `ss -ltnp` (or `Get-NetTCPConnection`) — not just by trusting the server's own printed output.
- [ ] I deliberately reproduced "connection refused," a wrong port, and "port already in use," and
      correctly diagnosed each one using this lesson's steps, not guesswork.
- [ ] I stopped my own test server gracefully and confirmed both the process and the port were
      gone.
- [ ] I completed Section 12's exercises and my answers match Section 13's expected results.
- [ ] I can answer Section 14's review questions aloud without reading from this file.

---

_This file is the completed lesson for Concept 16 of Module 0.2, extending Stage 0's original four
modules with Gap 0C from the Stage 0 roadmap. It intentionally does not teach subnets, routing,
firewalls, NAT, TLS/HTTPS internals, load balancing, DNS server administration, IPv6 in depth, raw
socket programming, or container/cluster networking — those remain the subject of later, more
advanced curriculum, not this beginner-level foundation. The hands-on diagnostic skills in this
lesson are practiced further and turned into a written incident report in
[`Projects/01-process-resource-and-port-diagnosis.md`](./Projects/01-process-resource-and-port-diagnosis.md)._
