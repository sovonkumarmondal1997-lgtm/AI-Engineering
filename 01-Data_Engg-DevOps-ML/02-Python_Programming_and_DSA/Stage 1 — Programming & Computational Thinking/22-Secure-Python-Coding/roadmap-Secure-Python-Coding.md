# Roadmap — Module 1.22: Secure Python Coding

This is the learning roadmap for the twenty-second module of Stage 1,
**Programming & Computational Thinking**. It tells you **what** to learn
about writing Python that is hard to attack and safe to operate, **in what
order**, **how** to practise each topic, and **how to prove to yourself**
that you have learned it.

Security is not a separate phase; it is a property of how you handle inputs,
files, processes, secrets, network calls and dependencies in every program.
Data and AI engineers are especially exposed: pipelines ingest untrusted
files and APIs, notebooks run arbitrary code, model artifacts can be pickles,
agents execute tool calls and generated code, and credentials for data
warehouses, cloud accounts and LLM providers sit in environment variables.
One injection or leaked key can expose an entire data platform.

Earlier modules planted the seeds: `eval`/`exec` risks (1.12), `shell=True`
and archive extraction (1.13), pickle and decompression bombs (1.14),
supply-chain awareness (1.10, 1.18), regex DoS (1.14). This module
consolidates them into a **threat-model-driven** discipline. The dedicated
AI security stage (prompt injection, agent sandboxing, model supply chain,
privacy) comes later and builds directly on these foundations; platform
security (IAM, network, KMS) is covered in Stage 2 cloud modules.

> This module teaches **defensive** practice. Exploit demonstrations are
> limited to tiny, local, self-contained examples against your own code in a
> lab environment — never against systems you do not own or have permission to test.

---

## 1. Module outcome

By the end of this module you will be able to:

- Build a basic **threat model** (assets, entry points, attackers, trust boundaries) for a small Python service or pipeline.
- Validate and sanitise **untrusted input** by allow-listing, and prevent SQL, shell, template, log and path injection.
- Avoid **unsafe deserialisation** (`pickle`, `yaml.load`, `eval`, `marshal`, unsafe model files) and choose safe formats.
- Handle files and paths safely (traversal, symlinks, temp files, permissions, archive extraction, uploads).
- Run subprocesses and call external services without command injection.
- Manage **secrets, tokens and cryptography** correctly using vetted libraries and secure defaults.
- Write HTTP clients that resist **SSRF**, enforce TLS, timeouts and size limits.
- Use **static analysis and dependency auditing** (`bandit`, `ruff` security rules, `pip-audit`, secret scanners) in CI.
- Respond to a vulnerability or secret leak with a clear process.

---

## 2. Prerequisites

| Earlier skill | Where you learned it | Why it matters here |
| --- | --- | --- |
| Environment variables, config, secrets hygiene | Modules 1.5 (09), 1.10 (01); Stage 0 — Module 0.4 (12) | Secret handling |
| `subprocess`, `tempfile`, archives, hashing, `secrets` | Module 1.13 | Safe usage patterns |
| Pickle, regex DoS, decompression, Unicode confusables | Module 1.14 | Specific attack classes |
| `eval`/`exec`, AST allow-lists | Module 1.12 (08, 09) | Dynamic code risks |
| Exceptions, logging, validation errors | Modules 1.3, 1.10 | Safe errors and logs |
| Supply-chain awareness, SBOM, trusted publishing | Modules 1.10 (07), 1.18 | Dependency security |
| Testing and fuzzing | Modules 1.7, 1.16 | Security regression tests |
| OS permissions, processes, networking | Stage 0 — Modules 0.2, 0.3 | File modes, sandboxing, ports |
| HTTP basics | Module 1.13 (09) | SSRF, TLS |

**Tools:** `uv add --dev bandit pip-audit detect-secrets semgrep` (optional), `ruff` with `S` (flake8-bandit) rules,
`gitleaks`/`trufflehog` (CLI), `pre-commit`, `mitmproxy` or `httpbin` locally for client tests, Docker for sandbox exercises.

---

## 3. How the module is organised

```text
Phase A — Mindset and Input                     (Basics)
  01 untrusted input and injection risks
  02 unsafe deserialization
Phase B — Files, Processes and Network          (Intermediate)
  03 path traversal and safe file handling
  04 shell and subprocess injection
  05 secrets, tokens and cryptography basics
  06 SSRF and safe HTTP clients
Phase C — Process and Assurance                 (Advanced)
  07 static analysis with bandit and pip-audit
  08 threat modelling small Python services
```

Pace: about 2–3 weeks part-time. Use a deliberately vulnerable sample app
(`vulnpy`, ~300 lines: file upload, report generator, URL fetcher, config
loader, admin CLI) that you **find, exploit locally, fix and regression-test**
issue by issue.

---

## Lesson 01 — `01-untrusted-input-and-injection-risks.md`

**Why it matters.** Injection is consistently among the top vulnerability
classes: data is interpreted as code in some context (SQL, shell, HTML,
templates, logs, regex, format strings, LLM prompts). The root cause is
always the same — mixing **data** and **instructions** — and the fix is also
always the same: keep them separate, validate at the boundary, encode for the
sink.

### Basic — what to learn

- **Trust boundaries**: anything from outside your process is untrusted — user input, files, HTTP bodies/headers, environment variables, DB contents written by others, model outputs, filenames, third-party APIs, config from shared locations.
- **Validate early, encode late**: parse into typed values at the edge (allow-list formats, ranges, lengths, enums), and context-encode when outputting.
- **SQL injection**: never build SQL with f-strings/`%`/`+`; use parameterised queries (`cursor.execute("... WHERE id = ?", (user_id,))`); identifiers can't be parameterised → allow-list table/column names.

```python
# vulnerable
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")      # name = "x' OR '1'='1"
# safe
cur.execute("SELECT * FROM users WHERE name = ?", (name,))
# safe identifiers
ALLOWED_SORT = {"name", "created_at"}
if sort not in ALLOWED_SORT: raise ValueError("bad sort column")
cur.execute(f"SELECT * FROM users ORDER BY {sort}")           # only after allow-list
```
- Log injection / log forging (newlines in user input), and why structured logging helps.
- Never trust client-side validation; validation messages shouldn't leak internals.

### Intermediate — what to learn

- Injection families beyond SQL: **command** (lesson 04), **template injection** (Jinja2 SSTI: never render user-controlled *templates*; use autoescape and `SandboxedEnvironment` only as defence-in-depth), **HTML/XSS** (escape on output, `markupsafe.escape`, framework autoescape, Content-Security-Policy), **LDAP/NoSQL/GraphQL** injection, **header/CRLF injection**, **format-string** (`str.format` with user-controlled format → attribute access `{0.__class__}`), **regex** (ReDoS and user-controlled patterns), **XML** (XXE, billion laughs → `defusedxml`), **CSV/Excel formula injection** (cells starting with `= + - @`), **path** (lesson 03), **LLM prompt injection** (preview of the AI security stage: treat model/tool outputs as untrusted data).
- Input validation toolkit: type parsing (`int()`, `Decimal`, `datetime.fromisoformat`, `uuid.UUID`, `ipaddress`), `enum`, regex with `fullmatch`, length limits, Unicode normalisation (Module 1.14 lesson 03), Pydantic models at API boundaries (Stage 2/7), schema validation (`jsonschema`).
- Allow-list vs deny-list: deny-lists fail; prefer positive validation and canonicalise before validating (normalise → validate → use the *normalised* value).
- Resource limits as security: max body size, max items, max depth for nested JSON, max string length, timeouts, rate limiting (Stage 7).
- Error handling: return generic messages to users, log detail internally with correlation ids; don't expose stack traces or SQL errors.
- ORM and query-builder safety: SQLAlchemy `text()` with bind params; raw queries are the risk; stored procedures aren't automatically safe.

