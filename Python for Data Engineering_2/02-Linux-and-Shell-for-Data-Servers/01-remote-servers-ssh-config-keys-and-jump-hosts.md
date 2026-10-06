# Remote Servers — SSH Config, Keys, and Jump Hosts

> **Stage 2B — Gap Module G2: Linux and Shell for Data Servers**
>
> **Topic 01:** Remote servers, SSH config, keys, and jump hosts
> **Learning progression:** Beginner → Core SSH → Intermediate → Advanced → Production Data Engineering
> **Primary outcome:** Confidently and securely connect to remote Linux data servers, manage SSH credentials, use bastions/jump hosts, automate remote checks, and troubleshoot access failures from evidence.

---

## 1. What This Topic Is About

Data Engineers rarely operate every pipeline, database, scheduler, object-storage gateway, or Spark environment directly on their laptop. Production workloads normally run on Linux servers, virtual machines, private subnets, or managed infrastructure.

That creates a fundamental operational question:

> **How do I securely reach a machine that I cannot physically sit in front of?**

The answer in many environments is **SSH — Secure Shell**.

This topic teaches SSH as a **Data Engineering server-access skill**, not as a generic Linux administration course. You will learn how to:

- connect to remote Linux servers;
- authenticate with public-key credentials;
- protect and rotate SSH keys;
- use `~/.ssh/config` to make access repeatable;
- use `ssh-agent` safely;
- understand the risks of agent forwarding;
- enter private networks through bastions/jump hosts;
- use `ProxyJump`;
- verify server identity through host keys;
- investigate changed-host-key warnings;
- keep SSH connections healthy;
- reuse SSH connections efficiently;
- run noninteractive operational checks;
- reason correctly about exit codes and shell quoting;
- troubleshoot access failures systematically.

### The server-operator loop

The G2 roadmap uses this learning loop:

```text
Read
  ↓
Do it on a real practice server
  ↓
Make it repeatable
  ↓
Break it
  ↓
Diagnose from evidence
  ↓
Fix it
  ↓
Write the runbook entry
  ↓
Explain it aloud
```

Do not learn SSH by memorizing commands. Learn the **connection model**, then use commands to operate that model.

---

# 2. Prerequisites and Scope

G2 assumes that you already know basic command-line navigation, text processing, pipes, redirection, shell scripts, permissions, quoting, processes, signals, and basic SSH-key usage from earlier stages.

This topic extends those skills into **server-side operations**.

## Practice environment

Use one of these safe environments:

1. **Containers** — two or three SSH-enabled Linux containers on a private Docker network; one is the bastion and the others are private servers.
2. **Local VMs** — lightweight Ubuntu VMs or another Linux VM setup.
3. **Small cloud VMs** — one public bastion and one private server, with a budget alert and immediate teardown after practice.

Use placeholders such as:

```text
bastion.example.com
private-data.example.internal
dataeng
```

Never use real production credentials or private keys in a learning file.

---

# 3. Learning Progression

```text
LEVEL 1 — BEGINNER
    Remote server
        ↓
    SSH client/server
        ↓
    ssh user@host
        ↓
    SSH connection flow
        ↓
    Authentication vs authorization

LEVEL 2 — CORE SSH
    Public/private keys
        ↓
    Ed25519
        ↓
    authorized_keys
        ↓
    ssh-copy-id
        ↓
    ~/.ssh/config

LEVEL 3 — INTERMEDIATE
    ssh-agent
        ↓
    Agent forwarding and its risks
        ↓
    Bastion architecture
        ↓
    ProxyJump
        ↓
    Host-key verification

LEVEL 4 — ADVANCED
    Keepalives
        ↓
    Connection multiplexing
        ↓
    Key separation
        ↓
    Key rotation/revocation
        ↓
    Noninteractive SSH
        ↓
    Exit codes and quoting

LEVEL 5 — PRODUCTION DATA ENGINEERING
    Secure access architecture
        ↓
    Break/fix troubleshooting
        ↓
    Incident reasoning
        ↓
    Operational runbook
        ↓
    Final checkpoint
```

Do not skip directly to `ProxyJump`. A Data Engineer who can copy a configuration but cannot explain authentication, host identity, or the network path will struggle during an incident.

---

# 4. Remote Servers: The Mental Model

## 4.1 What is a remote server?

A **remote server** is a computer whose operating system and resources are accessed over a network rather than through the keyboard and display in front of you.

For a Data Engineer, that server may run:

- an ingestion process;
- a PostgreSQL database;
- an Airflow deployment;
- a Spark environment;
- a data-quality job;
- a pipeline API;
- a staging area;
- a private data service.

Your laptop is the **local machine**.

The server is the **remote machine**.

```text
+-----------------------+          Network          +-----------------------+
| Data Engineer laptop  | ------------------------> | Linux data server    |
|                       |           SSH             |                       |
| SSH client            |                           | SSH daemon (sshd)     |
| ~/.ssh/config         |                           | user accounts         |
| private keys          |                           | authorized_keys       |
+-----------------------+                           +-----------------------+
```

## 4.2 Why Data Engineers use remote Linux servers

Remote Linux access matters because:

- production workloads should not depend on your laptop;
- servers can be inside private networks;
- data may be too large to move locally;
- services need stable compute and network access;
- cloud data services often live behind network controls;
- incidents frequently require direct server inspection.

SSH therefore becomes part of the operational interface to the data platform.

---

# 5. SSH Client vs SSH Server

## 5.1 SSH client

The **SSH client** is the program you run when you type:

```bash
ssh user@server
```

It usually runs on your laptop or another machine from which you initiate access.

The OpenSSH client includes commands such as:

```bash
ssh
ssh-keygen
ssh-add
ssh-agent
```

## 5.2 SSH server

The remote machine runs an SSH server, commonly provided by **OpenSSH**.

Its daemon is commonly called:

```text
sshd
```

Conceptually:

```text
LOCAL MACHINE                         REMOTE MACHINE
-------------                        --------------
ssh client       ===== SSH =====>    sshd
```

The client initiates the connection. The server accepts and authenticates it.

## 5.3 SSH protocol

SSH is an encrypted protocol used for secure remote access and related operations.

At a conceptual level it provides:

- confidentiality for the session;
- integrity protection;
- server identity verification through host keys;
- user authentication;
- interactive and noninteractive sessions.

Do not reduce SSH to "a command that opens a terminal." The SSH command is the user interface to a protocol with several security stages.

---

# 6. What Happens When You Run `ssh user@server`?

Start with the simple model:

```bash
ssh user@server
```

Think:

```text
1. Find the server
2. Connect to it
3. Negotiate SSH
4. Verify the server's identity
5. Prove the user's identity
6. Establish a session
7. Run the shell
8. Execute commands
9. Close the session
```

## 6.1 Detailed connection flow

### Step 1 — Name resolution

If `server` is a hostname, the client needs an IP address.

Conceptually:

```text
server.example.com
        ↓
DNS/name resolution
        ↓
203.0.113.10
```

You can inspect resolution with:

```bash
getent hosts server.example.com
```

or, where available:

```bash
dig server.example.com
```

The important point is that **DNS answers "where is this hostname?"** It does not authenticate the server.

### Step 2 — TCP connection

SSH normally uses TCP port `22`.

```text
Laptop
  |
  | TCP connection to server:22
  v
sshd
```

For a custom port:

```bash
ssh -p 2222 dataeng@server.example.com
```

Here:

- `-p 2222` selects the destination TCP port;
- `dataeng` is the remote user;
- `server.example.com` is the destination hostname.

A wrong port can produce errors such as:

```text
Connection refused
```

or:

```text
Connection timed out
```

Those are not automatically authentication failures.

### Step 3 — SSH protocol negotiation

The client and server negotiate compatible SSH protocol parameters and cryptographic algorithms.

You do not need to memorize the algorithm list to operate SSH safely at this stage.

The important mental model is:

> **The client and server first establish an SSH-protected communication channel before user authentication is completed.**

### Step 4 — Host-key verification

The server presents a **host key**.

Your client checks whether it recognizes that server identity, commonly using:

```text
~/.ssh/known_hosts
```

On a first connection you may see:

```text
The authenticity of host 'server.example.com' can't be established.
ED25519 key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Do not automatically type `yes`.

Verify the fingerprint through a trusted channel when the environment is security-sensitive.

### Step 5 — User authentication

The server now needs to establish:

> "Can this user prove that they are allowed to authenticate as this account?"

For public-key authentication, the client proves possession of the private key corresponding to a public key accepted by the server.

### Step 6 — Session establishment

After authentication succeeds, SSH establishes the requested session.

For an interactive connection:

```bash
ssh dataeng@server.example.com
```

you receive a remote shell.

### Step 7 — Remote shell

Your prompt now represents the remote machine.

For example:

```text
dataeng@pipeline-server:~$
```

The commands you type are interpreted by the remote shell.

### Step 8 — Command execution

If you type:

```bash
hostname
```

the command executes on the remote server.

### Step 9 — Session termination

When you run:

```bash
exit
```

or press:

```text
Ctrl-D
```

the remote shell terminates and the SSH session closes.

---

# 7. Hostname vs IP Address vs SSH Port

These three concepts are easy to mix up.

| Concept | Example | Meaning |
|---|---|---|
| Hostname | `pipeline.example.com` | Human-friendly network name |
| IP address | `203.0.113.20` | Network address |
| SSH port | `22` | TCP port where SSH is listening |

You can connect using an IP:

```bash
ssh dataeng@203.0.113.20
```

or a hostname:

```bash
ssh dataeng@pipeline.example.com
```

A hostname is generally preferable when infrastructure may change because the name can remain stable while the underlying IP changes.

---

# 8. Authentication vs Authorization

These concepts must remain separate.

## Authentication

Authentication asks:

> **Who are you?**

Example:

```text
Can this client prove it possesses the private key?
```

## Authorization

Authorization asks:

> **What is this authenticated identity allowed to do?**

For example, after authentication, the account might:

- access `/data`;
- read a specific service directory;
- run permitted commands;
- have no `sudo` access.

### Mental model

```text
Authentication
    ↓
