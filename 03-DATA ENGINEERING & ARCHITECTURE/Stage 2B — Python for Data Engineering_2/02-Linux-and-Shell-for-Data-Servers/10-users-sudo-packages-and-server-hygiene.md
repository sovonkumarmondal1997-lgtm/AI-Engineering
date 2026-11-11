# Users, sudo, Packages, and Server Hygiene

> **Stage 2B — Linux and Shell for Data Servers**  
> **Topic 10 — Users, sudo, packages, and server hygiene**  
> **Phase D — Keeping Servers Safe (Advanced)**

## Learning Objective

This is the final topic of G2. The goal is not to turn you into a generic Linux security specialist. The goal is to make you capable of operating a production-like Linux Data Engineering server that is:

- secure;
- least-privileged;
- patched;
- auditable;
- correctly time-synchronized;
- safely networked;
- reproducible;
- maintainable;
- rebuildable from code.

The central progression is:

```text
Identity
  ↓
Permissions
  ↓
Privilege
  ↓
Packages
  ↓
Network exposure
  ↓
Time
  ↓
Secrets
  ↓
Auditing
  ↓
Automation
  ↓
Rebuildability
```

The final operational principle is:

> **A production server should not depend on one engineer remembering how it was manually configured.**

---

# 1. Where This Topic Fits

The G2 dependency chain is:

```text
01 SSH
  ↓
02 SSH tunnels
  ↓
03 tmux
  ↓
04 file transfer
  ↓
05 systemd services
  ↓
06 resource diagnosis
  ↓
07 disk management
  ↓
08 command-line data tools
  ↓
09 log investigation
  ↓
10 server safety
```

Earlier topics taught you how to reach, operate, diagnose, and inspect a server.

Topic 10 asks:

> **Can I keep that server secure, consistent, auditable, and replaceable?**

This is why hygiene comes last.

---

# 2. Prerequisites

You should already understand:

- Linux command-line navigation;
- files and permissions;
- processes and signals;
- shell scripts;
- SSH and SSH keys;
- systemd;
- logs;
- networking;
- basic secrets hygiene;
- `jq` and other command-line data tools.

We will refresh concepts when necessary, but this module does not repeat Stage 0.

The learning loop remains:

```text
Read
  ↓
Do it on a practice server
  ↓
Make it repeatable
  ↓
Break it
  ↓
Diagnose from evidence
  ↓
Fix it
  ↓
Verify
  ↓
Write the runbook
  ↓
Explain aloud
```

---

# 3. Practice Environment and Safety

Use one of:

- an Ubuntu VM;
- WSL2 with systemd enabled;
- a disposable cloud VM;
- a small private Docker/VM lab with a bastion.

For SSH and firewall exercises, a VM or cloud topology is preferable.

A useful topology is:

```text
Internet
   |
   v
Bastion
   |
private network
   |
   +------> data-server
               |
               +--> pipeline service
               +--> database client
```

## Critical Safety Rule

Never harden a remote server blindly.

Before changing SSH or firewall configuration:

```text
keep current recovery session open
        ↓
validate configuration
        ↓
open second session
        ↓
test
        ↓
only then close original session
```

Do not perform destructive experiments on a production server.

Use synthetic credentials and test data.

Never put real:

- passwords;
- API tokens;
- private keys;
- cloud credentials;
- customer data

into this training module or lab.

---

# 4. Core Server-Hygiene Mental Model

```text
WHO
  ↓
user / group / service account

WHAT
  ↓
process / service / file

PERMISSIONS
  ↓
read / write / execute

AUTHORIZATION
  ↓
sudo / SSH / firewall

PATCHING
  ↓
secure software versions

TIME
  ↓
UTC + synchronization

SECRETS
  ↓
restricted permissions

AUDITING
  ↓
know who did what

AUTOMATION
  ↓
repeatable bootstrap

REBUILDABILITY
  ↓
immutable infrastructure
```

Server hygiene is not only security.

It affects:

- reliability;
- reproducibility;
- debugging;
- incident response;
- deployment;
- compliance;
- data correctness;
- operational cost.

---

# 5. Linux Users and Groups

A Linux process runs with an identity.

That identity determines what the process can access.

The simplified model is:

```text
user
  ↓
UID
  ↓
process
  ↓
file permissions
```

Groups extend this model:

```text
user
  ↓
primary group
  +
supplementary groups
  ↓
additional access
```

## 5.1 UID and GID

A user has a numeric UID.

A group has a numeric GID.

Inspect your current identity:

```bash
id
```

Example:

```text
uid=1001(operator) gid=1001(operator) groups=1001(operator),27(sudo)
```

This tells you:

- username;
- UID;
- primary group;
- supplementary groups.

## 5.2 `whoami`

```bash
whoami
```

Answers:

> Which username am I currently operating as?

## 5.3 `groups`

```bash
groups
```

Shows the groups associated with your current account.

## 5.4 `getent passwd`

```bash
getent passwd
```

Queries the configured passwd database.

A record conceptually contains:

```text
username:x:UID:GID:comment:home:shell
```

Do not interpret `/etc/passwd` as a password store. Password hashes are normally stored in the protected shadow database.

## 5.5 `getent group`

```bash
getent group
```

Shows group membership information.

## 5.6 `/etc/shadow`

Be aware of:

```text
/etc/shadow
```

It contains sensitive authentication-related information and must not be world-readable.

Do not casually copy or expose its contents.

---

# 6. Regular Users vs Service Accounts

A human operator and a pipeline process have different security requirements.

| Identity | Purpose | Interactive Login | Typical Privilege |
|---|---|---:|---|
| `root` | system administration | yes | extremely high |
| `operator` | human operations | yes | controlled |
| `pipeline` | service execution | normally no | narrowly scoped |
| `analytics` | approved data access | depends | narrowly scoped |

The important distinction is:

```text
human identity
≠
service identity
```

A production pipeline should not normally run under a developer's personal account.

It should not run as `root` merely because root makes permissions easier.

---

# 7. Service Accounts

A service account is a dedicated identity used by a service or job.

For example:

```text
pipeline
```

might own and execute an ingestion service.

Create one on a disposable Ubuntu lab:

```bash
sudo useradd \
  --system \
  --home /nonexistent \
  --shell /usr/sbin/nologin \
  pipeline
```

## Explain Every Option

### `--system`

Creates a system/service-oriented account.

### `--home /nonexistent`

The service does not need a normal human home directory.

### `--shell /usr/sbin/nologin`

Prevents normal interactive shell login.

### `pipeline`

The service identity name.

Inspect it:

```bash
getent passwd pipeline
```

Then:

```bash
id pipeline
```

## Service-Account Mental Model

```text
dedicated identity
+
no interactive login
+
minimal permissions
+
owns only required files
=
safer service execution
```

---

# 8. Why Service Accounts Matter to Data Engineering

Consider an ingestion service:

```text
API
 ↓
Python consumer
 ↓
raw-data directory
 ↓
database
```

If it runs as root:

```text
Python process
    ↓
root
    ↓
can potentially modify almost everything
```

If it runs as `pipeline`:

```text
Python process
    ↓
pipeline
    ↓
read source configuration
write /data/raw
connect to approved service
```

The blast radius is much smaller.

This matters for:

- ingestion pipelines;
- Airflow workers;
- batch jobs;
- API consumers;
- Spark wrappers;
- database clients;
- file-processing services;
- scheduled systemd jobs.

