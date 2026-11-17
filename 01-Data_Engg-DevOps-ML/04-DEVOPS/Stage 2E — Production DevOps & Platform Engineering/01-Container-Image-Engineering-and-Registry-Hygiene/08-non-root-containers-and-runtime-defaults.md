## Unit 8 — Non-root containers and runtime defaults

**Target file:** `08-non-root-containers-and-runtime-defaults.md`  
**Estimated time:** 8–12 hours, including labs and review  
**Prerequisites:** Units 1–2 and basic Docker/Linux  
**Core tools:** Docker CLI/Engine, Dockerfile, shell, `id`, `ps`, `/proc/self/status`, `docker inspect`  
**Awareness:** Podman/rootless modes, Conftest/OPA, Kubernetes security controls  
**Last reviewed:** 2026-10-24 — structural self-review only; current official documentation was not independently checked during authoring.

> **Status:** DRAFT-AUDITED, not production-verified. Commands and scripts are provided for local testing but were not executed during authoring. Sample outputs are marked `[ILLUSTRATIVE]`. Verify version-sensitive behavior against the installed Docker Engine, operating system, and runtime documentation.

### 8.0 Why this matters in production

A model-serving API was deployed after a routine image update. The process ran as root inside the container, the root filesystem was writable, and a host directory was mounted for model-cache data. During startup, a new code path wrote a cache file into a directory whose ownership had changed. The first attempted “fix” was to run the container as privileged and mount more of the host filesystem. That might have hidden the immediate permission symptom, but it would also have expanded the impact of an application compromise and made the host boundary harder to defend.

A safer response starts with evidence: identify the effective UID/GID, inspect the target path and mount ownership, determine which directories genuinely need writes, and make the smallest configuration change that restores intended behavior. A production FastAPI inference service may need to read model files, write temporary files, and emit logs to stdout/stderr. It usually does not need arbitrary writes across its image filesystem, host access, or every Linux capability. A pandas/pyarrow ETL worker, Airflow-style task, or PySpark job has different scratch and output requirements, but the same principle applies: make runtime privileges and writable paths explicit.

Running as a non-root user reduces the authority available to a compromised process, but it does not make the container a complete sandbox. Container isolation depends on the kernel, runtime, namespaces, capabilities, mandatory access controls, mounts, and host configuration. A non-root process can still exploit application flaws, access data mounted into it, exhaust resources, or abuse permissions it has been granted.

The practical goal is not “make every container work with one magic flag.” It is to define a tested runtime contract: identity, filesystem write locations, capabilities, resource limits, process/signal behavior, health semantics, and exceptions. Unit 1 covers multi-stage builds and Dockerfiles; Unit 2 covers minimal/distroless images. This unit turns those image-level choices into runtime defaults. Unit 5's digest-based release discipline helps prove which image was tested. M02 covers CI/CD enforcement; M03 covers Kubernetes operations and `securityContext`; M09 covers secrets; M12 covers supply-chain security. Those later units extend the controls here rather than replacing them.

### 8.1 Learning objectives

- **[L1] Inspect** the effective UID/GID and process identity with `id`, `ps`, `/proc/self/status`, and `docker inspect`.
- **[L1] Explain** why container root is not automatically host root, why it remains risky, and how user namespaces change identity mapping.
- **[L2] Build** an image with a dedicated fixed numeric UID/GID and correctly owned application files using `COPY --chown`.
- **[L2] Validate** the exact writable paths required by a service and run it with a read-only root filesystem plus narrowly scoped writable mounts.
- **[L2] Diagnose** permission errors using identity, ownership, mode bits, mounts, and minimal write tests instead of broad privilege escalation.
- **[L3] Configure** runtime restrictions for capabilities, privilege escalation, memory, CPU, PIDs, health checks, and graceful shutdown.
- **[L3] Compare** a non-root process in a rootful engine with rootless Docker/Podman and map the concepts to Kubernetes security controls.
- **[L4] Implement** a hardening conformance test that distinguishes image metadata checks from Dockerfile-source checks and runtime behavior tests.
- **[L4] Review** exceptions and incident evidence, assigning an owner, compensating controls, and an expiry date.

### 8.2 Concept map and vocabulary

| Term | Precise definition | Common misconception |
|---|---|---|
| UID | Numeric user identifier used by Linux permission checks. | A username alone guarantees the same identity across hosts. |
| GID | Numeric group identifier used for group permissions. | A named group necessarily has the same numeric GID everywhere. |
| Root | Conventionally UID 0 in a user namespace. | UID 0 in a container is always identical to unrestricted host root—or is harmless. Both are wrong. |
| User namespace | Kernel namespace that can map container UIDs/GIDs to different host IDs. | Every Docker or Kubernetes deployment uses user-namespace remapping by default. |
| `USER` | Dockerfile instruction setting the default user (and optionally group) for subsequent build/run stages as defined by the image format/builder. | It changes ownership of files already copied into the image. |
| Numeric identity | UID/GID specified by number, not just account name. | Numeric IDs eliminate every permission issue. |
| File ownership | UID/GID and mode bits (plus ACLs/labels where applicable) governing access. | `chmod 777` is the right fix for ownership mismatch. |
| Writable layer | Container's writable layer above read-only image layers. | Changes in the container layer are automatically persisted in the image. |
| Bind mount | A host path mounted into the container namespace. | The image's ownership settings necessarily override host path permissions. |
| Read-only root filesystem | Runtime configuration preventing writes to the container root filesystem layer. | It also makes all mounted volumes and tmpfs mounts read-only. |
| tmpfs | In-memory or memory-backed temporary filesystem, subject to runtime/platform behavior. | It has unlimited capacity or is always persisted to disk. |
| Linux capability | A separable unit of privileged kernel authority. | Dropping capabilities replaces all other isolation controls. |
| seccomp | A mechanism to restrict system calls available to a process. | The default profile is identical across all runtimes and versions. |
| AppArmor | Linux mandatory access-control framework that can confine process behavior. | An AppArmor profile is automatically active and identical on every host. |
| `no-new-privileges` | Runtime setting that prevents a process from gaining additional privileges through mechanisms such as set-user-ID execution. | It prevents all privilege misuse or fixes unsafe mounts. |
| PID 1 | First process in a PID namespace, with special signal and child-reaping responsibilities. | Any process launched in a container handles signals and child processes correctly. |
| Signal forwarding | Delivery of termination/control signals from the runtime or init process to the application process. | Shell-form entrypoints always forward signals correctly. |
| Health check | A command or probe that reports a defined health condition. | A healthy container necessarily means the service meets its SLO or is secure. |
| Resource limit | A runtime-enforced bound on resources such as memory, CPU, or process count. | Limits guarantee good performance or prevent all host pressure. |
| Rootless container engine | An engine/daemon arrangement that runs without a privileged root daemon, subject to its supported features and constraints. | It means only that the application process uses a non-root UID. |
| Kubernetes `securityContext` | Pod/container fields controlling identity and runtime security options in Kubernetes. | Docker CLI flags transfer one-to-one to every Kubernetes field and runtime. |

#### Security-boundary diagram

```text
Host OS / kernel
┌──────────────────────────────────────────────────────────────┐
│ Container engine / runtime                                   │
│  namespaces + cgroups + seccomp/MAC + mounts + capabilities  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Container filesystem view                              │  │
│  │ image layers (read-only) + writable layer (if enabled) │  │
│  │ bind mounts / volumes / tmpfs (each has own permissions)│ │
│  │                                                        │  │
│  │ Process: UID 10001, GID 10001, supplementary groups     │  │
│  │  id / proc status / process tree / effective caps      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

Container root is not automatically host root because namespaces, capability restrictions, and runtime isolation can limit what UID 0 can do. But root in a container may still have significant authority within the container and can become dangerous when combined with privileged mode, broad capabilities, dangerous host mounts, a Docker socket, kernel/runtime vulnerabilities, or weak isolation. Do not treat a container as a security boundary that can compensate for unsafe host configuration.

### 8.3 Level 1 — Beginner

#### UID/GID and the effective user

Linux permission checks primarily use numeric identities and access-control metadata. If an image's application files are owned by UID 10001 but the process runs as UID 10002, the process may be unable to read or write them depending on the mode bits, groups, ACLs, and mount options. The username displayed by `id` is a lookup label; the numeric ID is what the kernel uses.

Root inside a container is usually UID 0 in the container's user namespace. Whether it maps to host UID 0 or another host UID depends on the engine and configuration. User namespaces can map container IDs to different host IDs. **[VERIFY]** User-namespace remapping and rootless behavior depend on the engine, operating system, and deployment configuration.

#### Inspect a running container

Start with a disposable container using an image already available locally. The examples below use Alpine as a diagnostic tool; minimal production images may not contain `id`, `ps`, a shell, or `/proc` utilities.

```bash
# terminal: inspect identity inside a disposable container
docker run --rm alpine:3.20 sh -c '
  id
  printf "\n--- process list ---\n"
  ps
  printf "\n--- status identity/capability fields ---\n"
  grep -E "^(Uid|Gid|Groups|Cap(Inh|Prm|Eff|Bnd|Amb)):" /proc/self/status