"Can you prove who you are?"
    ↓
Authorization
    ↓
"What are you allowed to access/do?"
```

A valid SSH key does not automatically make a user root.

---

# 9. Password Authentication vs Public-Key Authentication

## 9.1 Password authentication

The traditional model is:

```text
Client → username/password → server
```

Problems in production include:

- password reuse;
- phishing;
- brute-force attempts;
- credential leakage;
- shared-password practices;
- operational difficulty when many servers are involved.

Password authentication can be appropriate in controlled circumstances, but production environments often prefer stronger centralized controls and/or key-based access.

## 9.2 Public-key authentication

The basic model is:

```text
Laptop
  |
  | private key remains secret
  |
  +--------------------+
                       |
                       v
Server
  |
  | authorized public key
  v
Accept authentication
```

The private key is not sent to the server as a password.

The server has a corresponding public key and verifies that the client can prove possession of the private key.

### Core mental model

```text
Private key = secret proof
Public key  = verification material
```

The private key must remain private.

---

# 10. Ed25519 SSH Keys

The G2 roadmap prefers **Ed25519** for new SSH key generation.

## 10.1 Generate an Ed25519 key

```bash
ssh-keygen -t ed25519
```

Break it down:

- `ssh-keygen` — OpenSSH key-generation utility;
- `-t` — select key type;
- `ed25519` — select Ed25519.

You will be prompted for a filename and passphrase.

A typical result is:

```text
~/.ssh/id_ed25519
~/.ssh/id_ed25519.pub
```

The exact filename can differ if you choose another name.

## 10.2 Private vs public file

```text
id_ed25519
    ↓
PRIVATE KEY — protect it

id_ed25519.pub
    ↓
PUBLIC KEY — can be installed on servers
```

Inspect the directory:

```bash
ls -la ~/.ssh/
```

You might see:

```text
-rw-------  id_ed25519
-rw-r--r--  id_ed25519.pub
```

## 10.3 Protect the directory and private key

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

Meaning:

- `700` on `~/.ssh` — only the owner can access the directory;
- `600` on the private key — only the owner can read/write it;
- `644` on the public key — it is not secret.

The exact permissions accepted by OpenSSH can vary with platform and configuration, but the principle is constant:

> **A private key must not be broadly readable.**

If the private key is exposed, assume it may be compromised.

## 10.4 Passphrases

A passphrase protects the private key on disk.

Think of it as:

```text
Private key
    +
Passphrase
    ↓
Protected credential
```

A passphrase does not replace server-side authorization. It protects the local private-key material.

---

# 11. `authorized_keys`

The remote user's SSH authorization file is commonly:

```text
~/.ssh/authorized_keys
```

Conceptually:

```text
SERVER
~/.ssh/authorized_keys
        |
        +-- public key A
        +-- public key B
        +-- public key C
```

Each authorized public key can represent a different device, person, automation identity, or access purpose.

## 11.1 How authentication uses it

Suppose your laptop owns:

```text
~/.ssh/id_ed25519
```

and the corresponding public key is:

```text
~/.ssh/id_ed25519.pub
```

The server may have that public key in:

```text
~/.ssh/authorized_keys
```

During authentication, the server checks whether the client's proof corresponds to an authorized public key.

## 11.2 View your public key

```bash
cat ~/.ssh/id_ed25519.pub
```

The output is a single public-key line.

Do not confuse this with:

```bash
cat ~/.ssh/id_ed25519
```

Never publish the private-key contents.

## 11.3 `ssh-copy-id`

If password authentication or another bootstrap path is available, you can use:

```bash
ssh-copy-id user@server.example.com
```

Conceptually, `ssh-copy-id`:

1. authenticates using an existing method;
2. obtains the public key from your local machine;
3. appends the public key to the remote user's authorization file;
4. makes subsequent public-key authentication possible.

It is an onboarding utility, not a magic security mechanism.

## 11.4 Manual conceptual equivalent

The conceptual operation is similar to:

```bash
cat id_ed25519.pub >> ~/.ssh/authorized_keys
```

But be careful: this command is context-sensitive.

It must be run **on the server**, with the correct user, correct file, and correct permissions. Blindly appending keys can:

- authorize the wrong identity;
- create duplicate entries;
- corrupt formatting;
- leave unauthorized access behind.

In production, treat `authorized_keys` as an access-control list.

---

# 12. SSH Key Lifecycle

A production SSH key is not "generate once and forget forever."

The lifecycle is:

```text
Create
  ↓
Protect
  ↓
Use
  ↓
Rotate
  ↓
Remove old authorization
  ↓
Audit
```

## 12.1 Creation

Generate the key for a specific purpose.

Example:

```text
id_ed25519_bastion
```

rather than an ambiguous key that will eventually be used everywhere.

## 12.2 Storage

Keep private keys in an appropriately protected local credential store or filesystem.

Do not:

- commit private keys to Git;
- put private keys into application repositories;
- paste them into chat;
- put them in shell history;
- email them around.

## 12.3 Usage

Use a passphrase and/or an SSH agent where appropriate.

## 12.4 Rotation

Replace keys periodically or according to organizational policy.

More importantly, rotate immediately when:

- a key is suspected to be exposed;
- a laptop is lost;
- an employee or contractor loses authorization;
- a credential boundary changes.

## 12.5 Removal

Remove old public keys from:

```text
~/.ssh/authorized_keys
```

Deleting the local private-key file does **not** revoke a public key already authorized on a server.

This is critical:

```text
Deleting local private key
        ≠
Removing server authorization
```

## 12.6 Separate credentials by trust boundary

Do not automatically use one key for:

```text
Personal machine
Development
Staging
Production
Bastion
Cloud servers
```

A practical pattern is:

```text
~/.ssh/
├── id_ed25519_bastion
├── id_ed25519_bastion.pub
├── id_ed25519_dev
├── id_ed25519_dev.pub
├── id_ed25519_prod
└── id_ed25519_prod.pub
```

The principle is:

> **Separate credentials by purpose and trust boundary.**

The reason is **blast radius**. If a development credential is exposed, you do not want that event to automatically grant production access.

---

# 13. SSH Configuration: `~/.ssh/config`

Long SSH commands become difficult to maintain:

```bash
ssh -p 22 -i ~/.ssh/id_ed25519_bastion dataeng@bastion.example.com
```

SSH configuration lets you create a stable alias.

The client configuration is commonly:

```text
~/.ssh/config
```

## 13.1 Basic configuration

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    Port 22
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes
```

Now:

```bash
ssh data-bastion
```

## 13.2 Explain every directive

### `Host`

```sshconfig
Host data-bastion
```

This is the alias you type:

```bash
ssh data-bastion
```

It does not have to be the real DNS hostname.

### `HostName`

```sshconfig
HostName bastion.example.com
```

This is the actual destination hostname or IP.

### `User`

```sshconfig
User dataeng
```

This specifies the remote login account.

### `Port`

```sshconfig
Port 22
```

The SSH TCP port.

For a nonstandard service:

```sshconfig
Port 2222
```

### `IdentityFile`

```sshconfig
IdentityFile ~/.ssh/id_ed25519_bastion
```

Selects the private key.

### `IdentitiesOnly`

```sshconfig
IdentitiesOnly yes
```

Tells the client to use the configured identity files rather than trying a broad collection of agent/default identities.

This is especially useful when many keys are loaded and the server might reject authentication after too many attempted keys.

---

# 14. Progressive SSH Configuration

## Level 1 — Simple alias

```sshconfig
Host dev-server
    HostName 10.0.0.10
    User dataeng
```

Use:

```bash
ssh dev-server
```

### Why it helps

You stop repeating:

```text
username + address
```

and create a meaningful operational name.

---

## Level 2 — Add port and key

```sshconfig
Host dev-server
    HostName 10.0.0.10
    User dataeng
    Port 2222
    IdentityFile ~/.ssh/id_ed25519_dev
    IdentitiesOnly yes
```

Now the access policy is explicit.

---

## Level 3 — Separate environments

```sshconfig
Host data-dev
    HostName dev.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_dev
    IdentitiesOnly yes

Host data-staging
    HostName staging.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_staging
    IdentitiesOnly yes

Host data-production
    HostName prod.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_prod
    IdentitiesOnly yes
```

This makes the environment boundary visible in the command itself:

```bash
ssh data-dev
ssh data-staging
ssh data-production
```

That reduces typing errors and makes review easier.

---

## Level 4 — Add a bastion

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes
```

Then the private server:

```sshconfig
Host data-private
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_private
    IdentitiesOnly yes
    ProxyJump data-bastion