---

# 9. Group Design

Use groups for shared responsibilities rather than sharing human accounts.

Example:

```text
pipeline
operator
analytics
```

Possible model:

```text
pipeline
  ↓
owns service runtime files

operator
  ↓
can operate approved services

analytics
  ↓
reads approved datasets
```

Avoid:

```text
everyone
  ↓
shared root account
```

because shared identities destroy accountability.

A good design preserves:

```text
individual human identity
+
group-based authorization
+
dedicated service identities
```

---

# 10. File Ownership and Service Identity

Suppose:

```text
/data/pipeline/
```

belongs to:

```text
pipeline:pipeline
```

A service can then operate on its own data without needing root.

Inspect:

```bash
ls -ld /data/pipeline
```

Inspect files:

```bash
ls -l /data/pipeline/
```

A useful question is:

> Why does this process need access to this directory?

If the answer is unclear, permissions are probably too broad.

---

# 11. `sudo` Fundamentals

`sudo` provides controlled privilege elevation.

Instead of:

```text
human
  ↓
root login
```

you can use:

```text
named user
  ↓
sudo
  ↓
specific privileged operation
```

Example:

```bash
sudo systemctl restart orders-consumer.service
```

Conceptually:

```text
authenticate
  ↓
authorize
  ↓
execute privileged command
  ↓
record/audit action
```

This improves:

- accountability;
- least privilege;
- auditing;
- operational discipline.

---

# 12. Least Privilege

Least privilege means:

> Give an identity only the permissions required for its actual job.

Bad:

```text
operator
  ↓
unrestricted root
```

Better:

```text
operator
  ↓
restart orders-consumer.service
  ↓
inspect its status
  ↓
read approved logs
```

The difference matters.

A compromised operator credential should not automatically become:

```text
complete server compromise
```

---

# 13. Narrow `sudo` Rules

A narrow rule might permit one service operation.

Conceptually:

```text
%operator ALL=(root) /usr/bin/systemctl restart orders-consumer.service
```

The exact `systemctl` path must be verified on the target system:

```bash
command -v systemctl
```

Do not copy paths blindly across distributions.

A narrow rule is preferable to:

```text
%operator ALL=(ALL) ALL
```

The second grants broad administrative capability.

---

# 14. `visudo`

Edit sudo policy safely with:

```bash
sudo visudo
```

Why?

Because `visudo` validates sudoers syntax before installing the new configuration.

A malformed sudoers file can prevent administrators from using `sudo`.

That is a high-impact failure.

The operational rule is:

```text
edit safely
→ validate
→ test
```

not:

```text
edit /etc/sudoers directly
→ hope
```

---

# 15. Sudo Rule Design

When creating a sudo rule, ask:

1. Who needs it?
2. What exact command?
3. What exact arguments?
4. Which host?
5. Does it need a password?
6. Can the command itself escape into a shell?
7. Can wildcards broaden the permission?
8. Can the same operation be achieved without sudo?

## Example

Suppose operators only need:

```bash
systemctl restart orders-consumer.service
```

Do not automatically authorize:

```text
systemctl *
```

because many systemctl operations are far more powerful.

## `NOPASSWD`

You may encounter:

```text
NOPASSWD
```

This removes a password prompt for a permitted command.

It can be appropriate for carefully controlled automation, but it should not become a shortcut to unrestricted root access.

---

# 16. Sudo Auditing

Auditing asks:

> Who used privilege, when, and for what?

Useful sources vary by distribution and logging configuration.

Search journal evidence:

```bash
journalctl | grep sudo
```

Authentication logs may also contain sudo activity.

Inspect login history:

```bash
last
```

Inspect last-login information:

```bash
lastlog
```

The exact files and logging behavior vary by Ubuntu/Debian release and configuration.

Do not assume:

```text
one command
=
complete audit trail
```

Correlate:

```text
login
+
sudo
+
service changes
+
application logs
```

---

# 17. Package Management on Debian/Ubuntu

Data servers depend on software packages.

Examples:

- Python runtimes;
- PostgreSQL clients;
- compression utilities;
- `jq`;
- monitoring tools;
- system libraries.

Debian/Ubuntu uses APT.

The most important distinction is:

```text
apt update
```

versus:

```text
apt upgrade
```

---

# 18. `apt update`

Run:

```bash
sudo apt update
```

This refreshes local package metadata.

It does **not** mean:

> Upgrade every installed package.

Think:

```text
repository metadata
        ↓
local package index
```

After `apt update`, the system knows more accurately what versions are available.

---

# 19. `apt upgrade`

Run:

```bash
sudo apt upgrade
```

This installs available upgrades according to APT's dependency and upgrade rules.

Think:

```text
available package metadata
        ↓
installed package
        ↓
newer package version
```

Therefore:

```text
apt update
=
refresh knowledge

apt upgrade
=
apply eligible upgrades
```

This distinction is essential.

---

# 20. Installing Packages

Example:

```bash
sudo apt install jq
```

Before installing in production, consider:

- package source;
- version;
- security status;
- dependency impact;
- maintenance policy;
- whether the package is actually needed.

Avoid installing arbitrary packages simply because a command is convenient.

---

# 21. Removing Packages

```bash
sudo apt remove jq
```

This removes the package but may leave configuration files.

A stronger cleanup operation can have additional effects, so understand the command before using it.

Do not turn package cleanup into:

```text
remove everything that looks unused
```

on a production server.

---

# 22. Inspecting Package Versions

Use:

```bash
apt policy jq
```

You can also inspect installed package state:

```bash
dpkg -l jq
```

The key questions are:

```text
Installed version?
Candidate version?
Repository source?
Upgradeable?
```

---

# 23. Why Package Versions Matter to Data Engineering

Suppose a pipeline depends on:

```text
PostgreSQL client
```

A major version change could affect:

- authentication;
- SQL behavior;
- TLS defaults;
- client/server compatibility;
- scripts;
- tooling.

Similarly:

```text
Python
OpenSSL
database drivers
compression libraries
```

can affect runtime behavior.

Therefore:

> "latest" is not automatically synonymous with "safe for this pipeline."

---

# 24. Security Updates

A server must be patched.

An unpatched server can contain:

- known vulnerabilities;
- bugs;
- outdated libraries;
- security weaknesses.

But production patching must also consider:

- compatibility;
- downtime;
- service restarts;
- reboot requirements;
- maintenance windows;
- rollback/recovery.

The balanced model is:

```text
Never patch
    ↓
security exposure

Patch blindly
    ↓
availability/compatibility risk

Controlled patching
    ↓
security + reliability
```

---

# 25. Unattended-Upgrades — Automatic Security Updates

Ubuntu/Debian environments can use `unattended-upgrades`.

Install when appropriate:

```bash
sudo apt install unattended-upgrades
```

Configuration and enablement vary by distribution release.

A common configuration file is:

```text
/etc/apt/apt.conf.d/50unattended-upgrades
```

A common periodic configuration is:

```text
/etc/apt/apt.conf.d/20auto-upgrades
```

Inspect the configuration rather than assuming defaults:

```bash
cat /etc/apt/apt.conf.d/20auto-upgrades
```

and:

```bash
grep -n 'Unattended-Upgrade' /etc/apt/apt.conf.d/50unattended-upgrades
```

---

# 26. Automatic Updates vs Automatic Reboots