'
```

Expected output is **[ILLUSTRATIVE]**; exact UIDs, capability masks, process listing, and output formatting depend on image and runtime:

```text
uid=0(root) gid=0(root) groups=0(root)
--- process list ---
PID   USER     TIME  COMMAND
...
--- status identity/capability fields ---
Uid:    0    0    0    0
Gid:    0    0    0    0
Groups: 0
CapInh: 0000000000000000
CapPrm: 00000000a80425fb
CapEff: 00000000a80425fb
CapBnd: 00000000a80425fb
CapAmb: 0000000000000000
```

Do not memorize the example capability mask. Read the labels and compare the actual process with the intended policy. In `/proc/self/status`, the four UID/GID columns represent real, effective, saved-set, and filesystem IDs in Linux procfs documentation; verify interpretation for the platform and kernel. `CapEff` is the effective capability set, while other capability fields describe different sets. The mask is not self-explanatory without a capability decoder and knowledge of the runtime.

Inspect the configured image user:

```bash
# terminal: inspect image configuration without starting it
docker image inspect alpine:3.20 --format '{{json .Config.User}}'
```

An empty string is commonly returned for an image with no explicit configured user, which generally means the image's default user is root. **[VERSION-SENSITIVE]** Verify the behavior against the selected image and Docker version; do not infer the effective runtime identity from image metadata alone when a runtime override is present.

Now run with an explicit numeric user:

```bash
# terminal: override the image default user for this run
docker run --rm --user 10001:10001 alpine:3.20 sh -c 'id; grep -E "^(Uid|Gid|Groups):" /proc/self/status'
```

Expected identity is **[ILLUSTRATIVE]**: UID 10001 and GID 10001. The account name may be absent because the image may not contain a matching `/etc/passwd` entry. Numeric identity can still work for kernel permission checks, although applications that require username lookup may need an account entry.

#### Dockerfile `USER`: build default versus runtime override

`USER` establishes the default identity for subsequent Dockerfile instructions that execute commands and for the resulting container's default runtime identity. It does not retroactively change ownership of files already created. A runtime option such as `docker run --user 10001:10001 ...` overrides the image's configured default for that container invocation. Orchestrators can also specify identity settings.

```dockerfile
# Dockerfile: examples/unit-08/identity/Dockerfile
FROM alpine:3.20
RUN addgroup -g 10001 app && adduser -D -H -u 10001 -G app app
WORKDIR /app
COPY --chown=10001:10001 hello.txt /app/hello.txt
USER 10001:10001
CMD ["cat", "/app/hello.txt"]
```

The `addgroup`/`adduser` syntax above is Alpine-specific. For Debian/Ubuntu or distroless images, use the appropriate supported account-management mechanism or copy in a verified passwd/group entry. Do not assume one distribution's account-creation flags work in another. `COPY --chown` is supported by Dockerfile builders, but ownership syntax and name resolution should be checked for the chosen builder/base image. See the Dockerfile reference in §8.14.

#### `docker inspect`: image default and container override

```bash
# terminal: inspect configured user and runtime configuration
docker image inspect YOUR_IMAGE --format 'image-user={{json .Config.User}}'
docker inspect YOUR_CONTAINER --format 'configured-user={{json .Config.User}} readonly={{.HostConfig.ReadonlyRootfs}}'
```

Replace placeholders with your own image/container. These inspect fields describe configuration; to prove the process's effective identity, run `id` or inspect `/proc` inside the running container. A runtime setting may differ from the image default.

#### Beginner mistakes → symptom → cause → fix

| Mistake | Symptom | Likely cause | Safer fix |
|---|---|---|---|
| Add `USER 10001` without checking file ownership | App cannot read its code/config | Files are readable only by prior owner | Inspect owner/mode; use correct `COPY --chown` or narrow read permissions |
| Assume username equals numeric ID | Works on one host, fails on another mount | Host and container ID mapping differs | Inspect numeric UID/GID and mount ownership |
| Run as root to silence permission errors | Service works but has unnecessary authority | Root cause is ownership or mount configuration | Diagnose path and grant only required access |
| Assume rootless engine equals non-root process | Misunderstand threat boundary | Engine and application identity are different layers | Document both engine mode and process UID/GID |
| Use `ps` in a distroless image | Command not found | Diagnostic tools are absent | Use a debug image or host/runtime inspection without adding tools to production image |

**What just happened?** `docker run --user` changes the process identity for that invocation; it does not rewrite file ownership, add a named account, or grant access to a path. The correct next step is to compare identity with the path's owner, mode, mount type, and required operation.

### 8.4 Level 2 — Intermediate

#### Dedicated numeric user/group

Choose a stable, documented UID/GID that does not conflict with assumptions in the base image, host-mounted files, or orchestrator policy. A fixed numeric identity makes image ownership more predictable across builds and helps Kubernetes enforce `runAsNonRoot` when configured correctly. It is not a guarantee that all external volumes will have matching ownership.

Example for a Debian-based Python service:

```dockerfile
# Dockerfile: examples/unit-08/fastapi/Dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN groupadd --gid 10001 app \
 && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY --chown=10001:10001 app/ /app/app/

RUN mkdir -p /tmp/app-cache /var/lib/app-cache \
 && chown -R 10001:10001 /tmp/app-cache /var/lib/app-cache

USER 10001:10001
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

This is a teaching example; pin base images and dependencies according to the project's reproducibility policy (Unit 3). For a production build, use a lockfile and controlled dependency source. `EXPOSE` is metadata, not a firewall rule. The application binds port 8080, a useful unprivileged-port convention, but the port number alone is not a security guarantee. Capabilities, host networking, port forwarding, platform behavior, and orchestrator settings still matter.

`COPY --chown=10001:10001` assigns ownership to copied files. It does not fix files created later by a root-running build command, host bind-mount ownership, or volume permissions. Verify:

```bash
# terminal: inspect image metadata and file ownership in a disposable container
docker image inspect local/fastapi-demo:dev --format 'user={{json .Config.User}}'
docker run --rm --entrypoint sh local/fastapi-demo:dev -c 'id; stat -c "%u:%g %a %n" /app /app/app'
```

The image name is an example; build and tag it locally before running the inspection. If the runtime image intentionally lacks a shell or `stat`, use a diagnostic stage/image or another verified inspection method rather than shipping debug utilities in production.

#### Writable paths: explicit, limited, and bounded

Common data-service paths:

- `/tmp`: short-lived temporary files; contents may be lost on restart.
- `/var/lib/app-cache` or a model cache: cache data that may be regenerated; bound its capacity and avoid putting secrets there.
- Airflow worker logs: prefer the platform's logging architecture or a dedicated volume with explicit lifecycle and access policy.
- PySpark scratch/shuffle: may require substantial ephemeral storage; estimate from workload behavior and set capacity/cleanup policy.
- ETL output: usually belongs in an explicit output mount or remote data system, not in the image's root filesystem.

A read-only root filesystem prevents writes to the container's root layer, but explicitly mounted volumes and tmpfs mounts have their own write permissions. Therefore, test each writable path separately.

```bash
# terminal: run a sample image with read-only root and one ephemeral writable path
docker run --rm \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --user 10001:10001 \
  local/fastapi-demo:dev
```

`--tmpfs` option syntax and supported options can vary by Engine/host. **[VERIFY]** Check `docker run --help` and the official Docker run reference for the installed version. The example is not guaranteed to start the service if it writes elsewhere or if UID 10001 cannot use `/tmp`. Add a separate named volume only for data that must persist, and set its ownership/access deliberately.

#### Permission troubleshooting flow

Use this order rather than jumping to root or `chmod 777`.

1. **Identify process:** run `id`; inspect UID/GID/groups and, if needed, `/proc/self/status`.
2. **Identify exact failing path and operation:** read, create, append, rename, delete, or execute?
3. **Inspect ownership and mode:** `stat -c '%u:%g %a %n' PATH` on Linux; inspect ACLs/labels if relevant.
4. **Inspect mount:** determine whether the path is a bind mount, volume, tmpfs, or part of the image; inspect mount configuration and host ownership.
5. **Test minimally:** attempt a write to a dedicated test file in the exact target directory. Do not write into production data just to test permissions.
6. **Check read-only settings:** inspect `ReadonlyRootfs` and mount modes.
7. **Change the narrowest thing:** fix copied-file ownership, directory mode, volume ownership, or mount configuration. Avoid broad permissions and privileged mode.
8. **Rerun the same test** and retain the before/after evidence.

Examples:

```bash
# terminal: inspect a path and test a harmless write in a lab container
id
stat -c '%u:%g %a %n' /var/lib/app-cache
testfile="/var/lib/app-cache/.permission-test"
printf 'test\n' > "$testfile"
rm -- "$testfile"
```

Use this only against a disposable test directory. If the write fails, capture the error and inspect the path and mount before changing anything. On WSL2, Docker Desktop, native Linux, network filesystems, and rootless engines may have different ownership/mapping behavior. **[VERIFY]** Test the exact target environment.

#### Pattern catalogue

| Pattern | Use when | Avoid when |
|---|---|---|
| Fixed numeric UID/GID | Predictable image/runtime ownership is required | The platform mandates a different UID and image cannot be adapted; document the exception |
| `COPY --chown` | Copying application files that should be owned by the runtime user | Files need root ownership for a justified reason; document it and ensure readability |
| `--read-only` plus narrow tmpfs | Application can run with only temporary writes | The app has unmodeled writes; inventory them first |
| Explicit volume for persistent output | Data must outlive the container | Data is cache/temp and persistence would create unnecessary lifecycle risk |
| Port above 1024 | Application does not need a privileged port | A platform-specific proxy/capability design requires something else; verify that design |
| Runtime user override | Testing or platform policy needs a controlled identity | It silently conflicts with image assumptions or makes ownership unpredictable |

#### Anti-pattern catalogue

| Bad example | Why it fails | Corrected version |
|---|---|---|
| `USER root` to fix a cache permission error | Broadens process authority and hides root cause | Create/cache directory with correct owner or mount ownership |
| `chmod -R 777 /app` | Any process with access can modify code/data; can mask mistakes | Set the smallest owner/group/mode needed |
| Mount the whole host filesystem writable | Expands exposure and blast radius | Mount only a dedicated data path with least privilege |
| Use `--read-only` but forget `/tmp` | Startup may fail on legitimate temporary writes | Add a bounded tmpfs or use a documented writable volume |
| Assume image `USER` fixes bind mount ownership | Host path permissions remain relevant | Inspect host/mount ownership and align access intentionally |
| Use `latest` as the only production identifier | Tag movement weakens reproducibility | Use reviewed immutable/digest-based references (Unit 5) |