```

Now:

```bash
ssh data-private
```

automatically uses the bastion.

---

## Level 5 — Production-oriented private-server access

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    Port 22
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host data-private
    HostName private-data.example.internal
    User dataeng
    Port 22
    IdentityFile ~/.ssh/id_ed25519_prod
    IdentitiesOnly yes
    ProxyJump data-bastion
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

The configuration now describes:

- who to log in as;
- where to connect;
- which key to use;
- how to reach the private server;
- how to keep the connection healthy.

---

# 15. Understanding How SSH Resolves Configuration

When you run:

```bash
ssh data-private
```

the client looks at the configuration and matches:

```sshconfig
Host data-private
```

It then obtains:

```text
HostName
User
Port
IdentityFile
IdentitiesOnly
ProxyJump
ServerAliveInterval
ServerAliveCountMax
```

You can inspect the effective configuration with:

```bash
ssh -G data-private
```

This is extremely useful for troubleshooting because it answers:

> "What does SSH think the configuration actually is?"

For example:

```bash
ssh -G data-private | grep -E '^(hostname|user|port|identityfile|proxyjump|identitiesonly)'
```

Do not debug SSH configuration only by visually reading a long config file. Ask the client what it resolved.

---

# 16. `ssh-agent`

## 16.1 What problem does the agent solve?

Suppose your private key has a passphrase.

Without an agent, repeated SSH commands may require repeated passphrase entry.

The agent provides a process that holds unlocked key material for a session.

Mental model:

```text
Private key on disk
        |
        | unlock once
        v
   ssh-agent
        |
        +---- SSH connection A
        +---- SSH connection B
        +---- SSH connection C
```

The agent does not mean "make the private key public."

It means:

> **Use a credential helper to perform key operations without repeatedly unlocking the key file.**

## 16.2 Start an agent

On many Unix-like environments:

```bash
eval "$(ssh-agent -s)"
```

This starts an agent and exports environment information so your shell can communicate with it.

## 16.3 Add a key

```bash
ssh-add ~/.ssh/id_ed25519
```

You enter the key's passphrase.

## 16.4 List loaded keys

```bash
ssh-add -l
```

This shows identities currently loaded in the agent.

## 16.5 Remove all loaded identities

**Important:** understand the consequence before running:

```bash
ssh-add -D
```

This removes all identities from the current agent.

It does **not** delete the private-key files.

Mental model:

```text
ssh-add -D
    ↓
Agent forgets loaded keys
    ↓
Private key files remain on disk
```

## 16.6 Security considerations

An SSH agent is useful, but an agent containing powerful production identities becomes a valuable target.

Good habits include:

- load only keys you need;
- avoid leaving production keys loaded indefinitely;
- use separate credentials;
- inspect loaded identities with `ssh-add -l`;
- remove unnecessary keys;
- understand whether forwarding is enabled.

---

# 17. SSH Agent Forwarding

Agent forwarding is often misunderstood.

The architecture is:

```text
Laptop
   |
   | SSH + forwarded agent channel
   v
Bastion
   |
   | SSH
   v
Private server
```

The convenience is:

> You can use your laptop's agent to authenticate to the private server without copying the private key file onto the bastion.

That sounds ideal, but there is a security trade-off.

## 17.1 What forwarding does NOT do

Agent forwarding does **not** normally copy your private key file to the remote machine.

That is good.

## 17.2 What forwarding DOES allow

A compromised remote environment may be able to request cryptographic signatures from the forwarded agent.

Conceptually:

```text
Private key
    stays on laptop

but

Remote bastion
    can potentially ask forwarded agent
    to perform signing operations
```

If the bastion is untrusted or compromised, this can expose the security boundary of the forwarded credential.

## 17.3 Why shared bastions are risky

A bastion is often a security boundary.

If many users share it and you forward a high-privilege production agent, compromise of that host/session can become materially more dangerous.

Do not treat:

```bash
ssh -A bastion
```

as a harmless convenience flag.

## 17.4 Safer alternatives

Depending on the organization's architecture:

- use `ProxyJump` so the client connects through the bastion without requiring broad agent forwarding;
- use separate keys for the private target;
- use short-lived credentials;
- use cloud session-manager/identity-aware access mechanisms;
- use centralized access controls.

For the G2 learning path, the key principle is:

> **Prefer access designs that keep powerful credentials within the smallest possible trust boundary.**

---

# 18. Bastion / Jump Host Architecture

A **bastion host** is a controlled entry point into a private network.

A typical Data Engineering architecture is:

```text
                         Internet
                            |
                            v
                    +---------------+
                    |    Bastion    |
                    |    Server     |
                    +---------------+
                            |
                     Private Network
                            |
              +-------------+-------------+
              |                           |
              v                           v
      +---------------+           +---------------+
      | Data Pipeline |           | PostgreSQL    |
      | Server        |           | Server        |
      +---------------+           +---------------+
```

## 18.1 Why not expose every server?

Suppose you have:

```text
Bastion
Pipeline server
PostgreSQL
Airflow
Spark
Grafana
```

If every machine accepts SSH from the public Internet, the attack surface is larger.

A private architecture can instead expose only the bastion:

```text
Internet
   |
   v
Bastion
   |
   +--> private pipeline server
   +--> private database
   +--> private Airflow
```

The bastion becomes a controlled doorway.

## 18.2 Security benefits

A bastion can provide:

- network isolation;
- limited ingress;
- centralized access control;
- logging/auditing opportunities;
- a smaller exposed surface;
- an explicit trust boundary.

It is not automatically secure merely because it is called a bastion. It must itself be hardened and monitored.

---

# 19. `ProxyJump`

The simplest jump-host syntax is:

```bash
ssh -J bastion private-server
```

Mental model:

```text
Laptop
   |
   | SSH
   v
Bastion
   |
   | SSH forwarding
   v
Private server
```

The important distinction is:

```text
Direct:
Laptop --------------------> Private server
```

versus:

```text
Through bastion:
Laptop ------> Bastion ------> Private server
```

The private server can remain unreachable directly from the laptop's network.

---

# 20. ProxyJump in SSH Config

Example:

```sshconfig
Host bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes

Host private-server
    HostName 10.0.2.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_private
    IdentitiesOnly yes
    ProxyJump bastion
```

Now:

```bash
ssh private-server
```

## 20.1 What happens?

Conceptually:

1. SSH reads the `private-server` configuration.
2. It sees `ProxyJump bastion`.
3. It establishes access through the bastion.
4. It creates the connection path to `10.0.2.20`.
5. The SSH session authenticates to the private server using the configured private-server identity.
6. You receive a shell on the private server.

The bastion is the network path, not necessarily the identity used to log in to the private target.

That distinction becomes important when separate credentials are used.

---

# 21. Multiple Jump Hosts

Some organizations have layered networks:

```text
Laptop
   |
   v
Public Bastion
   |
   v
Internal Bastion
   |
   v
Private Data Server
```

This can happen when:

- environments are segmented;
- production has a separate management network;
- regulated systems have additional access boundaries.

`ProxyJump` can be chained conceptually:

```text
Laptop
  ↓
public-bastion
  ↓
internal-bastion
  ↓
private-data
```

Example:

```sshconfig
Host public-bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion

Host internal-bastion
    HostName 10.10.0.10
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_internal
    ProxyJump public-bastion

Host private-data
    HostName 10.20.0.20
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_prod
    ProxyJump internal-bastion
```

Use multi-hop only when the network architecture requires it. Do not create unnecessary layers just because SSH supports them.

---

# 22. Host-Key Verification

One of the most important SSH concepts is:

> **Authentication proves who YOU are; host-key verification helps prove which SERVER you are connecting to.**

These are different.

## 22.1 `known_hosts`

The SSH client commonly records known server identities in:

```text
~/.ssh/known_hosts
```

Mental model:

```text
known_hosts
    ↓
Known server identities
```

When you reconnect, SSH can compare the presented host key with the known identity.

## 22.2 First connection

You may see:

```text
The authenticity of host 'bastion.example.com' can't be established.
ED25519 key fingerprint is SHA256:EXAMPLE...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

This is a security decision.

Do not blindly accept a fingerprint for a sensitive environment.

Verify it through a trusted source, such as:

- a documented infrastructure record;
- a trusted administrator;
- a cloud console;
- an out-of-band management channel.

## 22.3 Find a known host entry

```bash
ssh-keygen -F bastion.example.com
```

This asks the SSH key utility to find matching known-host entries.

Useful when investigating:

> "What key does my client currently associate with this hostname?"

---

# 23. Changed Host-Key Warning

A particularly important SSH warning is:

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

Do **not** immediately run:

```bash
ssh-keygen -R host.example.com
```

without investigating.

A changed host key can mean:

- legitimate server rebuild;
- replacement VM;
- restored image;
- DNS now points to another machine;
- IP reuse;
- hostname moved to a new server;
- or a potential man-in-the-middle attack.

## 23.1 Correct investigation process

Use:

```text
1. STOP
   ↓
2. Determine whether the server was legitimately rebuilt
   ↓
3. Verify the new fingerprint through a trusted channel
   ↓
4. Remove the stale entry only if appropriate
   ↓
5. Reconnect
   ↓
6. Verify the new identity again
```

## 23.2 Remove a stale known-host entry

After legitimate verification:

```bash
ssh-keygen -R host.example.com
```

This removes matching known-host entries for that host.

Then reconnect:

```bash
ssh dataeng@host.example.com
```

and verify the new fingerprint.

## 23.3 Why `StrictHostKeyChecking no` is dangerous

Never use this as a blanket security solution:

```sshconfig
StrictHostKeyChecking no
```

