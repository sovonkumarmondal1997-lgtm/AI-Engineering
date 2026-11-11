# Ports, Networks, and Service Discovery for Data Engineering

> **Gap Module G1 — Docker Essentials for Data Labs — Topic 03**

This module builds the networking mental model required to operate containerized Data Engineering services. It progresses from basic ports and `localhost` through Docker networks and service discovery to Kafka internal/external listeners and advertised listeners.

The goal is not to memorize Docker commands. The goal is to reason about **client location, service location, network membership, hostname resolution, port selection, connectivity, and readiness**.

## The Core Question

> **Where is my client, where is my service, what network are they on, what address should I use, and why?**

The primary troubleshooting sequence is:

```text
Client
 ↓
Where is the client?
 ↓
Where is the service?
 ↓
What network?
 ↓
What hostname?
 ↓
Does DNS resolve?
 ↓
What port?
 ↓
Is the port published?
 ↓
Can TCP connect?
 ↓
Is the application ready?
 ↓
For Kafka: what address is advertised?
```

## Scope

This is a **production-oriented Docker operator module for Data Engineering labs**. It focuses on ports, container networking, service discovery, host/container addressing, and Kafka listener architecture.

It does not teach Dockerfile authoring, image-building pipelines, Kubernetes, or the complete curricula of later G1 topics.

## 1. Learning Objectives

By the end of this module you should be able to answer:

> **Where is my client, where is my service, what network are they on, what address should I use, and why?**

You will be able to:

- Explain IP addresses, hostnames, ports, TCP, clients, servers, listening sockets, connections, `localhost`, and loopback.
- Distinguish a service's container port from a host-published port.
- Use `-p HOST_PORT:CONTAINER_PORT` correctly and diagnose port conflicts.
- Explain why `localhost` means something different inside a container.
- Create and use user-defined Docker networks.
- Use Docker DNS and container/service names for service discovery.
- Explain why container-to-container traffic normally uses the container port and does not require publishing.
- Explain host-to-container and container-to-host communication.
- Use `127.0.0.1` bindings for local-only exposure.
- Understand `host.docker.internal` and platform-specific considerations.
- Reason about Kafka listeners and advertised listeners for host and container clients.
- Diagnose networking failures layer by layer using `nslookup`, `nc`, `curl`, Docker network inspection, and service-readiness checks.
- Build and debug a local Data Engineering network architecture without changing multiple networking settings blindly.

## 2. Prerequisites

This module assumes the learner already understands:

**Stage 0 / Stage 1**
- Processes
- Ports
- `localhost`
- Basic networking
- Shell commands
- Client/server concepts

**Topic 01 — Containers, Images, and Registries**
- Containers
- Images
- `docker run`
- Container lifecycle

**Topic 02 — Running Databases and Services in Containers**
- PostgreSQL
- MinIO
- Redis
- Kafka
- Service readiness

Topic 03 now explains how those services communicate across Docker networking boundaries.

### The central question

Every networking problem should begin with:

```text
WHO IS THE CLIENT?
        ↓
WHERE IS THE CLIENT?
        ↓
WHERE IS THE SERVICE?
        ↓
WHAT NETWORK ARE THEY ON?
        ↓
WHAT ADDRESS SHOULD THE CLIENT USE?
        ↓
IS THAT PORT PUBLISHED?
        ↓
IS DNS AVAILABLE?
```

## 3. Connection to Topics 01 and 02

Topic 01 taught what a container is and how to run one. Topic 02 taught how to run PostgreSQL, MinIO, Redis, and Kafka as services and how to think about readiness.

Topic 03 adds the missing communication model:

```text
Topic 01
Containers + Images + Lifecycle
          ↓
Topic 02
Databases + Services + Readiness
          ↓
Topic 03
Ports + Networks + Service Discovery
          ↓
Client can reach the correct service for the correct reason
```

The boundary is intentional:

- Topic 03 focuses on **where traffic goes and how clients find services**.
- Persistence belongs to Topic 04.
- Configuration and secrets belong to Topic 05.
- General troubleshooting belongs to Topic 06; this module includes only the networking diagnostics required to reason about connectivity.
- Docker Compose is introduced only at awareness level; detailed Compose work belongs to Topic 07.
- Full platform differences belong to Topic 10; this module covers only networking-relevant differences.

## 4. Networking Fundamentals

Docker networking becomes much easier when the basic client/server model is clear.

A service exposes a listening socket:

```text
Client
  |
  | TCP connection
  v
IP Address : Port
  |
  v
Server
```

### IP address

An IP address identifies a network endpoint. In a Docker lab, a container can have an IP address on a Docker network.

### Hostname

A hostname is a human-readable name that can be resolved to an IP address. Docker's user-defined networks provide DNS-based name resolution for connected containers.

### Port

A port identifies a transport endpoint associated with a service. Common Data Engineering service ports include:

| Service | Typical service port |
|---|---:|
| PostgreSQL | 5432 |
| Redis | 6379 |
| Kafka | 9092 |
| MinIO API | 9000 |

### Protocol and TCP

TCP provides a reliable connection-oriented transport. For this module, think in layers:

```text
Name
 ↓
IP
 ↓
TCP port
 ↓
Application protocol
 ↓
Service readiness
```

### Client and server

The client initiates a connection. The server/service listens for connections.

### `localhost` and loopback

`localhost` normally resolves to the local loopback context, commonly `127.0.0.1`.

The critical Docker rule is:

```text
Host localhost
    ≠
Container localhost
```

A host process using `localhost` refers to the host's own network context. A process inside a container using `localhost` refers to that container's own network context.

This single distinction explains a large percentage of beginner Docker networking failures.

## 5. Ports

A port is a transport-layer endpoint used by a service.

In a Data Engineering lab:

```text
PostgreSQL → 5432
Redis      → 6379
Kafka      → 9092
MinIO API  → 9000
```