```python
import csv

def csv_safe(cell: str) -> str:
    return "'" + cell if cell[:1] in ("=", "+", "-", "@", "\t", "\r") else cell
```

### Advanced — what to learn

- **Second-order injection** (stored then used unsafely), **blind injection**, injection via filenames/metadata/headers; out-of-band exfiltration.
- Contextual output encoding matrix: HTML body vs attribute vs JS vs URL vs CSS vs SQL vs shell vs log; use the sink's own safe API instead of hand-rolled escaping.
- Canonicalisation attacks: Unicode normalisation differences, case folding, double URL-encoding, overlong UTF-8, null bytes (`\x00`), mixed path separators, homoglyphs; validate *after* canonicalisation and use the same canonical form downstream.
- Parser differentials: two components parse the same input differently (e.g. proxy vs app URL parsing, JSON duplicate keys, multipart boundaries) → request smuggling, WAF bypass; prefer single parsing, strict parsers, reject ambiguity.
- Type confusion in dynamic languages: JSON `["a"]` where a string is expected; `int` vs `str` vs `bool` (`True == 1`); NaN/Infinity; huge ints; negative numbers; empty values — validate types, not just values.
- Designing safe APIs: typed parameters (e.g. a `SafeSQL` wrapper, t-strings in Python 3.14 for SQL/HTML with automatic escaping — Module 1.15 lesson 08), builders that cannot create injectable strings, least-privilege database accounts (read-only roles, row-level security, separate migration vs app users).
- Secure-by-default library design: make the safe path the easy path, require explicit `unsafe_` opt-ins, provide secure examples.
- Testing for injection: unit tests with malicious payload tables, fuzzing (Module 1.16 lesson 09), `sqlmap`-style testing against your own staging app only, Semgrep/Bandit rules, code review checklist ("where does this string end up?").
- Threat-model several data-pipeline entry points: filenames in an object store, CSV headers, JSON keys, partition values, table names derived from files.
- Exercise: in `vulnpy`, find and exploit one SQL injection, one template injection, one CSV formula injection and one log-forging bug **locally**; fix each; add regression tests with payload tables.

### Common mistakes

- "Sanitising" with blacklists or ad-hoc `replace("'", "")`.
- Validating the raw value then using a transformed value.
- Using f-strings for SQL "just for table names" without an allow-list.

### Self-check

1. Why can't table names be parameterised and what is the safe approach?
2. List five injection sinks and the safe API for each.
3. Write a validator for `/reports/<name>?from=<date>&limit=<n>` that rejects everything not explicitly allowed and add payload tests.

---

## Lesson 02 — `02-unsafe-deserialization.md`

**Why it matters.** Deserialising attacker-controlled data with a powerful
format gives the attacker code execution. In data/ML contexts this appears as
pickled models, cached DataFrames, YAML configs, `joblib` files, notebooks,
and "model zoo" downloads — a real and growing supply-chain risk.

### Basic — what to learn

- Why it's dangerous: formats that can instantiate arbitrary objects/call arbitrary functions during load (`pickle`, `marshal`, `shelve`, `yaml.load` (unsafe loader), `jsonpickle`, `dill`, `cloudpickle`, `torch.load` pickle mode, `numpy.load(allow_pickle=True)`, `joblib.load`).
- Safe by default: **JSON**, **CSV**, **TOML**, **Parquet/Arrow**, **MessagePack**, **Protocol Buffers**, **`yaml.safe_load`**, `numpy.load(allow_pickle=False)`, `safetensors`, ONNX (with validation).
- Rule: **never unpickle/unsafe-load data that came from an untrusted or unauthenticated source** — including network, shared drives, user uploads, downloaded model files and caches in world-writable locations.

```python
import yaml
data = yaml.safe_load(text)           # NOT yaml.load(text) / Loader=yaml.Loader
import numpy as np
arr = np.load("x.npy", allow_pickle=False)
```

### Intermediate — what to learn

- How pickle exploits work conceptually (`__reduce__` returning `(callable, args)`) — Module 1.14 lesson 06; demonstrate with a harmless payload in an isolated lab (e.g. writing a marker file in a temp dir) to prove the risk, then never run such payloads outside the lab.
- Mitigations and their limits: restricted `Unpickler.find_class`, HMAC-signing payloads (authenticity from a trusted producer, not safety against a malicious signer), file permissions, loading only from trusted internal registries, scanning tools (`fickling`, ModelScan, `picklescan`) as defence-in-depth — scanning is not a guarantee.
- Safer model/data formats for ML: `safetensors` for tensors (no code), `torch.load(weights_only=True)`, ONNX, GGUF; keep architecture code separate from weights; verify hashes/signatures from model hubs; pin revisions; read the model licence (Module 1.18 lesson 10).
- Other deserialisation hazards: XML external entities and entity expansion (`defusedxml`), YAML anchors/aliases bombs, JSON/YAML **depth and size bombs**, ZIP/tar bombs and traversal (lessons 03 and Module 1.14 lesson 07), Java-like gadget chains are rare in Python but `__reduce__`/`__setstate__` provide equivalents, template engines with `!!python/object`.
- Validate after deserialising: even "safe" formats yield attacker-controlled *structure*; validate with schemas/Pydantic and limits (size, depth, counts).
- Signing & integrity: store content hashes (SHA-256) and signatures (Sigstore, minisign, `cryptography` Ed25519) alongside artifacts; verify before loading.

### Advanced — what to learn

- Design a **safe artifact pipeline**: build → hash/sign → publish to internal registry → verify at load → load with restricted loader in a low-privilege sandbox; admission checks in CI/CD; deny pickles from outside the trust domain.
- Sandboxing risky loads when unavoidable: separate process with dropped privileges (no network, read-only FS, seccomp), container with resource limits, ephemeral VM; communicate results over a typed channel (JSON/Arrow), not pickle.
- Reading pickle opcodes safely with `pickletools.dis` (no execution) and writing a **policy checker** that rejects dangerous `GLOBAL`/`STACK_GLOBAL` references (`os.system`, `subprocess`, `builtins.eval/exec/__import__`, `posix`, `socket`) — then understanding why allow-listing known-good classes is the only robust approach.
- `multiprocessing`/`concurrent.futures` use pickle between your own processes (trusted channel) — make sure ports/sockets are not exposed; `multiprocessing.connection` with `authkey`; Dask/Ray/Spark security models (pickle on the wire → network isolation, authentication, TLS — Stage 2 distributed modules).
- Caches as attack surface: `joblib.Memory`, `diskcache`, `functools`-on-disk caches, Python bytecode caches (`__pycache__`), `shelve`, `dbm` — protect directories (permissions, not world-writable), per-user cache paths, integrity checks.
- Incident scenarios: a data scientist downloads a "fine-tuned model" pickle from a public hub; a shared bucket is writable by many; a compromised dev laptop poisons a feature cache. Write detection/response steps and preventive controls (egress filtering, immutable buckets, signed artifacts, least privilege).
- Compare ecosystems: Java serialisation vulnerabilities, PHP `unserialize`, .NET `BinaryFormatter` (obsolete) — the pattern repeats.
- Exercise: implement `safe_load_model(path)` that (1) checks a signature/hash allow-list, (2) refuses pickle formats unless `--i-trust-this` and running inside a sandbox flag, (3) loads `safetensors`, (4) validates metadata with a schema; add tests including a malicious pickle fixture that must be rejected, never executed.

