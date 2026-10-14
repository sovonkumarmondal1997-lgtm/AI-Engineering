# SSH Tunnels and Port Forwarding for Data Tools

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**  
> **Topic 02 — SSH Tunnels and Port Forwarding for Data Tools**  
> **Progression:** Basic → Intermediate → Advanced → Production Data Engineering

---

## 1. Module Purpose

Production Data Engineering frequently requires access to services that are deliberately **not exposed to the public Internet**.

A database may be private:

```text
Laptop
   |
   | Internet
   v
Bastion
   |
   | Private network
   v
Private PostgreSQL
```

An internal web service may be private:

```text
Laptop
   |
   v
Bastion
   |
   v
Airflow / Grafana / MinIO / internal API
```

The problem is simple:

> **My laptop cannot directly reach the private service, but the bastion can.**

An SSH tunnel provides a controlled path through an existing SSH connection:

```text
Laptop
   |
   | SSH connection
   v
Bastion
   |
   | TCP connection
   v
Private service
```

This module teaches how to establish, use, verify, troubleshoot, and close these tunnels safely.

It also teaches an equally important production skill:

> **Knowing when an SSH tunnel is the correct operator-access mechanism—and when it is a workaround for a network architecture that should be fixed instead.**

---

# 2. What You Will Learn

By the end of this topic you should be able to:

- explain the SSH tunneling mental model;
- create local port forwards with `ssh -L`;
- connect to private PostgreSQL through `psql`;
- connect to a private database through Python;
- access private web UIs through a browser;
- use `-N` for tunnel-only sessions;
- use `-f` to background a tunnel deliberately;
- inspect, verify, and close tunnels;
- combine `ProxyJump` with local forwarding;
- configure `LocalForward` in `~/.ssh/config`;
- understand safe local bind addresses;
- explain why `127.0.0.1` is usually safer than `0.0.0.0`;
- understand remote forwarding with `-R`;
- explain the security risks of remote forwarding;
- use dynamic forwarding with `-D`;
- explain SOCKS proxy behavior;
- understand auto-reconnecting tools at a high level;
- recognize `kubectl port-forward`;
- recognize cloud-provider session/port-forwarding mechanisms;
- troubleshoot broken tunnels using evidence;
- create a simple tunnel helper script;
- distinguish operator access from production application connectivity;
- explain when private networking is the correct long-term solution.

---

# 3. Prerequisites and Scope

Topic 01 established the SSH foundation:

- SSH client/server;
- keys and authentication;
- `~/.ssh/config`;
- bastion/jump-host architecture;
- `ProxyJump`;
- host-key verification;
- SSH troubleshooting fundamentals.

This topic builds on those concepts rather than repeating them as a separate SSH fundamentals course.

## Practice environment

Use a safe lab consisting of:

```text
Laptop
   |
   v
Bastion
   |
   v
Private Data Server
   |
   +---- PostgreSQL :5432
   |
   +---- Internal Web UI :8080
```

Use example values such as:

```text
bastion.example.com
private-data.example.internal
private-postgres
dataeng
127.0.0.1
```

Never use real production credentials, private keys, passwords, or infrastructure in these exercises.

---

# 4. The Networking Mental Model

## 4.1 The problem SSH tunneling solves

Imagine:

```text
Laptop
   |
   | Internet
   v
Bastion
   |
   | Private Network
   v
Private PostgreSQL
```

The laptop cannot directly route to:

```text
private-postgres:5432
```

but the bastion can.

Without a tunnel:

```text
Laptop  -X->  private-postgres:5432
```

With a tunnel:

```text
Laptop
   |
   | SSH
   v
Bastion
   |
   | TCP
   v
private-postgres:5432
```

SSH provides a transport path through the bastion.

## 4.2 What a tunnel actually does

A local tunnel creates a **listening port on the laptop**.

When an application connects to that local port, SSH transports the connection through the SSH session and causes the SSH server side to connect to the configured destination.

Conceptually:

```text
Application
    |
    v
127.0.0.1:15432
    |
    | SSH tunnel
    v
Bastion
    |
    | TCP
    v
private-postgres:5432
```

The local application does not need direct network reachability to PostgreSQL.

## 4.3 Critical distinction

These are different endpoints:

```text
127.0.0.1:15432
```

and:

```text
private-postgres:5432
```

The first is the local listener.

The second is the destination reached through the SSH path.

This distinction is fundamental.

---

# 5. Local Port Forwarding — `-L`

## 5.1 Syntax

The fundamental syntax is:

```bash
ssh -L local_port:target_host:target_port user@ssh_server
```

For example:

```bash
ssh -L 15432:private-postgres:5432 dataeng@bastion.example.com
```

## 5.2 Explain every component

```text
-L
```

Requests local port forwarding.

```text
15432
```

The local listening port on your laptop.

```text
private-postgres
```

The target hostname as reachable from the SSH server side.

```text
5432
```

The target service port.

```text
dataeng
```

The SSH login user.

```text
bastion.example.com
```

The SSH server through which the tunnel is established.

## 5.3 Traffic flow

```text
psql / Python / browser
        |
        | 127.0.0.1:15432
        v
+-----------------------+
| Laptop                |
| SSH local listener    |
+-----------------------+
        |
        | encrypted SSH connection
        v
+-----------------------+
| Bastion               |
+-----------------------+
        |
        | TCP connection
        v
+-----------------------+
| private-postgres:5432 |
+-----------------------+
```

## 5.4 Why the destination is important

A common beginner mistake is to think:

```bash
ssh -L 15432:private-postgres:5432 ...
```

means the laptop must resolve `private-postgres`.

The important operational model is:

> The target destination is reached from the SSH server side.

This is why tunneling through a bastion can reach private DNS names and private IP addresses that the laptop cannot normally resolve or route to.

---

# 6. Local Forwarding with PostgreSQL

## 6.1 Architecture

```text
Laptop
   |
   | 127.0.0.1:15432
   v
Bastion
   |
   | private network
   v
PostgreSQL :5432
```

Create the tunnel:

```bash
ssh -L 15432:private-postgres:5432 dataeng@bastion.example.com
```

Then connect locally:

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

## 6.2 What PostgreSQL sees

The application is connecting to:

```text
127.0.0.1:15432
```

on the laptop.

SSH carries the traffic.

The destination is:

```text
private-postgres:5432
```

from the server-side network context.

PostgreSQL does not need to be exposed publicly.

## 6.3 Why use `127.0.0.1`?

The client connects only to the local listener:

```text
127.0.0.1:15432
```

This is generally the safest default for a personal operator tunnel.

## 6.4 Verify with `psql`

After opening the tunnel:

```bash
psql \
  -h 127.0.0.1 \
  -p 15432 \
  -U analytics \
  -d warehouse
```

Inside PostgreSQL you can verify the connection with an appropriate query, for example:

```sql
SELECT current_database(), current_user;
```

The tunnel's existence does not grant PostgreSQL authorization. Database authentication and authorization still apply.

---

# 7. Local Forwarding with Python

The same local listener can be used by application code.

Example with `psycopg`:

```python
import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=15432,
    dbname="warehouse",
    user="analytics",
    password="YOUR_PRACTICE_PASSWORD",
)

with conn.cursor() as cur:
    cur.execute("SELECT current_database(), current_user;")
    print(cur.fetchone())

conn.close()
```

## What Python knows

Python only knows:

```text
host = 127.0.0.1
port = 15432
```

It does not need to know the private PostgreSQL hostname.

The SSH tunnel handles the network path.

## Security note

Do not place real passwords into this learning module.

In production, credentials should be supplied through an appropriate secret-management mechanism rather than committed to source code.

The tunnel solves **network reachability**. It does not solve **credential management**.

---

# 8. Local Forwarding with Web UIs

The same technique works with private HTTP services.

Example:

```text
Laptop
   |
   v
Bastion
   |
   v
Airflow Web UI :8080
```

Create the tunnel:

```bash
ssh -L 8080:airflow.internal:8080 dataeng@bastion.example.com
```

Then open:

```text
http://127.0.0.1:8080
```

The browser thinks it is talking to:

```text
127.0.0.1:8080
```

SSH carries that connection to:

```text
airflow.internal:8080
```

through the bastion.

## Realistic Data Engineering targets

The same pattern can be useful for temporary operator access to:

- Airflow;
- Grafana;
- MinIO;
- internal monitoring dashboards;
- internal HTTP APIs.

These are examples of access patterns, not separate courses in those products.

---

# 9. `-N`: Tunnel Without a Remote Shell

Use:

```bash
ssh -N ...
```

`-N` means:

> **Do not execute a remote command or open an interactive shell; use the SSH connection for forwarding.**

Example:

```bash
ssh -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

This is a natural form for a dedicated tunnel.

## Foreground behavior

The terminal remains occupied by the tunnel.

Conceptually:

```text
Terminal
   |
   +-- SSH tunnel process
          |
          +-- local forwarding
```

Press:

```text
Ctrl+C
```

to terminate a foreground tunnel.

---

# 10. `-f`: Backgrounding a Tunnel

You can combine `-f` and `-N`:

```bash
ssh -f -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

## What `-f` does

It requests that SSH go into the background after authentication.

The result is:

```text
Terminal
   |
   +-- command returns
          |
          v
      background SSH process
          |
          v
      local tunnel
```

## Why this is convenient

You can open a tunnel and continue using the same terminal.

## Why it is risky operationally

Background processes are easy to forget.

You may later see:

```text
Address already in use
```

because an old tunnel is still listening.

Therefore:

> **Backgrounding a tunnel creates an operational lifecycle problem: you must know how to identify and close it.**

---

# 11. Tunnel Lifecycle

Treat a tunnel as an operational object:

```text
Create
  ↓
Verify
  ↓
Use
  ↓
Inspect
  ↓
Close
```

Do not treat:

```bash
ssh -f -N ...
```

as the end of the workflow.

---

# 12. Inspecting Local Tunnel Listeners

On Linux/macOS and many Unix-like environments:

```bash
ss -ltn
```

A listening socket might appear conceptually as:

```text
LISTEN ... 127.0.0.1:15432
```

This tells you that something is listening on that local port.

Depending on the operating system, other tools may be available.

The important question is:

> **Is the expected local port actually listening?**

## Process inspection

You can inspect SSH processes:

```bash
ps aux | grep '[s]sh'
```

This avoids matching the `grep` process itself.

On systems where supported, a more targeted approach can be useful:

```bash
pgrep -af 'ssh.*15432'
```

Do not blindly terminate every SSH process.

First identify:

- PID;
- command line;
- target host;
- forwarded port;
- whether it is the tunnel you intend to close.

---

# 13. Closing a Foreground Tunnel

For:

```bash
ssh -N -L 15432:private-postgres:5432 dataeng@bastion.example.com
```

the simplest closure is:

```text
Ctrl+C
```

The SSH process exits and the local listener disappears.

Verify:

```bash
ss -ltn
```

---

# 14. Closing a Background Tunnel Safely

First inspect:

```bash
ps aux | grep '[s]sh'
```

Identify the correct process.

Then terminate that specific process.

A controlled approach is:

```bash
kill PID
```

where `PID` is the verified process ID.

Then check:

```bash
ps -p PID
```

If it has exited, verify the listener:

```bash
ss -ltn
```

Avoid blindly using broad commands such as:

```bash
pkill ssh
```

because that can terminate unrelated SSH sessions.

---

# 15. Verifying a Tunnel

A listening port is necessary but not sufficient.

Use this evidence sequence:

```text
1. SSH connection established
        ↓
2. Local port is listening
        ↓
3. TCP connection reaches the tunnel
        ↓
4. SSH server can reach target
        ↓
5. Target service is healthy
        ↓
6. Application protocol works
```

## Evidence command

```bash
ss -ltn
```

## SSH diagnostics

```bash
ssh -vv \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

## Application-level test

For PostgreSQL:

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

For HTTP:

```bash
curl http://127.0.0.1:8080
```

The final test is important.

> A listening local port does not prove that PostgreSQL, Airflow, or another target application is healthy.

---

# 16. `ProxyJump` + Local Forwarding

A common production-like Data Engineering topology is:

```text
Laptop
   |
   v
Bastion
   |
   v
Private Server
   |
   v
Private PostgreSQL
```

Suppose PostgreSQL is reachable from the private server, but the laptop cannot reach either private machine directly.

You can combine `ProxyJump` with local forwarding:

```bash
ssh -J bastion \
  -L 15432:private-postgres:5432 \
  dataeng@private-server
```

## Traffic path

Think through the layers:

```text
psql
 |
 | 127.0.0.1:15432
 v
Laptop
 |
 | local forwarding
 v
SSH connection through ProxyJump
 |
 v
Bastion
 |
 | network path
 v
Private server / private network
 |
 v
private-postgres:5432
```

The exact network path depends on the infrastructure, but the essential model is:

> **The jump host provides the SSH path; the port-forward destination must be reachable from the appropriate SSH/server-side network context.**

Do not assume the laptop itself can resolve or route to `private-postgres`.

---

# 17. `ProxyJump` in SSH Configuration

Topic 01 introduced configuration such as:

```sshconfig
Host bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes

Host data-server
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_data
    IdentitiesOnly yes
    ProxyJump bastion
```

You can add a local forward:

```sshconfig
Host data-server
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_data
    IdentitiesOnly yes
    ProxyJump bastion
    LocalForward 15432 private-postgres:5432
```

Now:

```bash
ssh data-server
```

establishes the configured SSH connection and local forwarding.

---

# 18. `LocalForward` in SSH Config

The directive:

```sshconfig
LocalForward 15432 private-postgres:5432
```

means:

```text
local port 15432
        ↓
private-postgres:5432
```

through the SSH connection.

A complete example:

```sshconfig
Host bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes

Host data-server
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_data
    IdentitiesOnly yes
    ProxyJump bastion
    LocalForward 127.0.0.1:15432 private-postgres:5432
```

Then:

```bash
ssh data-server
```

and separately:

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

## Why configuration is useful

It provides:

- repeatability;
- fewer typing errors;
- explicit access architecture;
- easier review;
- easier operational runbooks.

It also reduces command-line complexity.

---

# 19. Safe Bind Addresses

This is one of the most important security concepts in the module.

Compare:

```bash
ssh -L 127.0.0.1:15432:private-postgres:5432 ...
```

with:

```bash
ssh -L 0.0.0.0:15432:private-postgres:5432 ...
```

## `127.0.0.1`

`127.0.0.1` means:

> Listen on the local loopback interface.

In practical terms:

```text
Your laptop
  |
  +-- 127.0.0.1:15432
```

Other machines on the network normally cannot directly use that loopback listener.

## `0.0.0.0`

`0.0.0.0` means:

> Listen on all available local IPv4 interfaces, subject to the platform and SSH configuration.

Conceptually:

```text
Other machines
     |
     v
Laptop network interface
     |
     v
0.0.0.0:15432
     |
     v
SSH tunnel
     |
     v
Private PostgreSQL
```

This can expose a private service to other machines that can reach your laptop.

---

# 20. Why Binding to All Interfaces Can Be Dangerous

Suppose you are on a corporate network or shared Wi-Fi.

You run:

```bash
ssh -L 0.0.0.0:15432:private-postgres:5432 ...
```

You may unintentionally create:

```text
Network peers
    |
    v
Your laptop:15432
    |
    v
Private PostgreSQL
```

The database itself remains private, but you have potentially created a new path to it.

This is a serious trust-boundary change.

## Default security rule

> **Bind personal operator tunnels to `127.0.0.1` unless there is a deliberate, understood reason to expose the listener.**

---

# 21. Demonstrating the Binding Difference

Use a safe local practice environment.

Start a tunnel bound to:

```text
127.0.0.1
```

Then inspect:

```bash
ss -ltn
```

You should see a listener associated with the loopback address.

Now, only in a controlled lab, compare with:

```text
0.0.0.0
```

Inspect again:

```bash
ss -ltn
```

The binding will reflect the broader interface scope.

Do not use this experiment against a real production database.

The purpose is to understand the security implication.

---

# 22. Local Forwarding vs Remote Forwarding

Local forwarding:

```text
Laptop
  |
  | local port
  v
SSH
  |
  v
Remote destination
```

Remote forwarding:

```text
Remote side
  |
  | remote port
  v
SSH
  |
  v
Local destination
```

The direction of the exposed listener changes.

---

# 23. Remote Port Forwarding — `-R`

Syntax:

```bash
ssh -R remote_port:target_host:target_port user@ssh_server
```

A simplified example:

```bash
ssh -R 18080:127.0.0.1:8080 dataeng@bastion.example.com
```

Conceptually:

```text
Bastion
   |
   | remote forwarded port
   v
SSH connection
   |
   v
Laptop
   |
   v
127.0.0.1:8080
```

This means the remote side gets a forwarded path to a service available from the local side.

## Why `-R` exists

Remote forwarding can be useful when:

- a local development service needs controlled remote reachability;
- an operator needs to expose a local diagnostic service temporarily;
- a controlled reverse-access workflow is required.

It is powerful precisely because it changes the direction of reachability.

---

# 24. Risks of Remote Forwarding

Remote forwarding can be dangerous because it can turn a local service into something reachable from the remote environment.

Potential consequences include:

- remote users reaching a local service;
- accidental exposure of development endpoints;
- bypassing expected network boundaries;
- unexpected access through a trusted bastion;
- firewall-policy surprises;
- exposing services that were designed to be local-only.

The correct question is not:

> "Does `-R` work?"

The correct question is:

> **"Who can reach the remote forwarded listener, and what service becomes reachable through it?"**

## Trust-boundary diagram

```text
Without forwarding:

Remote environment
      X
      |
      | cannot reach
      v
Local service

With remote forwarding:

Remote environment
      |
      v
Remote forwarded listener
      |
      v
SSH connection
      |
      v
Local service
```

That new path must be intentional.

---

# 25. Remote Forwarding and Bind Scope

A remote forwarded port can have its own exposure implications.

Do not assume:

```text
remote_port
```

is automatically reachable only by you.

The exact exposure depends on SSH server configuration and bind-address behavior.

For production reasoning, ask:

1. Where does the forwarded listener bind?
2. Which interfaces can reach it?
3. Which users can connect to it?
4. What service is behind it?
5. Is the SSH server configured to permit or restrict remote forwarding?
6. Does the forwarding bypass an intended network boundary?

---

# 26. Dynamic Port Forwarding — `-D`

Dynamic forwarding creates a **SOCKS proxy**.

Example:

```bash
ssh -D 1080 dataeng@bastion.example.com
```

Mental model:

```text
Application
    |
    | SOCKS
    v
127.0.0.1:1080
    |
    | SSH
    v
Bastion
    |
    v
Internal destination
```

## What is a SOCKS proxy?

SOCKS is a proxy protocol that allows a proxy-aware application to request connections to different destinations through the proxy.

Unlike a fixed local forward:

```text
-L 15432:private-postgres:5432
```

which specifies one destination, `-D` creates a dynamic proxy endpoint.

---

# 27. `-L` vs `-D`

### Local forwarding

```bash
ssh -L 15432:private-postgres:5432 ...
```

Mental model:

```text
One local port
      ↓
One configured destination
```

### Dynamic forwarding

```bash
ssh -D 1080 ...
```

Mental model:

```text
One local SOCKS endpoint
      ↓
Application chooses destinations
      ↓
SSH carries the connection
```

Therefore:

```text
-L = fixed destination
-D = dynamic destinations through SOCKS
```

---

# 28. SOCKS Proxy Use Case

A controlled internal-web-access scenario might be:

```text
Browser
   |
   | SOCKS proxy
   v
127.0.0.1:1080
   |
   | SSH
   v
Bastion
   |
   v
Internal web destination
```

The browser or application must support SOCKS proxy configuration.

The important concept is that the destination can be selected dynamically rather than being hard-coded into one `-L` rule.

## Security implications

A SOCKS proxy is more powerful than a single fixed port forward because it can potentially provide access to many destinations reachable from the SSH server.

Therefore:

> **Treat a SOCKS proxy as a broad network-access capability, not merely another convenient tunnel flag.**

Do not create uncontrolled SOCKS access into production networks.

---

# 29. Compare `-L`, `-R`, and `-D`

| Feature | `-L` | `-R` | `-D` |
|---|---|---|---|
| Name | Local forwarding | Remote forwarding | Dynamic forwarding |
| Listener | Local side | Remote side | Local SOCKS listener |
| Destination | Fixed | Fixed | Selected dynamically |
| Typical use | Local access to private service | Remote access to local service | Proxy-aware access to multiple destinations |
| Example | `-L 15432:db:5432` | `-R 18080:localhost:8080` | `-D 1080` |
| Typical operator use | PostgreSQL/internal UI | Controlled reverse access | Controlled troubleshooting/access |
| Main risk | Accidental local exposure | Accidental remote exposure | Broad network reachability |
| Security question | Who can reach my local listener? | Who can reach the remote listener? | Which destinations can the proxy reach? |

The goal is not to memorize flags.

The goal is to understand:

```text
Where does the listener exist?
Where does traffic go?
Who can reach the listener?
What trust boundary does the tunnel cross?
```

---

# 30. Tunnel Verification: Evidence First

Use an evidence-driven workflow.

```text
Application cannot connect
        |
        v
Is local port listening?
        |
        +---- NO ----> SSH tunnel problem
        |
       YES
        |
        v
Can SSH reach the target network?
        |
        +---- NO ----> Bastion/routing/firewall problem
        |
       YES
        |
        v
Is the target service healthy?
        |
        +---- NO ----> Application/service problem
        |
       YES
        |
        v
Does the application configuration work?
```

## Step 1 — Check the local listener

```bash
ss -ltn
```

## Step 2 — Inspect the SSH connection

```bash
ssh -vv \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

## Step 3 — Test the actual application

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

or:

```bash
curl http://127.0.0.1:8080
```

## Critical lesson

A successful SSH connection is not proof that the target service is reachable.

A listening local port is not proof that the target service is healthy.

---

# 31. SSH Verbose Troubleshooting

Use:

```bash
ssh -v ...
```

for useful diagnostics.

Increase when necessary:

```bash
ssh -vv ...
```

or:

```bash
ssh -vvv ...
```

Verbose output can help identify:

- SSH configuration;
- authentication behavior;
- ProxyJump behavior;
- connection setup;
- forwarding setup;
- failures while connecting.

## Do not blindly copy verbose output

Verbose SSH output can contain:

- hostnames;
- usernames;
- IP addresses;
- file paths;
- environment-specific details.

Treat it as operational information.

Use only the relevant lines when documenting an incident.

---

# 32. Common Tunnel Failure Modes

## Failure 1 — Local port already in use

### Symptom

The tunnel cannot bind:

```text
Address already in use
```

### Evidence

```bash
ss -ltn
```

Identify what is listening on the port.

### Diagnosis

Another process or an old tunnel already owns the local port.

### Fix

Either:

- close the stale tunnel safely; or
- choose another local port.

### Verification

Recreate the tunnel and verify the listener.

---

## Failure 2 — Wrong destination hostname

### Symptom

SSH starts, but the application cannot connect.

### Evidence

Review:

```bash
ssh -vv ...
```

and verify the destination:

```text
private-postgres
```

### Diagnosis

The SSH server cannot resolve or reach the target hostname.

### Fix

Correct the destination name or use the correct private address.

### Verification

Test from the relevant server-side environment.

---

## Failure 3 — Wrong destination port

Example:

```bash
-L 15432:private-postgres:5433
```

when PostgreSQL listens on `5432`.

### Diagnosis

The tunnel is established but the application connection fails.

### Fix

Use the correct target port:

```bash
-L 15432:private-postgres:5432
```

---

## Failure 4 — Bastion can SSH but cannot reach target

This is a crucial distinction.

```text
Laptop → Bastion
        works

Bastion → private service
        fails
```

SSH authentication can therefore be completely healthy.

The problem may be:

- routing;
- firewall;
- security group;
- private DNS;
- target service availability.

Do not rotate SSH keys for a network-routing failure.

---

## Failure 5 — Private service is down

The tunnel may be perfectly healthy while PostgreSQL/Airflow/etc. is unavailable.

Therefore test the application protocol after verifying the tunnel.

---

## Failure 6 — Firewall or security group blocks traffic

The bastion may not be allowed to reach:

```text
private-postgres:5432
```

This is a network policy problem.

The tunnel does not bypass every firewall.

---

## Failure 7 — Incorrect `ProxyJump`

### Symptom

The direct bastion connection works, but the private target does not.

### Evidence

```bash
ssh data-bastion
```

then:

```bash
ssh -vv data-private
```

### Diagnosis

Inspect:

```text
ProxyJump
HostName
User
IdentityFile
```

and verify the network path.

---

## Failure 8 — Incorrect SSH credentials

### Symptom

```text
Permission denied (publickey).
```

This is primarily an SSH authentication issue, not a port-forwarding issue.

Topic 01 covers the SSH credential model.

---

## Failure 9 — Tunnel immediately terminates

Possible causes:

- SSH authentication failed;
- bastion is unreachable;
- forwarding was rejected;
- target connection failed;
- local port could not bind;
- SSH configuration is invalid.

Use:

```bash
ssh -vv ...
```

instead of guessing.

---

## Failure 10 — Tunnel listens but application fails

This usually means:

```text
Local listener exists
        ↓
But target/application path is failing
```

Check:

- target hostname;
- target port;
- target service;
- network path from SSH server;
- application credentials;
- application protocol.

---

## Failure 11 — Wrong bind address

If the tunnel is unintentionally exposed:

```bash
ss -ltn
```

may reveal:

```text
0.0.0.0:15432
```

instead of:

```text
127.0.0.1:15432
```

Correct the configuration unless broader exposure is deliberate and justified.

---

## Failure 12 — Forgotten background tunnel

### Symptom

A later attempt to create the same tunnel reports:

```text
Address already in use
```

Inspect:

```bash
ps aux | grep '[s]sh'
```

and:

```bash
ss -ltn
```