It can cause the client to accept unexpected host identities without giving you the intended protection.

The correct response to a changed key is **investigation**, not suppression.

---

# 24. Host-Key Security Mental Model

Keep these two questions separate:

```text
USER AUTHENTICATION
"Can this user prove who they are?"

HOST-KEY VERIFICATION
"Am I talking to the server I think I am?"
```

Together:

```text
          SSH ACCESS
              |
      +-------+-------+
      |               |
      v               v
Server identity   User identity
   host key        user key
      |               |
      v               v
"Which server?"   "Which user?"
```

This distinction is fundamental during incidents.

---

# 25. SSH Keepalives

Long-lived SSH connections may fail even when neither side intentionally closes them.

Possible causes include:

- NAT timeouts;
- firewalls;
- VPN infrastructure;
- idle connection policies;
- unstable networks.

OpenSSH provides:

```text
ServerAliveInterval
ServerAliveCountMax
```

## 25.1 Example

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Interpretation:

```text
ServerAliveInterval 60
    ↓
send an SSH-level keepalive after roughly 60 seconds
when appropriate

ServerAliveCountMax 3
    ↓
allow up to three unanswered probes
before considering the connection dead
```

The exact behavior should be understood as an SSH client mechanism rather than a guarantee that every network device will preserve the session.

## 25.2 Command-line equivalent

```bash
ssh -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=3 \
    data-bastion
```

## 25.3 Critical distinction

Keepalives solve:

> **Is the SSH connection itself being dropped because of idle/network behavior?**

They do not solve:

> **Will my long-running data process survive after the SSH session disappears?**

That second problem belongs to mechanisms such as `tmux`, services, schedulers, or orchestrators, which are covered later in G2.

```text
Keepalive
    ↓
Keep the connection healthy

Process supervision/session persistence
    ↓
Keep the workload alive
```

Do not confuse the two.

---

# 26. SSH Connection Multiplexing

If you repeatedly connect to the same host, SSH may repeatedly perform connection setup.

Connection multiplexing allows multiple logical sessions to reuse one underlying connection.

Key directives:

```text
ControlMaster
ControlPath
ControlPersist
```

## 26.1 Example

```sshconfig
Host bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    ControlMaster auto
    ControlPath ~/.ssh/control-%C
    ControlPersist 10m
```

## 26.2 What each directive means

### `ControlMaster auto`

Allows the first connection to become a master connection and later connections to reuse it.

### `ControlPath`

Defines where the local control socket is stored.

The `%C` token helps create a collision-resistant path based on connection parameters.

### `ControlPersist 10m`

Keeps the master connection available for reuse after the original session exits, for the configured period.

## 26.3 Why it helps

Without multiplexing:

```text
SSH command A → connection setup
SSH command B → connection setup
SSH command C → connection setup
```

With multiplexing:

```text
First connection
      ↓
Master connection
      ↓
+----+----+----+
|    |    |    |
A    B    C    sessions
```

This can reduce repeated connection overhead, especially for automation that executes many SSH commands.

## 26.4 Troubleshooting considerations

If multiplexing behaves strangely, inspect:

```bash
ls -la ~/.ssh/
```

for control sockets.

A stale control socket can cause confusing failures after a network or server change.

Do not share control sockets across users or unsafe directories. They are local IPC mechanisms and should remain appropriately protected.

---

# 27. Noninteractive SSH Commands

A Data Engineer frequently needs to execute a single operational check rather than open an interactive shell.

Syntax:

```bash
ssh server 'command'
```

Examples:

```bash
ssh data-server 'hostname'
```

```bash
ssh data-server 'df -h'
```

```bash
ssh data-server 'free -h'
```

```bash
ssh data-server 'uptime'
```

A small health check:

```bash
ssh data-server 'df -h /data && free -h'
```

This is useful in scripts and runbooks.

---

# 28. Local vs Remote Execution

This is a common source of bugs.

Consider:

```bash
ssh data-server 'hostname'
```

The `hostname` command executes remotely.

Your local shell launches `ssh`; the remote shell executes `hostname`.

Think:

```text
LOCAL
  |
  | ssh
  v
REMOTE
  |
  +-- hostname
```

---

# 29. Remote Exit Codes

SSH automation depends on correct exit-code reasoning.

Example:

```bash
ssh data-server 'test -d /data'
echo $?
```

A successful remote test should normally result in:

```text
0
```

A failed test produces a non-zero status.

Mental model:

```text
0       = success
nonzero = failure
```

## 29.1 Why this matters

A script might use:

```bash
if ssh data-server 'test -d /data'; then
    echo "Data directory exists"
else
    echo "Data directory check failed"
fi
```

The command's result can therefore become an operational decision.

## 29.2 Differentiate two failures

### Failure A — SSH itself failed

Example:

```text
Permission denied (publickey).
```

or:

```text
Connection timed out.
```

The remote command may never have executed.

### Failure B — SSH succeeded but remote command failed

Example:

```bash
ssh data-server 'test -d /data/missing'
```

SSH can successfully establish the session while the remote command returns non-zero.

This distinction is essential.

```text
SSH transport/authentication failure
        ≠
Remote command failure
```

---

# 30. Shell Quoting Through SSH

Shell quoting becomes more important when you run remote commands.

Compare:

```bash
ssh server 'command'
```

with:

```bash
ssh server "command"
```

The difference is that the **local shell** processes quoting and expansions before `ssh` sends the resulting command to the remote shell.

## 30.1 `$HOME`

Suppose:

```bash
echo "$HOME"
```

on your laptop returns:

```text
/home/alice
```

Now:

```bash
ssh server "echo $HOME"
```

may expand `$HOME` locally before the command reaches the server.

But:

```bash
ssh server 'echo $HOME'
```

passes the literal `$HOME` to the remote shell, which can expand it there.

Mental model:

```text
Double quotes
    ↓
Local shell may expand variables first

Single quotes
    ↓
Protect the expression from local shell expansion
    ↓
Remote shell can expand it
```

## 30.2 `$(date)`

Compare:

```bash
ssh server "echo $(date)"
```

with:

```bash
ssh server 'echo $(date)'
```

The first may execute `date` locally.

The second asks the remote shell to perform the command substitution.

This matters when timestamps, environment variables, paths, or wildcard expressions must be evaluated on the server.

## 30.3 Wildcards

Consider:

```bash
ssh server 'ls /data/*.csv'
```

The wildcard is intended for the remote shell.

If the quoting is wrong, the local shell may try to expand it first.

### Rule

Before running a complex remote command, ask:

> **Which shell is supposed to interpret this expression?**

---

# 31. Data Engineering Use Cases

## 31.1 Pipeline server

```text
Laptop
   |
   v
Bastion
   |
   v
Pipeline VM
```

Typical actions:

```bash
ssh data-private
```

Then:

```bash
hostname
```

```bash
df -h /data
```

```bash
systemctl status pipeline-service
```

The last command belongs to the later systemd topic; here it is only an example of why server access matters.

## 31.2 Private PostgreSQL

```text
Laptop
   |
   | SSH access
   v
Bastion
   |
   v
Private PostgreSQL server
```

The detailed SSH tunnel mechanics belong to Topic 02. Topic 01 establishes the access architecture and identity model.

## 31.3 Private Airflow

```text
Laptop
   |
   v
Bastion
   |
   v
Private Airflow server
```

You may need SSH access to inspect configuration, logs, processes, or deployment state.

Topic 01 does not teach Airflow administration.

## 31.4 Spark environment

```text
Laptop
   |
   v
Bastion
   |
   v
Private Spark environment
```

Again, the point is not to teach Spark administration here. The point is that production Data Engineers need reliable server access before they can diagnose data-platform workloads.

---

# 32. Separate Keys by Environment

A practical layout:

```text
~/.ssh/
├── id_ed25519_bastion
├── id_ed25519_bastion.pub
├── id_ed25519_dev
├── id_ed25519_dev.pub
├── id_ed25519_staging
├── id_ed25519_staging.pub
├── id_ed25519_prod
└── id_ed25519_prod.pub
```

SSH config:

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes

Host data-dev
    HostName dev.example.internal
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_dev
    IdentitiesOnly yes

Host data-staging
    HostName staging.example.internal
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_staging
    IdentitiesOnly yes

Host data-prod
    HostName prod.example.internal
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_prod
    IdentitiesOnly yes
```

Benefits:

- reduced blast radius;
- clear environment separation;
- easier rotation;
- less accidental production access;
- easier auditing.

Do not create dozens of keys without a reason. Credential separation should follow meaningful trust boundaries.

---

# 33. Key Rotation and Revocation

Imagine:

> A production SSH private key may have been exposed.

Do not treat this as a routine file replacement.

## Correct response

```text
1. Identify affected credential
        ↓
2. Stop using it
        ↓
3. Remove/revoke its server-side authorization
        ↓
4. Generate a replacement
        ↓
5. Install the replacement
        ↓
6. Test the replacement
        ↓
7. Audit access
        ↓
8. Update configuration
        ↓
9. Document the incident
```

## 33.1 Critical distinction

Suppose:

```text
Local:
~/.ssh/id_ed25519_prod
```

is deleted.

The server may still contain its public key:

```text
~/.ssh/authorized_keys
```

Therefore:

```text
Delete private key locally
        ≠