### Common mistakes

- `yaml.load` without `SafeLoader`.
- Treating "internal" shared storage as trusted.
- Relying solely on scanners.

### Self-check

1. Why is HMAC-signing a pickle not a defence against a malicious trusted producer?
2. Choose a format for each: tensor weights, feature cache, user-uploaded config, RPC payload — and justify.
3. Demonstrate (in a lab) that a restricted `Unpickler` blocks `os.system` payloads and explain what it still doesn't protect against.

---

## Lesson 03 — `03-path-traversal-and-safe-file-handling.md`

**Why it matters.** File handling bugs lead to arbitrary file read/write
(`../../etc/passwd`, overwriting `~/.ssh/authorized_keys`), account
takeover, data leaks, and code execution (overwrite a module or cron file).
Data jobs constantly construct paths from filenames, partition values,
archive members and user parameters.

### Basic — what to learn

- Path traversal: `../`, absolute paths, drive letters, UNC paths, symlinks, URL-encoded `%2e%2e/`, null bytes.
- **Contain paths**: resolve and verify the result is inside the base directory.

```python
from pathlib import Path

BASE = Path("/srv/app/uploads").resolve()

def safe_join(user_path: str) -> Path:
    p = (BASE / user_path).resolve()
    if not p.is_relative_to(BASE):                  # 3.9+
        raise PermissionError("path escapes base directory")
    return p
```
- Prefer **IDs over names**: store uploads under server-generated names (UUID), keep the original filename as metadata only (sanitised); never trust `Content-Type` or extension.
- Least privilege on files: restrictive modes (`0o600` files, `0o700` dirs), `umask`, don't run as root, separate read-only and writable directories.
- Temp files: `tempfile.NamedTemporaryFile/mkstemp/TemporaryDirectory` (never `mktemp`, never predictable names in `/tmp`).

### Intermediate — what to learn

- **TOCTOU** (time-of-check/time-of-use): check then open is racy; use `open` with flags (`os.O_NOFOLLOW`, `os.O_EXCL | os.O_CREAT` for exclusive creation) and `dir_fd`-relative operations (`os.open(name, dir_fd=fd)`), or `Path.open("x")` exclusive mode `"x"`.
- **Symlink/hardlink attacks**: resolve symlinks (`resolve(strict=True)`), reject symlinks in upload dirs (`is_symlink()`), `O_NOFOLLOW`; Windows reparse points/junctions.
- Safe archive extraction (Module 1.13 lesson 03): validate every member path, reject absolute paths/`..`, reject links and device files, limit total size/count/ratio, use `tarfile` `filter="data"` (default in 3.14) — and extract into a fresh empty directory.
- Uploads: size limits, content sniffing (magic bytes, not extension), allowed types, antivirus scanning for user-facing apps, store outside web root, serve with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`, random names, quotas.
- Downloads: construct paths from validated IDs; stream with limits; set timeouts; verify checksums.
- Windows specifics: reserved names (`CON`, `NUL`), trailing dots/spaces, alternate data streams (`file.txt:stream`), case-insensitivity, long path prefixes; use `pathlib.PureWindowsPath` to validate cross-platform inputs.
- Secure file writes: write temp file in the same directory with `0o600`, `fsync`, `os.replace` (Module 1.10 lesson 05); avoid following attacker-controlled symlinks for the target.
- Permissions and ownership checks for config/secret files (warn if group/world-readable); `os.stat().st_mode`.

```python
import os, stat
def read_secret_file(path):
    st = os.stat(path)
    if st.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise PermissionError(f"{path} must not be accessible by group/others")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
```

### Advanced — what to learn

- Capability-style file APIs: open a directory fd once (`os.open(base, os.O_DIRECTORY)`) and perform all operations relative to it with `dir_fd`; Python 3.13+ `os.path.realpath(strict=...)`/`pathlib` changes; `Path.full_match` (3.13) for glob-like validation; `os.path.commonpath` pitfalls on case-insensitive filesystems.
- Linux hardening: `openat2` with `RESOLVE_BENEATH` (not in stdlib → via `ctypes`/libraries, awareness), mount options (`noexec,nosuid,nodev`), read-only root filesystems in containers, `tmpfs` for scratch, separate volumes with quotas, SELinux/AppArmor profiles.
- Sandbox directories per tenant/job; chroot/containers/user namespaces; unprivileged worker users; avoiding `sudo` in pipelines; secrets mounted read-only, in memory (tmpfs).
- Information leakage via errors and paths: don't reveal absolute server paths; sanitise file names in logs; avoid exposing directory listings.
- Data-lake specific: object-store keys are not file paths (no `..` semantics, but prefix collisions and "directory" confusion), partition values derived from data (`dt=../../x`) → validate; bucket policies; pre-signed URLs scope/expiry; avoid world-readable ACLs; versioning/immutability for audit.
- Zip/tar bombs and resource exhaustion (disk, inodes, memory, CPU): quotas, streaming, ratio checks, timeouts, file count limits.
- File-type confusion and polyglots; parser vulnerabilities in image/PDF/office libraries — process in sandboxed workers with resource limits (`resource.setrlimit`, containers), keep libraries updated.
- Automated testing: payload tables (`../`, `..\\`, `%2e%2e%2f`, `/etc/passwd`, `C:\\Windows`, `\\\\server\\share`, symlink to outside, very long names, unicode normalisation tricks), property-based tests asserting "result is always inside BASE", fuzzing archive handlers.
- Exercise: build `safe_storage` — a small library for saving/loading user files with ID-based names, containment checks, symlink rejection, atomic writes, size/type limits, archive extraction safe-mode, and a test-suite of traversal payloads; document threat model and residual risks.

### Common mistakes

- Using `os.path.join(base, user_input)` (absolute input discards `base`).
- Checking `startswith(base)` on strings (`/srv/app/uploads-evil` passes).
- Following symlinks in upload directories.

### Self-check

1. Why does `Path("/base") / "/etc/passwd"` equal `/etc/passwd` and how do you guard against it?
2. Explain a TOCTOU symlink attack on "check then open" and a fix.
3. Write a zip extractor that rejects traversal, links and bombs, and test with malicious archives built in the test.

---

## Lesson 04 — `04-shell-and-subprocess-injection.md`

**Why it matters.** Pipelines shell out to `git`, `ffmpeg`, `pg_dump`,
`kubectl`, compilers and converters. A single untrusted value interpolated
into a shell string gives the attacker your privileges. Module 1.13 lesson 04
taught correct `subprocess` usage; this lesson focuses on the attack surface
and defence in depth.

### Basic — what to learn

- Dangerous APIs: `os.system`, `os.popen`, `subprocess.*(..., shell=True)`, `commands`-style string building, backticks in other languages, `eval`/`exec` of command strings, `pty.spawn` with user data.
- Safe pattern: **argument list, no shell**: `subprocess.run(["git", "clone", "--", url, dest], check=True, timeout=60)`.
- Shell metacharacters: `; | & $() \` > < * ? ~ \n`; quoting is fragile; `shlex.quote` only when a shell is unavoidable.
- **Argument injection** even without a shell: a value starting with `-` becomes an option (`git clone --upload-pack=…`, `tar --checkpoint-action`, `curl -o`): use `--` separators, validate values, or prefix paths with `./`.