Identify the correct process before closing it.

---

# 33. Tunnel Troubleshooting Decision Tree

```text
Application cannot connect
        |
        v
Is the expected local port listening?
        |
      +---+---+
      |       |
     NO      YES
      |       |
      v       v
Fix SSH    Can SSH/server-side path
tunnel     reach the destination?
              |
            +---+---+
            |       |
           NO      YES
            |       |
            v       v
      Check route,   Is target service
      DNS, firewall  healthy?
                       |
                     +---+---+
                     |       |
                    NO      YES
                     |       |
                     v       v
                Fix target   Check application
                service      configuration
```

## Expanded evidence sequence

```text
Local listener
    ↓
SSH connection
    ↓
ProxyJump path
    ↓
Server-side DNS
    ↓
Server-side TCP reachability
    ↓
Target service
    ↓
Application protocol
    ↓
Application authentication
```

This order prevents you from changing application settings when the real problem is a network path.

---

# 34. Tunnel Helper Script — `tunnels.sh`

The roadmap explicitly calls for a small tunnel helper.

A simple version:

```bash
#!/usr/bin/env bash

set -euo pipefail

ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  data-server
```

## Explain the script

### Shebang

```bash
#!/usr/bin/env bash
```

Requests Bash through the environment.

### Strict mode

```bash
set -euo pipefail
```

A common shell safety pattern:

- `-e` — stop when a command fails;
- `-u` — treat unset variables as errors;
- `pipefail` — propagate failures through pipelines.

This is shell-script behavior, not SSH-specific behavior.

### SSH command

```bash
ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  data-server
```

It assumes `data-server` is already configured in `~/.ssh/config`.

---

# 35. Improving the Tunnel Helper

A readable helper can provide named operations:

```bash
#!/usr/bin/env bash

set -euo pipefail

PORT="${PORT:-15432}"

open_tunnel() {
    ssh -N \
      -L "127.0.0.1:${PORT}:private-postgres:5432" \
      data-server
}

check_tunnel() {
    ss -ltn | grep ":${PORT} "
}

close_tunnel() {
    echo "Inspect the SSH process before terminating it."
    ps aux | grep '[s]sh'
}

case "${1:-}" in
    open)
        open_tunnel
        ;;
    check)
        check_tunnel
        ;;
    close)
        close_tunnel
        ;;
    *)
        echo "Usage: $0 {open|check|close}"
        exit 1
        ;;
esac
```

## Important operational lesson

The `close` action intentionally does not blindly kill an SSH process.

A good operational tool should make it difficult to terminate unrelated SSH sessions accidentally.

---

# 36. Auto-Reconnecting Tools — Awareness

Some applications and wrappers can automatically reconnect when network connections drop.

You may encounter:

- database clients;
- application connection pools;
- SSH tunnel wrappers;
- process supervisors;
- cloud session tools.

Do not assume automatic reconnection exists.

Separate:

```text
Application retry
```

from:

```text
SSH tunnel availability
```

For example:

```text
Application
   |
   | retry
   v
SSH tunnel
   |
   X
Tunnel is dead
```

Application retry cannot succeed until the network path is restored.

Conversely:

```text
SSH tunnel
   |
   | reconnects
   v
Application
   |
   X
Application session is broken
```

Tunnel availability does not guarantee application-level recovery.

## Production lesson

For critical production connectivity, use infrastructure and service mechanisms designed for availability rather than relying on a personal SSH tunnel and an auto-reconnect wrapper.

---

# 37. `kubectl port-forward` — Awareness

Kubernetes provides its own forwarding mechanism:

```bash
kubectl port-forward
```

Conceptually:

```text
Laptop
   |
   | kubectl port-forward
   v
Kubernetes API/control path
   |
   v
Pod / Service
```

For example, a development workflow might use:

```bash
kubectl port-forward service/example 8080:80
```

This is conceptually similar to SSH local forwarding because:

```text
Local port
    ↓
Forwarded connection
    ↓
Internal service
```

But it is not the same mechanism.

## Why know about it?

A Data Engineer working with Kubernetes may encounter:

```text
ssh -L ...
```

in one environment and:

```text
kubectl port-forward ...
```

in another.

The operational principle is similar:

> **Provide temporary local access to a service that is not directly exposed.**

Do not turn this topic into Kubernetes administration.

---

# 38. Cloud Provider Session and Port-Forwarding Mechanisms — Awareness

Modern cloud platforms may provide managed access mechanisms that can establish temporary sessions or port forwarding without exposing a server's SSH port publicly.

Conceptually:

```text
Engineer
   |
   | identity-aware session
   v
Cloud management plane
   |
   v
Private server/service
```

Benefits can include:

- identity-based access;
- temporary sessions;
- centralized auditing;
- reduced public exposure;
- less dependence on manually managed SSH entry points.

Examples of the general pattern include cloud session-management and managed port-forwarding facilities.

The architectural lesson is:

> **Use the access mechanism that fits the organization's identity, network, auditing, and security model.**

This is awareness only, not AWS/Azure/GCP certification training.

---

# 39. Auto-Reconnect and Production Reliability

A personal SSH tunnel should not normally become the reliability mechanism for a production pipeline.

### Bad architecture

```text
Production ETL
    |
    v
Developer laptop
    |
    v
Personal SSH tunnel
    |
    v
Production database
```

Potential failure modes:

- laptop sleeps;
- VPN disconnects;
- network changes;
- user logs out;
- laptop is unavailable;
- tunnel dies;
- credentials expire;
- local process crashes.

### Better architecture

```text
Production application
        |
        v
Private network
        |
        v
Private database
```

The application and database communicate through proper infrastructure.

---

# 40. When SSH Tunneling Is the Wrong Answer

SSH tunneling is excellent for:

- operator access;
- debugging;
- development;
- temporary database access;
- internal web UI access;
- incident investigation;
- controlled administrative workflows.

It is generally not the correct permanent architecture for:

- high-availability production pipelines;
- permanent service-to-service connectivity;
- scalable production integrations;
- long-lived production application communication;
- infrastructure that depends on one engineer's laptop.

## Better architectural mechanisms

Depending on the environment, the correct solution may involve:

- private networking;
- VPC/VNet networking;
- firewall/security-group rules;
- private endpoints;
- service-to-service connectivity;
- VPN/private connectivity;
- managed network access;
- identity-aware access mechanisms.

The key principle:

> **An SSH tunnel can solve an operator-access problem without solving the underlying production networking problem.**

---

# 41. SSH Tunnel vs Production Private Networking

| Question | SSH Tunnel | Proper Private Networking |
|---|---|---|
| Best for | Temporary/operator access | Production application connectivity |
| Depends on laptop? | Often | No |
| Long-lived service path? | Usually inappropriate | Yes |
| High availability | Poor fit | Designed for it |
| Auditing | Possible but context-dependent | Infrastructure-level controls available |
| Scaling | Manual/limited | Designed for service connectivity |
| Typical use | Debugging/admin access | Application-to-application communication |

---

# 42. Operator Access vs Application Connectivity

Keep these two architecture classes separate.

## Operator access

```text
Engineer
   |
   v
Bastion
   |
   v
Private service
```

A tunnel can be appropriate.

## Application connectivity

```text
Application
   |
   v
Private network
   |
   v
Database/service
```

The application should normally not depend on:

```text
Engineer laptop
```

as a network component.

This distinction is one of the most important production lessons in Topic 02.

---

# 43. Production Security Model

## Principle 1 — Least privilege

Give engineers and services only the access required.

## Principle 2 — Bind local tunnels to localhost by default

Prefer:

```text
127.0.0.1
```

over broad interface exposure.

## Principle 3 — Do not expose databases for convenience

If PostgreSQL is private, keep it private.

Use controlled operator access rather than opening the database to the Internet.

## Principle 4 — Use bastions for controlled access

A bastion can provide a controlled entry point into private networks.

## Principle 5 — Do not use personal tunnels as permanent production architecture

A laptop is not a highly available network gateway.

## Principle 6 — Audit who can establish tunnels

Tunnel capability can provide meaningful network reach.

## Principle 7 — Protect SSH credentials

Use the key-management practices established in Topic 01.

## Principle 8 — Close tunnels when finished

Temporary access should remain temporary.

## Principle 9 — Prefer temporary/short-lived access where available

Managed access mechanisms may reduce long-lived credential and network exposure.

## Principle 10 — Understand the complete traffic path

Before opening a tunnel, know:

```text
Who listens?
Who can connect?
Where does traffic go?
Which server performs the next connection?
What service is exposed?
What trust boundary is crossed?
```

---

# 44. Production Data Engineering Scenarios

## Scenario A — Private PostgreSQL

A Data Engineer needs to inspect a private warehouse database without exposing PostgreSQL publicly.

Use:

```text
Laptop
   |
   v
Bastion
   |
   v
PostgreSQL
```

A local `-L` tunnel can provide temporary operator access.

---

## Scenario B — Airflow UI

A private Airflow web UI is reachable from the bastion.

Use:

```bash
ssh -L 8080:airflow.internal:8080 dataeng@bastion.example.com
```

Then:

```text
http://127.0.0.1:8080
```

---

## Scenario C — Grafana

A monitoring dashboard is private:

```text
Laptop
   |
   v
Bastion
   |
   v
Grafana
```

A temporary local forward can provide controlled access.

---

## Scenario D — MinIO

A private MinIO UI is accessible from the internal network.

A local forward can make the UI available through:

```text
127.0.0.1
```

without exposing MinIO publicly.

---

## Scenario E — Internal API

A Data Engineer needs to debug an internal HTTP endpoint.

A fixed local forward can expose a specific service endpoint to a local debugging tool.

The important questions remain:

```text
Is the service reachable from the SSH server?
Is the local listener correctly bound?
Is the target service healthy?
```

---

## Scenario F — Bastion Access

A private data server is only reachable through a bastion.

Use:

```text
ProxyJump
+
LocalForward
```

rather than attempting to make the private server publicly accessible.

---

## Scenario G — Architecture Review

A team proposes:

```text
Production ETL
    ↓
Engineer laptop
    ↓
SSH tunnel
    ↓
Production database
```

The correct engineering response is:

> **Do not treat the tunnel as the production network architecture.**

Investigate proper private connectivity.

---

# 45. Hands-On Lab Environment

Build:

```text
                       Laptop
                          |
                          |
                          v
                  +---------------+
                  |    Bastion    |
                  | SSH entrypoint |
                  +---------------+
                          |
                   Private network
                          |
             +------------+------------+
             |                         |
             v                         v
      +-------------+           +-------------+
      | Private     |           | Internal    |
      | PostgreSQL  |           | Web UI      |
      | :5432       |           | :8080       |
      +-------------+           +-------------+
```

The learner should practice:

1. local forwarding;
2. PostgreSQL access;
3. Python access;
4. browser access;
5. `-N`;
6. `-f`;
7. tunnel verification;
8. `ProxyJump`;
9. `LocalForward`;
10. safe localhost binding;
11. intentionally unsafe binding in a controlled lab;
12. remote forwarding;
13. dynamic SOCKS forwarding;
14. troubleshooting;
15. a tunnel helper script.

Never use real production systems.

---

# 46. Progressive Hands-On Labs

Every exercise follows:

```text
Objective
  ↓
Architecture
  ↓
Prerequisites
  ↓
Commands
  ↓
Expected behavior
  ↓
What happened
  ↓
Why it works
  ↓
Verification
  ↓
Failure scenario
  ↓
Diagnosis
  ↓
Fix
  ↓
Cleanup
  ↓
Key takeaway
```

---

## Lab 1 — Basic Local Forward

### Objective

Create a tunnel from a local port to a private service.

### Command

```bash
ssh -L 15432:private-postgres:5432 dataeng@bastion.example.com
```

### Verify

In another terminal:

```bash
ss -ltn
```

Look for:

```text
127.0.0.1:15432
```

### What happened?

SSH created a local listener and associated it with a forwarding rule.

### Key takeaway

A local port can represent a path to a private destination.

---

## Lab 2 — PostgreSQL Through the Tunnel

### Objective

Use `psql` through the local tunnel.

Create:

```bash
ssh -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Then:

```bash
psql \
  -h 127.0.0.1 \
  -p 15432 \
  -U analytics \
  -d warehouse
```

Verify:

```sql
SELECT current_database(), current_user;
```

### Key takeaway

`psql` does not need direct network access to PostgreSQL.

---

## Lab 3 — Python Through the Tunnel

Create the tunnel:

```bash
ssh -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Run Python:

```python
import psycopg

conn = psycopg.connect(
    host="127.0.0.1",
    port=15432,
    dbname="warehouse",
    user="analytics",
    password="YOUR_PRACTICE_PASSWORD",
)

with conn.cursor() as cur:
    cur.execute("SELECT current_database();")
    print(cur.fetchone())

conn.close()
```

### Key takeaway

Python sees a local endpoint; SSH handles the private route.

---

## Lab 4 — Browser Access to an Internal UI

Create:

```bash
ssh -N \
  -L 127.0.0.1:8080:airflow.internal:8080 \
  dataeng@bastion.example.com
```

Open:

```text
http://127.0.0.1:8080
```

### Key takeaway

A private web UI can be temporarily exposed only to the operator's local machine.

---

## Lab 5 — `-N`

Run:

```bash
ssh -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Explain:

- no remote shell;
- tunnel remains in the foreground;
- `Ctrl+C` closes it.

---

## Lab 6 — `-f`

Run:

```bash
ssh -f -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Verify:

```bash
ss -ltn
```

Inspect:

```bash
ps aux | grep '[s]sh'
```

Then close only the identified tunnel process.

### Key takeaway

Backgrounding is convenient but creates lifecycle responsibility.

---

## Lab 7 — ProxyJump + Forwarding

Configure:

```sshconfig
Host bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes

Host data-server
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_data
    IdentitiesOnly yes
    ProxyJump bastion
```

Then test:

```bash
ssh -J bastion \
  -L 15432:private-postgres:5432 \
  dataeng@10.0.2.20
```

### Key takeaway

`ProxyJump` controls the SSH path; local forwarding controls the local service access.

---

## Lab 8 — `LocalForward`

Add:

```sshconfig
Host data-server
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_data
    IdentitiesOnly yes
    ProxyJump bastion
    LocalForward 127.0.0.1:15432 private-postgres:5432
```

Run:

```bash
ssh data-server
```

Then in another terminal:

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

### Key takeaway

Repeatable tunnel workflows belong in configuration.

---

## Lab 9 — Safe Binding

Use:

```bash
ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Inspect:

```bash
ss -ltn
```

Confirm the listener is local.

### Key takeaway

Default operator tunnels should normally use loopback binding.

---

## Lab 10 — Controlled Broad Binding Demonstration

Only in a local lab, compare:

```bash
ssh -N \
  -L 0.0.0.0:15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Inspect:

```bash
ss -ltn
```

Observe the difference in binding.

### Security lesson

This can make the forwarded service reachable through other local network interfaces.

Do not perform this experiment against production infrastructure.

---

## Lab 11 — Remote Forwarding

In a controlled environment:

```bash
ssh -R 18080:127.0.0.1:8080 dataeng@bastion.example.com
```

Understand the path:

```text
Bastion
   |
   v
remote forwarded listener
   |
   v
SSH
   |
   v
Laptop:8080
```

### Questions

- Who can reach the remote listener?
- What service is behind it?
- Is that exposure intentional?
- What firewall rules apply?

---

## Lab 12 — Dynamic SOCKS

Start:

```bash
ssh -D 1080 dataeng@bastion.example.com
```

Configure a SOCKS-aware practice client to use:

```text
127.0.0.1:1080
```

Observe that destinations can be selected dynamically.

### Key takeaway

`-D` is broader than a single fixed `-L` destination.

---

## Lab 13 — Break the Local Port

Start one tunnel:

```bash
ssh -N \
  -L 15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Attempt a second tunnel on the same port.

### Expected symptom

```text
Address already in use
```

### Diagnose

```bash
ss -ltn
ps aux | grep '[s]sh'
```

Identify the existing tunnel.

### Key takeaway

A local port conflict is a local listener problem, not automatically a database problem.

---

## Lab 14 — Break the Target Port

Use an intentionally incorrect target port:

```bash
ssh -N \
  -L 15432:private-postgres:5433 \
  dataeng@bastion.example.com
```

Then test:

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

### Diagnose

The local listener can exist even though the target application connection fails.

### Key takeaway

```text
Listening
≠
Target service healthy
```

---

## Lab 15 — Break `ProxyJump`

Intentionally use an incorrect jump-host alias.

Run:

```bash
ssh -vv data-server
```

Identify the first configuration/path failure.

Repair it.

### Key takeaway

Troubleshoot one network layer at a time.

---

## Lab 16 — Tunnel Helper Workflow

Create:

```text
tunnels.sh
```

with:

```bash
#!/usr/bin/env bash