These are different decisions.

```text
automatic security package installation
            ≠
automatic server reboot
```

A production data server may tolerate automatic security package installation but require controlled reboot scheduling.

Before enabling automatic restarts, understand:

- service restart behavior;
- reboot windows;
- stateful workloads;
- cluster redundancy;
- pipeline schedules;
- maintenance policy.

The objective is:

```text
patch promptly
+
control availability impact
```

---

# 27. Package Holds

Sometimes a critical package must remain at a known-compatible version temporarily.

Hold:

```bash
sudo apt-mark hold <package>
```

Inspect holds:

```bash
apt-mark showhold
```

Release:

```bash
sudo apt-mark unhold <package>
```

A hold is a control mechanism, not a permanent maintenance strategy.

The correct lifecycle is:

```text
hold
→ investigate compatibility
→ test newer version
→ upgrade deliberately
→ remove hold
```

---

# 28. Package Pinning

Package pinning provides more expressive version/source preference rules than a simple hold.

Conceptually:

```text
package
  ↓
candidate selection policy
  ↓
preferred version/source
```

Pinning can be useful when:

- a repository provides multiple versions;
- a package needs controlled selection;
- compatibility is being managed deliberately.

It also creates maintenance complexity.

Therefore:

> Document why a package is pinned, who owns the decision, and when it should be revisited.

---

# 29. SSH Hardening

Topic 01 taught SSH access.

Now we harden it.

The core goals are:

```text
strong authentication
+
no unnecessary root access
+
no unnecessary password authentication
+
restricted users
+
private network exposure
+
bastion access
```

---

# 30. Disable Password Authentication

A typical SSH server configuration uses:

```text
PasswordAuthentication no
```

The exact configuration file and effective setting should be verified on the target distribution.

Inspect effective SSH configuration where supported:

```bash
sshd -T | grep -i passwordauthentication
```

The desired result is conceptually:

```text
passwordauthentication no
```

Do not make this change until you have confirmed that key-based access works.

---

# 31. Disable Direct Root Login

A typical hardening setting is:

```text
PermitRootLogin no
```

The desired access pattern becomes:

```text
named user
  ↓
SSH key
  ↓
sudo when required
```

instead of:

```text
root
  ↓
direct SSH
```

This improves accountability because actions begin with a named human identity.

---

# 32. Restrict SSH Users

You can restrict access with:

```text
AllowUsers operator
```

or group-based policies where appropriate.

Example concept:

```text
AllowGroups server-operators
```

Do not blindly add both mechanisms without understanding their interaction.

Verify the effective configuration and test a second connection.

---

# 33. Safe SSH Hardening Procedure

Never do:

```text
edit sshd_config
restart ssh
disconnect
hope
```

Use:

```text
1. Keep current SSH session open.
2. Make one controlled change.
3. Validate configuration.
4. Reload/restart carefully.
5. Open a SECOND SSH session.
6. Confirm key authentication.
7. Confirm allowed user.
8. Confirm bastion path.
9. Only then close original session.
```

Validate configuration:

```bash
sudo sshd -t
```

If validation fails:

```text
do not restart blindly
```

Fix the configuration first.

---

# 34. SSH Hardening Through a Bastion

A secure topology is often:

```text
Internet
   |
   v
bastion
   |
private network
   |
   v
data-server
```

The private data server does not need a public SSH endpoint.

Topic 01's `ProxyJump` pattern can then be used:

```bash
ssh -J bastion operator@data-server
```

This reduces exposure.

The principle is:

> Prefer private networking plus controlled entry points over exposing every server directly to the Internet.

---

# 35. Firewall Fundamentals

A firewall controls network reachability.

Conceptually:

```text
packet
  ↓
firewall policy
  ↓
allow / deny
```

Important dimensions include:

- source;
- destination;
- port;
- protocol;
- direction;
- interface/network.

Least exposure means:

```text
only expose what must be reachable
```

---

# 36. UFW

Ubuntu commonly provides UFW as a simpler firewall management interface.

Check:

```bash
sudo ufw status
```

A policy should be designed before enabling the firewall.

For a bastion-only SSH rule:

```bash
sudo ufw allow from <BASTION_IP> to any port 22 proto tcp
```

Replace `<BASTION_IP>` with the actual private/source address in the lab.

Then allow only the required application ports.

Example:

```text
SSH
  ← bastion only

database
  ← private application network only

web UI
  ← approved private network only
```

Do not expose databases to the public Internet merely because a client needs connectivity.

---

# 37. Firewall Safety

A remote firewall mistake can lock you out.

Use:

```text
current recovery session
+
known-good bastion path
+
test connection
```

before closing access.

In a lab, practice failure recovery deliberately.

For example:

```text
allow SSH from wrong source
        ↓
second connection fails
        ↓
recover through existing session
        ↓
correct rule
        ↓
verify
```

This teaches the operational skill, not just the syntax.

---

# 38. Private Networking

A firewall is not a substitute for network architecture.

Prefer:

```text
public bastion
        ↓
private data server
        ↓
private database
```

over:

```text
Internet
  ↓
public SSH
public database
public internal UI
```

Private networking reduces the attack surface.

It also makes architectural intent clearer:

```text
external access
    ↓
controlled entry point
    ↓
internal services
```

---

# 39. Time Synchronization

Time is infrastructure.

Data Engineering systems depend on correct timestamps for:

- scheduled jobs;
- logs;
- incremental ingestion;
- event ordering;
- partitions;
- retries;
- monitoring;
- incident correlation.

A server with incorrect time can create data correctness problems.

---

# 40. UTC

Use UTC as the operational server timezone.

Check:

```bash
timedatectl
```

A UTC system should report:

```text
Time zone: Etc/UTC
```

or an equivalent UTC designation.

Set it in a disposable lab:

```bash
sudo timedatectl set-timezone UTC
```

Verify:

```bash
timedatectl
```

and:

```bash
date -u
```

---

# 41. Time Synchronization

Check:

```bash
timedatectl status
```

Look for synchronization information.

On systems using `systemd-timesyncd`, inspect:

```bash
systemctl status systemd-timesyncd
```

Other environments may use chrony or another time synchronization service.

The exact implementation can vary.

The invariant is:

```text
server clock
  ↓
synchronized reference
  ↓
trusted timestamps
```

---

# 42. Timezone Bugs in Data Engineering

Imagine:

```text
job schedule:
02:00 local time

server:
UTC

developer:
IST
```

If scheduling assumptions are unclear, jobs can:

- run at unexpected times;
- miss partitions;
- duplicate windows;
- misorder events;
- produce incorrect reports.

For incident investigation:

```text
application: 14:30 UTC
database: 20:00 IST
operator: 20:00 local
```

may represent the same instant.

Normalize to UTC.

---

# 43. Secrets and Environment Files

A common Data Engineering pattern is:

```text
systemd service
    ↓
EnvironmentFile
    ↓
database credentials
```

The environment file must not be world-readable.

Example:

```bash
sudo install -o pipeline -g pipeline -m 600 /dev/null /etc/orders-consumer.env
```

Then write synthetic lab values:

```text
DB_HOST=private-db
DB_USER=orders_reader
DB_PASSWORD=LAB_ONLY_EXAMPLE
```

The important permission is:

```text
-rw-------
```

owned by the service account.

Verify:

```bash
ls -l /etc/orders-consumer.env
```