```python
# vulnerable: filename = "x; rm -rf ~"
os.system(f"convert {filename} out.png")
# safe
subprocess.run(["convert", "--", str(filename), "out.png"], check=True, timeout=30)
```

### Intermediate — what to learn

- Environment hardening: pass a minimal `env={...}` (explicit `PATH`), avoid inheriting secrets; absolute paths for executables (`shutil.which` once at startup) to avoid PATH hijacking; set `cwd` to a safe directory; `close_fds=True` (default).
- Interpreter-level injection: `python -c`, `bash -c`, `sh -c "$VAR"`, `sudo`, `ssh host "cmd $x"` (remote shell!), `docker exec`, `kubectl exec`, `xargs`, `find -exec`, `awk`/`sed` program strings — treat *every* command string passed to another interpreter as code.
- Allow-list approach: map user choices to fixed command templates (`{"png": ["convert", ...], "jpg": [...]}`), validate parameters by type/range/regex, reject unknown options.
- Output handling: treat stdout/stderr as untrusted data; limit output size (`stdout` streaming with caps), decode with explicit encoding and `errors="replace"`; don't feed command output back into another shell.
- Timeouts and resource limits: `timeout=`, `resource.setrlimit` via `preexec_fn` is discouraged → use `prlimit`/cgroups/containers; kill process groups (`start_new_session=True`, `os.killpg`).
- Privilege: never run as root/with `sudo`; drop privileges (separate service user); use `sudoers` entries with exact commands (no wildcards) when truly needed.
- Logging: record command argv (with secrets redacted) and exit status for audit; don't log full environments.
- Static detection: Bandit B602/B603/B604/B605/B606/B607 and Ruff `S602–S607`; code-review grep for `shell=True`, `os.system`, `popen`.

### Advanced — what to learn

- Win32 specifics: `CreateProcess` command-line parsing (`subprocess.list2cmdline` rules), `.bat`/`.cmd` file handling (BatBadBut-style argument injection even with `shell=False`), `cmd.exe` metacharacters, PowerShell injection; prefer executables and avoid passing untrusted args to batch files.
- Argument injection catalogue for common tools and how to neutralise (`git`, `tar`, `rsync`, `curl`/`wget`, `ssh`, `find`, `zip`, `openssl`, `ffmpeg` protocol handlers `concat:`/`file:`/`http:` → SSRF/LFI): use `-protocol_whitelist`, scheme allow-lists, or replace with library calls (e.g. use `zipfile`, `tarfile`, `httpx`, `GitPython`/`dulwich` instead of shelling out).
- Replace subprocess with libraries when possible (less attack surface, better errors) and **sandbox the rest**: containers with `--network none`, read-only FS, no capabilities (`--cap-drop ALL`), non-root user, seccomp, `no-new-privileges`, resource limits; `bubblewrap`/`firejail`/`nsjail` for process-level sandboxes; gVisor/Firecracker for stronger isolation. Link to the AI Agents stage's sandboxed code execution.
- Command construction DSLs: a typed `Command` builder that only accepts known flags and validated values and renders an argv list; golden tests on rendered argv; fuzz parameter combinations.
- Pipelines and CI: injection through environment variables/branch names/PR titles in GitHub Actions (`${{ github.event.pull_request.title }}` in `run:` steps) — pass via `env:` and quote; script injection in `Makefile`s and `docker build` args; secrets echo in logs.
- Container/Kubernetes: command injection via `ENTRYPOINT` shell form, `docker run` with user-controlled args, mounting the Docker socket; `kubectl exec` from services.
- Detection and response: auditd/Falco rules for unexpected `sh`/`curl` spawns from Python workers; EDR alerts; egress allow-lists; incident playbook for suspected RCE (isolate, preserve evidence, rotate secrets).
- Exercise: in `vulnpy`, fix a thumbnail generator that shells out to ImageMagick with a user-supplied filename and format: (1) exploit locally with `; touch /tmp/pwned` and `-write` option injection, (2) replace with Pillow, (3) keep a sandboxed `convert` fallback with allow-listed options in a no-network container, (4) add tests with malicious filenames and a Bandit CI check.

### Common mistakes

- Thinking `shell=False` alone prevents argument injection.
- Relying on `shlex.quote` for cross-platform safety.
- Passing user strings to `ssh`/`docker exec` command strings.

### Self-check

1. Give two ways `subprocess.run(["tar", "xf", user_archive])` can be abused despite no shell, and mitigations.
2. How would you design a fixed-template command runner and test it?
3. Write a Bandit/Ruff configuration that fails CI on `shell=True` and `os.system`, with a documented exception process.

---

## Lesson 05 — `05-secrets-tokens-and-cryptography-basics.md`

**Why it matters.** Leaked credentials are the most common real-world
cause of data breaches and cloud compromise; custom cryptography is the most
common way to get security wrong. Data and AI platforms hold API keys
(cloud, warehouse, LLM providers), database passwords, tokens and PII.

### Basic — what to learn

- **Secrets management basics**: never hard-code secrets; never commit them (`.env` in `.gitignore`); load from environment variables or a secrets manager at runtime; separate secrets per environment; least privilege and short lifetimes; rotate.
- Detection: `detect-secrets`, `gitleaks`, GitHub secret scanning; pre-commit hook; what to do if a secret is committed (revoke/rotate **first**, then clean history — removing from git history does not un-leak it).
- Safe handling in code: don't log secrets or full request headers/URLs with tokens; redact in repr (`pydantic.SecretStr`, custom `__repr__`), avoid secrets in command-line arguments (visible in `ps`/shell history) and exception messages; `getpass` for interactive input.
- **Use vetted libraries for cryptography** — never invent algorithms or protocols. Know the vocabulary: hashing, MAC/HMAC, symmetric encryption (AES-GCM, ChaCha20-Poly1305), asymmetric (RSA/ECDSA/Ed25519), key derivation (scrypt/Argon2/PBKDF2), randomness (`secrets`/`os.urandom`), TLS.

```python
import os, secrets
API_KEY = os.environ["PROVIDER_API_KEY"]            # fail fast if missing (KeyError)
session_token = secrets.token_urlsafe(32)           # not random.random()
```

### Intermediate — what to learn