Revoke server authorization
```

The server-side authorization must be removed.

## 33.2 Safe rotation pattern

If you still have access:

1. create a replacement key;
2. install the replacement public key;
3. test a new connection;
4. confirm the replacement works;
5. remove the old public key;
6. audit and document.

Do not remove the only working key before confirming the replacement.

---

# 34. Short-Lived SSH Certificates and Cloud Access

The roadmap requires awareness, not a full implementation course.

Traditional model:

```text
Long-lived private key
        ↓
Many servers
```

Modern production architectures may instead use:

```text
Central identity
      ↓
Short-lived credential
      ↓
Temporary server access
```

Advantages can include:

- shorter credential lifetime;
- centralized access control;
- easier revocation;
- reduced long-lived secret distribution.

Cloud platforms may provide session-management or identity-aware access mechanisms that avoid exposing an SSH port publicly.

Examples include:

- managed session managers;
- identity-aware proxies;
- short-lived SSH certificates.

The architectural principle is:

> **Minimize long-lived credentials and minimize exposed network entry points.**

Do not turn this Topic 01 file into an SSH Certificate Authority implementation course.

---

# 35. Production Security Principles

Use these principles consistently.

## Protect private keys

Never expose private keys.

## Use passphrases

A passphrase adds protection if the local key file is copied.

## Separate credentials

Use separate credentials where trust boundaries differ.

## Least privilege

An SSH user should receive only the access needed for the job.

## Avoid shared accounts

Prefer attributable identities over:

```text
shared-user
admin
root
```

where organizational policy permits.

## Avoid unnecessary root login

Production access should normally use controlled user identities rather than routine direct root login.

## Avoid unnecessary password authentication

Where key-based or stronger identity mechanisms are appropriate, prefer them.

## Verify host keys

Do not treat host-key warnings as annoying prompts.

## Avoid blanket `StrictHostKeyChecking no`

Security checks exist for a reason.

## Be careful with agent forwarding

A forwarded agent crosses a trust boundary.

## Keep SSH configuration understandable

Complex access configuration becomes an operational risk if nobody can explain it.

## Rotate credentials

Old credentials should not remain authorized indefinitely.

## Use bastions for private systems

Keep private infrastructure private where appropriate.

## Audit access

Know who can access which servers and which credentials are authorized.

---

# 36. Hands-On Lab: `server_lab/01/`

## Lab architecture

Use:

```text
                 Laptop
                    |
                    | SSH
                    v
             +-------------+
             |   Bastion   |
             | public SSH  |
             +-------------+
                    |
             Private network
                    |
                    v
             +-------------+
             | Private     |
             | Data Server |
             +-------------+
```

The private server should not be directly reachable from your laptop.

### Lab safety

- Use practice hosts only.
- Use placeholder/example domains.
- Do not use production private keys.
- Do not expose production infrastructure.
- Keep a rollback/rebuild path.

---

## Lab 1 — Connect Directly to a Practice Server

### Objective

Understand the basic SSH path.

### Command

```bash
ssh dataeng@bastion.example.com
```

### Expected behavior

You should either:

- receive a host-key verification prompt; or
- connect if the host is already trusted.

### What happened?

Your SSH client attempted to establish a TCP/SSH session with the practice server.

### Verify

```bash
hostname
whoami
```

Expected conceptually:

```text
practice-bastion
dataeng
```

### Cleanup

```bash
exit
```

---

## Lab 2 — Create an Ed25519 Key

### Objective

Create a dedicated practice credential.

### Command

```bash
ssh-keygen -t ed25519
```

Use a practice-specific filename if desired:

```text
~/.ssh/id_ed25519_g2_lab
```

Use a strong passphrase.

### Verify

```bash
ls -l ~/.ssh/id_ed25519_g2_lab*
```

You should have:

```text
id_ed25519_g2_lab
id_ed25519_g2_lab.pub
```

### Security check

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519_g2_lab
chmod 644 ~/.ssh/id_ed25519_g2_lab.pub
```

---

## Lab 3 — Install the Public Key

### Objective

Allow key-based login.

### Command

```bash
ssh-copy-id -i ~/.ssh/id_ed25519_g2_lab.pub dataeng@bastion.example.com
```

### What it does

It installs your public key into the remote user's authorized-key list.

### Verify

Log in and inspect:

```bash
cat ~/.ssh/authorized_keys
```

Do not copy private-key material.

### Common failure

```text
Permission denied
```

Possible cause: the bootstrap authentication method is unavailable or the remote account cannot modify its SSH authorization files.

---

## Lab 4 — Use `ssh-agent`

### Objective

Load the passphrase-protected key into an agent.

### Commands

```bash
eval "$(ssh-agent -s)"
```

Then:

```bash
ssh-add ~/.ssh/id_ed25519_g2_lab
```

Verify:

```bash
ssh-add -l
```

### Expected result

Your Ed25519 identity should appear in the agent.

### Test

```bash
ssh -i ~/.ssh/id_ed25519_g2_lab dataeng@bastion.example.com
```

Then exit and reconnect.

The agent should be able to perform the key operation without repeatedly asking for the key passphrase during the same agent lifetime.

---

## Lab 5 — Create SSH Config

### Objective

Replace long commands with an alias.

Create:

```text
~/.ssh/config
```

Example:

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    Port 22
    IdentityFile ~/.ssh/id_ed25519_g2_lab
    IdentitiesOnly yes
```

Set appropriate permissions:

```bash
chmod 600 ~/.ssh/config
```

Test:

```bash
ssh data-bastion
```

### Verify effective configuration

```bash
ssh -G data-bastion | grep -E '^(hostname|user|port|identityfile|identitiesonly)'
```

---

## Lab 6 — Add a Private Server

### Objective

Create the two-machine architecture.

```text
Laptop → Bastion → Private server
```

Configure:

```sshconfig
Host data-private-direct
    HostName private-data.example.internal
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_g2_lab
    IdentitiesOnly yes
```

Do not expect direct connectivity from the laptop if the private server is intentionally isolated.

### Test

```bash
ssh data-private-direct
```

### Expected result

It should fail or be unreachable from the laptop by design.

This failure is useful evidence: the private server is not supposed to be directly accessible.

---

## Lab 7 — Use ProxyJump

### Objective

Reach the private server through the bastion.

Configure:

```sshconfig
Host data-private
    HostName private-data.example.internal
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_g2_lab
    IdentitiesOnly yes
    ProxyJump data-bastion
```

Now:

```bash
ssh data-private
```

### Verify

```bash
hostname
```

The hostname should identify the private server, not the bastion.

### Explain aloud

You should be able to say:

> "My laptop connects through the bastion as the network path, but the target SSH session is to the private server."

---

## Lab 8 — Configure Keepalives

Add:

```sshconfig
Host data-bastion
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

For the private host:

```sshconfig
Host data-private
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Test:

```bash
ssh data-private
```

The objective is not to wait for an outage. The objective is to understand the configuration and explain what it protects against.

---

## Lab 9 — Configure Connection Multiplexing

Add:

```sshconfig
Host data-bastion
    ControlMaster auto
    ControlPath ~/.ssh/control-%C
    ControlPersist 10m
```

Connect:

```bash
ssh data-bastion
```

Then run another connection:

```bash
ssh data-bastion 'hostname'
```

Inspect:

```bash
ls -la ~/.ssh/control-*
```

### What happened?

The second connection may reuse the established master connection.

### Cleanup

After the experiment, allow the persistent control connection to expire or remove the practice control socket if necessary.

---

## Lab 10 — Run Noninteractive Health Checks

Run:

```bash
ssh data-private 'hostname'
```

Then:

```bash
ssh data-private 'uptime'
```

Then:

```bash
ssh data-private 'df -h /data'
```

Combine checks:

```bash
ssh data-private 'hostname && uptime && df -h /data'
```

### Objective

Practice operating a remote server without opening an interactive shell.

---

## Lab 11 — Test Exit Codes

Run:

```bash
ssh data-private 'test -d /data'
echo $?
```

Then deliberately test a missing path:

```bash
ssh data-private 'test -d /this/path/should/not/exist'
echo $?
```

### Expected concept

First:

```text
0
```

Second:

```text
non-zero
```

### Explain

You must distinguish:

```text
SSH connection worked
    ↓
Remote command returned failure
```

from:

```text
SSH connection itself failed
```

---

## Lab 12 — Simulate a Rebuilt Server

### Objective

Understand changed host-key warnings.

1. Record the current practice server identity.
2. Rebuild/recreate the practice server so its host key changes.
3. Connect using the same hostname.
4. Observe the warning.
5. Stop.
6. Verify whether the rebuild was legitimate.
7. Obtain the new fingerprint through your trusted practice setup.
8. Only then remove the stale entry.

Find the entry:

```bash
ssh-keygen -F private-data.example.internal
```

Remove the stale entry after verification:

```bash
ssh-keygen -R private-data.example.internal
```

Reconnect:

```bash
ssh data-private
```

### Critical lesson

Never turn a host-key warning into a routine "delete and continue" workflow.

---

## Lab 13 — Practice Key Rotation

### Objective

Rotate an SSH credential without locking yourself out.

1. Generate a replacement Ed25519 key.
2. Install the replacement public key.
3. Test a new session using the replacement key.
4. Confirm it works.
5. Remove the old public key from `authorized_keys`.
6. Confirm the old key no longer authenticates.
7. Update `IdentityFile` in your SSH config.
8. Record the change in your runbook.

### Success condition

You can rotate the key without losing access.

---

# 37. Break/Fix Exercises

Follow:

```text
Break
  ↓
Observe symptom
  ↓