### 8.5 Level 3 — Advanced

#### Runtime controls: threat, verification, trade-off

| Control | Threat/failure addressed | Verification | Trade-off / limitation |
|---|---|---|---|
| `--read-only` | Unintended writes to image root filesystem | Inspect `ReadonlyRootfs`; test a write fails | Requires every legitimate writable path to be modeled |
| `--tmpfs` | Need for ephemeral writable scratch | Test intended path writes and size pressure | Contents are ephemeral; capacity and option support vary |
| `--cap-drop=ALL` | Excess Linux capability authority | Inspect runtime config and `/proc/self/status` | Some applications need a specific capability; add only with justification |
| `--cap-add=CAP_NAME` | Restore a narrowly required capability | Test the exact operation and inspect effective caps | Capability names/support depend on runtime/kernel; not a substitute for other controls |
| `--security-opt no-new-privileges` | Prevent privilege gains through supported mechanisms | Inspect runtime configuration and behavior | Does not remove existing privileges or fix unsafe mounts; support is platform-dependent |
| `--pids-limit` | Fork/process exhaustion | Inspect configured limit and test controlled process creation | Too low can break legitimate worker pools |
| `--memory` | Bound container memory usage | Inspect config and observe OOM/working set | Too low causes OOM; cgroup behavior varies by host |
| `--cpus` | Bound CPU scheduling share | Inspect configuration and observe throttling | Can increase latency; not a reservation or throughput guarantee |
| seccomp | Restrict system calls | Inspect runtime/profile configuration; controlled tests | Default profiles vary; overly strict profiles can break workloads |
| AppArmor | Constrain filesystem/process behavior on supported Linux hosts | Inspect active profile and audit denials | Not available/enforced identically on all platforms |
| `HEALTHCHECK` | Detect a defined process/service condition | Inspect health status and probe logs | Does not guarantee end-to-end SLO or security |
| Exec-form `CMD` | Improve signal delivery to the application process | Send SIGTERM and measure shutdown | App must still handle signals correctly |
| `--init` / `tini` | Reap child processes and forward signals in common cases | Spawn/reap test children; shutdown test | Adds a process and does not fix an application that ignores termination |
| Locale/timezone/`umask` | Predictable text/time/file-creation behavior | Inspect environment and created file modes | Minimal images may lack locale/tzdata utilities or data |

**[VERSION-SENSITIVE]** Confirm each runtime flag in the installed Docker CLI reference and test behavior on the actual engine/host. Defaults for seccomp and AppArmor are not universal. Avoid claiming a profile is active just because the host supports the feature; inspect the effective configuration.

#### Compose a restricted local run

```bash
# terminal: example runtime command; assumes image local/fastapi-demo:dev exists
docker run --rm --name u8-fastapi-hardened \
  --user 10001:10001 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop=ALL \
  --security-opt no-new-privileges \
  --pids-limit 128 \
  --memory 512m \
  --cpus 1.5 \
  --init \
  -p 127.0.0.1:8088:8080 \
  local/fastapi-demo:dev
```

This is a candidate baseline, not a universal set of correct values. Memory, CPU, PIDs, tmpfs size, port mapping, and `--init` behavior must be measured and verified. The service may fail if it needs another writable directory, capability, or resource. Keep port publishing on loopback for a local lab. If `--security-opt no-new-privileges` or a particular flag is unsupported, stop and verify the engine/OS rather than silently dropping the control.

To justify an added capability, state the exact operation that needs it, why an unprivileged alternative is insufficient, the target platform, the verification test, and the expiry/review date. Do not add capabilities “just in case.”

#### `HEALTHCHECK` and service health

A Dockerfile `HEALTHCHECK` can execute a command to report a container health state. For a FastAPI service, an endpoint such as `/health/live` may indicate that the process is responsive; a readiness endpoint may need to check required dependencies. Do not make a health check depend on a large model download or an external service in a way that causes false failures during a transient dependency outage. A health check is a signal, not a complete SLO.

```dockerfile
# Dockerfile: examples/unit-08/fastapi/Dockerfile.healthcheck-fragment
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health/live', timeout=2).read()" || exit 1
```

This is a fragment, not a complete Dockerfile. It assumes Python and the endpoint exist in the image. Timing values are **[ILLUSTRATIVE]** and should be derived from startup behavior and service needs. Minimal/distroless images may not include a shell or Python, so choose a probe mechanism compatible with the image. The exact health status and orchestration response differ by platform.

#### PID 1, signals, and graceful shutdown

When a container's main process is PID 1 in its PID namespace, signal handling and orphaned child reaping deserve attention. Exec-form `CMD ["uvicorn", ...]` avoids inserting a shell as the command process. A shell-form entrypoint may require explicit `exec` to replace the shell with the application. `--init` or a small init such as `tini` can help reap child processes and forward signals, but does not make the application gracefully terminate on its own.

A good shutdown test sends SIGTERM, measures time to exit, and checks whether requests/tasks finish or are cancelled safely. For ETL/Airflow/PySpark workloads, graceful shutdown may mean stopping intake, checkpointing or safely terminating work, and releasing resources. The required behavior depends on job semantics. **[VERIFY]** Runtime stop timeouts and orchestrator termination grace periods vary by platform.

#### Locale, timezone, and umask

Set locale/timezone deliberately when the application depends on them. Minimal images may not contain locale definitions, timezone data, or the usual configuration tools. Setting `TZ=UTC` does not guarantee every image has timezone data installed. Python and libraries may use their own behavior. A restrictive `umask`, for example `027`, can reduce default permissions on newly created files, but the exact resulting mode also depends on the application's requested mode. Verify the setting in the actual process and inspect created files rather than assuming it was applied.

#### Rootless engine versus non-root process

A rootful Docker Engine can run an application process as UID 10001. Rootless Docker runs the engine/daemon and containers without a root-owned daemon in the usual rootful model, subject to user-namespace and platform constraints. Podman has its own rootless and rootful modes and compatibility differences. These are related but distinct layers of defense.

Rootless modes can reduce the impact of a daemon/runtime compromise, but may have constraints around networking, storage drivers, device access, ports, cgroups, and volume ownership. **[VERSION-SENSITIVE]** Verify current Docker rootless and Podman documentation for your operating system. WSL2 behavior depends on whether Docker Desktop, a Linux daemon inside WSL, or another engine is used.

#### Kubernetes forward mapping

| Docker/local concept | Kubernetes concept | Important difference |
|---|---|---|
| `--user 10001:10001` | `runAsUser`, `runAsGroup` | Pod and container security contexts have precedence/merging rules. |
| Image has non-root default | `runAsNonRoot: true` | Kubelet/runtime validation depends on image metadata and configured UID; test the selected image. |
| `--read-only` | `readOnlyRootFilesystem: true` | Writable volumes remain writable according to their own configuration. |
| `--cap-drop=ALL` / narrow add | `capabilities.drop` / `capabilities.add` | Exact schema and runtime behavior must be checked. |
| `no-new-privileges` | `allowPrivilegeEscalation: false` | Conceptually related; runtime/platform semantics need verification. |
| Docker seccomp/AppArmor options | `seccompProfile`, AppArmor controls where supported | Availability and policy enforcement depend on cluster/runtime version. |
| Resource/PID limits | Pod/container resources and platform controls | Kubernetes has resource request/limit semantics; PIDs may be governed by node/runtime settings. |

Kubernetes `securityContext` and Pod Security Standards are forward references to M03/M12, not a full Kubernetes lesson. Review the exact cluster version and admission policy before assuming a manifest is enforced.

#### Runtime design trade-offs

| Option | Benefit | Cost | Risk | Choose when |
|---|---|---|---|---|
| Non-root fixed UID/GID | Reduces process authority; stable file ownership | Requires ownership and volume design | Mounts or application behavior may still expose data | Default for ordinary application services |
| Read-only root filesystem | Prevents accidental writes to image layer | Requires path inventory and writable mounts | Can cause startup/runtime failure if incomplete | Service can enumerate its write needs |
| Drop all capabilities | Strong reduction in kernel privilege set | Some legitimate operations may fail | Re-adding broadly defeats intent | Most APIs/workers not requiring privileged operations |
| tmpfs scratch | Ephemeral and scoped writes | Uses memory/resource budget; not persistent | Exhaustion or data loss | Small temporary data |
| Dedicated volume | Explicit persistence and capacity lifecycle | Requires ownership, backup, cleanup design | Persistent sensitive data may outlive job | Output/log/cache that must persist |
| Rootless engine | Reduces daemon/root exposure | Feature and operations constraints | Does not remove application vulnerabilities | Local dev or platforms where requirements are supported |
| Strict seccomp/MAC | Restricts syscall or access behavior | Compatibility testing and maintenance | Incorrect profile can break service | Threat model justifies and tests the restriction |

**Lab challenge:** for the FastAPI API, defend the smallest safe permission set. Start with UID/GID 10001, read-only root, only `/tmp` writable if needed, no capabilities, no-new-privileges where supported, bounded resources, and exec-form command. Add another permission only when a reproducible test shows the requirement and the security review approves it.

### 8.6 Level 4 — Expert

#### Separate static checks from runtime proofs

No single image-only checker can prove every property. Use three evidence layers:

1. **Dockerfile/source checks:** whether the source contains a `USER` instruction, uses exec-form `CMD`, references `latest`, declares a health check, or includes suspicious secret patterns. Source scans can have false positives and false negatives.
2. **Image metadata checks:** configured user, command, labels, health-check metadata, and image reference. Metadata cannot prove the runtime override, effective capabilities, mount permissions, or absence of secrets in all image layers.
3. **Runtime checks:** effective UID/GID, read-only root behavior, writable-path behavior, capability/runtime settings, health status, and signal behavior under the actual engine.

Secret detection is especially limited: a regex scan can detect obvious tokens but cannot prove no secret exists. Use secret scanning in CI and treat any finding as a review item; never print secret values in reports.

#### Hardening conformance test script

The following script inspects a local image and performs safe runtime tests. It expects a service image with a writable `/tmp` and a configured non-root user. It does not inspect Dockerfile source, cannot prove secret absence, and does not automatically assert every runtime flag across all Docker versions. It emits a JSON pass/fail report. The write test uses a disposable container and deliberately expects a write to the root filesystem to fail while a `/tmp` write succeeds.

Save as `conformance_check.py`:

```python
#!/usr/bin/env python3
# file: examples/unit-08/conformance_check.py
"""Local image conformance checks. No registry push/pull or deletion."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def run(args, *, check=False):
    return subprocess.run(args, text=True, capture_output=True, check=check)


def record(results, name, passed, evidence, limitation=""):
    results.append({
        "check": name,
        "result": "PASS" if passed else "FAIL",
        "evidence": evidence.strip(),
        "limitation": limitation,
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="local image reference; do not use an unspecified remote")
    parser.add_argument("--report", default="conformance-report.json")
    parser.add_argument("--require-healthcheck", action="store_true")
    args = parser.parse_args()
    results = []

    inspect = run(["docker", "image", "inspect", args.image])
    if inspect.returncode != 0:
        print(inspect.stderr, file=sys.stderr)
        return 2
    try:
        image = json.loads(inspect.stdout)[0]
    except (json.JSONDecodeError, IndexError, TypeError) as exc:
        print(f"ERROR: unexpected docker inspect output: {exc}", file=sys.stderr)
        return 2

    config = image.get("Config") or {}
    user = str(config.get("User") or "").strip()
    record(results, "image_user_configured",
           bool(user) and user not in ("0", "0:0", "root", "root:root"),
           f"Config.User={user!r}",
           "Metadata only; numeric/effective runtime identity is tested below.")

    labels = config.get("Labels") or {}
    required_labels = ("org.opencontainers.image.source",
                       "org.opencontainers.image.version")
    missing = [key for key in required_labels if not labels.get(key)]
    record(results, "required_oci_labels_present", not missing,
           f"present={sorted(k for k in required_labels if labels.get(k))}; missing={missing}",
           "Presence does not prove label truthfulness or provenance.")

    health = config.get("Healthcheck")
    record(results, "healthcheck_present",
           bool(health) if args.require_healthcheck else True,
           f"Healthcheck={'present' if health else 'absent'}",
           "If not required by policy, absence is recorded but not failed. Health checks are not security controls.")

    # Run identity probe with a read-only root filesystem. This image must contain sh/id.
    # For distroless images, provide a separate runtime test appropriate to that image.
    probe = run([
        "docker", "run", "--rm", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--entrypoint", "sh", args.image, "-c",
        'id; printf "UID="; id -u; printf " GID="; id -g'
    ])
    identity_evidence = probe.stdout + probe.stderr
    nonroot = False
    if probe.returncode == 0:
        uid_result = run([
            "docker", "run", "--rm", "--read-only",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
            "--entrypoint", "sh", args.image, "-c", "id -u"
        ])
        nonroot = uid_result.returncode == 0 and uid_result.stdout.strip().isdigit() and int(uid_result.stdout.strip()) != 0
        identity_evidence += "\nuid_probe=" + uid_result.stdout.strip()
    record(results, "effective_nonroot_identity", nonroot, identity_evidence,
           "Requires sh/id in image and assumes no external runtime user override. Distroless images need a compatible probe.")

    # A write in the root filesystem should fail with --read-only; /tmp should remain writable.
    # Both tests use disposable containers and do not touch host paths.
    root_write = run([
        "docker", "run", "--rm", "--read-only", "--entrypoint", "sh", args.image,
        "-c", "printf x > /u8-root-write-test"
    ])
    record(results, "read_only_root_write_denied", root_write.returncode != 0,
           f"exit={root_write.returncode}; stderr={root_write.stderr}",
           "The test is meaningful only if sh exists and the target path would otherwise be writable.")
    tmp_write = run([
        "docker", "run", "--rm", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--entrypoint", "sh", args.image,
        "-c", "printf x > /tmp/u8-write-test && test -s /tmp/u8-write-test"
    ])
    record(results, "approved_tmp_write_succeeds", tmp_write.returncode == 0,
           f"exit={tmp_write.returncode}; stdout={tmp_write.stdout}; stderr={tmp_write.stderr}",
           "This tests only /tmp, not all application writable paths.")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "image": args.image,
        "image_id": image.get("Id"),
        "mode": "local-runtime-conformance",
        "checks": results,
        "summary": {
            "pass": sum(r["result"] == "PASS" for r in results),
            "fail": sum(r["result"] == "FAIL" for r in results),
        },
        "not_proven": [
            "No embedded secrets across all layers",
            "Dockerfile source policy",
            "Runtime behavior under every production mount/override",
            "Provenance/signature validity",
            "All capabilities and seccomp/AppArmor effective state",
            "Graceful shutdown under production traffic",
        ],
    }
    with open(args.report, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report["summary"], indent=2))
    print(f"report={args.report}")
    return 1 if report["summary"]["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Important:** this checker is designed for a sample image that contains `sh` and `id`. A distroless image will fail the probe because the diagnostic tools are absent; that is not proof the image runs as root. Adapt the test using a supported runtime inspection method rather than adding a shell to production solely for the checker. The script reports metadata and behavior separately and explicitly lists properties it cannot prove.

Example invocation:

```bash
# terminal: run against a locally built sample image
python3 conformance_check.py local/fastapi-demo:dev --report conformance-report.json
status=$?
printf 'checker_exit=%s\n' "$status"
```

Exit status `0` means all checks performed by this script passed; `1` means one or more checks failed; `2` indicates a fatal input/inspection error. This behavior is defined by the script and has not been executed during authoring. A PASS is not a production certification.

#### Defensive detection of dangerous runtime settings

Inspect a known container:

```bash
# terminal: inspect runtime configuration for a named test container
docker inspect u8-fastapi-hardened --format \
'privileged={{.HostConfig.Privileged}} readonly={{.HostConfig.ReadonlyRootfs}} cap_add={{json .HostConfig.CapAdd}} cap_drop={{json .HostConfig.CapDrop}} pid_limit={{.HostConfig.PidsLimit}} memory={{.HostConfig.Memory}} nano_cpus={{.HostConfig.NanoCpus}}'
```

Review mounts:

```bash
# terminal: list mounts for a named test container
docker inspect u8-fastapi-hardened --format '{{json .Mounts}}'
```

Look for privileged mode, broad host paths, writable host mounts, and Docker socket mounts. Mounting the Docker socket can grant the container control over the host daemon and is often equivalent to a high-trust administrative interface. Do not demonstrate exploitation; detect and remove the mount or replace it with a narrowly scoped service/API. A host mount is not inherently unsafe in every case, but its path, mode, ownership, contents, and tenant boundary must be justified.

#### Exceptions and governance

An exception is not a permanent undocumented bypass. Every exception should include:

- named owner and service;
- exact control that cannot be met and reproducible reason;
- narrow scope (image, repository, runtime, environment);
- compensating controls;
- approval from the appropriate platform/security owner;
- expiry date and review cadence;
- test evidence and removal plan.

For example, a legacy data conversion tool may need a narrowly scoped writable mount. That does not justify `--privileged` or a Docker socket. Prefer a dedicated volume, bounded size, specific UID/GID, and a job lifecycle that removes temporary data. Expired exceptions should fail policy or alert, not silently continue.

#### Incident scenario: hardened service fails after deployment

**Symptom:** the API starts locally but fails in production with `PermissionError`, or the container exits during rollout.

1. Capture image digest, runtime configuration, effective UID/GID, mounts, logs, health state, and exit reason.
2. Compare the known-good and failing configuration; do not change several controls simultaneously.
3. For permission errors, identify the exact path and operation, then inspect UID/GID, ownership, mode, mount options, and read-only root configuration.
4. For shutdown failures, inspect command/entrypoint form, PID 1, signal delivery, termination timeout, and application shutdown logs.
5. Mitigate narrowly: create/own the specific directory or add a bounded writable mount; adjust shutdown handling or timeout only when evidence supports it.
6. Rerun the same conformance and service tests, then verify health, rollback, and cleanup.
7. Add the failing case to CI/runtime tests and document any time-bound exception.

Avoid disabling read-only root, running as root, or adding broad capabilities as the first response. Those changes may be acceptable as a temporary, explicitly approved emergency mitigation only after risk assessment, with an owner and expiry.

### 8.7 SRE lens

#### SLIs and SLOs

A service-level indicator (SLI) is a measured property; a service-level objective (SLO) is the target agreed for that property. Define targets from service needs and observed behavior, not from a generic lesson.

| Signal | SLI definition | Why it matters |
|---|---|---|
| Startup success | Successful starts / attempted starts | Detects ownership and missing-writable-path failures |
| Restart rate | Restarts per workload/time window | Can expose crash loops or resource limits |
| Health-check behavior | Probe success, latency, and failure reason | Detects liveness/readiness misconfiguration |
| Graceful shutdown | Percentage of terminations completed within the service's required window | Protects in-flight requests/jobs |
| Permission failure rate | Count/rate of permission-denied errors | Detects ownership/mount regressions |
| OOM events | Count of memory-limit terminations | Helps tune memory budgets |
| PID exhaustion | PID-limit events or fork failures | Protects host but can break workers if too low |
| Writable-path exhaustion | tmpfs/volume capacity and write failures | Prevents cache/log/scratch failures |

An example target such as “99.9% of starts succeed over a rolling window” is **[ILLUSTRATIVE]**, not a recommendation. Set targets using business impact, historical baselines, release cadence, and acceptable recovery time.

#### Runbook: hardened container fails after deployment

**Alert/symptom:** failed startup, repeated restarts, failed health check, permission error, OOM, PID-limit error, or shutdown timeout.

1. **Triage:** identify affected service, image digest, node/host, rollout time, and whether users/jobs are impacted.
2. **Collect evidence:** container logs, exit code, health state, `docker inspect`, effective UID/GID, mounts, resource events, and recent image/runtime configuration changes.
3. **Form one hypothesis:** path ownership, read-only root, missing tmpfs/volume, resource limit, capability denial, health-check mismatch, or signal handling.
4. **Test safely:** reproduce with the exact image digest in a disposable environment; perform minimal write and signal tests; inspect effective config.
5. **Mitigate:** roll back to a known-good digest or make the narrowest approved config fix. Do not grant broad privilege to suppress symptoms.
6. **Validate:** startup, health, normal request/job path, graceful shutdown, resource headroom, and rollback all work.
7. **Follow up:** add a regression test, update the hardening policy, and record an exception only if unavoidable.

#### Capacity notes

- **Memory:** include application heap, native libraries, model weights, cache, tmpfs, and overhead. A memory limit that ignores model loading can cause repeated OOMs.
- **CPU:** CPU limits can throttle latency-sensitive inference or parallel ETL; measure under representative load.
- **PIDs:** worker pools and child processes can exhaust PID limits; size based on measured concurrency.
- **Ephemeral storage:** `/tmp`, Spark shuffle/scratch, logs, and caches need size/lifecycle bounds. tmpfs often consumes memory budget.
- **Writable mounts:** monitor free space, inode pressure where relevant, permissions, and cleanup. A persistent volume can fill even when the root filesystem is read-only.
- **Shutdown:** termination windows must account for draining requests, task completion/checkpointing, and application cleanup.

### 8.8 Security lens

| Threat | Control | Verification | Limitation | Owner |
|---|---|---|---|---|
| Process compromise with excessive privilege | Fixed non-root UID/GID; drop capabilities | `id`, `/proc/self/status`, runtime inspection | Does not eliminate application or kernel vulnerabilities | Service owner + platform |
| Unexpected filesystem modification | Read-only root; explicit writable mounts | Root-write-fails and allowed-path-write-succeeds tests | Mounted writable paths remain writable | Service owner |
| Privilege escalation | `no-new-privileges` where supported; avoid setuid surprises | Inspect runtime config; test intended behavior | Does not remove current privileges or fix dangerous mounts | Platform |
| Host exposure | Avoid privileged mode, broad host mounts, Docker socket | `docker inspect` mount/privileged checks | Some legitimate host integrations need separate threat review | Platform/security |
| System-call abuse | Seccomp and MAC profiles | Verify active profile and controlled denial logs | Defaults/platforms differ; profile errors can break service | Platform |
| Secret disclosure | Do not bake secrets into image; runtime secret delivery | CI secret scan, layer review, runtime config review | Scanners can miss secrets; mounted secrets still need access controls | Service/security |
| Resource exhaustion | CPU/memory/PID/ephemeral limits and monitoring | Inspect settings; controlled load/failure tests | Incorrect limits cause availability failures | SRE/service owner |
| Supply-chain compromise | Trusted bases, digest pinning, provenance/signature verification | M12 process and release evidence | Non-root does not establish artifact trust | Supply-chain/security |
| Unsafe exception | Owner, approval, compensating control, expiry | Exception inventory and expiry alerts | Governance can fail if reviews are not enforced | Policy owner |

Non-root is defense in depth, not a complete boundary. `readOnlyRootFilesystem` does not make mounts read-only. Dropping capabilities does not replace seccomp, MAC, namespaces, or host isolation. A health check is an operational signal, not a security control. TLS and immutable image references are important but do not prove the running process has least privilege.

Use NIST SP 800-190 and the CIS Docker Benchmark as review frameworks, not as a substitute for version-specific testing. A benchmark item may be inapplicable or implemented differently on a managed platform; record the rationale and compensating controls.

### 8.9 Production checklist

- [ ] Image has an explicit, fixed numeric non-root UID/GID where appropriate.
- [ ] Effective runtime identity has been verified, not inferred from the Dockerfile alone.
- [ ] Application code/config files have correct owner and read permissions.
- [ ] Required writable paths are inventoried and narrowly scoped.
- [ ] Root filesystem is read-only where compatible with the service.
- [ ] Writable tmpfs/volumes have ownership, size/capacity, and lifecycle policy.
- [ ] Linux capabilities are dropped by default where compatible; each addition is justified.
- [ ] `no-new-privileges` is enabled where supported and verified.
- [ ] Memory, CPU, PID, and ephemeral storage limits are based on measured workload needs.
- [ ] Health check has meaningful semantics and does not masquerade as a complete SLO.
- [ ] Exec-form command and graceful SIGTERM behavior are tested.
- [ ] No secrets are baked into image layers or committed source.
- [ ] Privileged mode, Docker socket, and broad host mounts are avoided or formally approved.
- [ ] Seccomp/AppArmor/runtime defaults are understood for the target platform.
- [ ] Automated image/runtime conformance tests run in the delivery process.
- [ ] Exceptions have owner, rationale, compensating control, scope, approval, and expiry.
- [ ] Evidence is retained without credentials or sensitive raw logs.
- [ ] Rollback image digest and recovery path are verified.

### 8.10 Hands-on lab set

#### Lab safety and environment

These labs are designed for a local machine with approximately 4 CPUs, 8 GB RAM, and 30 GB disk. Use a disposable workspace and local images; no cloud or paid service is required. On WSL2, confirm both the Linux filesystem and host/virtual disk have sufficient capacity. Docker Desktop, a daemon inside WSL2, and native Linux can expose different mount and UID mapping behavior. **[VERIFY]** Confirm which daemon your CLI controls.

Use unique lab names and inspect before cleanup. Never use production images, real secrets, or an unspecified remote registry.

#### L8-LAB-01 — Inspect identity and capabilities

**Goal:** inspect UID/GID and capability fields inside a running container.

**Prerequisites:** Docker working; Alpine image available or obtainable through the normal trusted image process.

```bash
# terminal: run disposable identity probe
docker run --rm --name u8-lab01 alpine:3.20 sh -c \
'id; ps; grep -E "^(Uid|Gid|Groups|Cap(Inh|Prm|Eff|Bnd|Amb)):" /proc/self/status'
```

**Expected evidence:** terminal output and notes identifying effective UID/GID, group list, and capability fields. Output is **[ILLUSTRATIVE]**; do not copy a capability mask as a baseline.

**Success criterion:** explain what the identity proves and what it does not prove about host privileges.

**Troubleshooting:** if the image is unavailable, use an approved local diagnostic image. If `/proc` fields differ, record kernel/runtime details. Do not run the probe against a production workload.

**Cleanup:** `--rm` should remove the container on exit. Verify with `docker ps -a --filter name=u8-lab01`; expected no matching container. No volume is created.

**Stretch goal:** compare the same probe with `--user 10001:10001` and explain account-name lookup versus numeric identity.

#### Lab L8-LAB-02 — Convert a sample service to non-root

**Goal:** build a sample image with fixed numeric UID/GID and correct file ownership.

**Prerequisites:** Docker, Python/pip or a small local service project, and a disposable working directory.

Create a small FastAPI app and dependency file; this is a minimal local example.

```python
# file: examples/unit-08/fastapi/app/main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/health/live")
def health_live():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"service": "unit-8-demo"}
```

```text
# file: examples/unit-08/fastapi/requirements.txt
fastapi
uvicorn
```

Use the Dockerfile from §8.4, building in the directory containing `requirements.txt` and `app/`.

```bash
# terminal: build and inspect the local image
docker build -t local/fastapi-demo:dev examples/unit-08/fastapi
docker image inspect local/fastapi-demo:dev --format 'user={{json .Config.User}}'
docker run --rm --entrypoint sh local/fastapi-demo:dev -c 'id; stat -c "%u:%g %a %n" /app/app'
```

**Expected evidence:** build output, configured user, effective UID/GID, ownership check. The exact output is **[ILLUSTRATIVE]**.

**Safe failure:** temporarily remove or alter `COPY --chown` in a copy of the lab Dockerfile, rebuild under a distinct tag, and observe whether a permission-sensitive operation fails. Do not modify the only working Dockerfile; keep the known-good version for comparison.

**Success criterion:** process is non-root and the application can read its code while writing only to the explicitly approved paths.

**Cleanup:** inspect the exact local image names before removal. **⚠ DESTRUCTIVE** `docker image rm local/fastapi-demo:dev` removes that named local image only; run only if it is the lab image and you no longer need it. Verify no lab containers remain with `docker ps -a --filter name=u8-lab02`.

**Stretch goal:** run with `--read-only` and document every required writable path.

#### Lab L8-LAB-03 — Read-only root and permission failure

**Goal:** intentionally fail a write safely, diagnose it, and prove the corrected configuration.

```bash
# terminal: inspect image and attempt a root-layer write in a disposable container
docker image inspect local/fastapi-demo:dev --format 'user={{json .Config.User}}'
docker run --rm --read-only --entrypoint sh local/fastapi-demo:dev \
  -c 'printf x > /app/root-write-test'