- **Passwords**: never store plaintext or fast hashes (MD5/SHA-*); use Argon2id (`argon2-cffi`), scrypt or bcrypt with per-user salts and tuned cost; constant-time comparison (`hmac.compare_digest`); password policy (length over complexity), breach checks, rate limiting/lockouts, MFA.
- **Authenticated encryption** with the `cryptography` package: `AESGCM`, `ChaCha20Poly1305`, `Fernet` (simple, includes timestamp/HMAC); unique nonces per key (never reuse a nonce with GCM); store nonce with ciphertext; associated data.
- **Signatures & MACs**: HMAC for webhook verification (Module 1.13 lesson 06); Ed25519 signatures for artifacts; JWT pitfalls (`alg: none`, algorithm confusion, missing audience/expiry validation, storing sensitive data in tokens) — use `PyJWT`/`authlib` with explicit algorithms and claims validation.
- **TLS**: verify certificates (never `verify=False`), use system CA store or pinned CA bundle, minimum TLS 1.2+, SNI/hostname checks (`ssl.create_default_context()`), mutual TLS for service-to-service when appropriate.
- **Key management**: separate keys from data; envelope encryption (data keys wrapped by KMS key — Stage 2 AWS/KMS), key rotation, access via IAM roles/workload identity instead of long-lived keys, hardware-backed keys; never derive keys from short passwords without a KDF.
- Randomness: `secrets`/`os.urandom` for tokens and keys; `random` is predictable; UUID4 is fine as an identifier but not a secret capability (use 128+ bits from `secrets`).
- Secrets in infrastructure: CI/CD secrets, container images (no secrets in layers or build args; BuildKit secrets), Kubernetes secrets (base64 ≠ encryption → enable encryption at rest/external secret operators), `.env` handling in production, Docker Compose.
- Short-lived credentials & OIDC federation (GitHub Actions → cloud roles; Module 1.18 lesson 06), instance/workload identities, token exchange; scoped API keys with budgets/rate limits (LLM providers).

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
key = AESGCM.generate_key(bit_length=256)
aes, nonce = AESGCM(key), os.urandom(12)
ct = aes.encrypt(nonce, b"secret data", b"context:user42")
pt = aes.decrypt(nonce, ct, b"context:user42")
```

### Advanced — what to learn

- Common crypto mistakes: ECB mode, nonce reuse, unauthenticated encryption (CBC without MAC → padding oracle), MAC-then-encrypt ordering, homemade key derivation, hard-coded IVs, comparing MACs with `==`, truncating hashes unsafely, using hashing as encryption, rolling your own JWT/session scheme, insufficient entropy at boot in containers (rare), weak RSA padding (PKCS#1 v1.5 for encryption), encrypting without key rotation/versioning.
- Timing and side channels: constant-time comparisons; avoid secret-dependent branching in custom code; Python is not suitable for side-channel-resistant primitives—delegate to audited libraries.
- Protecting data at rest and in transit: field-level encryption, tokenisation, format-preserving needs, deterministic encryption trade-offs, searchable encryption (awareness); database/object-store encryption (KMS), TLS everywhere; **hashing/pseudonymising PII is not anonymisation** (Module 1.13 lesson 06; Stage 2 governance).
- Secrets lifecycle & incident response: inventory, ownership, rotation automation, break-glass procedures, audit logs, detection (canary tokens, anomaly detection on key use), leak response runbook (revoke → rotate → investigate usage → clean history → postmortem).
- Memory handling: Python strings are immutable and may linger in memory/core dumps/swap; limit lifetime, avoid logging, use `bytearray`/`memoryview` zeroisation only as best-effort (limited guarantees), disable core dumps for sensitive processes.
- Supply-chain for crypto: pin and audit `cryptography`, `pyopenssl`, `paramiko`; prefer wheels; track CVEs; FIPS requirements and compliance contexts (awareness).
- Post-quantum awareness: harvest-now-decrypt-later, hybrid key exchange in TLS, NIST PQC standards (ML-KEM, ML-DSA) landing in libraries — track, don't implement.
- LLM/AI-specific secrets: provider keys in notebooks and prompts, keys exposed to agents/tools (give tools scoped credentials, never the master key), logs/traces capturing prompts with secrets, proxies that inject credentials server-side, per-user keys and budgets — preview of the AI Safety/Security stage.
- Exercise: build `secretkit`: (1) config loader that reads secrets from env/secret-manager stubs with `SecretStr`-like redaction and a `doctor` check for world-readable files; (2) an `encrypt_field/decrypt_field` pair using AES-GCM with key IDs for rotation and associated data; (3) HMAC webhook verifier with replay protection; (4) a pre-commit/CI setup with `detect-secrets` + `gitleaks`; (5) a leak-response runbook; (6) tests that assert secrets never appear in `repr`, logs or exceptions.

### Common mistakes

- Committing `.env` or notebooks with keys; assuming deleting the commit is enough.
- `verify=False` "temporarily".
- Using `hashlib.sha256(password)` or reusing a GCM nonce.

### Self-check

1. A key was pushed to a public repo 5 minutes ago — what do you do, in order?
2. Why is AES-GCM nonce reuse catastrophic?
3. Implement password hashing with Argon2id and verification, with a test for timing-safe comparison and parameter upgrade (rehash on login).

---

## Lesson 06 — `06-ssrf-and-safe-http-clients.md`

**Why it matters.** Server-side request forgery (SSRF) turns your service
into a proxy into places the attacker can't reach: cloud metadata endpoints
(`169.254.169.254` → temporary credentials), internal admin panels, databases,
localhost services. Data and AI systems fetch URLs constantly (web
ingestion, link previews, webhooks, RAG crawlers, agent browsing tools,
model downloads), which makes SSRF a core risk.

### Basic — what to learn

- What SSRF is: the app fetches a URL influenced by the attacker; the request originates from the app's network position and credentials.
- High-value targets: cloud metadata services (AWS IMDS `169.254.169.254`, GCP `metadata.google.internal`, Azure IMDS), localhost (`127.0.0.1`, `[::1]`, `0.0.0.0`), RFC1918 private ranges (`10/8`, `172.16/12`, `192.168/16`), link-local, internal DNS names, Kubernetes services, Docker socket proxies, admin panels, internal APIs.
- Baseline client hygiene: **always set timeouts**, limit response size, limit redirects, verify TLS, set a descriptive User-Agent, don't send ambient credentials to arbitrary hosts.

```python
import httpx
client = httpx.Client(timeout=httpx.Timeout(5.0, connect=3.0),
                      follow_redirects=False, max_redirects=0)
resp = client.get(url)                      # still need URL validation (below)
```
- URL basics with `urllib.parse`/`httpx.URL`: scheme, userinfo (`http://a@evil`), host, port, path; only allow `https` (and `http` if required).

### Intermediate — what to learn