There are several related terms:

- **Service port:** the port on which the application expects to receive traffic.
- **Container port:** the port exposed/listened to inside the container's network context.
- **Host port:** a port on the host that Docker publishes for host-side access.
- **Listening port:** the endpoint on which a process is actually listening.

A container port and host port are **not automatically the same thing**.

For example:

```text
Host port:       5433
Container port:  5432
Application:     PostgreSQL
```

The application remains a PostgreSQL service listening on `5432` inside the container even though a host client reaches it through `5433`.

## 6. Port Publishing

Port publishing connects a host-side endpoint to a container-side endpoint.

The basic syntax is:

```bash
-p HOST_PORT:CONTAINER_PORT
```

Example:

```bash
docker run -d   --name pg-lab   -p 5432:5432   postgres:16
```

Conceptually:

```text
Host
localhost:5432
      |
      | Docker port publishing
      v
Container
:5432
      |
      v
PostgreSQL
```

The important question is not merely "what port did I type?" but:

> Which client is connecting from where?

A host client can use the published host port. A container on the same user-defined network normally does not need to go through that host-published path.

## 7. Host Ports vs Container Ports

Consider:

```bash
docker run -d   --name pg-lab   -p 5433:5432   postgres:16
```

The mapping is:

```text
Host
localhost:5433
      |
      v
Container
5432
      |
      v
PostgreSQL
```

Therefore:

- Host Python/`psql` → `localhost:5433`
- Another container on the same Docker network → `pg-lab:5432`

The internal PostgreSQL port did not become `5433`. Only the host-side published endpoint changed.

### Rule

> **Host → Container uses the published host port. Container → Container uses the service's container port.**

Do not substitute the host port when talking directly to a service over the Docker network.

## 8. Port Conflicts

A host port can normally be bound by only one listener at a time.

A common failure looks like:

```text
Host PostgreSQL already uses 5432
        ↓
Docker tries to publish 5432
        ↓
Port conflict
```

This can happen with:

```bash
docker run -d   --name another-pg   -p 5432:5432   postgres:16
```

If `5432` is already occupied, choose another host port:

```bash
docker run -d   --name another-pg   -p 5433:5432   postgres:16
```

Nothing about PostgreSQL's internal port changed. The host simply reaches this container through `5433`.

### Diagnostic principle

A port conflict is a **host binding problem**, not necessarily an application configuration problem. First identify which side owns the conflicting port.

## 9. The Critical Meaning of `localhost`

This is the most important mental model in the module.

### From the host

```text
Host process
    |
localhost:5433
    |
published port
    |
PostgreSQL container
```

Here, `localhost` means the host's loopback context.

### From inside a container

```text
Python container
    |
localhost:5432
    |
Python container itself
```

It does **not** mean:

- the host machine;
- PostgreSQL in another container;
- every container on the Docker network.

Therefore:

> **`localhost` inside a Python container does not mean the host machine and does not mean another container.**

This is why a Python container trying `localhost:5432` will fail when PostgreSQL is running in a separate container.

### Hands-on proof

1. Start PostgreSQL.
2. Start a Python container.
3. Enter the Python container.
4. Try to connect to `localhost:5432`.
5. Observe that the connection does not reach PostgreSQL.
6. Put both containers on the same user-defined network.
7. Retry using the PostgreSQL service/container name and container port.

The objective is to understand **why** the first attempt failed, not to memorize a replacement hostname.

## 10. User-Defined Docker Networks

A Docker network provides a communication boundary in which connected containers can communicate.

Create a named network:

```bash
docker network create datalab
```

Run PostgreSQL on it:

```bash
docker run -d   --name postgres   --network datalab   postgres:16
```

Run a temporary Python client on the same network:

```bash
docker run --rm -it   --network datalab   python:3.12-slim
```

The important properties are:

- both containers are attached to `datalab`;
- the network provides connectivity between them;
- the user-defined bridge provides Docker DNS/service discovery;
- the Python client can address PostgreSQL by its container/service name;
- no host port publication is required for the container-to-container path.

### Why named networks are preferred in labs

A named network makes the architecture explicit:

```text
Docker network: datalab
    |
    +-- postgres
    +-- python
    +-- redis
    +-- kafka
```

It also makes diagnosis easier because you can inspect the network directly.

## 11. Container DNS and Service Discovery

Within a user-defined Docker network, Docker provides DNS-based discovery for connected containers.

The conceptual path is:

```text
Container Name
      ↓
Docker DNS
      ↓
Container IP
```

For example:

```text
postgres:5432
```

instead of:

```text
localhost:5432
```

The name `postgres` is a service identifier from the client's point of view.

### Why this is useful

Container IP addresses can change when containers are recreated. A service name provides a stable logical address within the lab network.

The application can therefore use:

```text
postgres:5432
redis:6379
kafka:9092
minio:9000
```

rather than hard-coding container IP addresses.

### Important boundary

Docker DNS answers the naming question:

> "What IP is associated with this service/container name?"

It does not prove that:

- the service is ready;
- the port is listening;
- the application protocol is healthy.

Those are separate checks.

## 12. Container-to-Container Communication

The normal internal Data Engineering path is:

```text
Python container
       |
       | postgres:5432
       v
PostgreSQL container
```

For this to work:

1. both containers must share a network;
2. the hostname must resolve;
3. the client must use the PostgreSQL container/service port;
4. PostgreSQL must be listening and ready.

No host port publication is required for this path.

A typical Python connection target is conceptually:

```python
host = "postgres"
port = 5432
```

not:

```python
host = "localhost"
port = 5433
```

The second form describes a host-side path, not the direct Docker-network path.

## 13. Published Ports vs Internal Ports

Compare the two paths.

### Host → Container

```text
Host
localhost:5433
      |
      | published host port
      v
Container:5432
      |
      v
PostgreSQL
```

### Container → Container