---

# 44. Why `chmod 644` Is Wrong for Credentials

This:

```bash
chmod 644 /etc/orders-consumer.env
```

makes the file readable by other users.

For a secret-bearing file, that is usually inappropriate.

Prefer owner-only access:

```bash
chmod 600 /etc/orders-consumer.env
```

or a carefully chosen group model when multiple identities genuinely need access.

Never use:

```bash
chmod 777
```

as a permission workaround.

---

# 45. Environment Variables and Process Exposure

A secret can be exposed in more than one place.

Potential exposure points include:

```text
shell history
process arguments
environment
logs
configuration files
source code
backup files
```

Avoid:

```bash
python job.py --password='real-secret'
```

because command arguments can be observable.

Prefer a secret-management mechanism appropriate to the environment, or a protected configuration file in this local server-learning scope.

This module does not attempt to replace dedicated cloud secret-management systems.

---

# 46. `authorized_keys` Review

SSH public keys are stored in files such as:

```text
~/.ssh/authorized_keys
```

Review them periodically.

For a user:

```bash
cat /home/operator/.ssh/authorized_keys
```

Then ask:

- Who owns each key?
- Is the key still required?
- Is it associated with a former employee?
- Does its comment identify ownership?
- Is the file permission correct?

Inspect:

```bash
ls -ld /home/operator/.ssh
ls -l /home/operator/.ssh/authorized_keys
```

Typical private-key directory/file permissions should be restrictive.

Do not copy real private keys into a lab.

---

# 47. Login Auditing

Useful commands include:

```bash
last
```

and:

```bash
lastlog
```

Also inspect journal/authentication evidence where available:

```bash
journalctl
```

Search for SSH events:

```bash
journalctl | grep -Ei 'sshd|ssh'
```

The exact log source depends on distribution and configuration.

The audit question is:

```text
Who logged in?
When?
From where?
Was it expected?
What happened afterward?
```

---

# 48. Brute-Force Protection Awareness

A publicly exposed SSH service can receive repeated authentication attempts.

Tools such as:

- Fail2ban;
- cloud security controls;
- network firewalls;
- rate-limiting systems

can reduce brute-force exposure.

For this roadmap, understand the role rather than becoming an expert in every tool.

A stronger architecture is still:

```text
private server
+
bastion
+
key authentication
+
restricted users
+
firewall
```

Brute-force protection should complement, not replace, good network design.

---

# 49. Server Bootstrap

Manual server configuration creates drift.

A server may slowly become:

```text
Server A
  manually configured

Server B
  slightly different

Server C
  one emergency fix

Server D
  unknown
```

This is configuration drift.

A bootstrap process defines the desired baseline.

---

# 50. Server Bootstrap Checklist

A production-like checklist should cover:

```text
IDENTITY
[ ] service users
[ ] operator groups

SSH
[ ] key authentication
[ ] no password login
[ ] no direct root login
[ ] allowed users
[ ] bastion path

FIREWALL
[ ] required ports
[ ] restricted sources
[ ] private services

PACKAGES
[ ] package metadata updated
[ ] security updates
[ ] critical versions reviewed
[ ] held/pinned packages documented

TIME
[ ] UTC
[ ] time synchronization

FILES
[ ] data directories
[ ] correct ownership
[ ] secret permissions

SERVICES
[ ] dedicated service account
[ ] systemd units
[ ] restart policy

LOGGING
[ ] journal
[ ] logrotate where needed
[ ] retention

MONITORING
[ ] CPU
[ ] memory
[ ] disk
[ ] service health

AUDITING
[ ] login history
[ ] sudo activity
[ ] authorized_keys review

REBUILDABILITY
[ ] bootstrap script
[ ] tested from clean server
```

---

# 51. Bootstrap Script Design

A bootstrap script should be:

- readable;
- repeatable;
- idempotent;
- safe;
- tested;
- version-controlled.

A minimal skeleton:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Starting server bootstrap"

apt_update() {
    apt-get update
}

install_packages() {
    apt-get install -y jq curl
}

create_service_user() {
    if ! id pipeline >/dev/null 2>&1; then
        useradd \
          --system \
          --home /nonexistent \
          --shell /usr/sbin/nologin \
          pipeline
    fi
}

create_directories() {
    install -d \
      -o pipeline \
      -g pipeline \
      -m 0750 \
      /data/pipeline
}

apt_update
install_packages
create_service_user
create_directories

echo "Bootstrap complete"
```

This is intentionally simplified.

A production bootstrap should also handle:

- SSH configuration;
- firewall;
- time;
- package policy;
- monitoring;
- log policy;
- validation.

---

# 52. Idempotency

An idempotent script can be run repeatedly without causing unintended changes.

Bad:

```bash
useradd pipeline
```

every time.

Second execution:

```text
user already exists
```

Better:

```bash
if ! id pipeline >/dev/null 2>&1; then
    useradd ...
fi
```

Likewise:

```text
create directory if absent
set desired ownership
set desired permissions
```

rather than blindly appending duplicate configuration.

---

# 53. Why Idempotency Matters

Suppose bootstrap runs:

```text
Day 1
Day 7
after incident
after rebuild
in staging
in production
```

If it is not idempotent, every execution can introduce:

- duplicate users;
- duplicate configuration;
- broken permissions;
- conflicting firewall rules;
- repeated lines;
- unexpected state.

Idempotency gives you:

```text
known input
+
repeatable process
=
predictable state
```

---

# 54. Validate Bootstrap Scripts

Before applying changes:

```text
syntax check
        ↓
dry-run where available
        ↓
disposable server
        ↓
first execution
        ↓
second execution
        ↓
compare state
```

Shell syntax can be checked with:

```bash
bash -n bootstrap.sh
```

Do not treat syntax validation as proof of correctness.

It only proves that the shell can parse the script.

---

# 55. Immutable Infrastructure

The next conceptual step is:

> Do not treat servers as unique pets that require manual care forever.

Instead:

```text
known code
+
known configuration
+
known image
        ↓
new server
```

This is the immutable-infrastructure mindset.

---

# 56. Pets vs Cattle

## Pets

A pet server is:

```text
special
manually configured
carefully repaired
hard to replace
```

Example:

```text
"analytics-prod-01 has a special fix that only Ravi knows."
```

This is dangerous.

## Cattle

A cattle-style server is:

```text
standardized
automated
replaceable
rebuildable
```

Example:

```text
server fails
   ↓
provision replacement
   ↓
run known bootstrap/image
   ↓
restore required state
   ↓
service resumes
```

The objective is not to make servers disposable carelessly.

The objective is to make them **replaceable deliberately**.

---

# 57. Rebuilding From Images and Code

A mature infrastructure workflow becomes:

```text
source code
+
bootstrap/configuration
+
image
+
infrastructure definition
        ↓
server
```

If the server is lost:

```text
rebuild
```

rather than:

```text
remember everything manually done
```

This connects directly to later infrastructure and cloud modules, including Module 2.18.

---

# 58. Manual Change vs Reproducible Change

Bad:

```text
SSH into production
edit file
change permission
restart service
forget what changed
```

Better:

```text
change code/configuration
        ↓
review
        ↓
apply
        ↓
validate
        ↓
record version
```

The server should increasingly become a **result of automation**, not the primary place where configuration is invented.

---

# 59. Data Engineering Scenario — Pipeline Service

Suppose:

```text
orders-consumer.service
```

runs a Python application.

A production design is:

```text
systemd
   ↓