Collect evidence
  ↓
Diagnose
  ↓
Fix
  ↓
Verify
  ↓
Document
```

Do not guess.

---

## Scenario 1 — Wrong SSH Username

### Symptom

```text
Permission denied
```

### Evidence

Check:

```bash
ssh -v data-private
```

Look for the attempted username.

### Diagnosis

The configured `User` is wrong.

### Fix

Correct:

```sshconfig
User dataeng
```

### Verification

```bash
ssh data-private
whoami
```

### Prevention

Use meaningful SSH aliases and verify effective configuration.

---

## Scenario 2 — Wrong Private Key

### Symptom

```text
Permission denied (publickey).
```

### Evidence

```bash
ssh -vv data-private
```

Inspect which identity files are offered.

### Diagnosis

The client is using the wrong key.

### Fix

Correct:

```sshconfig
IdentityFile ~/.ssh/id_ed25519_prod
IdentitiesOnly yes
```

### Verification

Reconnect and confirm:

```bash
whoami
```

---

## Scenario 3 — Incorrect Private-Key Permissions

### Symptom

OpenSSH refuses to use a private key.

### Evidence

```bash
ls -l ~/.ssh/id_ed25519_prod
```

### Diagnosis

The private key is too broadly readable.

### Fix

```bash
chmod 600 ~/.ssh/id_ed25519_prod
```

### Verification

Retry SSH.

### Prevention

Treat private-key permissions as part of credential hygiene.

---

## Scenario 4 — Wrong SSH Port

### Symptom

```text
Connection refused
```

or:

```text
Connection timed out
```

### Evidence

Inspect:

```bash
ssh -vv data-server
```

Check effective configuration:

```bash
ssh -G data-server | grep '^port '
```

### Diagnosis

The client is targeting the wrong port or the path is blocked.

### Fix

Correct:

```sshconfig
Port 2222
```

Do not assume every connection failure is an authentication failure.

---

## Scenario 5 — Incorrect `authorized_keys`

### Symptom

The correct private key is offered, but authentication fails.

### Evidence

Inspect the server-side authorization file and permissions through an existing administrative path.

### Diagnosis

The corresponding public key is missing or malformed.

### Fix

Install the correct public key.

### Verification

Reconnect using the intended private key.

### Prevention

Manage authorized keys deliberately and document ownership.

---

## Scenario 6 — Incorrect SSH Config

### Symptom

A known-working command fails after an alias is introduced.

### Evidence

```bash
ssh -G data-private
```

### Diagnosis

The effective `HostName`, `User`, `Port`, `IdentityFile`, or `ProxyJump` differs from the intended values.

### Fix

Correct the matching configuration.

### Verification

Repeat the effective-config check, then connect.

---

## Scenario 7 — Broken ProxyJump

### Symptom

The bastion works but the private server does not.

### Evidence

Test each layer:

```bash
ssh data-bastion
```

Then:

```bash
ssh -vv data-private
```

### Diagnosis possibilities

- bastion unavailable;
- wrong bastion key;
- wrong private target address;
- private target not reachable from bastion;
- wrong target username/key;
- configuration mismatch.

### Fix

Resolve the first failing layer rather than changing random settings.

---

## Scenario 8 — Changed Host Key

### Symptom

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

### Diagnosis

Do not assume compromise and do not assume a rebuild.

Determine whether the server was legitimately rebuilt.

### Fix

Verify the new fingerprint through a trusted channel, then:

```bash
ssh-keygen -R host.example.com
```

Reconnect and verify.

---

## Scenario 9 — SSH Session Drops

### Symptom

An idle session disconnects.

### Evidence

Check whether the environment has idle timeout behavior.

### Diagnosis

Potential NAT/firewall/VPN idle timeout.

### Fix

Configure:

```sshconfig
ServerAliveInterval 60
ServerAliveCountMax 3
```

### Important boundary

This does not guarantee a workload survives a disconnected session. Workload persistence is a separate concern.

---

## Scenario 10 — Incorrect Remote Shell Quoting

### Symptom

A command prints local values when you expected remote values.

### Example

```bash
ssh data-private "echo $HOME"
```

### Diagnosis

The local shell expanded `$HOME`.

### Fix

```bash
ssh data-private 'echo $HOME'
```

### Verification

Compare the result with:

```bash
ssh data-private 'hostname; echo $HOME'
```

---

## Scenario 11 — SSH Works but Remote Command Fails

### Symptom

SSH authentication succeeds, but the operation returns an error.

### Evidence

```bash
ssh data-private 'test -d /missing'
echo $?
```

### Diagnosis

Transport and authentication are healthy. The remote command failed.

### Fix

Investigate the command itself, permissions, paths, or remote state.

### Prevention

Always distinguish:

```text
transport
authentication
authorization
command execution
```

---

# 38. SSH Troubleshooting Decision Tree

Use evidence in this order:

```text
Cannot SSH
   |
   +--> Can the hostname resolve?
   |       |
   |       +--> No → DNS/name-resolution problem
   |
   +--> Can the network reach the target?
   |       |
   |       +--> No → routing/firewall/network problem
   |
   +--> Is the SSH port correct?
   |       |
   |       +--> No → configuration/port problem
   |
   +--> Is the SSH daemon reachable?
   |       |
   |       +--> No → service/network/server problem
   |
   +--> Is there a host-key problem?
   |       |
   |       +--> Yes → investigate identity change
   |
   +--> Is user authentication failing?
   |       |
   |       +--> Yes → inspect key/user/agent
   |
   +--> Is authorization failing?
   |       |
   |       +--> Yes → inspect account and authorized key
   |
   +--> Is ProxyJump failing?
   |       |
   |       +--> Yes → test each hop independently
   |
   +--> Did SSH succeed?
           |
           +--> Yes → inspect the remote command
```

## Useful verbose modes

Start with:

```bash
ssh -v data-private
```

Increase only when necessary:

```bash
ssh -vv data-private
```

```bash
ssh -vvv data-private
```

Use verbose output to answer specific questions:

- What host/port is being targeted?
- Which config is being applied?
- Which keys are being offered?
- Did host-key verification occur?
- Did authentication succeed?
- Did the proxy/jump path initialize?

Do not read verbose output as an undifferentiated wall of text. Ask a specific diagnostic question first.

---

# 39. Practical Diagnostic Commands

## Inspect SSH client version

```bash
ssh -V
```

Useful when behavior differs across environments.

## Inspect effective configuration

```bash
ssh -G data-private
```

## Inspect loaded agent identities

```bash
ssh-add -l
```

## Find a known host

```bash
ssh-keygen -F data-private.example.internal
```

## Remove a verified stale host entry

```bash
ssh-keygen -R data-private.example.internal
```

## Test name resolution

```bash
getent hosts data-private.example.internal
```

## Test a noninteractive connection

```bash
ssh data-private 'hostname'
```

## Check the remote exit status

```bash
ssh data-private 'test -d /data'
echo $?
```

---

# 40. Operational SSH Runbook

This is the short version you want during a 3 a.m. incident.

## 40.1 Access the bastion

```bash
ssh data-bastion
```

If it fails:

```bash
ssh -vv data-bastion
```

Check:

1. hostname;
2. port;
3. network reachability;
4. host key;
5. username;
6. identity;
7. agent.

## 40.2 Access the private server

```bash
ssh data-private
```

If the bastion works but the private server fails:

```bash
ssh -vv data-private
```

Test the bastion independently:

```bash
ssh data-bastion
```

## 40.3 Verify host identity

Find known entry:

```bash
ssh-keygen -F data-private.example.internal
```

If changed:

```text
STOP → verify rebuild → verify fingerprint → remove stale entry → reconnect
```

Only after verification:

```bash
ssh-keygen -R data-private.example.internal
```

## 40.4 Check loaded keys

```bash
ssh-add -l
```

If an unnecessary key is loaded:

```bash
ssh-add -d ~/.ssh/id_ed25519_old
```

If you intentionally need to clear all agent identities:

```bash
ssh-add -D
```

Understand the consequence before using the latter.

## 40.5 Diagnose authentication

```bash
ssh -vv data-private
```

Check:

```text
User
IdentityFile
IdentitiesOnly
authorized_keys
agent
```

## 40.6 Diagnose ProxyJump

```bash
ssh data-bastion
```

then:

```bash
ssh -vv data-private
```

Do not randomly change both hops at once.

## 40.7 Rotate a key

```text
Generate replacement
    ↓
Install public key
    ↓
Test replacement
    ↓
Remove old public key
    ↓
Update SSH config
    ↓