set -euo pipefail

ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  data-server
```

Then improve it with `open`, `check`, and `close` operations.

Document:

```text
How to open
How to verify
How to use
How to close
```

### Key takeaway

A repeatable operator workflow is safer than remembering a long command.

---

# 47. Break/Fix Exercises

Use:

```text
Read
→ Do
→ Make repeatable
→ Break
→ Diagnose from evidence
→ Fix
→ Verify
→ Write runbook entry
→ Explain aloud
```

## Break/Fix 1 — Local Port Already Occupied

### Symptom

```text
Address already in use
```

### Evidence

```bash
ss -ltn
```

### Diagnosis

Another process owns the local port.

### Fix

Close the verified stale tunnel or choose another local port.

### Verification

Recreate the tunnel and test the application.

### Prevention

Track tunnel lifecycle and avoid unnecessary background processes.

---

## Break/Fix 2 — Wrong Target Port

### Symptom

Tunnel appears to start, application cannot connect.

### Evidence

Review:

```text
target_host:target_port
```

### Diagnosis

The private service is on another port.

### Fix

Correct the forwarding destination.

### Verification

Test with `psql` or the relevant application.

---

## Break/Fix 3 — Wrong Target Hostname

### Symptom

Application cannot connect.

### Evidence

Use verbose SSH output and validate the destination from the SSH server-side environment.

### Diagnosis

Private DNS or hostname is incorrect.

### Fix

Correct the destination.

---

## Break/Fix 4 — Stop PostgreSQL

### Symptom

The tunnel listens, but `psql` fails.

### Diagnosis

The target service is unavailable.

### Key lesson

The tunnel is not the application.

---

## Break/Fix 5 — Broken `ProxyJump`

### Symptom

Bastion works, private target does not.

### Diagnosis

Inspect jump-host configuration and each hop independently.

---

## Break/Fix 6 — Wrong Bind Address

### Symptom

A forwarded service appears reachable from another machine.

### Evidence

```bash
ss -ltn
```

### Diagnosis

The tunnel was bound to a broader interface.

### Fix

Prefer:

```text
127.0.0.1
```

unless broader exposure is explicitly required.

---

## Break/Fix 7 — Forgotten Background Tunnel

### Symptom

A new tunnel cannot bind to the desired port.

### Evidence

```bash
ps aux | grep '[s]sh'
```

### Fix

Identify and safely close the old tunnel.

---

## Break/Fix 8 — Bastion Cannot Reach Service

### Symptom

SSH authentication works, tunnel exists, application fails.

### Diagnosis

Check:

- private DNS;
- routing;
- firewall;
- security group;
- target service.

Do not automatically change SSH credentials.

---

# 48. Practical Command Reference

| Command | Purpose | Example | Important consideration |
|---|---|---|---|
| `ssh -L` | Local forwarding | `ssh -L 15432:db:5432 bastion` | Local listener can expose a path |
| `ssh -R` | Remote forwarding | `ssh -R 18080:localhost:8080 bastion` | Can expose local services remotely |
| `ssh -D` | Dynamic SOCKS proxy | `ssh -D 1080 bastion` | Broad destination capability |
| `ssh -N` | No remote command | `ssh -N -L ...` | Ideal for tunnel-only sessions |
| `ssh -f` | Background SSH | `ssh -f -N -L ...` | Easy to forget |
| `ssh -J` | Jump host | `ssh -J bastion target` | Provides SSH path through bastion |
| `ssh -v` | Verbose diagnostics | `ssh -v ...` | Start here for troubleshooting |
| `ssh -vv` | More diagnostics | `ssh -vv ...` | More connection detail |
| `ssh -vvv` | Maximum common verbosity | `ssh -vvv ...` | Use when needed; output can be large |
| `ss -ltn` | Inspect TCP listeners | `ss -ltn` | Confirms local listening sockets |
| `ps` | Inspect processes | `ps aux` | Identify tunnel process before termination |

---

# 49. Command Patterns

## PostgreSQL tunnel

```bash
ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

## PostgreSQL client

```bash
psql \
  -h 127.0.0.1 \
  -p 15432 \
  -U analytics \
  -d warehouse
```

## Internal web UI

```bash
ssh -N \
  -L 127.0.0.1:8080:airflow.internal:8080 \
  dataeng@bastion.example.com
```

Browser:

```text
http://127.0.0.1:8080
```

## Background tunnel

```bash
ssh -f -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

## ProxyJump + forwarding

```bash
ssh -J bastion \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@private-server
```

## Remote forwarding

```bash
ssh -R 18080:127.0.0.1:8080 dataeng@bastion.example.com
```

## SOCKS

```bash
ssh -D 1080 dataeng@bastion.example.com
```

---

# 50. Comparison: Fixed Forwarding vs Dynamic Forwarding

| Dimension | Fixed `-L` | Dynamic `-D` |
|---|---|---|
| Destination | Explicit | Selected by application |
| Scope | Narrow | Potentially broad |
| Typical use | One database/UI/API | Proxy-aware multi-destination access |
| Operational reasoning | Easier | More complex |
| Exposure risk | Specific service | Potentially many services |
| Recommended default | Often appropriate for operator access | Use only when broader proxy capability is justified |

---

# 51. Comparison: Foreground vs Background Tunnel

| Dimension | Foreground | Background |
|---|---|---|
| Flag | No `-f` | `-f` |
| Visibility | High | Lower |
| Closing | `Ctrl+C` | Identify and terminate process |
| Forgetting risk | Lower | Higher |
| Good for | Debugging/interactive use | Repeatable short operator workflows |
| Operational burden | Simple | Requires lifecycle management |

---

# 52. Comparison: SSH Tunnel vs Direct Network Access

| Dimension | SSH Tunnel | Direct Private Network |
|---|---|---|
| Operator setup | Easy | Requires network access |
| Temporary access | Excellent | May require broader permissions |
| Production service path | Usually poor fit | Appropriate |
| Laptop dependency | Often | No |
| Scope | Per tunnel | Infrastructure-defined |
| Long-lived connectivity | Fragile | Designed for it |
| Best use | Human/operator access | Application connectivity |

---

# 53. Interview Preparation

## Question 1 — What is SSH port forwarding?

### Answer

SSH port forwarding transports TCP connections through an SSH connection so a local or remote listener can reach a destination that would otherwise not be directly reachable.

---

## Question 2 — Explain `ssh -L`.

### Answer

`-L` creates local port forwarding:

```text
local_port → target_host:target_port
```

through the SSH connection.

Example:

```bash
ssh -L 15432:private-postgres:5432 dataeng@bastion.example.com
```

---

## Question 3 — Explain `ssh -R`.

### Answer

`-R` creates remote port forwarding, placing the forwarded listener on the remote side and providing a path toward a destination reachable through the SSH connection.

---

## Question 4 — Explain `ssh -D`.

### Answer

`-D` creates a local SOCKS proxy. Applications configured to use that SOCKS endpoint can dynamically request connections to destinations reachable through the SSH server.

---

## Question 5 — What is a SOCKS proxy?

### Answer

A SOCKS proxy is a proxy endpoint through which a proxy-aware application can request connections to different destinations. With SSH `-D`, the SSH server becomes the network path for those requests.

---

## Question 6 — Why would a Data Engineer use SSH tunneling?

### Answer

To obtain temporary, controlled access from a laptop to private databases, internal web UIs, APIs, or other services without exposing those services publicly.

---

## Question 7 — How would you access a private PostgreSQL server?

### Answer

Create a local forward:

```bash
ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@bastion.example.com
```

Then:

```bash
psql -h 127.0.0.1 -p 15432 -U analytics -d warehouse
```

---

## Question 8 — What does `-N` do?

### Answer

It tells SSH not to execute a remote command or shell. It is useful when the SSH connection exists only to provide forwarding.

---

## Question 9 — What does `-f` do?

### Answer

It requests that SSH move into the background after authentication. It is convenient for tunnels but creates lifecycle-management responsibility.

---

## Question 10 — Why bind to `127.0.0.1`?

### Answer

It restricts the local listener to the loopback interface, which normally prevents other network machines from directly connecting to the forwarded port.

---

## Question 11 — What is the risk of `0.0.0.0`?

### Answer

It can make the local forwarded listener available on all local IPv4 interfaces, potentially allowing other machines that can reach the laptop to use the tunnel.

---

## Question 12 — How does `ProxyJump` work with port forwarding?

### Answer

`ProxyJump` provides the SSH path through one or more bastions, while port forwarding defines the local/remote listener and destination carried through that path.

---

## Question 13 — What is `LocalForward`?

### Answer

`LocalForward` is the SSH configuration directive corresponding to local port forwarding. It makes a forwarding rule part of a reusable `Host` configuration.

---

## Question 14 — How would you troubleshoot a tunnel?

### Answer

Check the local listener, inspect SSH verbose output, verify the ProxyJump path, confirm the target hostname and port from the server-side network, verify the target service, and finally test the application protocol.

---

## Question 15 — Why should production applications generally not depend on personal SSH tunnels?

### Answer

Because a personal laptop and interactive SSH session are not highly available infrastructure. Sleep, network changes, user logout, credential expiration, or process failure can break the application.

Production applications should normally use proper private networking.

---

## Question 16 — How is `kubectl port-forward` conceptually different?

### Answer

It is Kubernetes' own mechanism for forwarding local traffic to a Kubernetes pod/service through Kubernetes control-plane mechanisms. The access pattern resembles temporary SSH forwarding, but the underlying mechanism and trust model differ.

---

## Question 17 — What is the difference between application retry and SSH tunnel availability?

### Answer

Application retry can retry application connections, but it cannot succeed if the underlying tunnel is unavailable. Conversely, a healthy tunnel does not guarantee an application's session or connection pool will recover correctly.

---

# 54. Topic 02 Practice Questions

These are reinforcement questions for this topic only. They do not replace the consolidated G2 practice set.

## Beginner

### 1. Question

What problem does an SSH tunnel solve?

### Expected Thinking

Think:

```text
Laptop cannot reach private service
        ↓