```text
Python
  |
  | postgres:5432
  v
PostgreSQL
```

The key rule is:

> **Container-to-container communication uses the service's container port, not the published host port.**

Publishing exists primarily to make a container service reachable through the host-side interface.

If only other containers need PostgreSQL, publishing `5432` to the host may be unnecessary.

## 14. Default Bridge vs User-Defined Bridge

Docker commonly provides a default `bridge` network, but user-defined bridge networks are the preferred pattern for structured labs.

| Characteristic | Default bridge | User-defined bridge |
|---|---|---|
| Basic container connectivity | Yes | Yes |
| Explicit named network | No, unless configured | Yes |
| Convenient service discovery | More limited/legacy behavior | Yes, Docker DNS |
| Isolation by named lab | Less explicit | Stronger and clearer |
| Recommended for multi-service labs | No | Yes |

For this roadmap, prefer:

```bash
docker network create datalab
```

and explicitly attach related services.

The goal is not to memorize Docker networking internals. The goal is to build predictable, inspectable service-to-service communication.

## 15. Docker Compose Network Awareness

Docker Compose normally creates a project-specific network for a Compose application.

Conceptually:

```text
Compose project
      ↓
Project network
      ↓
service names
```

A multi-service project might therefore communicate using:

```text
postgres:5432
redis:6379
kafka:9092
```

The important Topic 03 takeaway is:

> **Compose services communicate through a project network and service names.**

Detailed Compose authoring, lifecycle, and orchestration belong to Topic 07. Here, only the network model matters.

## 16. Host-to-Container Communication

The host reaches a container through a published port:

```text
Host
  |
  | localhost:5433
  v
Published port
  |
  v
Container:5432
```

For example:

```bash
docker run -d   --name pg-lab   -p 127.0.0.1:5433:5432   postgres:16
```

A host-side client can use:

```text
127.0.0.1:5433
```

or:

```text
localhost:5433
```

The host uses the **published host port**, not the container port directly.

## 17. Container-to-Host Communication

The reverse path is different:

```text
Container
   |
   v
Host service
```

A process inside a container cannot normally reach a host service by simply using:

```text
localhost
```

because `localhost` points back to the container.

Docker environments may provide:

```text
host.docker.internal
```

as a special hostname for reaching the host from a container.

The exact behavior depends on the platform and Docker environment, so treat this as an environment-specific capability rather than a universal networking law.

## 18. `host.docker.internal`

Use `host.docker.internal` when a container needs to reach a service running on the host and the environment supports that name.

Conceptually:

```text
Python container
       |
       | host.docker.internal
       v
Host machine
       |
       v
Host service
```

### Why `localhost` is wrong

Inside the Python container:

```text
localhost
```

means the Python container itself.

`host.docker.internal` expresses the different intent:

> "Reach the host from this container."

### Platform considerations

Docker Desktop environments commonly provide this behavior. Linux setups can differ depending on Docker configuration and version. Windows + WSL2 and macOS also have platform-specific networking layers.

Therefore:

- check the environment's documentation;
- verify name resolution and connectivity;
- do not assume every Docker runtime behaves identically.

Full platform curriculum belongs to Topic 10.

## 19. Localhost Binding and Local-Only Exposure

When a local Data Engineering service should be reachable only from the host, bind the published port to loopback:

```bash
-p 127.0.0.1:5432:5432
```

Compare:

```bash
-p 5432:5432
```

with:

```bash
-p 127.0.0.1:5432:5432
```

The second explicitly says that the published endpoint should bind to the host's loopback interface.

For a local lab this helps avoid unnecessarily exposing the service through the host's LAN-facing interfaces.

Typical examples:

```bash
docker run -d   --name pg-lab   -p 127.0.0.1:5433:5432   postgres:16
```

and similarly for a local MinIO API or other lab service.

This is a useful exposure-control practice, but it should not be treated as a complete security boundary. Authentication, host firewall policy, service configuration, and other controls still matter.

## 20. Kafka Networking Fundamentals

Kafka networking is more subtle than a simple request/response database connection because Kafka clients can receive broker addresses and then establish additional connections using those addresses.

Conceptually:

```text
Client
  ↓
Kafka bootstrap address
  ↓
Kafka
  ↓
Broker metadata/address
  ↓
Client connects to advertised broker address
```

This means a Kafka configuration can appear to work during the first connection and still fail afterward.

The central Kafka networking question is:

> **Can the client reach the address Kafka tells it to use from the client's own network context?**

That is why Kafka networking must be reasoned about in terms of **listeners** and **advertised listeners**.

## 21. Kafka Listeners

A Kafka listener describes where Kafka accepts connections.

A useful conceptual model is:

```text
Kafka
 ├── INTERNAL listener
 │       ↓
 │   container clients
 │
 └── EXTERNAL listener
         ↓
     host clients
```

A listener has concepts such as:

- listener name;
- address/host;
- port;
- protocol/security mapping.

For a local lab, a common conceptual arrangement is:

```text
INTERNAL://kafka:9092
EXTERNAL://localhost:9094
```

The exact configuration syntax depends on the Kafka distribution/image and version. The important part is understanding the network paths rather than copying a configuration without understanding it.

## 22. Kafka Advertised Listeners

A listener answers:

> **Where is Kafka listening?**

An advertised listener answers:

> **What address should Kafka tell clients to use?**

The difference is critical.

```text
Client
  ↓
Bootstrap address
  ↓
Kafka
  ↓
Kafka advertises broker address
  ↓
Client connects to advertised address
```

If Kafka advertises:

```text
kafka:9092
```

to a host client that cannot resolve or reach `kafka`, the client can fail even if the initial bootstrap connection succeeded.

Similarly, if Kafka advertises:

```text
localhost:9094
```

to a container client, `localhost` may point to the container itself rather than the Kafka broker.

### Core rule