```

The second command is expected to fail if `/app` is on the read-only root filesystem. The exit status and error are environment-specific; this is a deliberate test, not an assumed output. Then test the approved ephemeral path:

```bash
# terminal: write only to explicitly mounted tmpfs
docker run --rm --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --entrypoint sh local/fastapi-demo:dev \
  -c 'printf x > /tmp/u8-test && test -s /tmp/u8-test'
```

**Expected evidence:** captured failure, identity/path ownership diagnosis, successful tmpfs write, and explanation of why the mount is writable while root is read-only.

**Troubleshooting:** if the first write succeeds, confirm the path is not a separate writable mount and that the intended flag reached the container. If `/tmp` fails, check the tmpfs syntax, effective user, and runtime support.

**Cleanup:** containers use `--rm`; verify `docker ps -a --filter name=u8-lab03` shows none. No persistent volume is created.

**Stretch goal:** use a named volume for a path that must persist and document ownership and cleanup lifecycle.

#### Lab L8-LAB-04 — Apply runtime restrictions

**Goal:** apply capability, privilege-escalation, resource, and PID restrictions, then inspect the resulting configuration.

```bash
# terminal: start the local service with a restricted runtime configuration
docker run -d --name u8-lab04 \
  --user 10001:10001 --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --cap-drop=ALL --security-opt no-new-privileges \
  --pids-limit 128 --memory 512m --cpus 1.0 --init \
  -p 127.0.0.1:8089:8080 local/fastapi-demo:dev