Audit/document
```

## 40.8 Run a health check

```bash
ssh data-private 'hostname && uptime && df -h /data'
```

The purpose is to quickly establish:

- which server you reached;
- whether the server is responsive;
- whether the expected data path is visible.

---

# 41. Common Mistakes

## Mistake 1 — Unprotected private keys

Why dangerous:

Anyone who obtains the private key may be able to authenticate wherever it is authorized.

---

## Mistake 2 — One key for everything forever

Why dangerous:

One compromise can cross development, staging, production, and bastion boundaries.

---

## Mistake 3 — Blindly disabling host-key checking

Bad pattern:

```sshconfig
StrictHostKeyChecking no
```

Why dangerous:

It weakens the mechanism designed to detect unexpected server identity changes.

---

## Mistake 4 — Blindly using agent forwarding

Why dangerous:

A remote environment can potentially request signing operations from the forwarded agent.

---

## Mistake 5 — Exposing private servers unnecessarily

Why dangerous:

It expands the externally reachable attack surface.

---

## Mistake 6 — Not understanding the access path

If you cannot explain:

```text
Laptop → Bastion → Private server
```

you will struggle to diagnose where a failure occurred.

---

## Mistake 7 — Confusing authentication with authorization

A valid login does not imply unrestricted permissions.

---

## Mistake 8 — Confusing host-key verification with user authentication

These answer different security questions.

---

## Mistake 9 — Ignoring exit codes

Automation can report success when a remote operation actually failed if its status is not checked correctly.

---

## Mistake 10 — Misunderstanding local vs remote shell expansion

Commands containing `$HOME`, `$(date)`, `*`, and other shell constructs can execute parts locally when you intended them to execute remotely.

---

## Mistake 11 — Treating an SSH session as process supervision

A connection that stays alive does not automatically make a workload production-safe.

Later G2 topics cover `tmux` and proper services.

---

# 42. What NOT to Teach in Topic 01

This file intentionally does **not** become the rest of G2.

Do not turn it into a deep course on:

- SSH tunnels and port forwarding;
- `tmux`;
- `rsync`;
- `rclone`;
- `systemd`;
- Linux performance monitoring;
- disk management;
- `jq`;
- `csvkit`;
- Miller;
- DuckDB CLI;
- logrotate;
- full log investigation;
- general Linux administration;
- Kubernetes;
- Terraform;
- Ansible;
- CI/CD;
- Dockerfile authoring;
- cloud networking certification.

The boundaries are:

```text
Topic 01 → SSH access, identity, configuration, jump hosts

Topic 02 → SSH tunnels and port forwarding

Topic 03 → tmux and long-running sessions

Topic 04 → file transfer

Topic 05 → systemd

Topic 06 → resource monitoring

Topic 07 → disks and large files

Topic 08 → command-line data tools

Topic 09 → log investigation

Topic 10 → users, sudo, packages, and hygiene
```

Related topics may be referenced for context, but they should not be duplicated deeply here.

---

# 43. Data Engineering Mental Models

## SSH

```text
SSH = secure remote control channel
```

## Private key

```text
Private key = secret proof
```

## Public key

```text
Public key = verification material
```

## `authorized_keys`

```text
Server-side allowlist of authorized public keys
```

## Bastion

```text
Controlled doorway into a private network
```

## ProxyJump

```text
SSH through the doorway to reach an internal server
```

## Host-key verification

```text
"Am I talking to the server I think I am?"
```

## User authentication

```text
"Can this user prove who they are?"
```

## Authorization

```text
"What is this authenticated identity allowed to do?"
```

## Keepalive

```text
"Is the SSH connection still healthy?"
```

## Connection multiplexing

```text
"Can repeated sessions reuse one underlying SSH connection?"
```

---

# 44. Practice Questions

These questions reinforce Topic 01 only.

## Question 1 — Conceptual

### Question

What is the difference between an SSH client and an SSH server?

### Expected Thinking

Identify which side initiates the connection and which side accepts it.

### Solution

The SSH client initiates the connection. The SSH server, commonly `sshd`, listens for and accepts SSH connections.

### Explanation

Your laptop normally runs the client; the remote Linux machine runs the SSH daemon.

---

## Question 2 — Authentication

### Question

What is the difference between authentication and authorization?

### Expected Thinking

Ask two different questions.

### Solution

Authentication proves identity. Authorization determines what that authenticated identity is allowed to do.

### Explanation

A user may authenticate successfully but still lack permission to read a database directory or use `sudo`.

---

## Question 3 — Key Security

### Question

Which file must remain secret?

```text
id_ed25519
id_ed25519.pub
```

### Expected Thinking

Identify the private key.

### Solution

`id_ed25519` is the private key and must remain secret. `id_ed25519.pub` is the public key.

### Explanation

The server can receive the public key. The private key should remain protected on the client.

---

## Question 4 — `authorized_keys`

### Question

What is the purpose of `~/.ssh/authorized_keys`?

### Expected Thinking

Think "server-side authorization."

### Solution

It contains public keys authorized to authenticate as that user.

### Explanation

Removing an old public key from this file can revoke that key's ability to authenticate to the account.

---

## Question 5 — SSH Config

### Question

What does this configuration accomplish?

```sshconfig
Host data-bastion
    HostName bastion.example.com
    User dataeng
    IdentityFile ~/.ssh/id_ed25519_bastion
    IdentitiesOnly yes
```

### Expected Thinking

Map each directive to its purpose.

### Solution

It creates the `data-bastion` alias and specifies the destination, user, private key, and identity-selection behavior.

### Explanation

It lets you run:

```bash
ssh data-bastion
```

instead of repeating all parameters.

---

## Question 6 — Agent Forwarding

### Question

Why can agent forwarding be risky?

### Expected Thinking

Separate "private key file copied" from "signing ability exposed."

### Solution

The private key normally remains on the client, but a compromised remote environment may be able to request signing operations from the forwarded agent.

### Explanation

Therefore forwarding a powerful production agent into an untrusted bastion can cross an important trust boundary.

---

## Question 7 — Bastion

### Question

Why might a PostgreSQL server be reachable only through a bastion?

### Expected Thinking

Think network isolation and attack surface.

### Solution

The database can remain on a private network and avoid direct Internet exposure.

### Explanation

The bastion becomes the controlled entry point.

---

## Question 8 — ProxyJump

### Question

What does this do?

```bash
ssh -J bastion private-server
```

### Expected Thinking

Identify the network path.

### Solution

It uses `bastion` as a jump host to reach `private-server`.

### Explanation

The client establishes the path through the bastion rather than requiring direct reachability from the laptop.

---

## Question 9 — Host Key

### Question

What should you do when you see:

```text
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

### Expected Thinking

Do not suppress the warning.

### Solution

Stop and determine why the key changed. Verify the new fingerprint through a trusted channel. If the change is legitimate, remove the stale known-host entry and reconnect.

### Explanation

The warning can represent a legitimate rebuild or a security problem.

---

## Question 10 — Keepalive

### Question

What problem does this address?

```sshconfig
ServerAliveInterval 60
ServerAliveCountMax 3
```

### Expected Thinking

Think connection health, not workload persistence.

### Solution

It helps detect/respond to an SSH connection that has become unresponsive due to network idle behavior.

### Explanation

It does not replace process supervision or job persistence.

---

## Question 11 — Exit Code

### Question

What does this check?

```bash
ssh data-private 'test -d /data'
echo $?
```

### Expected Thinking

Separate remote command status from SSH transport.

### Solution

It tests whether `/data` exists on the remote server and prints the resulting status.

### Explanation

`0` generally means the test succeeded; non-zero means it failed.

---

## Question 12 — Quoting

### Question

Why can these produce different results?

```bash
ssh server "echo $HOME"
```

```bash
ssh server 'echo $HOME'
```

### Expected Thinking

Ask which shell expands `$HOME`.

### Solution

Double quotes allow the local shell to expand `$HOME` before SSH sends the command. Single quotes protect it so the remote shell can expand it.

### Explanation

This distinction becomes important in automation.

---

## Question 13 — Key Rotation

### Question

A production private key is suspected to be exposed. Is deleting the local private-key file sufficient?

### Expected Thinking

Ask what remains authorized on the server.

### Solution

No. Remove the corresponding public key from the server's `authorized_keys` or otherwise revoke the credential.

### Explanation

Local deletion does not revoke a public key already authorized remotely.

---

## Question 14 — Troubleshooting

### Question

The bastion works, but `ssh data-private` fails. What should you do first?

### Expected Thinking

Break the problem into layers.

### Solution

Confirm the bastion independently, then use:

```bash
ssh -vv data-private
```

Inspect the resolved configuration and identify the first failing stage.

### Explanation

Do not change several settings at once. Find the first broken layer.

---

## Question 15 — Data Engineering

### Question

Why does SSH knowledge matter if your company uses Airflow and Spark?

### Expected Thinking

Consider what happens when the platform itself needs investigation.

### Solution

Production data platforms still run on infrastructure that may require direct server access for diagnosis, configuration inspection, credential operations, deployment checks, and incident response.

### Explanation

Higher-level tools do not eliminate infrastructure operations.

---

# 45. Interview Preparation

## What is SSH?

SSH is a secure protocol for encrypted remote access and related secure communication between a client and server.

## SSH client vs SSH server?

The client initiates the connection; the server daemon, commonly `sshd`, accepts and manages it.

## Password vs public-key authentication?

Password authentication uses a password credential; public-key authentication uses a public/private key pair and avoids sending the private key to the server.

## Why Ed25519?

Ed25519 is a modern public-key signature scheme supported by OpenSSH and is a preferred practical choice for new SSH keys in this roadmap.

## What is `authorized_keys`?

A server-side file containing public keys authorized to authenticate as a particular user.

## What is `ssh-agent`?

A credential helper that can hold unlocked SSH identities so they can be used without repeatedly entering their passphrases.

## What is agent forwarding?

It allows a remote SSH session to access signing capability from the client's forwarded agent without copying the private key file to the remote host.

## Why is agent forwarding risky?

A compromised remote environment can potentially request signing operations from the forwarded agent.

## What is a bastion host?

A controlled server used as an entry point into an otherwise private network.

## What is `ProxyJump`?

An OpenSSH mechanism for reaching a target through one or more jump hosts.

## What is `known_hosts`?

A local database of known server host-key identities used to detect unexpected host identity changes.