User=pipeline
   ↓
Python virtual environment
   ↓
/data/orders
   ↓
private database
```

The operator has:

```text
sudo systemctl restart orders-consumer.service
```

but does not have unrestricted root access.

This creates separation:

```text
pipeline
  = executes data workload

operator
  = operates workload

root
  = controlled system administration
```

---

# 60. Data Engineering Scenario — Package Compatibility

A database client upgrade changes behavior.

Without package control:

```text
automatic upgrade
   ↓
pipeline behavior changes
```

With controlled operations:

```text
security updates
+
critical package hold/pin
+
compatibility testing
   ↓
predictable production behavior
```

The hold must still be reviewed and eventually removed when safe.

---

# 61. Data Engineering Scenario — UTC

An incremental pipeline runs:

```text
WHERE updated_at >= start
AND updated_at < end
```

If servers and data producers interpret timestamps differently:

```text
missing rows
or
duplicate rows
```

can result.

UTC does not automatically solve every timestamp problem, but it removes one major source of ambiguity.

---

# 62. Data Engineering Scenario — Secrets

A pipeline requires:

```text
DB_HOST
DB_USER
DB_PASSWORD
```

Bad:

```text
script.sh
    ↓
password embedded in source
```

Better:

```text
protected environment file
    ↓
pipeline service account
    ↓
systemd service
```

Better still in mature cloud environments:

```text
managed secret store
    ↓
short-lived/controlled access
    ↓
application
```

This module teaches the server-side permission layer; dedicated secret-management systems are a separate topic.

---

# 63. Production Safety Rules

Before changing:

- SSH;
- firewall;
- users;
- sudo;
- package versions;
- credentials;
- system configuration;

use:

```text
Observe
   ↓
Understand
   ↓
Change
   ↓
Validate
   ↓
Test
   ↓
Document
```

## Never Lock Yourself Out

For remote SSH changes:

```text
current session
+
recovery path
+
second-session test
```

## Never Use Dangerous Shortcuts

Do not use:

```bash
chmod -R 777 /
```

Do not use unrestricted sudo as an operational convenience.

Do not expose databases publicly merely to avoid configuring private networking.

Do not disable security controls because an application is inconvenient to configure.

---

# 64. Common Mistakes

## Mistake 1 — Running Services as Root

Why it fails:

```text
application compromise
    ↓
root-level impact
```

Fix:

```text
dedicated service account
```

## Mistake 2 — Sharing Human Accounts

Why it fails:

```text
no individual accountability
```

Fix:

```text
individual identities
+
groups
```

## Mistake 3 — Giving `sudo ALL`

Why it fails:

```text
least privilege disappears
```

Fix:

```text
narrow commands
```

## Mistake 4 — Editing `/etc/sudoers` Directly

Why it fails:

A syntax error can break privilege management.

Fix:

```bash
sudo visudo
```

## Mistake 5 — Confusing `apt update` With Upgrade

Why it fails:

You may believe software is patched when only package metadata was refreshed.

Fix:

Understand:

```text
update
=
metadata

upgrade
=
package changes
```

## Mistake 6 — Holding Packages Forever

Why it fails:

Security updates can remain blocked indefinitely.

Fix:

Document holds and review them.

## Mistake 7 — Disabling SSH Password Login Before Testing Keys

Why it fails:

You can lock yourself out.

Fix:

Test a second key-based session first.

## Mistake 8 — Enabling Firewall Without Recovery Access

Why it fails:

SSH becomes unreachable.

Fix:

Keep a recovery session and test the bastion path.

## Mistake 9 — Running Servers in Local Time

Why it fails:

Schedules and incident timelines become ambiguous.

Fix:

Use UTC.

## Mistake 10 — World-Readable Credentials

Why it fails:

Any local user may be able to read secrets.

Fix:

Use owner-only permissions such as:

```text
0600
```

when appropriate.

## Mistake 11 — Manual Server Drift

Why it fails:

No one knows exactly how the server was configured.

Fix:

Bootstrap and infrastructure-as-code.

## Mistake 12 — Non-Idempotent Bootstrap

Why it fails:

Running the same script twice creates duplicate or conflicting state.

Fix:

Test:

```text
run 1
run 2
```

and verify the second run is safe.

---

# 65. Hands-on Labs — `server_lab/10/`

Use a disposable server.

Do not use real credentials.

---

## Lab 1 — Pipeline Service Account and Limited sudo

### Objective

Create:

```text
pipeline
operator
```

and run a Topic 05 service as `pipeline`.

### Step 1 — Create Service Account

```bash
sudo useradd \
  --system \
  --home /nonexistent \
  --shell /usr/sbin/nologin \
  pipeline
```

Verify:

```bash
id pipeline
getent passwd pipeline
```

### Step 2 — Create Operator Group

```bash
sudo groupadd operator
```

If the group already exists, handle that safely rather than failing.

Create a test human user:

```bash
sudo useradd --create-home laboperator
sudo usermod -aG operator laboperator
```

### Step 3 — Configure Topic 05 Service

Use a systemd service with:

```text
User=pipeline
Group=pipeline
```

Verify:

```bash
systemctl status orders-consumer.service
```

Inspect the process:

```bash
ps -eo user,pid,cmd | grep orders-consumer
```

### Step 4 — Grant Narrow sudo

Use:

```bash
sudo visudo
```

Create a narrow rule appropriate to your lab.

Verify:

```bash
sudo -l -U laboperator
```

### Step 5 — Prove Least Privilege

The operator should be able to:

```text
restart approved service
```

but should not automatically receive:

```text
arbitrary root shell
```

### Deliverable

Document:

```text
service account
service owner
operator group
sudo rule
why the rule is narrow
```

---

# 66. Lab 2 — SSH Hardening and Bastion-Only Firewall

### Objective

On a private practice server:

- disable password login;
- disable direct root login;
- restrict SSH users;
- allow SSH only from bastion.

### Step 1 — Verify Key Access

Open a second SSH session before making changes.

### Step 2 — Inspect Effective SSH Configuration

```bash
sudo sshd -T | grep -Ei 'passwordauthentication|permitrootlogin|allowusers|allowgroups'
```

### Step 3 — Configure

Conceptually:

```text
PasswordAuthentication no
PermitRootLogin no
AllowUsers operator
```

Use the appropriate account and configuration mechanism for the lab.

### Step 4 — Validate

```bash
sudo sshd -t
```

Do not continue if validation fails.

### Step 5 — Firewall

Example:

```bash
sudo ufw allow from <BASTION_IP> to any port 22 proto tcp
```

Allow other required application ports only from their intended private sources.

### Step 6 — Test From Bastion

```bash
ssh operator@data-server
```

### Step 7 — Test Password Rejection

From a controlled test client, verify that password authentication is refused.

Do not expose real credentials.

### Deliverable

Record:

```text
SSH authentication policy
allowed users
bastion address
firewall rules
verification evidence
```

---

# 67. Lab 3 — Automatic Security Updates and Package Hold

### Objective

Enable security update automation and hold one package in a disposable environment.

### Step 1 — Install

```bash
sudo apt update
sudo apt install unattended-upgrades
```

### Step 2 — Inspect Configuration

Review:

```text
/etc/apt/apt.conf.d/50unattended-upgrades
```

and:

```text
/etc/apt/apt.conf.d/20auto-upgrades
```

### Step 3 — Verify Service/Timer

Use the appropriate package/system mechanism for your Ubuntu release.

Inspect:

```bash
systemctl list-timers
```

where systemd timers are used.

### Step 4 — Hold a Lab Package

Choose a non-critical lab package:

```bash
sudo apt-mark hold jq
```

Verify:

```bash
apt-mark showhold
```

### Step 5 — Release It

```bash
sudo apt-mark unhold jq
```

### Deliverable

Document:

```text
automatic security update configuration
restart policy
held package
reason
unhold procedure
```

---

# 68. Lab 4 — UTC and Time Synchronization

### Objective

Configure UTC and verify synchronized time.

### Step 1 — Inspect

```bash
timedatectl
```

### Step 2 — Set UTC

On a disposable lab:

```bash
sudo timedatectl set-timezone UTC
```

### Step 3 — Verify

```bash
timedatectl
```

and:

```bash
date -u
```

### Step 4 — Verify Synchronization

Inspect:

```bash
timedatectl status
```

and the active synchronization service, for example:

```bash
systemctl status systemd-timesyncd
```

### Step 5 — Document

Record:

```text
timezone
sync service
synchronization state
UTC verification
```

---

# 69. Lab 5 — Secure Environment File and Idempotent Bootstrap

### Objective

Create a protected credential file and a bootstrap script that can safely run twice.

### Step 1 — Create Secret File

```bash
sudo install \
  -o pipeline \
  -g pipeline \
  -m 600 \
  /dev/null \
  /etc/orders-consumer.env