Bastion can
        ↓
SSH provides a path
```

### Solution

It provides a controlled path through an SSH connection so local or remote traffic can reach a service that is not directly reachable from the originating machine.

---

### 2. Question

What does this mean?

```bash
ssh -L 15432:private-postgres:5432 dataeng@bastion.example.com
```

### Solution

Listen locally on port `15432` and forward connections through the SSH server to `private-postgres:5432`.

---

### 3. Question

What should `psql` use?

```text
private-postgres:5432
```

or:

```text
127.0.0.1:15432
```

### Solution

For the local tunnel, `psql` uses:

```text
127.0.0.1:15432
```

---

### 4. Question

What does `-N` do?

### Solution

It prevents SSH from opening a remote command/shell and is useful for tunnel-only connections.

---

### 5. Question

Why is `127.0.0.1` usually safer than `0.0.0.0`?

### Solution

`127.0.0.1` restricts the listener to the local machine, while `0.0.0.0` can expose it through other local interfaces.

---

## Intermediate

### 6. Question

The tunnel starts, but PostgreSQL connection fails. What do you check?

### Solution

Check:

```text
local listener
target hostname
target port
bastion → target reachability
PostgreSQL health
database authentication
```

Do not assume SSH authentication is the problem.

---

### 7. Question

Why might `ssh -f -N ...` be operationally risky?

### Solution

The background process can be forgotten and later cause port conflicts or leave temporary access open longer than intended.

---

### 8. Question

What does this configuration do?

```sshconfig
LocalForward 127.0.0.1:15432 private-postgres:5432
```

### Solution

It configures local port `15432` to forward through the SSH connection to `private-postgres:5432`.

---

### 9. Question

Why combine `ProxyJump` and local forwarding?

### Solution

To reach a private service through a bastion while providing a local endpoint for tools such as `psql`.

---

### 10. Question

What does a listening local port prove?

### Solution

It proves something is listening locally. It does not prove the target service is reachable or healthy.

---

## Advanced

### 11. Question

Compare:

```text
-L
-R
-D
```

### Solution

```text
-L → local fixed forwarding
-R → remote fixed forwarding
-D → local dynamic SOCKS proxy
```

---

### 12. Question

Why can `-R` be more dangerous than it first appears?

### Solution

It can make a local service reachable from the remote side, potentially bypassing intended network boundaries.

---

### 13. Question

Why is `-D` broader than `-L`?

### Solution

`-L` maps one local listener to one configured destination. `-D` creates a SOCKS proxy through which applications can dynamically request multiple destinations reachable from the SSH server.

---

### 14. Question

A bastion is reachable and SSH authentication succeeds, but a private database cannot be reached. What is your next hypothesis?

### Solution

Investigate server-side DNS, routing, firewall/security-group rules, and database availability.

---

### 15. Question

A team wants to keep a production ETL alive through an engineer's laptop SSH tunnel. What is wrong with the design?

### Solution

The laptop and interactive tunnel become a fragile production dependency. The application should use proper private network connectivity.

---

## Troubleshooting

### 16. Question

You receive:

```text
Address already in use
```

What do you check?

### Solution

Inspect:

```bash
ss -ltn
ps aux | grep '[s]sh'
```

Identify which process owns the port before changing anything.

---

### 17. Question

The local port is listening, but `psql` cannot connect. What does that tell you?

### Solution

The local forwarding listener exists, but the complete path or target application may still be failing.

---

### 18. Question

Why is `ssh -vv` useful?

### Solution

It provides additional evidence about SSH configuration, authentication, jump-host behavior, and forwarding setup.

---

### 19. Question

How do you safely close a background tunnel?

### Solution

Identify the exact tunnel process and terminate that process rather than killing unrelated SSH sessions.

---

### 20. Question

What is the correct order of investigation?

### Solution

```text
local listener
→ SSH connection
→ ProxyJump path
→ server-side target reachability
→ target service
→ application protocol
→ application authentication
```

---

## Architecture

### 21. Question

When is SSH tunneling appropriate?

### Solution

Temporary operator access, debugging, development, controlled database/UI access, and incident investigation.

---

### 22. Question

When is it inappropriate?

### Solution

As a permanent, highly available service-to-service production network path.

---

### 23. Question

Why can a tunnel hide a networking problem?

### Solution

It can make an inaccessible private service reachable for one operator without fixing the underlying network architecture needed by applications.

---

### 24. Question

What should replace a personal production tunnel?

### Solution

The appropriate private networking architecture, such as private network routing, firewall/security-group policy, private endpoints, or managed connectivity.

---

## Security

### 25. Question

What is the main security question for a local forward?

### Solution

Who can reach the local listener?

---

### 26. Question

What is the main security question for remote forwarding?

### Solution

Who can reach the remote listener and what local service becomes reachable through it?

---

### 27. Question

What is the main security question for dynamic SOCKS forwarding?

### Solution

Which destinations can the proxy reach through the SSH server?

---

### 28. Question

Why should tunnel listeners normally use loopback?

### Solution

It minimizes accidental exposure by restricting access to the local machine.

---

### 29. Question

Why is closing a tunnel part of security hygiene?

### Solution

An open tunnel is an active network access path. Leaving it open unnecessarily extends the access window.

---

### 30. Question

What should you understand before opening a tunnel?

### Solution

The listener address/port, who can reach it, the SSH path, the target destination, the target service, and the trust boundaries crossed.

---

# 55. Operational Runbook

## 55.1 Open a PostgreSQL tunnel

```bash
ssh -N \
  -L 127.0.0.1:15432:private-postgres:5432 \
  data-server
```

## 55.2 Verify the local listener

```bash
ss -ltn
```

Look for:

```text
127.0.0.1:15432
```

## 55.3 Test PostgreSQL

```bash
psql \
  -h 127.0.0.1 \
  -p 15432 \
  -U analytics \
  -d warehouse
```

## 55.4 Open an internal web UI

```bash
ssh -N \
  -L 127.0.0.1:8080:airflow.internal:8080 \
  data-server
```

Open:

```text
http://127.0.0.1:8080
```

## 55.5 Use ProxyJump

```bash
ssh -J bastion \
  -L 127.0.0.1:15432:private-postgres:5432 \
  dataeng@private-server
```

## 55.6 Inspect a failed tunnel

```bash
ssh -vv ...
```

Then:

```bash
ss -ltn
```

Check:

```text
destination
port
ProxyJump
routing
firewall
target service
```

## 55.7 Close a foreground tunnel

```text
Ctrl+C
```

## 55.8 Close a background tunnel

Inspect:

```bash
ps aux | grep '[s]sh'
```

Identify the correct process.

Terminate that specific PID:

```bash
kill PID
```

Verify:

```bash
ss -ltn
```

## 55.9 Diagnose exposure

If you suspect a tunnel is too broadly exposed:

```bash
ss -ltn
```

Look for:

```text
127.0.0.1
```

versus:

```text
0.0.0.0
```

## 55.10 Stop and redesign when appropriate

If the tunnel is becoming:

```text
permanent
+
production-critical
+
application-dependent
+
high availability sensitive
```

stop treating SSH as the architecture.

Escalate to the proper private-networking solution.

---

# 56. Important Distinctions

## Tunnel vs network route

A tunnel transports traffic through an SSH connection.

It does not magically change the underlying network architecture.

---

## Local port vs remote destination

```text
127.0.0.1:15432
```

is the local listener.

```text
private-postgres:5432
```

is the destination reached through the tunnel.

They are not the same endpoint.

---

## SSH authentication vs target reachability

Successful SSH authentication means:

```text
You authenticated to the SSH server.
```

It does not mean:

```text
The SSH server can reach the target service.
```

---

## Listening socket vs healthy application

A listener proves:

```text
Something is listening locally.
```

It does not prove:

```text
PostgreSQL/Airflow/API is healthy.
```

---

## Tunnel vs production networking

A tunnel can solve:

```text
"How can I, the operator, temporarily reach this private service?"
```

without solving:

```text
"How should production applications reach this service reliably?"
```

---

# 57. Security Guardrails

Never use:

- real passwords;
- real private keys;
- real production IP addresses;
- real corporate infrastructure;
- real production database endpoints.

Use:

```text
bastion.example.com
private-postgres.internal
dataeng
127.0.0.1
```

Before demonstrating broader binding such as:

```text
0.0.0.0
```

understand the exposure it creates.

Before using remote forwarding, understand:

```text
Who can reach the remote listener?
```

Before using dynamic SOCKS forwarding, understand:

```text
Which destinations can the proxy reach?
```

---

# 58. Topic Boundaries

This module belongs to:

```text
02-Linux-and-Shell-for-Data-Servers/
```

and specifically:

```text
Topic 02 — SSH Tunnels and Port Forwarding for Data Tools
```

It does not deeply teach:

- SSH key generation;
- SSH configuration fundamentals;
- `tmux`;
- `rsync`;
- `rclone`;
- `systemd`;
- Linux CPU/memory monitoring;
- disk/inode management;
- `jq`;
- `csvkit`;
- Miller;
- DuckDB;
- log investigation;
- users/sudo/package management.

The G2 progression is:

```text
Topic 01
SSH access, identity, config, jump hosts
        ↓