## What happens when a host key changes?

SSH warns because the server identity no longer matches the known identity. Investigate and verify before changing `known_hosts`.

## Why is `StrictHostKeyChecking` important?

It controls how strictly SSH handles unknown or changed host keys. Disabling verification broadly weakens server-identity protection.

## What are `ServerAliveInterval` and `ServerAliveCountMax`?

They control SSH client keepalive behavior used to detect/respond to unresponsive connections.

## What is SSH connection multiplexing?

Reusing an existing SSH connection for additional sessions to reduce repeated connection setup.

## How would you troubleshoot SSH failure?

Separate the problem into name resolution, network reachability, port, SSH daemon, host-key verification, authentication, authorization, jump-host path, and finally remote command execution.

## How would you rotate a compromised SSH key?

Stop using the credential, install a replacement, verify the replacement, revoke/remove the old public key from server authorization, update configuration, audit access, and document the incident.

## How would you safely access private PostgreSQL through a bastion?

First establish the SSH identity and bastion access path. Use `ProxyJump` for server access and, when the database itself must be reached from the laptop, use the dedicated SSH tunnel mechanisms taught in Topic 02.

---

# 46. Final Knowledge Check

You are ready to move forward only when you can perform these tasks without copying blindly from notes.

## Architecture

- [ ] Explain local machine vs remote server.
- [ ] Explain SSH client vs SSH server.
- [ ] Explain the role of `sshd`.
- [ ] Draw the SSH connection flow.
- [ ] Explain direct vs bastion-mediated access.

## Authentication

- [ ] Explain authentication vs authorization.
- [ ] Explain password vs public-key authentication.
- [ ] Generate an Ed25519 key.
- [ ] Explain private vs public key.
- [ ] Protect the private key with a passphrase.
- [ ] Explain `authorized_keys`.
- [ ] Install a public key safely.
- [ ] Remove an obsolete public key.

## SSH Configuration

- [ ] Create a useful `~/.ssh/config`.
- [ ] Explain `Host`.
- [ ] Explain `HostName`.
- [ ] Explain `User`.
- [ ] Explain `Port`.
- [ ] Explain `IdentityFile`.
- [ ] Explain `IdentitiesOnly`.
- [ ] Inspect effective configuration with `ssh -G`.

## Agents

- [ ] Start/use `ssh-agent`.
- [ ] Add an identity with `ssh-add`.
- [ ] List loaded identities.
- [ ] Remove identities intentionally.
- [ ] Explain agent-forwarding risks.
- [ ] Explain safer alternatives.

## Bastions

- [ ] Explain why private servers may not expose SSH directly.
- [ ] Use `ssh -J`.
- [ ] Configure `ProxyJump`.
- [ ] Explain multi-hop architecture.
- [ ] Diagnose which hop is failing.

## Host Security

- [ ] Explain host-key verification.
- [ ] Explain `known_hosts`.
- [ ] Use `ssh-keygen -F`.
- [ ] Investigate a changed host key.
- [ ] Use `ssh-keygen -R` only after legitimate verification.
- [ ] Explain why blanket `StrictHostKeyChecking no` is unsafe.

## Reliability

- [ ] Configure `ServerAliveInterval`.
- [ ] Configure `ServerAliveCountMax`.
- [ ] Explain connection health vs process persistence.
- [ ] Explain `ControlMaster`.
- [ ] Explain `ControlPath`.
- [ ] Explain `ControlPersist`.

## Automation

- [ ] Run a noninteractive SSH command.
- [ ] Interpret its exit status.
- [ ] Distinguish SSH failure from remote-command failure.
- [ ] Reason correctly about local vs remote shell expansion.
- [ ] Correctly use single and double quotes for remote commands.

## Production Operations

- [ ] Use separate keys by environment/trust boundary.
- [ ] Rotate a credential without locking yourself out.
- [ ] Explain the response to a compromised key.
- [ ] Troubleshoot an SSH failure from evidence.
- [ ] Write a concise access runbook.
- [ ] Explain the complete architecture to another Data Engineer.

---

# 47. Topic 01 Checkpoint

The G2 roadmap defines these as the essential outcomes before moving on:

- [ ] Reach a private server through a bastion with one short command.
- [ ] Explain host-key verification and respond correctly to a changed key.
- [ ] Explain the risks of agent forwarding and a safer alternative.
- [ ] Manage keys per purpose and remove old ones.

A strong Topic 01 learner should be able to do all four **without blindly copying commands**.

---

# 48. Roadmap Coverage Audit

This module was structured against the Topic 01 requirements in the G2 roadmap and the supplied Topic 01 specification.

| Requirement | Covered |
|---|---|
| Remote server fundamentals | Yes |
| Data Engineer relevance | Yes |
| Local vs remote | Yes |
| SSH client/server/`sshd` | Yes |
| SSH protocol mental model | Yes |
| `ssh user@host` | Yes |
| Hostname/IP/port | Yes |
| Port 22/custom ports | Yes |
| First connection/host-key prompt | Yes |
| Authentication vs authorization | Yes |
| Full SSH connection flow | Yes |
| Password vs public-key authentication | Yes |
| Ed25519 | Yes |
| Passphrases | Yes |
| `~/.ssh/` | Yes |
| Private/public keys | Yes |
| Key permissions | Yes |
| `authorized_keys` | Yes |
| `ssh-copy-id` | Yes |
| Key lifecycle | Yes |
| Key separation | Yes |
| Key rotation/revocation | Yes |
| `~/.ssh/config` | Yes |
| `Host` | Yes |
| `HostName` | Yes |
| `User` | Yes |
| `Port` | Yes |
| `IdentityFile` | Yes |
| `IdentitiesOnly` | Yes |
| Progressive SSH config | Yes |
| `ssh-agent` | Yes |
| `ssh-add` | Yes |
| Agent forwarding | Yes |
| Forwarding risk | Yes |
| Safer alternatives | Yes |
| Bastion/jump-host architecture | Yes |
| Private-network model | Yes |
| `ProxyJump` / `-J` | Yes |
| Multiple hops | Yes |
| `known_hosts` | Yes |
| `ssh-keygen -F` | Yes |
| `ssh-keygen -R` | Yes |
| Changed host-key warning | Yes |
| Safe investigation workflow | Yes |
| `StrictHostKeyChecking no` risk | Yes |
| `ServerAliveInterval` | Yes |
| `ServerAliveCountMax` | Yes |
| Connection health vs process persistence | Yes |
| `ControlMaster` | Yes |
| `ControlPath` | Yes |
| `ControlPersist` | Yes |
| Noninteractive SSH | Yes |
| Exit codes | Yes |
| Local vs remote shell quoting | Yes |
| `$HOME` / `$(date)` / `*` reasoning | Yes |
| Data Engineering use cases | Yes |
| Short-lived credentials awareness | Yes |
| Production security principles | Yes |
| Hands-on progressive lab | Yes |
| Break/fix scenarios | Yes |
| Evidence-driven troubleshooting | Yes |
| Troubleshooting decision tree | Yes |
| Operational runbook | Yes |
| Common mistakes | Yes |
| Explicit Topic 01 boundaries | Yes |
| Topic-specific practice questions | Yes |
| Interview preparation | Yes |
| Final knowledge check | Yes |

### Coverage standard

A concept is considered covered only when the module gives enough explanation to understand its purpose, shows how it is used where appropriate, and connects it to operational reasoning.

---

# 49. Quality and Safety Checklist

- [x] Beginner → advanced progression preserved.
- [x] Data Engineering context maintained.
- [x] Commands are explained rather than presented as unexplained dumps.
- [x] Security-sensitive commands include consequences.
- [x] No real credentials are used.
- [x] Practice domains/IPs are placeholders.
- [x] Host-key verification is not bypassed.
- [x] Agent forwarding is not presented as universally safe.
- [x] Key rotation does not assume local key deletion is sufficient.
- [x] Troubleshooting is evidence-driven.
- [x] Topic 02–10 content is referenced only for boundaries/context.
- [x] Labs follow the server-operator learning loop.
- [x] Remote command exit-code behavior is explicitly covered.
- [x] Local vs remote shell evaluation is explicitly covered.
- [x] The final checkpoint aligns with the G2 Topic 01 outcome.

---

# 50. Final Takeaway

The goal of Topic 01 is not to memorize:

```bash
ssh -J ...
```

or:

```text
ProxyJump
```

The real skill is understanding the entire access path:

```text
                         Internet
                            |
                            v
                    +---------------+
                    |    Bastion    |
                    | controlled    |
                    | entry point   |
                    +---------------+
                            |
                     Private network
                            |
              +-------------+-------------+
              |                           |
              v                           v
       Pipeline server             PostgreSQL server
              |
              v
        Data workloads
```

And understanding the identity layers:

```text
HOST IDENTITY
    |
    | host key / known_hosts
    v
"Am I talking to the correct server?"

USER IDENTITY
    |
    | public/private key
    v
"Can this user prove who they are?"

AUTHORIZATION
    |
    | account permissions
    v
"What is this user allowed to do?"
```

A production-ready Data Engineer should be able to move from:

```text
"I can SSH into a machine."
```

to:

```text
"I understand exactly how this connection works,
which identity is being used,
which server identity I verified,
which network path I am taking,
which trust boundaries I am crossing,
how to diagnose a failure,
how to rotate the credential,
and how to document the access path for the next engineer."
```

That is the standard to carry into the rest of G2.