> **Advertised addresses must be reachable from the network context of the client receiving them.**

## 23. Host and Container Kafka Clients

Consider two clients:

```text
Host Python client
        ↓
      Kafka

Container Python client
        ↓
      Kafka
```

They may require different addresses.

For example:

```text
Host client:
localhost:9094

Container client:
kafka:9092
```

The host can use a published external listener. The container can use Docker DNS and the internal listener.

This is why a single address is often insufficient for a local lab containing both host and container clients.

## 24. Two-Listener Kafka Architecture

A common conceptual two-listener architecture is:

```text
Kafka
 ├── INTERNAL://kafka:9092
 └── EXTERNAL://localhost:9094
```

The intended paths are:

```text
Host client
    ↓
localhost:9094
    ↓
Kafka EXTERNAL listener
```

and:

```text
Container client
    ↓
kafka:9092
    ↓
Kafka INTERNAL listener
```

### Why this works

- `kafka` is meaningful inside the Docker network because Docker DNS resolves it.
- `localhost` from a host process refers to the host.
- `localhost` from a container refers to that container.
- The external host port must be published.
- The internal path can use the Kafka container port directly.

### Important implementation note

Kafka images and distributions differ in exact environment variables and configuration syntax. Treat the listener names and addresses above as the architectural model. When implementing the lab, verify the image's current configuration requirements.

## 25. Reproducing the Kafka Listener Failure

The goal is to understand the failure rather than memorize a fixed configuration.

### Controlled failure exercise

1. Start Kafka with an incorrect advertised address.
2. Connect from a host client.
3. Observe that bootstrap may succeed while subsequent communication fails.
4. Connect from a container client.
5. Identify which advertised address each client receives.
6. Inspect the listener configuration.
7. Determine whether the advertised hostname and port are reachable from that client.
8. Correct the advertised listener.
9. Verify both host and container clients.

### Failure reasoning

```text
Bootstrap succeeds
      ↓
Kafka returns broker metadata
      ↓
Advertised address is unreachable
      ↓
Client fails on subsequent connection
```

The important lesson is:

> **A successful initial connection does not prove that Kafka's advertised topology is reachable.**

## 26. Network Inspection and Diagnostics

Do not guess the Docker network topology. Inspect it.

List networks:

```bash
docker network ls
```

Inspect a named network:

```bash
docker network inspect datalab
```

Network inspection can reveal:

- connected containers;
- subnet;
- gateway;
- container IP addresses;
- network configuration.

Also inspect the container when needed:

```bash
docker inspect postgres
```

The professional habit is:

> **Inspect the network state before changing configuration.**

## 27. Temporary Troubleshooting Containers

A temporary diagnostic container is a powerful way to test connectivity from the same network context as the application.

Conceptually:

```text
Broken client
     ↓
Temporary diagnostic container
     ↓
Same Docker network
     ↓
Test service
```

For example, start a small troubleshooting container on `datalab` and test:

```text
postgres:5432
redis:6379
kafka:9092
minio:9000
```

This separates a networking problem from problems caused by the application's own dependencies, libraries, or configuration.

The principle is:

> **Test from the same network location as the failing client.**

## 28. `nc`, `curl`, and `nslookup`

Use the diagnostic tool that matches the layer you want to test.

### `nslookup` — name resolution

```bash
nslookup postgres
nslookup kafka
```

Question answered:

> **Can this client resolve the service name to an IP address?**

### `nc` — TCP reachability

```bash
nc -vz postgres 5432
```

Questions answered:

- Does the name resolve?
- Can I establish TCP connectivity?
- Is the target port reachable?

A successful TCP connection does **not** prove that the application protocol is healthy.

### `curl` — HTTP/application endpoint

For an HTTP service such as MinIO:

```bash
curl http://minio:9000/
```

or use the appropriate health endpoint supported by the service/version.

This tests progressively:

```text
DNS
 ↓
TCP
 ↓
HTTP
 ↓
Application response
```

## 29. Layered Network Troubleshooting

Use this sequence professionally:

```text
1. Where is the client?
2. Where is the service?
3. Are they on the same network?
4. What hostname is being used?
5. Does DNS resolve?
6. What port is the service listening on?
7. Is the port published?
8. Is the client using the host port or container port?
9. Is the service actually ready?
10. For Kafka: what address is advertised?
```

Think in layers:

```text
DNS
 ↓
TCP
 ↓
Application protocol
 ↓
Service readiness
```

### Example diagnosis

If:

```bash
nslookup postgres
```

fails, investigate naming/network membership before changing PostgreSQL.

If `nslookup` succeeds but:

```bash
nc -vz postgres 5432
```

fails, investigate TCP reachability, listening state, port selection, or network placement.

If `nc` succeeds but the application fails, investigate application protocol, credentials, client configuration, or readiness rather than assuming Docker networking is broken.

This module intentionally teaches networking reasoning; general container troubleshooting is expanded in Topic 06.

## 30. Host Networking Mode

Docker can also use:

```bash
--network host
```

Host networking changes the normal container-network model by making the container use the host's network stack more directly.

It can simplify some networking scenarios, but it also changes isolation and port behavior.

Be aware of:

- how host networking differs from bridge networking;
- why it can remove some port-mapping steps;
- platform-specific support and limitations;
- why it should not be the default approach for these labs.

The learning objective is awareness, not a deep dive into host networking internals.

## 31. Platform Networking Differences

Networking behavior can differ across:

- Linux;
- Docker Desktop;
- Windows + WSL2;
- macOS;
- Apple Silicon environments where relevant.

For this module, focus only on:

- `host.docker.internal`;
- localhost forwarding;
- host-networking support;
- networking behavior differences.

Do not assume that a command demonstrated on one Docker environment behaves identically everywhere.

A good operator verifies the runtime:

```text
Which Docker environment am I using?
What networking mode is active?
What host-to-container behavior does this platform provide?
```