Topic 02
SSH tunnels and port forwarding
        ↓
Topic 03
tmux
        ↓
Topic 04
file transfer
        ↓
Topic 05
systemd
        ↓
Topic 06
resource monitoring
        ↓
Topic 07
disks
        ↓
Topic 08
CLI data tools
        ↓
Topic 09
logs
        ↓
Topic 10
server hygiene
```

Topic 02 may reference later topics for context, but it does not duplicate their curricula.

---

# 59. Final Knowledge Check

You should be able to demonstrate all of the following without blindly copying commands:

## Fundamentals

- [ ] Explain SSH tunneling in simple language.
- [ ] Draw the laptop → bastion → private service path.
- [ ] Explain local listener vs remote destination.
- [ ] Explain why the destination is reached from the SSH/server side.

## Local forwarding

- [ ] Create a local `-L` forward.
- [ ] Explain every important argument.
- [ ] Use `psql` through a tunnel.
- [ ] Use Python through a tunnel.
- [ ] Access an internal web UI through a tunnel.
- [ ] Explain `-N`.
- [ ] Explain `-f`.
- [ ] Identify a background tunnel.
- [ ] Close a tunnel safely.

## ProxyJump and configuration

- [ ] Combine `ProxyJump` and forwarding.
- [ ] Configure `LocalForward`.
- [ ] Explain the traffic path.
- [ ] Troubleshoot a broken jump path.

## Security

- [ ] Explain `127.0.0.1`.
- [ ] Explain why `0.0.0.0` can be dangerous.
- [ ] Inspect local listeners.
- [ ] Explain remote forwarding risk.
- [ ] Explain SOCKS proxy risk.
- [ ] Close temporary tunnels when finished.

## Advanced forwarding

- [ ] Explain `-R`.
- [ ] Explain `-D`.
- [ ] Explain SOCKS.
- [ ] Compare `-L`, `-R`, and `-D`.

## Troubleshooting

- [ ] Diagnose local port conflicts.
- [ ] Diagnose wrong target ports.
- [ ] Diagnose wrong target hosts.
- [ ] Diagnose bastion-to-target failures.
- [ ] Diagnose target service failures.
- [ ] Use `ssh -v`, `-vv`, and `-vvv`.
- [ ] Follow the tunnel troubleshooting decision tree.

## Production reasoning

- [ ] Explain auto-reconnect awareness.
- [ ] Explain `kubectl port-forward` conceptually.
- [ ] Explain cloud session/port-forwarding awareness.
- [ ] Explain why a personal SSH tunnel should not be a permanent production dependency.
- [ ] Recommend proper private networking when appropriate.

---

# 60. Topic 02 Checkpoint

The module is complete when you can safely do all of these:

1. Create a local PostgreSQL tunnel.
2. Connect with `psql`.
3. Connect with Python.
4. Access an internal web UI.
5. Use `-N`.
6. Understand and deliberately use `-f`.
7. Inspect and close tunnel processes.
8. Combine `ProxyJump` with local forwarding.
9. Configure `LocalForward`.
10. Explain `127.0.0.1` vs `0.0.0.0`.
11. Explain `-R` and its risks.
12. Explain `-D` and SOCKS.
13. Troubleshoot a failed tunnel from evidence.
14. Explain why production applications normally need proper private networking instead of a personal SSH tunnel.

A strong Data Engineer should be able to explain not only **how** the tunnel works, but also **why it is safe or unsafe in a particular architecture**.

---

# 61. Roadmap Coverage Audit

The Topic 02 source specification requires the following coverage.

| Required Topic 02 Concept | Covered |
|---|---:|
| SSH tunneling fundamentals | Yes |
| Local port forwarding | Yes |
| `-L` | Yes |
| PostgreSQL / `psql` | Yes |
| Python usage | Yes |
| Browser/web UI usage | Yes |
| `-N` | Yes |
| `-f` | Yes |
| Opening tunnels | Yes |
| Verifying tunnels | Yes |
| Closing tunnels | Yes |
| `ProxyJump` + forwarding | Yes |
| `LocalForward` | Yes |
| Safe bind addresses | Yes |
| `127.0.0.1` | Yes |
| `0.0.0.0` risk | Yes |
| Remote forwarding | Yes |
| `-R` | Yes |
| Remote-forwarding risks | Yes |
| Dynamic forwarding | Yes |
| `-D` | Yes |
| SOCKS proxy concepts | Yes |
| Auto-reconnecting tools awareness | Yes |
| `kubectl port-forward` awareness | Yes |
| Cloud port-forward/session awareness | Yes |
| When SSH tunneling is wrong | Yes |
| Proper private networking | Yes |
| Hands-on tunnel exercises | Yes |
| Tunnel helper script | Yes |
| Verification workflow | Yes |
| Verbose troubleshooting | Yes |
| Common failure modes | Yes |
| Troubleshooting decision tree | Yes |
| Data Engineering tools | Yes |
| Production scenarios | Yes |
| Security principles | Yes |
| Interview preparation | Yes |
| Topic-specific practice questions | Yes |
| Final knowledge check | Yes |
| Operational runbook | Yes |
| Scope boundaries | Yes |
| Topic checkpoint | Yes |

---

# 62. Final File Quality Checklist

- [x] Basic → intermediate → advanced → production progression.
- [x] Data Engineering context throughout.
- [x] Commands are explained.
- [x] Important arguments are explained.
- [x] Network diagrams are included.
- [x] PostgreSQL, Python, and browser examples are included.
- [x] `-N` and `-f` are explained.
- [x] Tunnel lifecycle is covered.
- [x] `ProxyJump` and `LocalForward` are covered.
- [x] `127.0.0.1` vs `0.0.0.0` is explained.
- [x] `-R` and its security implications are covered.
- [x] `-D` and SOCKS are covered.
- [x] Auto-reconnect awareness is included.
- [x] Kubernetes and cloud port-forwarding are awareness-only.
- [x] Production-networking boundaries are explicit.
- [x] Hands-on labs are progressive.
- [x] Break/fix exercises use evidence-based diagnosis.
- [x] Tunnel helper script is included.
- [x] Troubleshooting decision tree is included.
- [x] Operational runbook is included.
- [x] Practice questions are topic-specific.
- [x] Interview preparation is included.
- [x] Final knowledge check is included.
- [x] No real credentials are used.
- [x] No production endpoints are required.
- [x] Later G2 topics are not duplicated.
- [x] Roadmap coverage is explicitly audited.

---

# 63. Final Takeaway

The most important mental model in this topic is:

```text
                    OPERATOR ACCESS

Laptop
   |
   | SSH
   v
Bastion
   |
   | Private network
   v
Private service
```

For a fixed local service:

```text
-L
```

means:

```text
Local port
    ↓
Fixed destination
```

For reverse access:

```text
-R
```

means:

```text
Remote listener
    ↓
Local destination
```

For dynamic proxying:

```text
-D
```

means:

```text
Local SOCKS endpoint
    ↓
Dynamic destinations
```

But the production lesson goes beyond syntax.

A tunnel should make you think:

```text
Where does the listener exist?
        ↓
Who can reach it?
        ↓
Where does traffic go?
        ↓
Which machine makes the next connection?
        ↓
What service is exposed?
        ↓
Which trust boundary is crossed?
        ↓
Is this temporary operator access
or permanent application connectivity?
```

If the answer is:

```text
Temporary operator access
```

an SSH tunnel can be an excellent tool.

If the answer is:

```text
Permanent production application connectivity
```

the correct next step is normally to fix or design the underlying private networking architecture rather than making a personal SSH tunnel more permanent.

That distinction is the core production skill of Topic 02.