docker inspect u8-lab04 --format \
'privileged={{.HostConfig.Privileged}} readonly={{.HostConfig.ReadonlyRootfs}} cap_drop={{json .HostConfig.CapDrop}} pids={{.HostConfig.PidsLimit}} memory={{.HostConfig.Memory}} cpus={{.HostConfig.NanoCpus}}'
```

**Expected evidence:** runtime config output and a request/health check result. Some values may be normalized in inspect output; exact fields depend on Docker version. Confirm support for each option in your installed Engine.

**Success criterion:** the service works with the smallest justified permission set; any failure has a specific diagnosis rather than a broad privilege workaround.

**Troubleshooting:** if startup fails, inspect logs and health, then test the read-only/writable paths, user, resource settings, and required capabilities one at a time. Do not add `--privileged`.

**Cleanup:** inspect first, then **⚠ DESTRUCTIVE** remove only the named lab container:
`docker ps -a --filter name=u8-lab04`
`docker rm -f u8-lab04`
Verify no matching container remains. No named volume is created.

**Stretch goal:** test graceful SIGTERM and record elapsed shutdown time under an idle request load.

#### Lab L8-LAB-05 — Hardening conformance report

**Goal:** produce a JSON pass/fail report for a local image.

**Prerequisites:** script from §8.6, local sample image, Python 3, Docker.

```bash
# terminal: run the checker against the lab image
python3 conformance_check.py local/fastapi-demo:dev --report conformance-report.json
status=$?
printf 'checker_exit=%s\n' "$status"
python3 -m json.tool conformance-report.json
```

**Expected evidence:** report file with individual checks, summary, and explicit `not_proven` list. Exit `0` means performed checks passed, `1` means one or more checks failed, `2` means fatal inspection/input error. These exit semantics are defined by the script but were not executed during authoring.

**Troubleshooting:** distroless images lack `sh`/`id`, so the current checker is not suitable unchanged. Record the limitation and create a compatible runtime test. A checker failure is evidence to investigate, not permission to bypass the policy.

**Cleanup:** preserve the report as evidence. Verify no container remains with `docker ps -a --filter name=u8`; the script's runtime containers use `--rm`. Remove only the report and temporary lab directory after checking the exact path. No volume is created.

**Stretch goal:** add Dockerfile-source checks and a test proving the policy rejects `latest` where forbidden; label the source checker as heuristic, not proof of secret absence.

### 8.11 Self-check questions

1. **Why is running as root inside a container risky if container root is not automatically host root?**  
   **Answer:** root may have substantial authority within the container and can interact dangerously with capabilities, mounts, sockets, runtime/kernel weaknesses, or misconfiguration. Isolation reduces risk but is not absolute.

2. **Why use numeric UID/GID rather than only a username?**  
   **Answer:** Linux permission checks use numeric IDs; a username can map to different IDs across images/hosts. Numeric identity improves predictability but does not automatically fix mount ownership.

3. **Does `--read-only` make every filesystem visible in the container read-only?**  
   **Answer:** No. Explicit volumes and tmpfs mounts have separate mount permissions and may remain writable. Test each mount.

4. **What should you do before adding a capability?**  
   **Answer:** identify the exact operation that fails, reproduce it, verify an unprivileged alternative is insufficient, add only the specific capability, test it, and document owner/review date. Dropping capabilities does not replace seccomp/MAC/isolation.

5. **Why can a non-root image fail when mounted to a host directory?**  
   **Answer:** the host path's numeric ownership, mode bits, ACLs, labels, or user-namespace mapping may not grant access to the container UID/GID.

6. **Why does PID 1 and exec-form `CMD` matter?**  
   **Answer:** signal delivery and child reaping affect graceful shutdown. Exec form avoids an unnecessary shell layer, but the application still needs correct signal handling; `--init` can help with reaping/forwarding.

7. **Is rootless Docker the same as running a non-root process under rootful Docker?**  
   **Answer:** No. One describes how the engine/daemon runs; the other describes the application process identity. They reduce different risks and have different operational constraints.

8. **Can an image-only checker prove no secrets are embedded?**  
   **Answer:** No. Metadata inspection and regex scanning are incomplete. Use source/layer secret scanning and review, and never print secret values in evidence.

9. **A service fails under read-only root. What is the correct first response?**  
   **Answer:** identify the exact failing path and operation, inspect UID/GID/ownership/mounts, and add only the required writable path with bounded capacity. Do not immediately disable read-only mode or run as root.

10. **What makes a hardening exception acceptable?**  
    **Answer:** a named owner, evidence-backed rationale, narrow scope, compensating control, approval, expiry date, and periodic review. An undocumented permanent bypass is not an exception process.

### 8.12 Evidence artifacts

Suggested evidence directory under the module (these are specifications; this lesson does not create these repository files):

```text
evidence/unit-08-non-root-runtime/
├── environment-and-engine-version.md
├── dockerfile-before-after.diff
├── image-inspect.json
├── effective-identity.txt
├── proc-status-capabilities.txt
├── runtime-config-inspect.json
├── permission-failure-and-diagnosis.md
├── readonly-root-write-test.txt
├── writable-path-test.txt
├── conformance-report.json
├── graceful-shutdown-test.md
├── cleanup-verification.txt
└── exception-adr-example.md
```

Acceptance criteria:

- **Environment record:** Docker/OS/WSL2 mode and image digest or image ID recorded.
- **Dockerfile diff:** fixed numeric user, ownership changes, command form, and any health check are visible.
- **Image inspection:** configured user, labels, command, and health-check metadata recorded without secrets.
- **Effective identity:** actual UID/GID and relevant `/proc/self/status` fields captured from a runtime test.
- **Runtime config:** read-only root, mounts, capabilities, resource limits, PID limit, and privilege setting captured.
- **Permission diagnosis:** failed operation, exact path, owner/mode/mount, hypothesis, fix, and repeat-test result.
- **Conformance report:** pass/fail for each implemented check and explicit unproven properties.
- **Shutdown evidence:** SIGTERM behavior, exit status, and elapsed time from an actual run.
- **Cleanup verification:** named lab containers/volumes inspected and confirmed removed or intentionally retained.
- **Exception ADR:** only if needed; includes owner, scope, compensating control, expiry, and approval.

Never commit credentials, tokens, private registry addresses, unredacted security logs, or secret-bearing environment output. Redact sensitive details while retaining enough context to reproduce the decision.

### 8.13 Common interview and design-review questions

#### 1. How would you design a non-root container for a FastAPI model-serving API?

**Model answer:** choose a stable numeric UID/GID, set it explicitly in the image, assign ownership to application files, and identify writable paths such as `/tmp` or a bounded model cache. Run with a read-only root filesystem where compatible, drop unnecessary capabilities, enable no-new-privileges where supported, set resource/PID limits based on measurement, use exec-form `CMD`, and test SIGTERM/health behavior. Keep model artifacts read-only when possible and never bake credentials into the image. Verify effective runtime identity rather than relying only on the Dockerfile.

#### 2. When would you enable a read-only root filesystem, and how would you roll it out?

**Model answer:** enable it when the application's write set is known. First inventory writes through logs/tests, then add explicit tmpfs or volumes for required paths, verify ownership and capacity, and run conformance tests. Roll out gradually with rollback by digest/config. The trade-off is increased configuration discipline; the benefit is preventing unexpected writes to the image layer. Mounted paths remain independently writable, so mount policy still matters.

#### 3. Why drop all capabilities, and when is adding one justified?

**Model answer:** capabilities split kernel privilege into smaller units. Dropping all provides a restrictive starting point; add back a specific capability only when an observed, required operation cannot be achieved safely otherwise. Document the operation, evidence, platform, owner, test, and expiry/review. Capability dropping does not replace seccomp, AppArmor, namespaces, or safe mounts.

#### 4. A non-root ETL worker gets `PermissionError` writing to `/data/output`. How do you troubleshoot?

**Model answer:** capture the exact path and operation; inspect `id`, UID/GID/groups, owner/mode/ACLs, mount source and mode, and user-namespace mapping. Test a harmless write in a disposable directory. Determine whether `/data/output` is a bind mount, named volume, or image path. Fix ownership/access on the narrowest required directory or volume and rerun the same test. Do not use `chmod 777`, root, or privileged mode as a shortcut.

#### 5. How do you enforce a hardening baseline without creating an unsafe exception culture?

**Model answer:** enforce policy in CI using source checks, image metadata checks, and runtime tests as distinct layers. Fail on missing non-root identity or forbidden `latest` where policy requires it, require labels and meaningful health checks where applicable, scan for secrets, and test read-only root/writable paths. Preserve evidence and document what the checker cannot prove. Exceptions need a named owner, rationale, compensating control, narrow scope, approval, expiry, and review. Audit expiry and make stale exceptions visible or blocking.

### 8.14 Sources and verification notes

#### Official sources to consult

Current official pages were **not independently opened or checked during authoring**. The following are canonical starting points to verify before applying the examples to a production engine:

1. **Dockerfile reference** — `USER`, `COPY --chown`, `HEALTHCHECK`, `CMD`: <https://docs.docker.com/reference/dockerfile/>
2. **Docker `run` reference** — runtime options, mounts, capabilities, security options, resource limits: <https://docs.docker.com/reference/cli/docker/container/run/>
3. **Docker security** — daemon access and security concepts: <https://docs.docker.com/engine/security/>
4. **Docker rootless mode** — setup and limitations: <https://docs.docker.com/engine/security/rootless/>
5. **Docker inspect reference**: <https://docs.docker.com/reference/cli/docker/inspect/>
6. **OCI Runtime Specification** — runtime configuration concepts: <https://github.com/opencontainers/runtime-spec>
7. **NIST SP 800-190, Application Container Security Guide**: <https://csrc.nist.gov/pubs/sp/800/190/final>
8. **CIS Docker Benchmark**: <https://www.cisecurity.org/benchmark/docker>
9. **Kubernetes security context**: <https://kubernetes.io/docs/tasks/configure-pod-container/security-context/>
10. **Kubernetes Pod Security Standards**: <https://kubernetes.io/docs/concepts/security/pod-security-standards/>
11. **Podman documentation**: <https://docs.podman.io/>

#### Items requiring verification

- **[VERSION-SENSITIVE] Dockerfile behavior:** exact builder support for `USER`, `COPY --chown`, `HEALTHCHECK`, and command parsing. Check the current Dockerfile reference and test the selected builder.
- **[VERSION-SENSITIVE] Runtime flags:** `--read-only`, `--tmpfs`, `--cap-drop`, `--cap-add`, `--security-opt no-new-privileges`, `--pids-limit`, `--memory`, `--cpus`, and `--init`. Check `docker run --help`, the matching Docker CLI reference, and target OS behavior.
- **[VERSION-SENSITIVE] Capability and procfs interpretation:** inspect `/proc/self/status` on the target kernel and use a trusted capability decoder if needed.
- **[VERSION-SENSITIVE] seccomp/AppArmor defaults:** verify effective profile and enforcement on the actual engine/host; do not assume platform parity.
- **[VERSION-SENSITIVE] Rootless Docker/Podman:** check current setup requirements, networking/storage constraints, and UID/GID mapping.
- **[VERSION-SENSITIVE] WSL2 mounts/ownership:** test the exact Docker Desktop or in-WSL engine arrangement and host filesystem.
- **[VERIFY] Health checks:** confirm endpoint semantics, command availability in the image, and orchestration response.
- **[VERIFY] PID 1/shutdown:** test SIGTERM, child reaping, and actual termination windows in the target runtime.
- **[VERIFY] Kubernetes mapping:** validate manifest fields and Pod Security Standards against the target cluster version and admission policy.
- **[VERIFY] Secret scanning:** confirm the chosen scanner's documented coverage and false-positive/false-negative limitations.
- **[VERIFY] Labels and image policy:** define required OCI label keys and forbidden tag rules in the organization's own policy; labels are metadata, not proof of provenance.

## Appendix A — Claim Register

Confidence indicates confidence in the general concept, not live verification of the current implementation. Source names are supplied for human checking; no current documentation was independently verified during this run.

| ID | Section | Claim | Source (document + section) | Confidence | Tag |
|---|---|---|---|---|---|
| A01 | 8.2–8.3 | Linux file permissions use numeric UID/GID identities. | Linux credentials and filesystem permissions documentation | High | [VERIFY] |
| A02 | 8.2–8.3 | Container UID 0 is not automatically equivalent to unrestricted host root. | NIST SP 800-190; Docker security docs | High | [VERIFY] |
| A03 | 8.2–8.3 | Root inside a container can still be risky when combined with capabilities, mounts, or weak isolation. | NIST SP 800-190; CIS Docker Benchmark | High | [VERIFY] |
| A04 | 8.2–8.3 | User namespaces can map container IDs to different host IDs. | Docker Engine security/rootless docs; OCI Runtime Specification | High | [VERIFY] |
| A05 | 8.3 | Dockerfile `USER` sets the default user for subsequent instructions and runtime. | Dockerfile reference — `USER` | High | [VERSION-SENSITIVE] |
| A06 | 8.3 | A runtime `--user` override can differ from image `Config.User`. | Docker run reference; Docker inspect reference | High | [VERIFY] |
| A07 | 8.4 | `COPY --chown` sets ownership for copied files. | Dockerfile reference — `COPY --chown` | High | [VERSION-SENSITIVE] |
| A08 | 8.4 | Numeric UID/GID can improve cross-image/mount predictability but does not fix every volume mapping issue. | Dockerfile docs; Linux permissions; Kubernetes security context | High | [VERIFY] |
| A09 | 8.4–8.5 | Read-only root filesystem does not automatically make mounted filesystems read-only. | Docker run reference — read-only and mounts | High | [VERIFY] |
| A10 | 8.4–8.5 | tmpfs is ephemeral and subject to runtime/host capacity constraints. | Docker run reference — tmpfs | High | [VERSION-SENSITIVE] |
| A11 | 8.4 | Ports above 1024 are a convention, not a complete security guarantee. | Docker run/network docs; Linux capabilities docs | High | [VERIFY] |
| A12 | 8.5 | `--cap-drop=ALL` can reduce process capability authority. | Docker run reference; Linux capabilities documentation | High | [VERSION-SENSITIVE] |
| A13 | 8.5 | Additional capabilities should be justified by a specific required operation. | CIS Docker Benchmark; NIST SP 800-190 | High | [VERIFY] |
| A14 | 8.5 | `no-new-privileges` limits privilege gains through supported mechanisms. | Docker run security options; Linux `no_new_privs` docs | High | [VERSION-SENSITIVE] |
| A15 | 8.5 | Memory/CPU/PID limits can prevent one container from using unbounded configured resources but can cause workload failures if mis-sized. | Docker run resource options; kernel cgroup docs | High | [VERSION-SENSITIVE] |
| A16 | 8.5 | seccomp restricts system calls and profiles/defaults can vary by runtime/platform. | Docker seccomp docs; OCI Runtime Specification | High | [VERSION-SENSITIVE] |
| A17 | 8.5 | AppArmor is a Linux mandatory access-control framework and requires platform enforcement. | Docker security docs; AppArmor documentation | High | [VERIFY] |
| A18 | 8.5 | A health check reports a configured condition but does not prove full SLO or security. | Dockerfile reference — `HEALTHCHECK`; SRE design | High | [VERIFY] |
| A19 | 8.5 | Exec-form commands avoid an extra shell command layer compared with shell form. | Dockerfile reference — `CMD` and `ENTRYPOINT` | High | [VERIFY] |
| A20 | 8.5 | PID 1/signal and child-reaping behavior should be tested for the actual process/runtime. | Docker run `--init`; OCI runtime docs | High | [VERIFY] |
| A21 | 8.5 | Rootless engine and non-root application process are distinct security choices. | Docker rootless docs; Podman docs | High | [VERIFY] |
| A22 | 8.5 | Kubernetes security context exposes identity and runtime security settings conceptually related to local Docker controls. | Kubernetes security context docs | High | [VERSION-SENSITIVE] |
| A23 | 8.6 | Image metadata alone cannot prove the effective runtime user under every override. | Docker inspect/run docs | High | [VERIFY] |
| A24 | 8.6 | Image-only inspection cannot prove that no secret exists anywhere in source/layers. | NIST SP 800-190; secret scanning tool docs | High | [VERIFY] |
| A25 | 8.6 | Runtime write tests are needed to verify read-only-root and writable-path behavior. | Docker run reference; local test procedure | High | [ILLUSTRATIVE] |
| A26 | 8.6 | Privileged mode, Docker socket, and broad host mounts can materially expand host exposure. | NIST SP 800-190; CIS Docker Benchmark | High | [VERIFY] |
| A27 | 8.6 | A policy exception should have owner, rationale, compensating control, scope, expiry, and review. | Organizational policy design; CIS/NIST guidance | High | [ASSUMPTION] |
| A28 | 8.7 | Startup, restart, health, shutdown, permission, OOM, and PID events are useful SRE signals. | SRE practice; service-specific telemetry design | High | [ASSUMPTION] |
| A29 | 8.7 | Resource targets should be derived from workload measurements and service needs. | Service performance testing and SLO design | High | [ASSUMPTION] |
| A30 | 8.8 | Non-root is defense in depth rather than a complete sandbox. | NIST SP 800-190; CIS Docker Benchmark | High | [VERIFY] |
| A31 | 8.8 | Read-only root filesystems do not protect writable mounts from writes. | Docker run reference | High | [VERIFY] |
| A32 | 8.8 | Dropping capabilities does not replace seccomp, MAC, namespace, or host isolation controls. | NIST SP 800-190; Docker security docs | High | [VERIFY] |
| A33 | 8.8 | A health check is not itself a security control. | Dockerfile reference; threat-model design | High | [ASSUMPTION] |
| A34 | 8.10 | Docker CLI output and behavior can vary by Engine/OS configuration. | Docker CLI reference; local verification | High | [VERSION-SENSITIVE] |
| A35 | 8.10 | WSL2, Docker Desktop, and native Linux can differ in filesystem/UID mapping behavior. | Docker Desktop WSL2 documentation; local verification | Medium | [VERIFY] |
| A36 | 8.14 | Current runtime flag support should be checked against installed CLI and official docs. | Docker run reference and `docker run --help` | High | [VERSION-SENSITIVE] |
| A37 | 8.14 | Kubernetes security enforcement depends on cluster version and admission policy. | Kubernetes security context and Pod Security Standards | High | [VERSION-SENSITIVE] |
| A38 | 8.14 | NIST SP 800-190 and CIS Docker Benchmark are review frameworks, not substitutes for local tests. | NIST SP 800-190; CIS Docker Benchmark | High | [VERIFY] |

## Appendix B — Audit Report

| Pass | Result (PASS/FIXED/OPEN) | Defects found | Fixes applied | Residual risk |
|---|---|---|---|---|
| 1. Completeness | PASS | Potential omissions in required section ordering | Included 8.0–8.14 and Appendices A–E; added all five lab themes | Human should compare against the full syllabus and repository tree |
| 2. Technical accuracy | OPEN | Runtime behavior depends on Docker/OS version and was not executed | Tagged version-sensitive flags and called out official verification | Commands may need adaptation on target engine |
| 3. Executability | OPEN | Sample FastAPI build and conformance script were not run | Provided complete sample app, Dockerfile pattern, checker, exit semantics, and cleanup | Runtime test assumptions (`sh`, `id`, writable `/tmp`) do not fit every image |
| 4. Currency | OPEN | Current official docs were not live-checked | Listed official document names and canonical entry points; documented verification items | URLs and section details require human validation |
| 5. Security correctness | PASS | Risk of overclaiming non-root/read-only/capabilities | Explicitly states limitations and layered controls | Actual host/runtime isolation not tested |
| 6. Fabrication scan | PASS | Sample output could be mistaken for measured output | Marked sample outputs illustrative; no performance/CVE claims | Human should preserve tags if adapting content |
| 7. Pedagogical consistency | PASS | Risk of mixing image identity and runtime identity | Separated concepts, source/metadata/runtime checks, and progression | Learner still needs practical execution |
| 8. Cross-consistency | PASS | Runtime command and checker assumptions need alignment | Used same sample image, non-root identity, read-only root, tmpfs and labels | Checker may require changes for distroless images |
| 9. Adversarial review | OPEN | Ten skeptical staff-engineer objections are not yet separately enumerated as a distinct list | Added limitations and explicit `not_proven` fields | Required ten-objection adversarial review needs human completion |
| 10. Lab safety/reproducibility | PASS WITH LIMITATION | Labs were not run in WSL2/native Linux | Named resources, local-only examples, scoped cleanup, inspection-first warnings | Must execute and verify before production adoption |

#### Ten skeptical staff-engineer objections and disposition

1. **“You have not run these commands on the target engine.”** Accepted: all execution status is disclosed; test labs locally before adoption.
2. **“Your sample image assumes `sh` and `id` exist.”** Accepted: checker documents this limitation and requires a compatible probe for distroless images.
3. **“A non-empty `Config.User` is not proof of non-root.”** Accepted: runtime identity probe is separate; checker has limitations for numeric/name forms and external overrides that require review.
4. **“The checker cannot prove no secrets are embedded.”** Accepted: explicitly listed as not proven; source/layer scanning and review are separate.
5. **“The script's read-only test could fail for reasons other than read-only root.”** Accepted: the report calls out preconditions; the learner must confirm shell availability and path behavior.
6. **“The health check may not exist or may require Python.”** Accepted: the example states its dependency and warns minimal images may need a different probe.
7. **“Capability masks are hard to interpret.”** Accepted: no fixed mask is recommended; verify with trusted tooling and actual policy.
8. **“WSL2 volume ownership differs from native Linux.”** Accepted: environment-specific verification is explicit.
9. **“A policy exception can become permanent.”** Accepted: owner, compensating control, scope, expiry, approval, and review are required.
10. **“Passing local tests does not prove Kubernetes admission or runtime enforcement.”** Accepted: Kubernetes is a forward reference; cluster-specific tests are required in M03/M12.

## Appendix C — Human Verification Checklist

#### Docker Engine / CLI

- [ ] Confirm the active daemon with `docker context show`, `docker info`, and environment inspection.
- [ ] Verify installed Engine/CLI versions with `docker version`.
- [ ] Check exact support/syntax for `--read-only`, `--tmpfs`, `--cap-drop`, `--cap-add`, `--security-opt no-new-privileges`, `--pids-limit`, `--memory`, `--cpus`, and `--init` using `docker run --help` and the current official run reference.
- [ ] Confirm inspect field meanings for `Config.User`, `HostConfig.ReadonlyRootfs`, capabilities, resource limits, and mounts.
- [ ] Verify image health-check behavior with `docker image inspect` and runtime health state.
- [ ] Check local resource availability before running labs; no broad prune cleanup.

#### Dockerfile / builder

- [ ] Verify `USER`, `COPY --chown`, `HEALTHCHECK`, `CMD`, and `ENTRYPOINT` syntax in the current Dockerfile reference.
- [ ] Confirm the chosen base image supports the account-creation commands used in the example.
- [ ] Pin base image and dependencies according to project policy.
- [ ] Verify required OCI label names and values in the organization's policy.
- [ ] Confirm the Dockerfile's actual build context and ownership after copying.

#### Linux kernel / capabilities / seccomp / AppArmor

- [ ] Inspect `Uid`, `Gid`, `Groups`, and capability fields in `/proc/self/status`.
- [ ] Verify capability interpretation with trusted tooling and current kernel documentation.
- [ ] Confirm effective seccomp and AppArmor profile on the target host; do not infer from host support alone.
- [ ] Test `no-new-privileges` behavior and support on the actual runtime.
- [ ] Verify rootless/user-namespace mappings and implications for mounted file ownership.

#### WSL2 / filesystem / volumes

- [ ] Record whether the environment is Docker Desktop, an engine inside WSL2, or native Linux.
- [ ] Check both host/virtual disk capacity and the filesystem reported inside WSL2.
- [ ] Test bind-mount ownership, mode bits, and mapping with the chosen engine.
- [ ] Verify that cleanup only targets named lab containers and does not remove useful volumes.

#### Application / health / shutdown

- [ ] Confirm the health endpoint is meaningful, local, fast, and present in the image.
- [ ] Confirm the health command's required utilities exist in the image.
- [ ] Send SIGTERM in a controlled test and record exit status/time.
- [ ] Verify child-process reaping if the service starts workers.
- [ ] Test memory, CPU, PID, and ephemeral storage limits with representative workload behavior.

#### Conformance policy / security

- [ ] Separate source inspection, image metadata inspection, and runtime behavior tests.
- [ ] Confirm the checker does not log secret values or credentials.
- [ ] Test a known-good image and a deliberately non-conforming lab image.
- [ ] Confirm report exit codes and failure handling.
- [ ] Verify Docker socket, privileged mode, broad host mounts, and writable host paths are detected in the intended inspection workflow.
- [ ] Define a real secret-scanning workflow and document its limits.
- [ ] Confirm exceptions have owner, scope, compensating control, approval, expiry, and review.

#### Kubernetes forward reference

- [ ] Validate `runAsNonRoot`, `runAsUser`, `runAsGroup`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation`, capabilities, seccomp, and Pod Security Standards against the target cluster version.
- [ ] Confirm admission policies actually enforce the intended settings.
- [ ] Test runtime behavior with the real volume and storage class; local Docker success is not proof of Kubernetes behavior.

