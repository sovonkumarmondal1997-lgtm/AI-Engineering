# Concept 16 — Local Networking for Development

**Main objective:** Understand how two programs communicate over a network, even when both are running on your own computer. This lesson extends Operating System Fundamentals and introduces the networking knowledge needed for backend and AI development.

---

## 1. Client-server communication

- **Client:** A program that sends a request and waits for a response.
- **Server:** A program that listens for incoming requests and responds.

Example: When you run `curl http://localhost:8000/`, `curl` acts as the client and a server listening on port 8000 responds.

Networking allows separate processes to communicate, even without sharing memory.

---

## 2. IP addresses and localhost

Think of a computer as an apartment building:

- **IP address** = building address.
- **Port** = apartment number.
- **Listening process** = person waiting to answer the door.

Important addresses:

- `127.0.0.1`: IPv4 loopback address; means your own machine.
- `::1`: IPv6 loopback address.
- `localhost`: Hostname commonly resolved to `127.0.0.1`, `::1`, or both.

A service listening on loopback is accessible only from your own machine.

IP address types:

- **Private IP:** Used within a local network, such as home Wi-Fi.
- **Public IP:** Identifies your network to the wider internet.

---

## 3. Ports, DNS and URLs

**Port:** A number from 0–65535 that, together with an IP address and transport protocol, identifies a network endpoint.

Common development conventions:

- `8000`, `8080`: Web servers.
- `5432`: PostgreSQL.
- `6379`: Redis.

Normally, two processes cannot bind the same local address, protocol and port in the same way. The OS enforces this rule.

**DNS:** Converts human-readable domain names, such as `example.com`, into IP addresses. Localhost normally uses local name resolution instead of public DNS.

**URL:** Contains the information needed to reach a resource.

Example: `http://localhost:8000/status`

- **Scheme:** `http` — communication protocol.
- **Host:** `localhost` — machine.
- **Port:** `8000` — listener.
- **Path:** `/status` — requested resource.

---

## 4. Running process vs. reachable service

This is the most important lesson.

- **Process running:** The program exists as a live OS process.
- **Service reachable:** The process has successfully bound to a port, is listening and can accept connections.

A process can be running but unreachable because it uses the wrong port or has not successfully started its listener.

---

## 5. How communication works

1. Server requests permission from the OS to listen on a port.
2. OS binds the port to the server's socket.
3. Server waits for incoming requests.
4. Client requests a connection to the server's address and port.
5. OS delivers the connection to the server.
6. Server processes the request and returns a response.
7. Client receives the response.

---

## 6. Practical commands and tools

Start a local Python server:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Test it from another terminal:

```bash
curl -i http://localhost:8000/
```

Inspect listening ports on Linux/WSL2:

```bash
ss -ltnp
```

- `-l`: Listening sockets.
- `-t`: TCP sockets.
- `-n`: Numeric addresses and ports.
- `-p`: Owning process information.

PowerShell equivalent:

```powershell
Get-NetTCPConnection -State Listen
```

Stop the server using Ctrl+C (`SIGINT`).

**Important:** Python's `http.server` is for development, not production. Use a dedicated practice directory and bind to `127.0.0.1`.

---

## 7. Troubleshooting

| Problem | Meaning and diagnostic approach |
|---|---|
| Connection refused | Nothing is accepting connections at the target address and port. Check `ss -ltnp`. |
| Wrong port | Server listens elsewhere. Inspect listening ports and correct the client URL. |
| Process not running | Server never started or crashed. Check its terminal error. |
| Port already in use | Another process owns that binding. Identify its PID and verify its command before stopping it. |

Never terminate an unknown process.

---

## 8. Exercises and production relevance

The lesson includes:

- Five practical exercises covering server startup, reachability, duplicate ports, wrong ports and definitions.
- Five review questions.
- Expected results and a completion checklist.
- A production diagnostic workflow.

These concepts apply directly to FastAPI, backend APIs, Docker port mapping, model-serving services, vector databases and AI agents calling tools or APIs.

**Scope boundaries:** Subnets, routing, firewalls, NAT, TLS/HTTPS internals, load balancing, advanced DNS, IPv6 internals, socket programming and container/cluster networking are reserved for later topics.

---

## Final takeaway

A running process is not necessarily a reachable service. Use `curl` to test reachability and `ss -ltnp` or `Get-NetTCPConnection` to identify which process owns a listening port. Diagnose using evidence, not assumptions.