Full platform-specific curriculum belongs to Topic 10.

## 32. Hands-On Lab — `docker_lab/03`

Create a lab directory:

```text
docker_lab/
└── 03/
    ├── README.md
    └── notes.md
```

The lab should document the topology, commands, observations, failures, fixes, and verification evidence.

### Exercise 1 — Port Conflict

Start PostgreSQL on host port `5432` while another process is already using it.

Observe the failure.

Then publish:

```text
5433:5432
```

Explain why the second mapping works without changing PostgreSQL's internal port.

### Exercise 2 — User-Defined Network

Create:

```bash
docker network create datalab
```

Run PostgreSQL and a Python client on the network.

Connect using:

```text
postgres:5432
```

### Exercise 3 — Prove `localhost` Is Container-Local

From the Python container, try:

```text
localhost:5432
```

When PostgreSQL is a separate container, this should not reach PostgreSQL.

Document the exact network-context reason.

### Exercise 4 — Service Discovery

From the Python container:

```bash
nslookup postgres
nc -vz postgres 5432
```

Explain:

- what `nslookup` proves;
- what `nc` proves;
- what neither command proves.

### Exercise 5 — Kafka Listener Failure

Create a Kafka setup in which:

- the host client can bootstrap;
- Kafka advertises an unreachable address.

Observe and diagnose the later failure.

### Exercise 6 — Two Kafka Listeners

Implement the conceptual:

```text
INTERNAL
EXTERNAL
```

and verify:

```text
Host client      → external listener
Container client → internal listener
```

Use the current Kafka image/distribution documentation for the exact configuration syntax.

### Exercise 7 — Localhost Binding

Run PostgreSQL or MinIO with:

```text
127.0.0.1
```

binding.

Explain what exposure changes compared with an unspecified host-interface binding.

### Exercise 8 — Host Service From Container

Run a simple service on the host.

Where supported, access it from a container through:

```text
host.docker.internal
```

Document platform-specific behavior and verification evidence.

## 33. Break/Fix Network Drills

For every drill, use:

```text
Symptom
  ↓
Evidence
  ↓
Root cause
  ↓
Fix
  ↓
Verification
```

### Failure 1 — Wrong host port

The client uses `localhost:5432`, but PostgreSQL is published as `5433:5432`.

### Failure 2 — Wrong container port

A container client uses the published host port instead of PostgreSQL's container port.

### Failure 3 — `localhost` inside a container

A Python container tries to reach PostgreSQL at `localhost:5432`.

### Failure 4 — Different Docker networks

The client and service are attached to different user-defined networks.

### Failure 5 — Wrong container hostname

The client uses `postgres-db`, while the actual service name is `postgres`.

### Failure 6 — DNS cannot resolve

Run `nslookup` and determine why the service name cannot be resolved.

### Failure 7 — DNS works but TCP fails

`nslookup` succeeds but `nc -vz postgres 5432` fails.

Determine whether the service is listening, whether the port is correct, and whether network placement is correct.

### Failure 8 — Kafka unreachable hostname

Kafka advertises a hostname that the client cannot resolve.

### Failure 9 — Kafka wrong port

Kafka advertises a port that is not reachable from the client's network context.

### Failure 10 — Reachable but not ready

The network path works, but the service is not yet ready to serve application traffic.

The goal of every drill is to identify the failing layer rather than randomly changing settings.

## 34. Real-World Data Engineering Scenarios

### Scenario 1 — Python on host → PostgreSQL container

If PostgreSQL is published as:

```text
5433:5432
```

the host Python client should use:

```text
localhost:5433
```

because the client is on the host.

### Scenario 2 — Python container → PostgreSQL container

The Python container should not use `localhost` because that refers to itself.

Use:

```text
postgres:5432
```

when both containers share the appropriate user-defined network.

### Scenario 3 — Python container → PostgreSQL on another network

DNS/service discovery fails because the client does not have the same network context as the service.

Verify:

```bash
docker network inspect datalab
```

and inspect the connected containers.

### Scenario 4 — Host client → Kafka container

Kafka may accept the initial bootstrap connection and then fail if its advertised listener points to an address unreachable from the host client.

Expected concept:

> **Advertised listeners.**

### Scenario 5 — Container client → Kafka

`localhost:9092` may fail because `localhost` refers to the client container rather than Kafka.

Use the Kafka service name and internal listener where appropriate.

### Scenario 6 — PostgreSQL works from host but not from another container

Diagnose:

```text
Where is the working client?
Where is the failing client?
Same network?
Hostname?
DNS?
Container port?
TCP?
Readiness?
```

Do not assume that host success proves internal Docker connectivity.

### Scenario 7 — `nslookup` succeeds but `nc` fails

DNS is working. Investigate the TCP/listening/network layer.

### Scenario 8 — `nc` succeeds but the application fails

TCP reachability exists, but the application protocol or readiness layer may be failing. Check application-specific behavior rather than changing Docker DNS.

## 35. Data Engineering Network Architecture

A complete local Data Engineering topology can look like:

```text
                         HOST MACHINE
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  Host Python Client                                      │
│       │                                                  │
│       │ localhost:5433                                   │
│       ▼                                                  │
│  Docker Port Publishing                                  │
│       │                                                  │
│       ▼                                                  │
│  ┌───────────────────────────────────────────────────┐   │
│  │ Docker Network: datalab                           │   │
│  │                                                   │   │
│  │ PostgreSQL      MinIO        Kafka                │   │
│  │ :5432           :9000        :9092                │   │
│  │                                                   │   │
│  │ Python container ──► postgres:5432                │   │
│  │                   ──► kafka:9092                  │   │
│  │                   ──► minio:9000                  │   │
│  └───────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Path 1 — Host → PostgreSQL

```text
Host Python
    ↓
localhost:5433
    ↓
published port
    ↓