## Appendix D — Known Limitations and Assumptions

- **Environment assumption:** examples target a recent Docker Engine/CLI on WSL2 Ubuntu or native Linux. Exact versions were not available or tested during authoring.
- **Image assumption:** the conformance script expects a locally available image with `sh` and `id`; distroless images need a compatible runtime probe.
- **Rootless assumption:** rootless Docker and Podman have different constraints; the lesson does not assert feature parity.
- **WSL2 limitation:** host/guest filesystem and UID/GID behavior depend on the chosen Docker setup and mount source.
- **Runtime limitation:** resource flags, tmpfs options, capabilities, seccomp, AppArmor, and `no-new-privileges` are platform/version-sensitive.
- **Health-check limitation:** Docker health status is not equivalent to Kubernetes readiness/liveness semantics or an end-to-end SLO.
- **Conformance limitation:** the script checks image metadata and selected runtime behavior; it does not prove absence of secrets, provenance, all capability restrictions, all mounts, or all platform policies.
- **Policy assumption:** `org.opencontainers.image.source` and `org.opencontainers.image.version` are example required labels; teams must define their own label policy.
- **Scope boundary:** full CI/CD enforcement is M02; Kubernetes security context and admission are M03/M12; secret delivery is M09; provenance/SBOM/signature verification is M12.
- **Verification status:** no command was executed and no current official documentation was independently checked during authoring.

## Appendix E — Sign-off

- **Content status:** DRAFT-AUDITED
- **Audit date:** 2026-10-24
- **Auditor role:** AI self-audit (requires human verification)
- **Unverified items count:** 12 grouped verification categories in §8.14, plus target-specific checks in Appendix C.
- **Commands/labs executed:** None during authoring.
- **Official documentation checked live:** None during authoring.
- **Repository tree inspected:** No; the lesson follows the supplied Unit 8 prompt and intended target path.
- **Production approval:** Not granted. Self-audit does not replace execution by a human in the target environment.

**Final disposition:** the required lesson structure, four levels, hardening conformance script, labs, checklists, source notes, and audit artifacts are included. Runtime commands, current documentation, platform behavior, and the conformance script remain unverified until a human runs the checks in the intended environment.