- **Validation steps** (defence in depth): (1) parse; (2) allow-list scheme (`https`) and ports (443); (3) allow-list **host names/domains** whenever possible (strongest control); (4) resolve DNS and reject non-public IPs — loopback, private, link-local, multicast, reserved, unspecified, IPv4-mapped IPv6, `100.64/10` CGNAT, metadata IPs (`ipaddress` module: `ip.is_global` is the key check); (5) connect to the **resolved IP** you validated (avoid re-resolution), keeping `Host`/SNI correct.
- **Bypass tricks to understand**: decimal/octal/hex IPs (`2130706433`, `0177.0.0.1`, `0x7f.1`), IPv6 forms, DNS names resolving to private IPs (`localtest.me`, attacker-controlled DNS), **DNS rebinding** (validate-then-fetch race with short TTL), redirects to internal addresses, URL parser differentials (`http://evil.com#@internal/`), userinfo tricks, Unicode/IDNA homoglyphs, `file://`, `gopher://`, `ftp://`, `dict://` schemes, HTTP request smuggling via CRLF in URLs.
- Redirect handling: disable automatic redirects or re-validate every hop with the same checks; cap hops.
- Response handling: stream with a maximum size; restrict content types; don't reflect raw responses/errors back to users (blind vs full-read SSRF); decompress with limits (Module 1.14 lesson 07).
- Network-level controls: egress firewall/proxy allow-lists, no direct internet from workers, dedicated egress proxy (e.g. Smokescreen) with allow-lists and logging, **IMDSv2** with hop limit 1 and disabling IMDS where unneeded, workload identity with minimal IAM, separate network segments, Kubernetes NetworkPolicies, block metadata endpoints for pods.
- Webhooks you *send*: validate customer-provided webhook URLs the same way, sign payloads (HMAC), retry policies with backoff (Stage 7).
- Webhooks you *receive*: verify signatures (Module 1.13 lesson 06), timestamps (replay), IP allow-lists as extra layer, small bodies, idempotency keys.

```python
import ipaddress, socket
from urllib.parse import urlparse

def resolve_public(host: str) -> list[str]:
    infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    ips = {i[4][0] for i in infos}
    for ip in ips:
        if not ipaddress.ip_address(ip).is_global:
            raise PermissionError(f"{host} resolves to non-public address {ip}")
    return sorted(ips)

def validate_url(url: str, allowed_hosts: set[str]) -> str:
    u = urlparse(url)
    if u.scheme != "https" or u.username or u.password:
        raise ValueError("https URLs without credentials only")
    if u.hostname not in allowed_hosts:
        raise PermissionError("host not allow-listed")
    resolve_public(u.hostname)
    return url
```

### Advanced — what to learn

- **Closing the DNS-rebinding gap**: connect by validated IP with a custom transport/`httpx` `Transport`/`urllib3` connection override or an `ssl` wrapper that sets SNI/Host; or route all fetches through an egress proxy that enforces policy at connect time; test with a rebinding DNS fixture (two-answer sequence).
- Libraries & behaviours: `requests`/`httpx`/`aiohttp` redirect and proxy environment behaviour (`HTTP_PROXY`, `NO_PROXY`, `trust_env`) — attacker-influenced env vars or `.netrc` credentials sent cross-host; `Authorization` header stripping on cross-origin redirects; cookie jars; `urllib` supporting `file:` URLs by default (`urlopen` danger).
- SSRF variants: via PDF/HTML renderers (`wkhtmltopdf`, headless Chrome), image/SVG processors (`ImageMagick` delegates), XML parsers (XXE → SSRF), `git clone` of user URLs, package installers (`pip install <url>`), Jupyter/`nbconvert` executing remote content, webhook testers, OAuth/OIDC discovery URLs, link-unfurling bots, **LLM agent browsing/tool-calling tools**, RAG ingestion crawlers (treat fetched content as untrusted data *and* the fetch destination as untrusted).
- Cloud-specific SSRF kill-chains: SSRF → IMDS credentials → S3/KMS access → data exfiltration; mitigations (IMDSv2, least-privilege roles, VPC endpoints & bucket policies with `aws:SourceVpce`, scoped credentials, GuardDuty/CloudTrail detections for metadata credential use from unusual IPs) — Stage 2 AWS modules.
- Safe crawling for AI ingestion: robots/allow-lists, per-domain rate limits, size/time budgets, content-type allow-list, sandboxed rendering, strip active content, provenance metadata, and **prompt-injection awareness** in fetched text (Stage 12).
- Building a reusable `safe_http` module: policy object (allowed schemes/hosts/ports, max bytes, timeouts, redirect policy, DNS pinning), typed errors (Module 1.20 lesson 08), structured audit logs (destination, resolved IP, bytes, status), metrics; contract tests with a local fake server and malicious URL table; fuzz the URL validator.
- Test corpus: 100+ SSRF payload URLs (IP encodings, redirects, mixed-case schemes, backslashes, tabs/newlines, IDN) — all must be rejected or safely handled; golden tests prevent regressions when libraries change.
- Alternatives that avoid the problem: let the *client* fetch (pre-signed URLs, browser-side), or accept uploads instead of URLs; queue + isolated fetcher service with no credentials and no internal network access.
- Exercise: implement `SafeFetcher` with host allow-list + DNS/IP validation + pinned connect + redirect re-validation + size/time limits; demonstrate (locally) that a naïve fetcher can reach a fake "metadata" service on `127.0.0.1:8000` while yours cannot; add DNS-rebinding and redirect tests; write the network-level control checklist for deploying it.

### Common mistakes

- Validating only the URL string (not the resolved IP).
- Following redirects blindly.
- Treating SSRF as "only an internet-facing app problem".

### Self-check

1. Why is checking the hostname string against a deny-list insufficient?
2. Explain DNS rebinding and one fix.
3. Which cloud-level controls would limit the blast radius if your validator has a bug?

---

## Lesson 07 — `07-static-analysis-with-bandit-and-pip-audit.md`

**Why it matters.** Humans miss things; automated checks catch whole classes
of mistakes cheaply and continuously. Static analysis (SAST), dependency
auditing (SCA), secret scanning and policy-as-code form the baseline
"security gate" for every repository.

### Basic — what to learn

- **Bandit**: Python SAST focusing on common issues (assert use, hard-coded passwords, `subprocess` with `shell=True`, `pickle`, weak hashes, `yaml.load`, `requests` without timeout/verify=False, `eval`/`exec`, insecure temp files, binding to `0.0.0.0`); run `bandit -r src -ll`; test IDs (B101…B703), severity/confidence, `# nosec` with justification (use sparingly).
- **Ruff `S` rules** (flake8-bandit port) — fast, in your existing lint run; `select = ["S"]`, per-file ignores for tests (`S101` assert).
- **pip-audit**: scan installed environment or requirements/lock for known vulnerabilities (PyPI Advisory DB/OSV); `pip-audit -r requirements.txt`, `uv export --no-dev | pip-audit -r /dev/stdin`, `--fix` suggestions, output formats (JSON, CycloneDX).
- Secret scanning basics: `detect-secrets scan`, `gitleaks detect`.

```bash
uv run bandit -r src -ll -f json -o bandit.json
uv run ruff check --select S src tests
uvx pip-audit --strict
uvx detect-secrets scan --baseline .secrets.baseline
```

### Intermediate — what to learn