PostgreSQL:5432
```

### Path 2 — Container → PostgreSQL

```text
Python container
    ↓
postgres:5432
    ↓
Docker DNS
    ↓
PostgreSQL container
```

### Path 3 — Container → MinIO

```text
Python container
    ↓
minio:9000
    ↓
Docker DNS
    ↓
MinIO container
```

### Path 4 — Host → Kafka

```text
Host client
    ↓
localhost:9094
    ↓
EXTERNAL listener
    ↓
Kafka
```

### Path 5 — Container → Kafka

```text
Container client
    ↓
kafka:9092
    ↓
INTERNAL listener
    ↓
Kafka
```

For every path label:

- client location;
- service location;
- network;
- hostname/address;
- port;
- published port, if any;
- internal port;
- protocol;
- readiness requirement.

## 36. Mental Models

Keep these rules available during every Docker networking lab.

### Mental Model 1

```text
Host localhost
    ≠
Container localhost
```

### Mental Model 2

```text
Host → Container
uses
published host port
```

### Mental Model 3

```text
Container → Container
uses
service/container name + container port
```

### Mental Model 4

```text
DNS
    answers:
"What IP is this service name?"
```

### Mental Model 5

```text
nc
    answers:
"Can I establish TCP connectivity?"
```

### Mental Model 6

```text
curl
    answers:
"Can I communicate with this HTTP endpoint?"
```

### Mental Model 7

```text
Kafka listener
    =
where Kafka listens
```

### Mental Model 8

```text
Kafka advertised listener
    =
address Kafka tells clients to use
```

### Master mental model

```text
Client
 ↓
Where is the client?
 ↓
Where is the service?
 ↓
What network?
 ↓
What hostname?
 ↓
Does DNS resolve?
 ↓
What port?
 ↓
Is the port published?
 ↓
Can TCP connect?
 ↓
Is the application ready?
 ↓
For Kafka: what address is advertised?
```

## 37. Command Reference

### Port publishing

```bash
docker run -p HOST_PORT:CONTAINER_PORT ...
```

**Purpose:** publish a container service through a host port.

**Example:**

```bash
docker run -d --name pg-lab -p 5433:5432 postgres:16
```

**Observe:** host port `5433` maps to PostgreSQL's container port `5432`.

**Data Engineering use:** host-side development tools connecting to containerized databases.

### Network creation

```bash
docker network create datalab
```

**Purpose:** create a named user-defined network.

**Observe:** `datalab` appears in `docker network ls`.

### Network listing

```bash
docker network ls
```

**Purpose:** see available Docker networks.

### Network inspection

```bash
docker network inspect datalab
```

**Purpose:** inspect connected containers, addressing, subnet, gateway, and configuration.

### Connect a running container to a network

```bash
docker network connect datalab my-container
```

**Purpose:** attach a running container to an additional network.

### Disconnect

```bash
docker network disconnect datalab my-container
```

**Purpose:** detach a container from a network.

### Remove network

```bash
docker network rm datalab
```

**Purpose:** remove an unused network.

### Container status

```bash
docker ps
```

**Purpose:** identify running containers and published ports.

### Container inspection

```bash
docker inspect postgres
```

**Purpose:** inspect container configuration and network attachments.

### DNS test

```bash
nslookup postgres
```

**Purpose:** test service-name resolution.

### TCP test

```bash
nc -vz postgres 5432
```

**Purpose:** test TCP reachability to the service port.

### HTTP test

```bash
curl http://minio:9000/
```

**Purpose:** test an HTTP endpoint after DNS/TCP connectivity.

For every diagnostic command, interpret the result in terms of the failing layer rather than treating the command as a generic "fix".

## 38. Common Mistakes

### Mistake: using `localhost` inside containers

**Why it happens:** people treat `localhost` as a synonym for "the Docker machine."

**Mental model:** `localhost` is local to the client's network context.

**Correct approach:** use the service/container name on a shared user-defined network.

### Mistake: confusing host and container ports

**Why it happens:** mappings such as `5433:5432` look like a single port.

**Mental model:** the left side is the host; the right side is the container.

**Correct approach:** host client uses `5433`; internal container client uses `5432`.

### Mistake: publishing every port

**Why it happens:** publishing feels like the universal way to make services accessible.

**Mental model:** containers on the same network can communicate internally without host publishing.

**Correct approach:** publish only when a host/external client needs that path.

### Mistake: relying on the default bridge without understanding it

**Why it happens:** Docker creates a default network automatically.

**Mental model:** explicit user-defined networks provide a clearer service-discovery boundary.

**Correct approach:** create named networks for multi-service labs.

### Mistake: forgetting shared network membership

**Why it happens:** containers exist but are isolated from one another.

**Correct approach:** inspect `docker network inspect datalab`.

### Mistake: wrong service name

**Why it happens:** the hostname does not match the container/service name available on the network.

**Correct approach:** inspect the network and verify DNS.

### Mistake: confusing DNS with TCP

**Why it happens:** "cannot connect" is treated as one failure.

**Correct approach:** use `nslookup` first, then `nc`.

### Mistake: assuming DNS success means service success

**Correct approach:** DNS only proves name resolution.

### Mistake: assuming TCP success means readiness

**Correct approach:** verify application-level readiness.

### Mistake: misunderstanding `host.docker.internal`

**Correct approach:** treat it as an environment-specific host-reachability mechanism and verify support.

### Mistake: incorrect Kafka advertised listeners

**Correct approach:** reason about the address from the client's network context.

### Mistake: using one Kafka listener for incompatible client locations

**Correct approach:** use internal/external listener architecture when the topology requires it.

### Mistake: exposing services unnecessarily to the LAN

**Correct approach:** for local-only labs, prefer explicit `127.0.0.1` binding when appropriate.

### Mistake: assuming host networking is identical across platforms

**Correct approach:** verify runtime/platform support.

## 39. Practice Questions

## Beginner

### 1. What is a port?

**Answer:** A transport endpoint used by a service to receive traffic.

**Explanation:** The application listens on a port associated with its network endpoint.

**Example:** PostgreSQL commonly listens on `5432`.

### 2. What is `localhost`?

**Answer:** The local loopback context of the client.

**Explanation:** From a container, it refers to that container; from the host, it refers to the host.

**Example:** `localhost:5432` inside a Python container does not mean PostgreSQL in another container.

### 3. What is port publishing?

**Answer:** Mapping a host port to a container port.

**Example:**

```bash
-p 5433:5432
```

### 4. What does `-p 5433:5432` mean?

**Answer:** Host port `5433` is published to container port `5432`.

**Example:** Host Python uses `localhost:5433`.

### 5. What is a Docker network?

**Answer:** A communication boundary through which containers can communicate.

**Example:** `datalab` connects Python, PostgreSQL, Kafka, and MinIO.

## Intermediate

### 6. Why does localhost behave differently inside a container?

**Answer:** Because the container has its own network context.

**Example:** Python container → `localhost:5432` points to Python container itself.

### 7. Why can containers communicate without publishing ports?

**Answer:** Containers on the same user-defined network can communicate directly through the Docker network.

**Example:** `postgres:5432`.

### 8. What is service discovery?

**Answer:** The mechanism by which a client finds the network address of a service.

**Example:** Docker DNS resolves `postgres` to the PostgreSQL container's network address.

### 9. What does Docker DNS do?

**Answer:** It resolves service/container names to reachable network addresses within the Docker network.

**Example:** `nslookup postgres`.

### 10. Why use user-defined networks?

**Answer:** They provide explicit grouping, predictable service discovery, and clearer isolation.

### 11. What is `host.docker.internal`?

**Answer:** A Docker-provided hostname used in supported environments to reach the host from a container.

## Advanced

### 12. Why do Kafka listeners create unique problems?

**Answer:** Kafka can return broker addresses that clients use for subsequent connections.

### 13. What is an advertised listener?

**Answer:** The address Kafka tells clients to use when connecting to a broker.

### 14. Why can Kafka bootstrap successfully but fail afterward?

**Answer:** The bootstrap endpoint may be reachable while the advertised broker address is not.

### 15. How do you troubleshoot DNS vs TCP vs application-layer failures?

**Answer:** Test progressively:

```text
nslookup
  ↓