```

Add only synthetic values:

```text
DB_HOST=private-db
DB_USER=orders_reader
DB_PASSWORD=LAB_ONLY_EXAMPLE
```

Verify:

```bash
ls -l /etc/orders-consumer.env
```

Expected concept:

```text
-rw-------
```

### Step 2 — Create Bootstrap Script

The script should:

- install required packages;
- create the service account if absent;
- create directories if absent;
- set ownership;
- set permissions;
- configure required baseline settings;
- avoid duplicating configuration.

### Step 3 — Validate Syntax

```bash
bash -n bootstrap.sh
```

### Step 4 — First Run

```bash
sudo bash bootstrap.sh
```

### Step 5 — Second Run

```bash
sudo bash bootstrap.sh
```

### Step 6 — Compare State

The second run should not:

- fail because the user exists;
- duplicate configuration;
- create conflicting groups;
- damage permissions.

### Deliverable

Write:

```text
What does the bootstrap guarantee?
What happens on the second run?
Which operations are conditional?
How would you test it on a clean server?
```

---

# 70. Break/Fix Scenarios

## Failure 1 — Pipeline Runs as Root

### Symptom

```text
systemctl status orders-consumer.service
```

shows root ownership.

### Diagnosis

Inspect the unit:

```bash
systemctl cat orders-consumer.service
```

Look for:

```text
User=
Group=
```

### Fix

Run under `pipeline`.

### Lesson

Service identity is a security boundary.

---

## Failure 2 — Operator Has Too Much sudo

### Symptom

```bash
sudo -l -U laboperator
```

shows unrestricted administration.

### Diagnosis

Inspect sudoers configuration.

### Fix

Replace broad permissions with a narrow service-specific rule.

### Lesson

Convenience is not least privilege.

---

## Failure 3 — SSH Lockout Risk

### Symptom

A proposed SSH hardening change prevents authentication.

### Diagnosis

Keep the existing recovery session.

Run:

```bash
sudo sshd -t
```

Inspect effective settings:

```bash
sudo sshd -T
```

### Fix

Correct configuration, then test a second session.

### Lesson

Never close the last known-good administrative path.

---

## Failure 4 — Firewall Lockout

### Symptom

Bastion cannot reach port 22.

### Diagnosis

From the recovery session:

```bash
sudo ufw status numbered
```

### Fix

Correct the source rule.

### Lesson

Firewall changes are connectivity changes.

---

## Failure 5 — Package Update Breaks Client

### Symptom

A database client upgrade changes pipeline behavior.

### Diagnosis

Inspect:

```bash
apt policy <package>
```

Compare known-good and current versions.

### Fix

Use controlled version management, such as a temporary hold while compatibility is tested.

### Lesson

Security maintenance and compatibility management must coexist.

---

## Failure 6 — Credentials Are World-Readable

### Symptom

```bash
ls -l /etc/orders-consumer.env
```

shows:

```text
-rw-r--r--
```

### Fix

For an owner-only secret file:

```bash
sudo chmod 600 /etc/orders-consumer.env
```

Then verify owner/group.

### Lesson

A credential file is a security boundary.

---

## Failure 7 — Server Clock Is Wrong

### Symptom

Logs appear out of order.

### Diagnosis

```bash
timedatectl
date -u
```

### Fix

Correct timezone and time synchronization configuration.

### Lesson

Time is part of data correctness.

---

## Failure 8 — Bootstrap Fails on Second Run

### Symptom

```text
user already exists
group already exists
configuration duplicated
```

### Diagnosis

Find unconditional operations.

### Fix

Make state transitions conditional and convergent.

### Lesson

Idempotency is a production requirement for automation.

---

## Failure 9 — Unknown SSH Key

### Symptom

An old key remains in:

```text
authorized_keys
```

### Diagnosis

Review:

```bash
cat ~/.ssh/authorized_keys
```

and ownership records.

### Fix

Remove obsolete access through an approved process.

### Lesson

Access should have an owner and lifecycle.

---

## Failure 10 — Server Drift

### Symptom

Two supposedly identical servers behave differently.

### Diagnosis

Compare:

```text
package versions
users
groups
SSH configuration
firewall
timezone
service units
permissions
bootstrap version
```

### Fix

Move configuration into automation and rebuild the outlier where practical.

### Lesson

Rebuildability is the long-term answer to configuration drift.

---

# 71. Production Server-Hygiene Checklist

Use this before declaring a server production-ready.

## Identity

- [ ] Named human users.
- [ ] No shared human account.
- [ ] Dedicated service accounts.
- [ ] Service accounts do not require interactive shells.
- [ ] Group membership is intentional.
- [ ] Unused accounts are removed or disabled.

## sudo

- [ ] sudo is used instead of direct root SSH.
- [ ] `visudo` is used for edits.
- [ ] Rules are narrow.
- [ ] Wildcards are reviewed.
- [ ] `NOPASSWD` is justified.
- [ ] sudo activity is auditable.

## Packages

- [ ] Package metadata is regularly refreshed.
- [ ] Security updates are applied.
- [ ] Upgrade policy is documented.
- [ ] Automatic security updates are understood.
- [ ] Reboots/restarts are controlled.
- [ ] Critical package holds are documented.
- [ ] Pins have an owner and review date.

## SSH

- [ ] Key authentication works.
- [ ] Password login is disabled where appropriate.
- [ ] Direct root login is disabled.
- [ ] Allowed users/groups are restricted.
- [ ] Bastion/private networking is used where appropriate.
- [ ] Configuration is validated before reload.
- [ ] Recovery access is tested.

## Firewall

- [ ] Only required ports are open.
- [ ] Source networks are restricted.
- [ ] Databases are private.
- [ ] Internal UIs are private.
- [ ] Bastion access is explicit.

## Time

- [ ] Server timezone is UTC.
- [ ] Time synchronization is active.
- [ ] Time status is monitored.

## Secrets

- [ ] Environment files are owner-only where appropriate.
- [ ] Credentials are not world-readable.
- [ ] Secrets are not embedded in source code.
- [ ] Secrets are not printed into logs.
- [ ] Secret rotation is understood.

## Auditing

- [ ] Login history is available.
- [ ] sudo activity is auditable.
- [ ] authorized_keys is reviewed.
- [ ] Unexpected access can be investigated.

## Operations

- [ ] systemd services have correct users.
- [ ] logs are retained/rotated appropriately.
- [ ] disk usage is monitored.
- [ ] monitoring exists.
- [ ] bootstrap is version-controlled.
- [ ] rebuild procedure is documented.

---

# 72. Server Hygiene Runbook

## Server Identity

```text
hostname:
environment:
owner:
purpose:
```

## Users

```text
human users:
service accounts:
groups:
```

## SSH

```text
allowed users:
authentication method:
bastion:
root login:
password login:
```

## Firewall

```text
allowed ports:
allowed sources:
private services:
```

## Packages

```text
security update policy:
held packages:
pinned packages:
maintenance window:
```

## Time

```text
timezone:
synchronization service:
sync status:
```

## Secrets

```text
secret locations:
owners:
permissions:
rotation procedure:
```

## Bootstrap

```text
bootstrap version:
last tested:
rebuild procedure:
```

## Verification

```text
last hygiene review:
reviewer:
findings:
remediation:
```

---

# 73. Integrated Final Capstone

## Scenario

You receive a fresh Ubuntu data server.

You must prepare it for a production-like Data Engineering pipeline.

## Requirements

```text
1. Create pipeline service account.
2. Create operator group.
3. Configure least-privilege sudo.
4. Install required packages.
5. Enable security updates.
6. Hold one critical package.
7. Harden SSH.
8. Configure firewall.
9. Restrict SSH through bastion.
10. Configure UTC.
11. Verify time synchronization.
12. Create secure data directories.
13. Create secure environment file.
14. Configure monitoring.
15. Build bootstrap.sh.
16. Run bootstrap twice.
17. Verify idempotency.
18. Document everything in a runbook.
19. Explain how the server could be rebuilt.
```

## Capstone Proof

You must demonstrate:

```text
secure
+
repeatable
+
auditable
+
least privilege
+
rebuildable
```

The capstone is not complete because the commands were typed once.

It is complete when the server's desired state can be explained, verified, and reproduced.

---

# 74. Production Decision Framework

When making a server-hygiene decision, ask:

### Identity

```text
Who should perform this?
```

### Permission

```text
What exact resource is required?
```

### Privilege

```text
Does this actually require root?
```

### Network

```text
Who needs to reach this?
```

### Package

```text
What version is required?
```

### Time

```text
Can timestamps be trusted?
```

### Secret

```text
Who can read this credential?
```

### Audit

```text
Can I determine who changed it?
```

### Automation

```text
Can this be repeated safely?
```

### Rebuildability

```text
Can I replace the server?
```

---

# 75. Practice Questions

## Fundamentals

1. What is a Linux user?
2. What is a UID?
3. What is a GID?
4. What is a primary group?
5. What are supplementary groups?
6. What is a service account?
7. Why should services avoid running as root?
8. Why use `nologin` for a service account?
9. What does `id` show?
10. What does `getent passwd` show?

## sudo

11. What is `sudo`?
12. Why is sudo preferable to direct root SSH?
13. What is least privilege?
14. Why use `visudo`?
15. What makes a sudo rule narrow?
16. Why can `systemctl *` be dangerous in sudoers?
17. What is `NOPASSWD`?
18. How can sudo activity be audited?

## Packages

19. What does `apt update` do?
20. What does `apt upgrade` do?
21. How do you install a package?
22. How do you remove a package?
23. How do you inspect a package version?
24. Why do package versions matter?
25. What are security updates?
26. What is unattended-upgrades?
27. Why might automatic reboots require control?
28. What is a package hold?
29. What is package pinning?
30. What is the difference between hold and pinning?

## SSH and Network

31. Why disable SSH password authentication?
32. Why disable direct root SSH login?
33. What is `AllowUsers`?
34. Why use a bastion?
35. Why keep data servers private?
36. What does `sshd -t` do?
37. Why test a second SSH connection?
38. What is a firewall?
39. What is UFW?
40. Why should only required ports be exposed?

## Time and Secrets

41. Why use UTC?
42. How can timezone errors affect data pipelines?
43. What does `timedatectl` show?
44. What is time synchronization?
45. Why should secret files not be world-readable?
46. Why is `chmod 600` commonly appropriate for owner-only credentials?
47. What are other places secrets can accidentally leak?
48. Why should credentials not be placed in command arguments?

## Auditing and Automation

49. What is `last`?
50. What is `lastlog`?
51. Why review `authorized_keys`?
52. What is brute-force protection?
53. What belongs in a server bootstrap checklist?
54. What is idempotency?
55. Why should bootstrap scripts be run twice in testing?
56. What is configuration drift?
57. What is immutable infrastructure?
58. What are pets vs cattle?
59. Why is rebuildability important?
60. How does server hygiene affect Data Engineering reliability?

---

# 76. Interview Practice

## 1. Why should a Data Engineering service run under a dedicated account?

**Model answer:**  
A dedicated service account isolates the process identity and limits the blast radius of compromise or bugs. It also makes file ownership, auditing, and operational permissions clearer.

**Senior framing:**  
Service identity is a security and reliability boundary, not merely a Linux convention.

---

## 2. Explain least privilege.

**Model answer:**  
Grant only the permissions required for the task.

**Senior framing:**  
Least privilege reduces blast radius, improves auditability, and makes operational behavior easier to reason about.

---

## 3. Why use `visudo`?

**Model answer:**  
It edits and validates sudoers safely, reducing the chance that a syntax error breaks sudo administration.

**Senior framing:**  
Privilege configuration is high-impact infrastructure configuration and should be changed through a validation-aware workflow.

---

## 4. What is the difference between `apt update` and `apt upgrade`?

**Model answer:**

```text
apt update
=
refresh package metadata