- Triage workflow: severity × confidence × exploitability × reachability; false positives vs true positives; fix > suppress; document suppressions (`# nosec B602 - fixed argv list, no user input`) and review them in code review; baseline files for legacy code (fail only on new issues).
- Pre-commit and CI integration: `pre-commit` hooks (ruff, bandit, detect-secrets/gitleaks, `check-added-large-files`, `detect-private-key`), CI jobs on PRs and nightly schedules, required status checks, SARIF upload to GitHub code scanning, annotations.
- **Dependency security practices**: pin with hashes (`uv lock`, `pip-compile --generate-hashes`), minimal dependencies, prefer well-maintained packages, review new dependencies (maintainers, release history, popularity, licences, typosquat checks), automated update PRs (Dependabot/Renovate) with tests and **minimum release age** to avoid freshly-compromised releases, vulnerability alerts, `pip-audit` in CI with allow-lists that expire.
- Other tools: **Semgrep** (custom rules in YAML; community rulesets for Python/Django/Flask/FastAPI), **CodeQL** (GitHub), **Safety**, **OSV-Scanner**, **Trivy/Grype** (containers & filesystems), **Snyk** (commercial), **mypy/pyright** (type safety reduces classes of bugs), **`pyupgrade`/`ruff UP`** (remove insecure/legacy patterns), **`vulture`** (dead code), `deptry` (unused/missing deps).
- Understanding limits: static analysis finds patterns, not logic flaws (authz bugs, business-logic abuse); data-flow/taint analysis is approximate; dynamic issues (SSRF DNS rebinding) need tests; scanning is necessary not sufficient.
- Writing a **security checklist for code review** (input boundaries, authz checks, secrets, subprocess/file/network use, deserialisation, logging, dependencies, error handling, tests).

### Advanced — what to learn

- Writing **custom rules**: Semgrep rules for your org's patterns (e.g. "all HTTP calls must go through `safe_http`", "no `requests.get` without timeout", "no direct `boto3.client` outside infra module", "no `pickle.load*`"), Ruff plugin alternatives, AST-based checks (Module 1.12 lesson 08) wired into CI; test rules with positive/negative fixtures.
- Taint tracking concepts (sources → sanitizers → sinks) and using them to design secure architecture (centralise sinks: DB access, HTTP, file ops, subprocess), so a few audited wrappers replace thousands of call-site checks.
- Handling CVEs in practice: triage via reachability (is the vulnerable function used?), exploitability (EPSS/KEV), mitigations (config flags, input filters), version bumps with compatibility tests (Module 1.15 lesson 10), temporary risk acceptance with expiry and owner, VEX statements (Module 1.18 lesson 10).
- Policy-as-code and gates: fail builds on new high/critical findings; SLAs for fixing (critical 7 days, high 30 days); dashboards of open findings; exception registry; metrics (mean time to remediate, findings per KLOC, dependency age).
- **Supply-chain controls** in CI: build from locked dependencies, verify hashes/provenance, isolated build jobs, SBOM generation, signed artifacts, artifact attestation checks at deploy; guard against dependency confusion (Module 1.18 lesson 09), typosquatting, malicious post-install scripts (sdists run code!) → `--only-binary :all:` where feasible, review `setup.py`/build backends of unknown sdists, use private mirrors with allow-lists.
- **Dynamic and runtime testing**: fuzzing (Module 1.16 lesson 09), property-based tests for validators, DAST (OWASP ZAP) against staging APIs, dependency runtime monitoring, audit hooks (Module 1.19 lesson 08), container scanning at build and runtime, secret scanning in container layers.
- Security regression tests: every fixed vulnerability gets a test with the exploit payload; run the payload corpus in CI; track CWE IDs in commit messages.
- AI/ML pipeline scanning: scan notebooks (`nbqa bandit`, secrets in outputs), model artifacts (ModelScan/picklescan), prompt templates for secrets, dataset manifests for PII, licence checks on models/datasets; policies for external model downloads (hash-pinned, internal mirror).
- Measuring effectiveness: seed known bugs in `vulnpy` and measure which tools catch them (detection matrix); tune rule sets; avoid alert fatigue by prioritising.
- Exercise: add a full security gate to the `vulnpy` repo: pre-commit (ruff `S`, detect-secrets), CI (bandit with SARIF, pip-audit, gitleaks, Semgrep custom rule), Dependabot/Renovate config with release-age delay, a baseline file for legacy findings, and a `SECURITY.md` describing reporting and SLAs; show the pipeline failing on a new vulnerability and passing after the fix.

### Common mistakes

- Blanket `# nosec` without justification.
- Ignoring `pip-audit` results because "dev dependency".
- Running scans but not enforcing or triaging.

### Self-check

1. Which classes of vulnerability can't Bandit find and what covers them?
2. How do you handle a CVE in a transitive dependency with no fixed release?
3. Write a Semgrep rule that forbids `requests.get(...)` without `timeout=` and test it with fixtures.

---

## Lesson 08 — `08-threat-modelling-small-python-services.md`

**Why it matters.** Tools find known patterns; threat modelling finds the
*design* flaws no scanner can — missing authorisation, trust placed in the
wrong component, secrets with excessive reach, data flows nobody reviewed. A
30-minute structured session on a small service catches issues that would
take weeks to fix later.

### Basic — what to learn

- Four questions (Shostack): **What are we working on? What can go wrong? What are we going to do about it? Did we do a good job?**
- Draw a **data-flow diagram (DFD)**: external entities, processes, data stores, data flows, **trust boundaries** (internet ↔ app, app ↔ DB, worker ↔ cloud API, CI ↔ production, laptop ↔ repo).
- Inventory **assets** (data, credentials, compute, reputation), **entry points** (HTTP routes, CLI args, queues, files, webhooks, env vars, dependencies, admin interfaces), and **actors** (anonymous user, authenticated user, admin, insider, compromised dependency, malicious file, other tenant).
- **STRIDE** per element: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
- Record findings as: threat → impact → likelihood → mitigation → owner → status.

```text
[User] --HTTPS--> (API service) --SQL--> [(Postgres)]
                       |  \--HTTP--> (LLM provider)    <- trust boundary: external
                       \--S3--> [(Object store)]
```

### Intermediate — what to learn