nc
  ↓
curl / client protocol
  ↓
readiness
```

### 16. How would you design networking for a local Data Engineering lab?

**Answer:** Use a named user-defined network, service names for internal traffic, published ports only for required host access, loopback binding for local-only host endpoints, and appropriate Kafka internal/external listeners.

## 40. Data Engineering Interview Practice

### 1. Explain Docker port publishing.

**Short answer:** It maps a host endpoint to a container endpoint.

**Detailed answer:** `-p HOST:CONTAINER` makes a container service reachable through the host-side port.

**Example:** `-p 5433:5432` lets a host client reach PostgreSQL on `localhost:5433`.

### 2. What does `-p 5433:5432` mean?

**Short answer:** Host `5433` → container `5432`.

**Detailed:** PostgreSQL remains on `5432` internally.

**Example:** host Python uses `localhost:5433`.

### 3. What happens when two services try to use the same host port?

**Short answer:** The host port binding conflicts.

**Detailed:** Only one endpoint can own the same host binding in the conflicting context.

**Example:** move one service to `5433:5432`.

### 4. Why doesn't localhost work between containers?

**Short answer:** Each container has its own network context.

**Detailed:** `localhost` points back to the client container.

**Example:** use `postgres:5432`.

### 5. How do containers discover each other?

**Short answer:** Docker DNS on a user-defined network resolves service/container names.

**Example:** `postgres` → PostgreSQL container IP.

### 6. What is a user-defined Docker network?

**Short answer:** An explicit Docker network used to connect related containers.

**Example:** `docker network create datalab`.

### 7. Why don't container-to-container connections require published ports?

**Short answer:** Internal traffic can travel directly over the shared Docker network.

**Example:** Python → `postgres:5432`.

### 8. What is `host.docker.internal`?

**Short answer:** A supported mechanism for a container to address the host.

**Example:** container → `host.docker.internal:<host-service-port>`.

### 9. What is the difference between a Kafka listener and advertised listener?

**Short answer:** A listener is where Kafka accepts connections; an advertised listener is the address Kafka tells clients to use.

**Example:** internal `kafka:9092`, external `localhost:9094`.

### 10. Why does Kafka often need internal and external listeners?

**Short answer:** Host and container clients may have different reachable addresses.

**Example:** host → `localhost:9094`; container → `kafka:9092`.

### 11. How would you debug a container that cannot connect to PostgreSQL?

**Short answer:** Establish the client's location, service location, network membership, hostname, DNS, port, TCP reachability, and readiness.

**Example:**

```text
docker network inspect datalab
nslookup postgres
nc -vz postgres 5432
```

### 12. How would you distinguish DNS failure from TCP failure?

**Short answer:** `nslookup` tests name resolution; `nc` tests TCP connectivity.

### 13. Why can `nc` succeed while an application still fails?

**Short answer:** TCP reachability does not prove that the application protocol or service is healthy.

### 14. What is host networking?

**Short answer:** A mode in which the container uses the host's network stack more directly.

**Example:** `--network host`.

### 15. What networking differences exist across Docker platforms?

**Short answer:** Host reachability, localhost forwarding, host networking, and related behavior can differ across Linux, Docker Desktop, WSL2, macOS, and other environments.

**Example:** verify `host.docker.internal` and host networking support on the actual runtime.

## 41. Final Knowledge Checkpoint

You should be able to explain the following without looking up the answer:

1. Why does `localhost` mean different things to a host process and a container process?
2. In `-p 5433:5432`, which port belongs to the host?
3. Which port does PostgreSQL continue listening on inside the container?
4. Why can a Python container use `postgres:5432` without publishing PostgreSQL's port?
5. What role does Docker DNS play?
6. What does `docker network inspect datalab` tell you?
7. What does `nslookup postgres` prove?
8. What does `nc -vz postgres 5432` prove?
9. Why does TCP success not prove application readiness?
10. When should a local lab use `127.0.0.1` in a port binding?
11. Why can `host.docker.internal` be useful?
12. Why can Kafka bootstrap successfully and then fail?
13. What is the difference between a Kafka listener and advertised listener?
14. Why might host and container Kafka clients need different addresses?
15. How would you diagnose a connection failure without changing five settings at once?

### Expected reasoning pattern

```text
Client
 ↓