apt upgrade
=
install eligible newer packages
```

**Senior framing:**  
Refreshing repository state and changing installed software are distinct operational actions.

---

## 5. Why might you hold a package?

**Model answer:**  
To temporarily keep a known-compatible version while testing a newer release.

**Senior framing:**  
A hold is a risk-control mechanism, not a substitute for maintaining supported versions.

---

## 6. How would you harden SSH without locking yourself out?

**Model answer:**

```text
keep current session
→ verify key access
→ edit configuration
→ sshd -t
→ reload carefully
→ test second session
→ close original only after verification
```

**Senior framing:**  
Treat SSH configuration as a change that can remove the recovery path.

---

## 7. Why use a bastion?

**Model answer:**  
It provides a controlled entry point to private servers.

**Senior framing:**  
A bastion reduces public attack surface and centralizes administrative ingress.

---

## 8. Why is UTC important for Data Engineering?

**Model answer:**  
It gives systems a common time reference for scheduling, logs, event ordering, and incremental processing.

**Senior framing:**  
UTC reduces temporal ambiguity but must be combined with explicit timestamp semantics and correct application/database handling.

---

## 9. What is idempotent infrastructure automation?

**Model answer:**  
Automation that can be applied repeatedly and converges on the desired state without creating unintended duplicates or damage.

**Senior framing:**  
Idempotency makes recovery, rebuilds, and repeated deployment safer.

---

## 10. Explain immutable infrastructure.

**Model answer:**  
Instead of manually repairing servers indefinitely, build replacement servers from known code, images, and configuration.

**Senior framing:**  
The goal is to make infrastructure replaceable and reproducible, reducing configuration drift and undocumented state.

---

# 77. Knowledge Check

You should be able to answer "yes" to all of these:

- [ ] I can explain users and groups.
- [ ] I can create a dedicated service account.
- [ ] I can run a systemd service under that account.
- [ ] I can explain least privilege.
- [ ] I can create a narrow sudo rule.
- [ ] I know why `visudo` is used.
- [ ] I can inspect sudo activity.
- [ ] I understand `apt update` vs `apt upgrade`.
- [ ] I can inspect package versions.
- [ ] I understand security updates.
- [ ] I understand unattended upgrades.
- [ ] I understand controlled restarts/reboots.
- [ ] I understand package holds.
- [ ] I understand package pinning.
- [ ] I can harden SSH.
- [ ] I can validate SSH configuration.
- [ ] I can safely test SSH changes.
- [ ] I can configure a firewall in a lab.
- [ ] I understand bastion-based access.
- [ ] I can explain private networking.
- [ ] I can configure/verify UTC.
- [ ] I can verify time synchronization.
- [ ] I can protect an environment file.
- [ ] I can review `authorized_keys`.
- [ ] I understand login auditing.
- [ ] I understand brute-force protection at a high level.
- [ ] I can design a bootstrap checklist.
- [ ] I can write an idempotent bootstrap script.
- [ ] I can explain pets vs cattle.
- [ ] I can explain immutable infrastructure.
- [ ] I can explain how to rebuild a practice server.

---

# 78. Roadmap Coverage Audit

| Roadmap Requirement | Covered? | Where |
|---|---|---|
| Users | ✅ | §5 |
| Groups | ✅ | §5, §9 |
| Service accounts | ✅ | §7–§8 |
| System users | ✅ | §7 |
| No-login service accounts | ✅ | §7 |
| Services use service accounts | ✅ | §59, Labs |
| `sudo` | ✅ | §11–§16 |
| Least privilege | ✅ | §12–§13 |
| `visudo` | ✅ | §14 |
| Limited sudo commands | ✅ | §13, Lab 1 |
| `apt update` | ✅ | §18 |
| `apt upgrade` | ✅ | §19 |
| Install/remove/show packages | ✅ | §20–§22 |
| Security updates | ✅ | §24 |
| Unattended upgrades | ✅ | §25–§26 |
| Restart control | ✅ | §26 |
| Package holding | ✅ | §27 |
| Package pinning | ✅ | §28 |
| SSH password-login disabling | ✅ | §30 |
| Root SSH disabling | ✅ | §31 |
| Allowed-user restriction | ✅ | §32 |
| Safe SSH validation | ✅ | §33 |
| Firewall/UFW | ✅ | §35–§37 |
| Bastion/private networking | ✅ | §34, §38 |
| Time synchronization | ✅ | §41 |
| UTC | ✅ | §40 |
| Timezone-related data bugs | ✅ | §42 |
| Secret file permissions | ✅ | §43–§45 |
| Owner-only credentials | ✅ | §43–§44 |
| Login auditing | ✅ | §47 |
| Login history | ✅ | §47 |
| sudo auditing | ✅ | §16 |
| `authorized_keys` review | ✅ | §46 |
| Brute-force protection awareness | ✅ | §48 |
| Server bootstrap checklist | ✅ | §50 |
| Bootstrap script | ✅ | §51 |
| Idempotent setup | ✅ | §52–§54 |
| Immutable infrastructure | ✅ | §55–§58 |
| Rebuilding from images/code | ✅ | §57 |
| Pets vs cattle | ✅ | §56 |
| Module 2.18 relationship | ✅ | §57 |
| `server_lab/10/` Exercise 1 | ✅ | §65 |
| `server_lab/10/` Exercise 2 | ✅ | §66 |
| `server_lab/10/` Exercise 3 | ✅ | §67 |
| `server_lab/10/` Exercise 4 | ✅ | §68 |
| `server_lab/10/` Exercise 5 | ✅ | §69 |
| Break/fix scenarios | ✅ | §70 |
| Production server-hygiene checklist | ✅ | §71 |
| Runbook | ✅ | §72 |
| Integrated capstone | ✅ | §73 |
| Production decision framework | ✅ | §74 |
| Practice questions | ✅ | §75 |
| Interview practice | ✅ | §76 |
| Knowledge check | ✅ | §77 |
| G2 checkpoint | ✅ | §79 |
| Final mental model | ✅ | §80 |

**Coverage result: PASS — every explicitly required Topic 10 roadmap concept and all five required `server_lab/10/` exercises are taught in this module.**

---

# 79. G2 Topic 10 Checkpoint

The learner must be able to demonstrate:

```text
[ ] Run services under dedicated accounts with least-privilege sudo.