- Applying STRIDE to a small Python service (e.g. an upload-and-summarise API): spoofing (API keys, JWT validation), tampering (file contents, request bodies, config), repudiation (audit logs), information disclosure (error messages, logs with PII, cross-tenant access, prompt/response storage), DoS (large files, regex, zip bombs, unbounded queues, expensive LLM calls → cost abuse), elevation (SSRF to metadata, deserialisation RCE, path traversal, overbroad IAM roles).
- Other frameworks: **PASTA**, **LINDDUN** (privacy), **attack trees**, **kill chains**, **OWASP Top 10 (web, API, LLM applications)**, **MITRE ATT&CK / ATLAS** (AI systems), **CWE Top 25**; use them as checklists, not as substitutes for thinking.
- **Mitigation strategies**: eliminate (remove the feature/data), reduce (validate, limit, sandbox, least privilege), transfer (use a managed service, insurance), accept (documented, time-boxed). Prefer mitigations that remove entire classes (use ORMs with parameters, not input filters).
- Data classification and handling: public/internal/confidential/restricted; retention, encryption, masking, access logging; PII minimisation (don't collect it; don't send it to LLM providers unless approved).
- Abuse cases and misuse stories alongside user stories: "As an attacker I upload a zip bomb to exhaust disk", "As a tenant I guess another tenant's report ID".
- Authentication/authorisation review: every endpoint enforces authN + object-level authZ (BOLA/IDOR: user A fetching user B's `/reports/123`), function-level authZ, token scopes, rate limits (links to Stage 7 API security).
- Output: a one-to-two-page threat model document stored in the repo (`docs/threat-model.md`) with diagram, assumptions, top threats and mitigations, and tickets for gaps; review when architecture changes.

### Advanced — what to learn

- **Threat modelling as code/process**: tools (OWASP Threat Dragon, `pytm` Python threat-modelling library, Microsoft TMT, IriusRisk), generating DFDs and threat lists from code descriptions (`pytm`), keeping models versioned and reviewed in PRs, threat-model triggers (new data class, new external integration, new privilege, new trust boundary), security champions, lightweight "10-minute" modelling for every design doc/ADR.
- Risk quantification and prioritisation: DREAD/CVSS/EPSS, business impact, likelihood, exploit complexity; risk register; defining acceptance criteria and **security requirements** (testable statements: "all outbound HTTP uses `safe_http`", "uploads limited to 20 MB and scanned", "no secret appears in logs") tied to automated checks.
- Architecture-level mitigations for data/AI systems: segregate ingestion workers (no credentials, no internal network), least-privilege roles per pipeline, per-tenant isolation (separate prefixes/keys/DB schemas/row-level security), signing and verification of artifacts, immutable audit logs, egress controls, secrets brokers, human-approval gates for risky agent actions, budget limits to prevent denial-of-wallet.
- LLM-application specifics (preview of the AI safety/security stage): prompt injection (direct/indirect), tool abuse, data exfiltration via model output/markdown images/links, insecure output handling, excessive agency, training-data and model supply chain, sensitive-information disclosure; add the LLM provider and tools as separate trust zones in the DFD.
- Validation of the model: tabletop exercises, red-team/abuse-case workshops, purple teaming, penetration tests, bug bounty/vulnerability disclosure policy (`SECURITY.md`, `security.txt`), chaos/fault-injection of security controls (revoked key, expired cert, blocked egress), verifying detection (alerts fire on simulated attacks).
- Security operations hooks: logging for detection (authN failures, privilege changes, unusual volumes, denied egress), alert routing, incident response plan (roles, severity levels, communication, evidence, containment, recovery, lessons learned), backup/restore and ransomware resilience, credential-rotation drills.
- Governance & compliance mapping: SOC 2, ISO 27001, GDPR/CCPA data-subject rights, HIPAA (awareness), EU AI Act obligations for AI systems; how a threat model supports audits; data-processing agreements for third-party LLMs.
- Common Python-service weak spots checklist: debug mode in production (Flask/Django `DEBUG=True`, Werkzeug console), default/weak secrets, permissive CORS, unauthenticated admin/health/metrics endpoints, verbose errors, `0.0.0.0` bindings, missing request limits, outdated base images, root containers, unpinned dependencies, secrets in images, writable code directories, shared temp dirs, missing TLS, `eval`-like features, unbounded caches (memory DoS).
- Capstone exercise: threat-model the **`vulnpy` upload-and-summarise service** end to end: (1) draw the DFD with trust boundaries; (2) list at least 20 threats using STRIDE + LLM-specific items; (3) rate and prioritise; (4) map each to a fix or accepted risk; (5) implement the top five mitigations (e.g. `safe_storage`, `safe_http`, parameterised queries, secret redaction, rate/size limits); (6) add automated security requirements as tests/CI rules; (7) write the incident response one-pager and `SECURITY.md`; (8) present the model to a peer (or record it) and revise.

### Common mistakes

- Treating threat modelling as a one-time document.
- Only listing technical vulnerabilities, ignoring abuse of legitimate features and business logic.
- Mitigations without owners, tests or follow-up.

### Self-check

1. Identify the trust boundaries in a service that ingests user URLs, stores files and calls an LLM provider.
2. Give three BOLA/IDOR examples in a reporting API and how to prevent each.
3. Convert five findings from your threat model into automated tests or CI rules.

---

## 4. Practice questions (`practice-questions.md`)

About **35 questions**:

| Phase | Question types |
| --- | --- |
| A | Spot-the-injection snippets; choose safe formats; design validators with allow-lists |
| B | Path containment puzzles; subprocess/argument-injection fixes; secrets and crypto code review; SSRF validator design |
| C | Triage Bandit/pip-audit output; write a Semgrep rule; STRIDE a described service; prioritise risks |

Include 8 **"find the vulnerability"** code-review items (SQL f-string, `yaml.load`, `os.path.join` with user path, `shell=True`, `verify=False`, `random` token, `startswith` path check, redirect-following fetcher) and 4 **incident-response** scenarios (leaked key, malicious pickle, SSRF to metadata, compromised dependency).

---

## 5. Module mini-project

**Harden `vulnpy`** (a deliberately vulnerable ~300-line service you build or are given) and publish a security write-up:

1. Inventory: DFD, assets, trust boundaries (`docs/threat-model.md`).
2. Discover & exploit **locally** at least eight issues (SQL injection, path traversal in upload/download, unsafe `yaml.load`/pickle cache, command injection in thumbnailing, SSRF in URL fetch, hard-coded secret + leaked in git history, `verify=False`, weak password hashing, verbose errors, log forging).
3. Fix each issue using the safe patterns from this module (`safe_storage`, `safe_http`, parameterised queries, `safe_load`, argv-only subprocess in a no-network sandbox, Argon2id, secrets from env with redaction).
4. Add a regression test per issue using the exploit payload; add fuzz/property tests for validators and path containment.
5. CI security gate: ruff `S`, Bandit (SARIF), `pip-audit`, `gitleaks`/`detect-secrets`, Semgrep custom rule, dependency update bot with release-age delay; baseline for legacy findings.
6. `SECURITY.md` (reporting, SLAs), an incident-response runbook (leaked key, suspected RCE), and a key-rotation procedure.
7. Final report `HARDENING_REPORT.md`: before/after findings table (CWE IDs), residual risks, what each control prevents, and what is still out of scope (e.g. network/IAM controls from Stage 2).

Acceptance: all exploits fail after fixes (proved by tests), CI gate blocks reintroduction, no secrets in history/outputs, threat model reviewed and updated, report understandable to a non-expert manager.

---

## 6. Completion checklist

- [ ] I can identify trust boundaries and validate input with allow-lists at the edge.
- [ ] I prevent SQL, command, template, log, CSV and path injection using safe APIs.
- [ ] I avoid unsafe deserialisation and choose safe data/model formats and verification.
- [ ] I handle files, uploads and archives safely, with containment, atomic writes and permissions.
- [ ] I run subprocesses without shell or argument injection, and sandbox what remains.
- [ ] I manage secrets properly, use vetted cryptography and respond correctly to leaks.
- [ ] I write HTTP clients with TLS, timeouts, size limits and SSRF defences.
- [ ] I run SAST, SCA, secret scanning and custom rules in CI and triage findings sensibly.
- [ ] I can threat-model a small service with STRIDE and turn findings into tests and controls.
- [ ] I completed the `vulnpy` hardening mini-project and report.

**Next:** Module 1.23 — Code Reading, Refactoring and Code Review.