Client location
 ↓
Service location
 ↓
Shared network?
 ↓
Hostname
 ↓
DNS
 ↓
Port
 ↓
Published vs internal path
 ↓
TCP
 ↓
Application protocol
 ↓
Readiness
 ↓
Kafka advertised address, when applicable
```

## 42. Final Mastery Checklist

### Core networking

- [ ] I can explain IP address, hostname, port, protocol, TCP, client, server, listening socket, and connection.
- [ ] I understand `localhost` and loopback.
- [ ] I can explain why host `localhost` is different from container `localhost`.

### Ports

- [ ] I understand service, container, host, and listening ports.
- [ ] I can read `-p HOST_PORT:CONTAINER_PORT`.
- [ ] I can diagnose a host port conflict.
- [ ] I can choose a different host port without changing the internal service port.

### Docker networks

- [ ] I can create a user-defined network.
- [ ] I understand network membership and isolation.
- [ ] I understand default bridge vs user-defined bridge at the required level.
- [ ] I understand why named networks are preferable for multi-service labs.
- [ ] I understand Compose's project-network concept.

### Service discovery

- [ ] I understand Docker DNS.
- [ ] I can use a container/service name.
- [ ] I can explain why container-to-container traffic uses the container port.
- [ ] I understand why publishing is not required for internal traffic.

### Host communication

- [ ] I understand host → container communication through published ports.
- [ ] I understand container → host communication.
- [ ] I understand `host.docker.internal` and its platform caveats.
- [ ] I can use `127.0.0.1` for appropriate local-only bindings.

### Kafka

- [ ] I understand Kafka listeners.
- [ ] I understand advertised listeners.
- [ ] I understand host vs container Kafka client locations.
- [ ] I can reason about internal and external listeners.
- [ ] I can reproduce and diagnose an advertised-listener failure.

### Diagnostics

- [ ] I can use `docker network ls`.
- [ ] I can use `docker network inspect`.
- [ ] I can inspect containers.
- [ ] I can use a temporary diagnostic container.
- [ ] I can use `nslookup` for DNS.
- [ ] I can use `nc` for TCP.
- [ ] I can use `curl` for HTTP/application-level checks.
- [ ] I can separate DNS, TCP, application, and readiness failures.

### Engineering mindset

- [ ] I identify the client location first.
- [ ] I identify the service location second.
- [ ] I identify the network third.
- [ ] I distinguish host ports from container ports.
- [ ] I avoid unnecessary port publishing.
- [ ] I test connectivity layer by layer.
- [ ] I document network assumptions.
- [ ] I diagnose from evidence rather than guessing.
- [ ] I follow the rule: **Never change five networking settings at once. Identify the failing layer first.**

## 43. Roadmap Coverage Audit

The Topic 03 roadmap requires all of the following. This audit confirms that each item is addressed in this module.

- [x] Port publishing
- [x] `-p HOST_PORT:CONTAINER_PORT`
- [x] Host access using `localhost`
- [x] Port conflicts
- [x] Container-local `localhost`
- [x] User-defined networks
- [x] Container-to-container communication
- [x] DNS by container name
- [x] Container port vs host port
- [x] Why publishing is unnecessary for internal traffic
- [x] Default bridge network
- [x] User-defined bridge network
- [x] Why named networks are preferable for labs
- [x] Compose-created network awareness
- [x] Host → container communication
- [x] Container → host communication
- [x] `host.docker.internal`
- [x] Platform differences relevant to networking
- [x] `127.0.0.1` binding
- [x] Local-only exposure
- [x] Kafka listeners
- [x] Kafka advertised listeners
- [x] Host vs container Kafka clients
- [x] Two-listener configuration
- [x] Kafka failure reproduction
- [x] `docker network ls`
- [x] `docker network inspect`
- [x] Temporary diagnostic containers
- [x] `nc`
- [x] `curl`
- [x] `nslookup`
- [x] Layered troubleshooting
- [x] Host networking awareness
- [x] Complete `docker_lab/03` lab design
- [x] Break/fix exercises
- [x] Real-world scenarios
- [x] Mental models
- [x] Command reference
- [x] Common mistakes
- [x] Practice questions
- [x] Interview practice
- [x] Final mastery checklist

### Scope boundary verification

This module does **not** replace:

- Topic 01 — Containers, Images, and Registries
- Topic 02 — Running Databases and Services
- Topic 04 — Persistence
- Topic 05 — Configuration and Secrets
- Topic 06 — General Troubleshooting
- Topic 07 — Docker Compose
- Topic 10 — Full Docker Desktop/WSL2/Platform Differences

Those topics may be referenced where necessary, but their full curricula remain outside Topic 03.

## Source and Implementation Notes

This module was constructed directly from the supplied authoritative Topic 03 specification. Kafka image-specific configuration syntax can vary by distribution and version; the architectural concepts in this document are the stable learning target, while exact image configuration should be verified against the selected Kafka image's current documentation during implementation.

For hands-on work, record commands and observations in `docker_lab/03/` as specified by the roadmap. Do not create or modify other roadmap files.