[ ] Keep packages updated and critical versions controlled.

[ ] Harden SSH and restrict network access.

[ ] Run servers in UTC with synchronized time.

[ ] Bootstrap a server repeatably.

[ ] Explain the immutable-infrastructure mindset.
```

## Practical Proof Requirement

Do not mark this checkpoint complete merely because you read the topic.

Demonstrate each skill on a disposable practice server.

The evidence should include:

```text
service identity
sudo policy
package policy
SSH policy
firewall policy
UTC/time-sync status
secret permissions
audit evidence
bootstrap script
second bootstrap run
rebuild explanation
```

---

# 80. Final Mental Model

```text
SERVER HYGIENE

IDENTITY
Who is running this?
        ↓
PERMISSIONS
What can they access?
        ↓
PRIVILEGE
What can they elevate to?
        ↓
NETWORK
Who can reach the server?
        ↓
PATCHING
Is the software maintained?
        ↓
TIME
Can I trust the timestamps?
        ↓
SECRETS
Who can read credentials?
        ↓
AUDITING
Can I determine who did what?
        ↓
AUTOMATION
Can I reproduce the setup?
        ↓
REBUILDABILITY
Can I replace the server?
        ↓
IMMUTABLE INFRASTRUCTURE
Can I rebuild it from known-good code/images?
```

The final equation is:

```text
Secure
+
Least Privilege
+
Patched
+
Auditable
+
UTC
+
Reproducible
+
Rebuildable
=
Production-Ready Data Server
```

> **A production server should not depend on one engineer remembering how it was manually configured.**

---

# 81. Completion Standard

You are ready to complete G2 Topic 10 when you can independently take a fresh Linux data server and:

```text
create service identities
        ↓
design least-privilege access
        ↓
configure sudo safely
        ↓
manage packages and security updates
        ↓
control critical versions
        ↓
harden SSH
        ↓
restrict network exposure
        ↓
use bastion/private networking
        ↓
configure UTC and time synchronization
        ↓
protect credentials
        ↓
audit access
        ↓
bootstrap repeatably
        ↓
verify idempotency
        ↓
document the server
        ↓
rebuild it from code/configuration
```

That is the production-oriented server-hygiene skill this final G2 topic is designed to build.
