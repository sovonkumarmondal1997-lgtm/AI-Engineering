# Module 1.22 — Secure Python Coding: Practice Questions

> **Source alignment:** This question bank follows `roadmap-Secure-Python-Coding.md`, including its eight lessons, Phase A/B/C progression, `vulnpy` exercises, mini-project, and completion checklist. Scenarios are hypothetical and intended for code you own or an isolated local lab. No scanner output or real vulnerability report is represented as real.

## How to use this bank

- Answer the **questions first**; the answer key is in Part II.
- For code-writing questions, state assumptions, provide runnable Python where requested, and test both legitimate and hostile inputs.
- For risk questions, explain impact, likelihood assumptions, reachable attack path, mitigation, owner, verification, and residual risk. Ratings are prioritisation aids, not objective measurements.
- Unless stated otherwise, use Python 3.11+ and established libraries. Adapt platform-specific file/process/network controls to the deployment OS.
- Never test against systems you do not own or have explicit permission to assess.

## Coverage map

| Phase | Main questions | Focus |
|---|---:|---|
| A — Mindset and input (beginner) | A01–A08 (8) | Trust boundaries, injection, validation, serialization, SQL, encoding, canonicalization |
| B — Files, processes, secrets, network (intermediate) | B01–B12 (12) | Paths, symlinks, archives, subprocesses, crypto, SSRF, deserialization, limits, tests |
| C — Process and assurance (advanced) | C01–C15 (15) | Scanner triage, Semgrep, STRIDE, prioritization, CI, exceptions, supply chain, residual risk |
| Special review section | REV01–REV08 (8) | The eight required code-review patterns |
| Incident response | IR01–IR04 (4) | Secret leak, malicious artifact, metadata SSRF, compromised dependency |

This contains **35 main questions**, plus **8 code-review items** and **4 incident-response scenarios**.

**Counting rule:** Count each uniquely identified top-level item (`Axx`, `Bxx`, `Cxx`, `REVxx`, or `IRxx`) once. Nested requirements, examples, requested tests, and subparts within a prompt are rubric elements—not extra questions. The bank therefore has **47 top-level assessment items**: 35 main questions, 8 required code-review items, and 4 incident-response scenarios.

---

# Part I — Questions

## Phase A — Mindset and input (beginner)

### A01 — Identify trust boundaries
- **Phase / difficulty:** A / Beginner
- **Prompt:** A Python reporting API accepts JSON from browsers, reads rows from PostgreSQL, downloads a CSV from an external provider, and sends a summary to an LLM provider. List at least six inputs or components that must not automatically be trusted. Identify three trust boundaries and explain why data retrieved from the database is not necessarily trusted.
- **Expected response format:** Short table: source/component, trust assumption, boundary, validation/control.
- **Skill assessed:** Trust-boundary reasoning and input provenance.

### A02 — Separate data from SQL instructions
- **Phase / difficulty:** A / Beginner
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  def find_user(conn, name: str):
      return conn.execute(
          f"SELECT id, name FROM users WHERE name = '{name}'"
      ).fetchall()
  ```
  Rewrite it using parameterized SQL for SQLite. If the caller can choose a sort column, explain how to handle that separate requirement.
- **Expected response format:** Corrected code and two regression tests.
- **Skill assessed:** SQL injection prevention and identifier allow-listing.

### A03 — Choose a serialization format
- **Phase / difficulty:** A / Beginner
- **Prompt:** A service receives a user-uploaded configuration document, and a separate ML worker loads numeric model weights from an external registry. Choose a suitable format and loading policy for each. Explain why a file extension, checksum alone, or “internal cache” label does not make an unsafe pickle trustworthy.
- **Expected response format:** Choose and justify one format/policy per use case; include one post-parse validation step.
- **Skill assessed:** Unsafe deserialization and artifact trust.

### A04 — Design an allow-list validator
- **Phase / difficulty:** A / Beginner
- **Prompt:** Design a validator for a report request with `report_name`, `limit`, and `format`. Requirements: name is 1–48 ASCII letters/digits/underscore/hyphen; `limit` is an actual integer from 1 to 100 (a Boolean must not pass as an integer); format is `csv` or `json`. Write a function or precise pseudocode and list edge cases.
- **Expected response format:** Code/pseudocode plus at least six tests, including invalid type, range, and length.
- **Skill assessed:** Typed validation, positive policy, boundary testing.

### A05 — Context-aware output encoding
- **Phase / difficulty:** A / Beginner
- **Prompt:** Explain why one generic “sanitize” function cannot safely prepare the same untrusted string for SQL, HTML body text, a URL query parameter, a shell command, a log event, and a CSV cell that may be opened in a spreadsheet. Name the safer mechanism for at least five sinks. For CSV, distinguish correct CSV quoting from protection against spreadsheet formula interpretation.
- **Expected response format:** Comparison table: sink, safe API/design, common failure.
- **Skill assessed:** Contextual encoding, CSV formula-injection awareness, and safe sink APIs.

### A06 — Spot injection in a template and a log
- **Phase / difficulty:** A / Beginner–Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  template = "Hello " + request.args["name"]
  rendered = template_engine.from_string(template).render()
  logger.warning("login failed: " + request.args["name"])
  ```
  Identify the distinct risks. Propose safe rendering and structured logging patterns. State what additional template-engine configuration is needed when rendering ordinary user-provided values.
- **Expected response format:** Review notes and corrected pseudocode.
- **Skill assessed:** Template injection, log forging, data/instruction separation.

### A07 — Canonicalize before validating
- **Phase / difficulty:** A / Intermediate
- **Prompt:** An API accepts an identifier that is URL-decoded by a proxy and decoded again by the application. Explain how double encoding, Unicode normalization, null bytes, or parser disagreement can undermine a validator. Propose an ordered boundary-processing pipeline and state what should happen to ambiguous inputs.
- **Expected response format:** Ordered steps and two concrete regression cases.
- **Skill assessed:** Canonicalization and parser-differential reasoning.

### A08 — Bound parser and request resources
- **Phase / difficulty:** A / Intermediate
- **Prompt:** A JSON endpoint accepts nested arrays and strings. List five independent limits or checks that reduce denial-of-service and type-confusion risk. Explain why schema validation alone does not replace resource limits.
- **Expected response format:** Checklist with a reason for each control.
- **Skill assessed:** Resource-aware input validation.

## Phase B — Files, processes, secrets, and network (intermediate)

### B01 — Path containment puzzle
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A download handler stores files under `/srv/app/reports`. A user supplies a filename. Explain why `base / user_value`, `resolve()` followed by a later `open()`, and string `startswith()` are each insufficient as a complete security argument. Give a path-aware containment check and describe the remaining race.
- **Expected response format:** Code sketch, threat explanation, and stronger deployment-level option.
- **Skill assessed:** Path traversal, canonical paths, TOCTOU awareness.

### B02 — Symlink and exclusive-create design
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A multi-tenant worker writes a user-named output file into a shared writable directory. Identify risks from symlinks, hard links, races, and predictable names. Recommend a safer design using server-generated IDs, exclusive creation or directory-relative APIs where supported, restrictive permissions, and isolated directories.
- **Expected response format:** Design review with platform caveats.
- **Skill assessed:** Filesystem race mitigation and least privilege.

### B03 — Safe archive extraction
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A user uploads a ZIP or TAR archive. Specify a complete extraction policy addressing traversal, absolute paths, symlinks/hard links, device files, member count, total uncompressed bytes, per-file size, compression ratio, duplicate names, and cleanup. Explain why “remove `../`” is not sufficient.
- **Expected response format:** Numbered algorithm and at least four rejection tests.
- **Skill assessed:** Archive extraction safety and resource controls.

### B04 — Subprocess and option injection
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A thumbnail service invokes an image utility with a user-supplied filename and format. Describe how shell injection differs from option/argument injection. Provide a safe `subprocess.run` design using an argv list, fixed executable, allow-listed options, timeout, controlled environment, bounded output handling, and a temporary working directory. State when a library alternative is preferable.
- **Expected response format:** Code sketch and residual-risk explanation.
- **Skill assessed:** Process invocation and interpreter boundaries.

### B05 — Secret lifecycle and leak prevention
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A developer commits an API key, prints request headers during debugging, and passes another credential as a command-line argument. Describe the correct immediate response and three design changes that prevent recurrence. Explain the roles of secret scanning, redaction, `getpass`, environment variables, and a managed secret store.
- **Expected response format:** Ordered response plan plus prevention controls.
- **Skill assessed:** Secret handling and incident response basics.

### B06 — Select the correct cryptographic primitive
- **Phase / difficulty:** B / Intermediate
- **Prompt:** Choose an appropriate primitive for each requirement: (1) detect file changes when no secret is shared, (2) authenticate a webhook using a shared secret, (3) encrypt a report so only a service with a key can read it and detect tampering, (4) prove an artifact was signed by a particular publisher, (5) store user passwords. State one unsuitable choice for each and why.
- **Expected response format:** Mapping table with purpose, primitive, and caveat.
- **Skill assessed:** Hash/MAC/encryption/signature/password-hashing distinctions.

### B07 — Review an authenticated-encryption design
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A service uses AES-GCM to encrypt reports. Describe requirements for key generation/storage, nonce uniqueness, associated data, ciphertext/tag storage, rotation, and tamper handling. Explain why “the ciphertext decrypted in my test” is not enough evidence of a sound design.
- **Expected response format:** Review checklist and two negative tests.
- **Skill assessed:** Authenticated encryption and key lifecycle.

### B08 — Safe HTTP fetcher and SSRF
- **Phase / difficulty:** B / Intermediate–Advanced
- **Prompt:** Design a fetcher that accepts a user URL but should only retrieve documents from a small approved set of hosts. Specify scheme/host/port parsing, DNS/IP policy, timeouts, TLS verification, redirect behavior, streaming size limit, content-type policy, and safe error logging. Explain why hostname validation followed by a separate ordinary connection cannot fully prevent DNS rebinding.
- **Expected response format:** Policy checklist plus pseudocode or component diagram.
- **Skill assessed:** SSRF defense in depth and connect-time enforcement.

### B09 — Safe deserialization and artifact provenance
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A shared cache contains a `.pkl` model file whose SHA-256 hash matches a value stored beside it. Explain what the hash proves and does not prove. Propose a safer loading pipeline, and describe what to do if pickle compatibility is unavoidable.
- **Expected response format:** Threat analysis and ordered controls.
- **Skill assessed:** Deserialization risk, integrity/authenticity, provenance.

### B10 — Webhook verification and replay
- **Phase / difficulty:** B / Intermediate
- **Prompt:** A service receives webhooks signed with HMAC. Outline verification order, raw-body handling, constant-time comparison, timestamp tolerance, replay/idempotency control, and response behavior. Explain why verifying a parsed/re-serialized JSON object may fail or create ambiguity.
- **Expected response format:** Ordered pseudocode and test list.
- **Skill assessed:** MAC verification and webhook operational security.

### B11 — Build a resource-exhaustion test plan
- **Phase / difficulty:** B / Intermediate
- **Prompt:** For a service that accepts files, extracts archives, calls an external fetcher, and queues LLM summaries, list at least six quotas/time bounds and write four regression/property-test ideas. Include rejection tests and legitimate-boundary cases.
- **Expected response format:** Table: resource, limit, enforcement point, test.
- **Skill assessed:** DoS/cost-abuse prevention and test design.

### B12 — TLS and HTTP client defaults
- **Phase / difficulty:** B / Intermediate
- **Prompt:** Review an HTTP client that disables certificate verification, has no timeout, follows redirects automatically, and logs full URLs including query parameters. Give the minimum corrections and explain when certificate pinning is—and is not—a reasonable default.
- **Expected response format:** Review checklist and one safe configuration sketch.
- **Skill assessed:** TLS validation, bounded requests, leakage prevention.

## Phase C — Process and assurance (advanced)

### C01 — Triage a hypothetical Bandit result
- **Phase / difficulty:** C / Advanced
- **Prompt:** A **hypothetical** Bandit report flags a high-severity/high-confidence shell call in a code path that processes user filenames. Describe triage before deciding whether to fix, suppress, or accept risk. Include reachability, attacker control, impact, remediation, owner, and regression verification.
- **Expected response format:** Triage record with decision and rationale.
- **Skill assessed:** SAST interpretation and risk-based remediation.

### C02 — Triage a hypothetical `pip-audit` result
- **Phase / difficulty:** C / Advanced
- **Prompt:** A **hypothetical** `pip-audit` result reports a vulnerable transitive dependency with a fixed release, but the lockfile pins an older version. Describe how to verify the finding, assess exposure, update safely, test compatibility, and document any temporary exception. Explain why ignoring it because it is “transitive” or “dev-only” is insufficient.
- **Expected response format:** Remediation plan with owner, deadline, and evidence.
- **Skill assessed:** SCA triage and dependency management.

### C03 — Design a Semgrep rule
- **Phase / difficulty:** C / Advanced
- **Prompt:** Write a Semgrep rule (or clearly labelled pseudocode if exact YAML syntax is unfamiliar) that flags `requests.get(...)` calls without an explicit `timeout` argument. State one false-positive/false-negative limitation and describe positive and negative fixtures.
- **Expected response format:** Rule plus fixture plan.
- **Skill assessed:** Custom static policy and rule validation.

### C04 — STRIDE a small service
- **Phase / difficulty:** C / Advanced
- **Prompt:** Threat-model `vulnpy`: an upload API stores files in object storage, queues a summarization job, a worker fetches optional source URLs, calls an LLM provider, stores summaries in PostgreSQL, and emits logs. Identify at least one credible threat for each STRIDE category and mark trust boundaries in a textual DFD.
- **Expected response format:** DFD plus six-row STRIDE table.
- **Skill assessed:** Design-level threat modelling.

### C05 — Prioritize a risk register
- **Phase / difficulty:** C / Advanced
- **Prompt:** Rank these hypothetical findings: (a) a low-confidence lint warning in unreachable test-only code; (b) cross-tenant report access through a missing object-level authorization check; (c) an outdated package with a published fix but no demonstrated reachable vulnerable path; (d) a public URL fetcher with no egress restriction that can reach internal addresses. State assumptions behind your order and evidence that could change it.
- **Expected response format:** Ordered list with impact/likelihood/reachability, mitigation, owner, verification, residual risk.
- **Skill assessed:** Risk prioritization without false precision.

### C06 — Turn findings into testable requirements
- **Phase / difficulty:** C / Advanced
- **Prompt:** Convert these statements into testable requirements: “uploads are safe,” “logs do not leak secrets,” “fetching is restricted,” “tenants are isolated,” and “dependencies are secure.” For each, name an automated check and one limitation needing review or runtime control.
- **Expected response format:** Requirement/control/test/limitation matrix.
- **Skill assessed:** Measurable security requirements.

### C07 — Design a CI security gate
- **Phase / difficulty:** C / Advanced
- **Prompt:** Propose a PR and nightly pipeline for Ruff `S`, Bandit (including SARIF or equivalent reviewable output), `pip-audit`, Gitleaks or `detect-secrets`, and a custom Semgrep rule. State which findings block merges, how legacy baselines work, how artifacts are retained, and how failures are surfaced without exposing secrets.
- **Expected response format:** Pipeline stages and explicit gate policy.
- **Skill assessed:** DevSecOps integration and actionable feedback.

### C08 — Write a defensible exception
- **Phase / difficulty:** C / Advanced
- **Prompt:** A Bandit finding cannot be removed immediately because a vendor interface requires a constrained subprocess call. Draft the minimum exception record and, if justified, a narrow `# nosec` comment. Include rationale, scope, owner, expiry/review date, compensating controls, and test evidence. Explain when not to suppress.
- **Expected response format:** Exception record and code-comment example.
- **Skill assessed:** Suppression governance.

### C09 — Supply-chain review of a new dependency
- **Phase / difficulty:** C / Advanced
- **Prompt:** A new package would save two dozen lines of code but has a very new release, unclear maintainership, broad transitive dependencies, and an sdist build backend you have not reviewed. Recommend approve/defer/reject and list evidence needed. Include hashes/lockfile, provenance, typosquatting, release-age policy, license, and automated-update considerations.
- **Expected response format:** Decision memo with conditions and residual risks.
- **Skill assessed:** Dependency minimization and supply-chain reasoning.

### C10 — Interpret scanner blind spots
- **Phase / difficulty:** C / Advanced
- **Prompt:** A repository passes Bandit, Ruff `S`, `pip-audit`, and secret scanning. Name at least five important classes of risk these results do not prove absent, and pair each with another verification method or control.
- **Expected response format:** Gap-analysis table.
- **Skill assessed:** Assurance boundaries and layered verification.

### C11 — Define a secure artifact pipeline
- **Phase / difficulty:** C / Advanced
- **Prompt:** Design a pipeline for a model artifact from build through registry publication to production loading. Include pinned source revision, hash/signature verification, license review, format choice, scanning, isolation, admission checks, and typed IPC. Explain the limits of signing and artifact scanners.
- **Expected response format:** Ordered pipeline with trust assumptions.
- **Skill assessed:** Data/ML supply-chain security.

### C12 — Evaluate LLM/tool trust boundaries
- **Phase / difficulty:** C / Advanced
- **Prompt:** A summarization agent reads uploaded documents, can fetch URLs, and can invoke a report-export tool. Identify direct/indirect prompt-injection and data-exfiltration paths. Propose controls for tool authorization, egress, tenant context, human approval, output handling, and cost budgets.
- **Expected response format:** Attack-path table with mitigations and tests.
- **Skill assessed:** LLM boundary and excessive-agency reasoning.

### C13 — Threat-model review triggers and governance
- **Phase / difficulty:** C / Advanced
- **Prompt:** List five architecture or operational changes that should trigger threat-model review. Explain how STRIDE, PASTA, LINDDUN, attack trees, OWASP Top 10, MITRE ATT&CK/ATLAS, and CWE Top 25 should support—not replace—system-specific analysis. State one appropriate use and one limitation of a compliance framework.
- **Expected response format:** Trigger list plus concise framework comparison.
- **Skill assessed:** Sustainable threat modelling and governance.

### C14 — Incident detection and recovery exercise
- **Phase / difficulty:** C / Advanced
- **Prompt:** Design a tabletop exercise for a revoked API key, expired TLS certificate, or blocked egress policy. Define expected detection, alert routing, containment, recovery, evidence preservation, rotation, and post-incident actions. Include one test proving the alert actually fires.
- **Expected response format:** Exercise plan and pass/fail criteria.
- **Skill assessed:** Operational validation and incident readiness.

### C15 — `vulnpy` capstone acceptance plan
- **Phase / difficulty:** C / Advanced
- **Prompt:** Write an acceptance checklist for the roadmap’s full `vulnpy` mini-project. Include DFD/trust boundaries, at least eight local exploit/fix/regression cycles, fuzz/property tests, a CI gate and legacy baseline, `SECURITY.md`, incident response and key rotation, and `HARDENING_REPORT.md` with CWE IDs and residual risks. Explain how to demonstrate that a new vulnerability makes CI fail and the fix makes it pass.
- **Expected response format:** Verifiable checklist with evidence artifacts.
- **Skill assessed:** End-to-end security engineering and evidence-based completion.

## Required special section A — Find the vulnerability (code review)

For each item: identify the vulnerability and attacker-controlled value, describe impact, specify a safe design, and name a regression test. Every snippet is an **assessment snippet**, not code to deploy.

### REV01 — SQL built with an f-string
- **Phase / difficulty:** A / Beginner
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  def get_report(conn, report_id: str):
      return conn.execute(
          f"SELECT body FROM reports WHERE id = '{report_id}'"
      ).fetchone()
  ```
  Find the vulnerability and fix it. What if the caller also chooses the sort column?
- **Expected response format:** Review, corrected query, test idea.
- **Skill assessed:** SQL parameterization and identifier allow-lists.

### REV02 — Unsafe `yaml.load`
- **Phase / difficulty:** A / Beginner–Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  import yaml

  def load_config(text: str):
      return yaml.load(text, Loader=yaml.Loader)
  ```
  Explain the risk for untrusted input and propose a safer parser and post-parse validation.
- **Expected response format:** Review and corrected code/pseudocode.
- **Skill assessed:** Unsafe deserialization.

### REV03 — `os.path.join` with user path
- **Phase / difficulty:** B / Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  import os

  def uploaded_path(root, filename):
      return os.path.join(root, filename)
  ```
  Explain how an absolute path or traversal component can escape the intended root. Give a path-aware containment strategy and describe the TOCTOU limitation.
- **Expected response format:** Review plus safer storage design.
- **Skill assessed:** Path traversal and filesystem race awareness.

### REV04 — `shell=True`
- **Phase / difficulty:** B / Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  import subprocess

  def thumbnail(filename):
      subprocess.run(f"convert {filename} /tmp/out.png", shell=True)
  ```
  Identify shell injection and option injection risks. Specify a safer argv-only design, option allow-list, timeout, and sandbox controls.
- **Expected response format:** Corrected code sketch and test plan.
- **Skill assessed:** Subprocess security.

### REV05 — TLS verification disabled
- **Phase / difficulty:** B / Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  import requests

  def get_status(url):
      return requests.get(url, verify=False).text
  ```
  Explain the security failure and add TLS verification, timeouts, redirect/URL policy, and response-size controls appropriate to a trusted fixed endpoint.
- **Expected response format:** Review and safe code sketch.
- **Skill assessed:** TLS and HTTP-client safety.

### REV06 — Security token generated with `random`
- **Phase / difficulty:** B / Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  import random
  import string

  def make_token(length=24):
      return "".join(random.choice(string.ascii_letters + string.digits)
                     for _ in range(length))
  ```
  Explain why this is inappropriate for authentication tokens and replace it with a cryptographically secure approach. State how token storage/expiry should be handled.
- **Expected response format:** Corrected code and lifecycle notes.
- **Skill assessed:** Secure randomness and token lifecycle.

### REV07 — Path containment using `startswith`
- **Phase / difficulty:** B / Intermediate
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  from pathlib import Path

  root = Path("/srv/app/reports").resolve()
  candidate = (root / user_path).resolve()
  if str(candidate).startswith(str(root)):
      open(candidate, "rb").read()
  ```
  Explain the sibling-prefix problem and the remaining race. Give a correct path-aware check and state what stronger OS-level design is needed for hostile concurrent filesystems.
- **Expected response format:** Review, corrected check, residual-risk note.
- **Skill assessed:** Path containment and TOCTOU.

### REV08 — Redirect-following fetcher without revalidation
- **Phase / difficulty:** B / Intermediate–Advanced
- **Prompt:** **Assessment snippet — vulnerable:**
  ```python
  import requests

  def fetch(url):
      response = requests.get(url, timeout=10, allow_redirects=True)
      response.raise_for_status()
      return response.content
  ```
  Explain why validating only the initial URL is insufficient. Design redirect handling that revalidates every hop or disables redirects, validates destination IP at connection time, and bounds body size.
- **Expected response format:** Review and safe fetcher policy.
- **Skill assessed:** SSRF and redirect/DNS enforcement.

## Required special section B — Incident-response scenarios

### IR01 — Secret/API key committed or leaked
- **Phase / difficulty:** B–C / Advanced
- **Prompt:** A developer discovers a live provider API key in a public repository and CI logs. Give the first actions in order, including revocation/rotation, scope assessment, log and artifact checks, history cleanup, communication, and regression controls. Explain why rewriting Git history alone is not containment.
- **Expected response format:** Ordered incident runbook with owners and evidence.
- **Skill assessed:** Secret-leak containment and recovery.

### IR02 — Malicious pickle/model artifact discovered
- **Phase / difficulty:** B–C / Advanced
- **Prompt:** A model artifact from a shared cache is suspected of containing malicious pickle behavior. Describe containment, identifying consumers and provenance, safe evidence handling, rebuild/replacement, credential review, and controls for future artifact admission. Do not execute the artifact to confirm suspicion.
- **Expected response format:** Incident steps, communication points, prevention actions.
- **Skill assessed:** Artifact incident response.

### IR03 — SSRF may have reached cloud metadata
- **Phase / difficulty:** B–C / Advanced
- **Prompt:** Logs indicate a URL-fetch feature may have reached a cloud metadata endpoint. Outline safe containment and investigation without repeating the request. Include workload credential revocation/rotation where warranted, access-log review, egress policy, identity scope, evidence preservation, and validation of the fix.
- **Expected response format:** Incident-response outline with stop conditions and verification.
- **Skill assessed:** SSRF/cloud blast-radius response.

### IR04 — Dependency or release may be compromised
- **Phase / difficulty:** C / Advanced
- **Prompt:** A dependency maintainer reports a potentially compromised release. Describe how to identify affected builds and runtime deployments, preserve evidence, block/revoke the artifact, pin or roll back to a verified release, rebuild in a clean environment, rotate potentially exposed credentials, and communicate residual uncertainty.
- **Expected response format:** Ordered incident plan and recovery criteria.
- **Skill assessed:** Software supply-chain incident response.

---

# Part II — Answer key and scoring guidance

Use this after completing Part I. These are model answers, not the only acceptable wording. Award credit for correct reasoning, stated assumptions, effective controls, and a way to verify them. Do not award full credit for naming a tool without explaining what it does and does not establish.

## Phase A — Mindset and input

### A01 — Identify trust boundaries
- **Correct answer / rubric:** Treat browser JSON, uploaded CSV contents, external-provider responses, LLM output, queue messages, and data written by another tenant or earlier process as untrusted until validated for the intended use. Boundaries include client-to-API, API-to-database/object store, worker-to-external fetcher, and application-to-LLM. Database origin does not prove safety: values may have entered through an earlier vulnerable path, another tenant, an import, or a compromised account.
- **Reasoning:** Trust follows provenance and use, not merely storage location. Validate at the receiving boundary and authorize each operation.
- **Common wrong answer:** “The database is trusted, so its contents need no validation.”
- **Safe principle:** Treat data as untrusted at every boundary; use context-specific validation and authorization.

### A02 — Separate data from SQL instructions
- **Correct answer / rubric:** Use `conn.execute("SELECT id, name FROM users WHERE name = ?", (name,)).fetchall()` for SQLite. If the sort column is variable, map a small set of accepted names to fixed SQL identifiers, then interpolate only the selected constant; values remain parameters. Test a normal name and a quote/injection-shaped value and assert it is treated as data.
- **Reasoning:** SQL parameters bind values, not identifiers or keywords.
- **Common wrong answer:** Escape single quotes manually or parameterize the column name.
- **Safe principle:** Parameterize values and allow-list SQL structure.

### A03 — Choose a serialization format
- **Correct answer / rubric:** Use a constrained data-only format such as JSON or TOML for configuration, then validate the parsed schema and ranges. For numeric model weights, prefer a non-executable, documented tensor format such as safetensors when compatible, or another format with a deliberately restricted loader. Verify artifacts against a trusted manifest/signature and validate shapes, dtypes, sizes, and expected model identity. A sidecar hash detects mismatch only if the expected hash is trusted; it does not establish publisher authenticity by itself.
- **Reasoning:** Pickle-family formats can invoke code during loading. Extensions and cache labels are metadata, not trust guarantees.
- **Common wrong answer:** Accept `.pkl` if it is in an internal cache or has a matching hash stored next to it.
- **Safe principle:** Prefer data-only formats, authenticated provenance, and isolated loading.

### A04 — Design an allow-list validator
- **Correct answer / rubric:** Require `isinstance(report_name, str)` and a full-match against `[A-Za-z0-9_-]{1,48}`; reject Boolean `limit` explicitly because `bool` subclasses `int` (`type(limit) is int` is suitable for this exact contract); require `1 <= limit <= 100`; require `format in {"csv", "json"}` and a string type. Return a typed validated object or a clear validation error. Tests should include valid boundaries 1/100, 0/101, `True`, `1.0`, empty/49-character names, whitespace, Unicode characters, unknown formats, and wrong types.
- **Reasoning:** A positive allow-list and explicit type/range limits avoid implicit coercion and surprising edge cases.
- **Common wrong answer:** Convert everything with `str()`/`int()` and silently coerce malformed inputs.
- **Safe principle:** Validate types and constraints at the boundary; reject ambiguous inputs.

### A05 — Context-aware output encoding
- **Correct answer / rubric:** SQL: parameterized query. HTML text: framework auto-escaping or context-appropriate HTML escaping. URL query: URL builder/parameter encoder. Shell: avoid a shell and pass an argv list. Logs: structured fields plus CR/LF handling and secret redaction. CSV: use a real CSV writer for correct field quoting, but do not mistake quoting for spreadsheet-formula protection; if files will be opened in spreadsheet software, apply a documented policy for cells beginning with formula-triggering characters (for example `=`, `+`, `-`, or `@`, including relevant leading whitespace/control characters), test it against supported spreadsheet clients, and preserve the original data separately if altering its representation is unacceptable. No single transformation is correct for every output context.
- **Reasoning:** Escaping for one parser does not neutralize another parser's metacharacters; syntactically valid CSV can still contain a cell interpreted as a formula by spreadsheet software.
- **Common wrong answer:** Use one `sanitize()` function for every output sink, or assume CSV quoting alone prevents formula execution.
- **Safe principle:** Prefer safe APIs that separate data from instructions; apply sink-specific encoding and an explicit spreadsheet-consumer policy where needed.

### A06 — Spot injection in a template and a log
- **Correct answer / rubric:** Concatenating untrusted data into template source can turn data into template instructions (server-side template injection); string concatenation in logs can permit forged lines or confusing records. Keep a trusted template fixed and pass `name` as a variable, e.g. render `"Hello {{ name }}"` with autoescaping enabled. Use structured logging such as `logger.warning("login failed", extra={"username": safe_log_value(name)})`; redact secrets and neutralize CR/LF if the log format is line-oriented. Never compile user text as template source.
- **Reasoning:** Template source and template data are different trust domains; logs are security-sensitive output too.
- **Common wrong answer:** HTML-escape the whole template after concatenation or remove only newline characters without controlling the template boundary.
- **Safe principle:** Keep executable templates trusted, escape by output context, and log structured/redacted data.

### A07 — Canonicalize before validating
- **Correct answer / rubric:** Define one decoding/normalization boundary; reject malformed or multiply encoded forms when the protocol does not require them; validate the canonical representation; do not decode again downstream. For identifiers, use a narrow accepted character set and avoid accepting path syntax if not needed. Regression examples include `%252e%252e%252f` where repeated decoding changes meaning and a Unicode-normalization pair that compares equal after normalization. Null bytes and parser disagreement should be rejected if not valid for the field.
- **Reasoning:** Different layers can validate different representations of the same input.
- **Common wrong answer:** Repeatedly decode until the string “looks clean.”
- **Safe principle:** Normalize once at a clearly owned boundary, validate after canonicalization, and reject ambiguous encodings.

### A08 — Bound parser and request resources
- **Correct answer / rubric:** Enforce request-body byte limits before parsing; maximum nesting/depth where supported; maximum string/array/object lengths and item counts; schema/type validation; request deadlines/rate limits; and bounded downstream work. Schema validation cannot stop a huge body, deeply nested parser workload, or expensive but schema-valid request on its own.
- **Reasoning:** Validity and resource affordability are separate properties.
- **Common wrong answer:** A JSON schema makes arbitrarily large valid input safe.
- **Safe principle:** Bound bytes, structure, time, concurrency, and downstream cost independently.

## Phase B — Files, processes, secrets, and network

### B01 — Path containment puzzle
- **Correct answer / rubric:** Absolute child paths can override the root during joining; traversal and symlinks can resolve outside it; string prefixes confuse `/reports-old` with `/reports`. For a basic check, resolve both paths and use `candidate.is_relative_to(root)` on supported Python versions (or a parent comparison fallback), catching resolution errors. Do not treat this check followed by a separate `open()` as race-free: directory entries can change between check and use. For hostile writable trees, use private directories and OS-level directory-relative/open-no-follow mechanisms or an isolated storage service.
- **Reasoning:** Canonical path checks help with containment but do not make the filesystem immutable.
- **Common wrong answer:** `str(candidate).startswith(str(root))` or “`resolve()` prevents all races.”
- **Safe principle:** Use path-aware checks plus race-resistant filesystem operations and least-privilege storage.

### B02 — Symlink and exclusive-create design
- **Correct answer / rubric:** Use server-generated opaque names, private per-tenant/job directories, restrictive permissions, exclusive creation (`O_CREAT | O_EXCL` where applicable), and no-follow/directory-relative APIs where supported. Avoid following attacker-controlled links. Hard-link semantics and available flags differ by OS/filesystem; do not claim one portable flag solves all cases. Keep shared directories non-writable by mutually untrusted principals and clean up safely.
- **Reasoning:** Predictable names and shared writable namespaces enable races and redirection of writes.
- **Common wrong answer:** Check `exists()` and then open the path, assuming that two operations are atomic together.
- **Safe principle:** Minimize shared writable namespaces and make creation atomic where the platform allows.

### B03 — Safe archive extraction
- **Correct answer / rubric:** Extract into a new private empty directory; normalize and validate every member path before writing; reject absolute paths, drive/UNC paths, traversal, links, device/special files, and unsafe duplicate-name collisions; enforce member count, per-file and aggregate uncompressed bytes, compression ratio, and processing time; avoid overwriting existing files; clean up on any failure. Use supported safe tar filters as an additional layer, not as a replacement for explicit resource limits and policy. Test traversal, absolute paths, link entries, duplicate names, excessive count/size/ratio, and an ordinary valid archive.
- **Reasoning:** Archive metadata controls both destination paths and resource consumption.
- **Common wrong answer:** Strip `../` and extract the rest, or rely on a single library default.
- **Safe principle:** Validate every entry and bound total work before trusting archive contents.

### B04 — Subprocess and option injection
- **Correct answer / rubric:** Use a fixed executable and argv list with `shell=False`; accept only enumerated formats/options; place `--` before filenames only when the target utility documents it; still validate arguments because the target program may interpret options or special protocols. Add a timeout, controlled environment/PATH, known working directory, restrictive permissions, bounded stdout/stderr, and a low-privilege no-network sandbox if a subprocess remains. Prefer Pillow or another library when it can safely perform the operation.
- **Reasoning:** Avoiding a shell prevents shell parsing but does not make arbitrary arguments safe for the child executable.
- **Common wrong answer:** `shlex.quote()` around the filename while keeping `shell=True`, or assuming `shell=False` solves option injection.
- **Safe principle:** Eliminate interpreter layers; constrain child arguments and isolate residual parser risk.

### B05 — Secret lifecycle and leak prevention
- **Correct answer / rubric:** Revoke/rotate the exposed live key first; identify scope and usage, review logs/artifacts and access records, then clean repository history and replicas, notify the responsible owner, and add prevention tests/scanning. Use secret managers/workload identity where available; environment variables can be a deployment bridge but remain visible to processes and diagnostics in some environments. `getpass` prevents echo for interactive input but is not a production secret store. Redact headers/tokens and avoid command-line arguments because process listings/history can expose them.
- **Reasoning:** Removing a secret from the current file does not invalidate copies already obtained.
- **Common wrong answer:** Rewrite Git history first and leave the credential active until cleanup finishes.
- **Safe principle:** Revoke first, investigate scope, clean up, and prevent recurrence.

### B06 — Select the correct cryptographic primitive
- **Correct answer / rubric:** (1) Hash such as SHA-256 for change detection only when the expected digest is obtained through a trusted channel; (2) HMAC-SHA-256 with shared secret for webhook authenticity/integrity; (3) authenticated encryption such as AES-GCM or ChaCha20-Poly1305; (4) digital signature such as Ed25519 with trusted public-key distribution; (5) password hashing with Argon2id (or appropriately configured scrypt/bcrypt where constraints require). A plain hash does not authenticate an attacker-controlled file, encryption alone may not detect tampering, and general-purpose hashes are too fast for password storage.
- **Reasoning:** The primitives provide different security properties and key assumptions.
- **Common wrong answer:** “Encrypt passwords with AES” or “a SHA hash proves who published the artifact.”
- **Safe principle:** Choose a vetted primitive based on the exact property and threat model.

### B07 — Review an authenticated-encryption design
- **Correct answer / rubric:** Generate keys with a secure cryptographic source or KMS; never reuse a nonce with the same AES-GCM key; store nonce, ciphertext, and authentication tag as required by the API; bind relevant metadata (tenant, object ID, version) as associated data; version key IDs and plan rotation/re-encryption; treat authentication failure as rejection and never return unauthenticated plaintext. Negative tests alter ciphertext, tag, nonce, and associated data.
- **Reasoning:** Authenticated encryption protects confidentiality and integrity only under correct key/nonce lifecycle and verification.
- **Common wrong answer:** Reuse a fixed nonce for deterministic output or ignore authentication failures.
- **Safe principle:** Follow the library's AEAD contract, enforce nonce uniqueness, and fail closed on tampering.

### B08 — Safe HTTP fetcher and SSRF
- **Correct answer / rubric:** Prefer exact HTTPS host allow-lists and allowed ports; reject userinfo and unsupported schemes; parse using a single well-defined URL policy; use explicit connect/read or total timeouts and TLS verification; disable redirects or manually follow a small capped number while revalidating each hop; stream with a byte cap and accepted content types; avoid ambient credentials/proxies unless explicitly intended; log a sanitized destination identifier, not sensitive query strings. Resolve and classify all candidate IPs, but recognize that validation followed by a normal hostname connection leaves a DNS-rebinding/TOCTOU gap. Enforce destination policy at connection time or through a policy-enforcing egress proxy.
- **Reasoning:** URL parsing, DNS resolution, and actual connection are separate stages.
- **Common wrong answer:** Block only `127.0.0.1`, check DNS once, or trust the initial URL while following redirects automatically.
- **Safe principle:** Use allow-lists, bounded HTTP behavior, and network-layer connect-time enforcement.

### B09 — Safe deserialization and artifact provenance
- **Correct answer / rubric:** A SHA-256 hash establishes equality to the digest supplied, not who supplied that digest or whether the artifact is benign. Obtain artifact identity from a trusted signed manifest or authenticated registry; prefer a data-only format; validate metadata/shape/size; scan and load in a disposable, low-privilege, no-network worker; promote only approved artifacts. If pickle is unavoidable, require a trusted producer/signature and strict provenance, restrict access, isolate loading, and document that restricted unpicklers/scanners do not prove safety.
- **Reasoning:** Integrity without authenticated provenance is insufficient, and pickle loading may execute code.
- **Common wrong answer:** Trust a hash stored beside the artifact or “sanitize” a pickle before loading.
- **Safe principle:** Authenticate provenance, minimize executable formats, and isolate unavoidable risky parsing.

### B10 — Webhook verification and replay
- **Correct answer / rubric:** Read the exact raw body bytes; parse the signature header strictly; compute the HMAC over the provider-defined signed message (often timestamp plus raw body); compare with `hmac.compare_digest`; enforce timestamp tolerance; atomically record event ID/idempotency key before side effects; reject invalid signatures before parsing or processing; return generic errors. Test altered body, invalid/missing signature, stale timestamp, duplicate event, and a valid request. Exact signing format is provider-specific.
- **Reasoning:** Re-serializing JSON can change whitespace, key order, or number representation and therefore the signed bytes.
- **Common wrong answer:** Compare strings with `==`, process first and verify later, or rely only on a timestamp to prevent duplicate side effects.
- **Safe principle:** Verify the specified bytes before side effects and make processing idempotent.

### B11 — Build a resource-exhaustion test plan
- **Correct answer / rubric:** Suitable limits include upload bytes, archive member count/expanded bytes/ratio, parser depth/items, fetch duration and response bytes, queue depth/concurrency, LLM tokens/cost per tenant, retries, and per-user rate. Tests should include over-limit rejection, exact-boundary acceptance, interrupted stream cleanup, repeated retries not multiplying side effects, and generated/property-based path or size edge cases. Enforce limits at the component that consumes the resource and also apply global quotas.
- **Reasoning:** Limits must be enforced before the expensive operation, not only after it completes.
- **Common wrong answer:** Limit only the HTTP request size while allowing archive expansion or unlimited downstream LLM work.
- **Safe principle:** Budget every expensive resource across the whole request path.

### B12 — TLS and HTTP client defaults
- **Correct answer / rubric:** Keep certificate and hostname verification enabled; configure finite connect/read/total deadlines; restrict URL/host/port and redirects for the trusted endpoint; stream and cap response bytes; avoid logging query tokens or full sensitive URLs; use generic external errors. Pinning is a specialized choice for a controlled client/server lifecycle with a rotation/fallback plan; it is not a universal substitute for normal PKI verification.
- **Reasoning:** TLS authenticates the endpoint only when verification is enabled; timeouts and size limits address different risks.
- **Common wrong answer:** Disable verification to “fix” a certificate error or assume a timeout alone bounds response size.
- **Safe principle:** Secure transport defaults plus independent resource and destination policy.

## Phase C — Process and assurance

### C01 — Triage a hypothetical Bandit result
- **Correct answer / rubric:** Confirm the rule, code path, attacker control, reachability, runtime environment, and impact; inspect whether the command uses a shell and whether user filenames/options can reach it. Prefer a library or fixed argv with strict options and sandboxing. Add regression tests and CI enforcement. Assign a code owner and due date. Suppress only if a documented, narrow, reviewed exception is justified; a high/high finding on a reachable user-controlled path normally warrants a fix.
- **Reasoning:** Severity/confidence are triage signals, not a substitute for contextual analysis.
- **Common wrong answer:** Delete the warning because it is static analysis or suppress it globally.
- **Safe principle:** Verify, fix reachable risk, and document residual risk with accountable ownership.

### C02 — Triage a hypothetical `pip-audit` result
- **Correct answer / rubric:** Confirm package/version/advisory and the actual environment/lock resolution; determine whether the affected component is installed or deployed and whether the vulnerable functionality is reachable. Upgrade to a fixed compatible release, update and review the lockfile, run tests and build/deployment checks, and record owner/evidence. If no fix is available, mitigate or isolate, set an expiry and review date, and monitor advisories. Do not dismiss solely because it is transitive or classified as development-only without checking packaging and deployment.
- **Reasoning:** Advisory matching indicates a known vulnerable version, not exploitability proof; absence of a finding does not prove safety.
- **Common wrong answer:** Ignore all transitive dependencies or blindly upgrade without testing.
- **Safe principle:** Reproduce the resolution, assess exposure, remediate, and retain traceable evidence.

### C03 — Design a Semgrep rule
- **Correct answer / rubric:** A valid rule can use a `pattern` for `requests.get($URL)` and a negative pattern for the same call with `timeout=...`; exact YAML syntax should be checked against the installed Semgrep version. Include a positive fixture with no timeout and a negative fixture with explicit timeout. A simple syntactic rule may miss aliases/wrappers or flag safe wrappers whose timeout is configured elsewhere.
- **Reasoning:** Custom rules need tests and known coverage boundaries.
- **Common wrong answer:** Claim the rule proves every HTTP request is bounded.
- **Safe principle:** Treat rules as focused guardrails, version them, test fixtures, and document blind spots.

### C04 — STRIDE a small service
- **Correct answer / rubric:** A plausible DFD: browser/client → upload API [internet trust boundary] → object store; API → queue; worker → object store/DB; worker → approved external fetch service and LLM provider [egress/provider boundaries]; services → centralized logs. Examples: Spoofing—stolen session; Tampering—replace uploaded object before processing; Repudiation—missing immutable audit record; Information Disclosure—cross-tenant summary access or secrets in logs; DoS—archive bomb/queue flood/LLM cost abuse; Elevation of Privilege—worker role can access all tenants or invoke unrestricted tools. Credit requires boundary labels and one mitigation/test per category.
- **Reasoning:** STRIDE should be applied to components, flows, and trust-boundary crossings, not just a generic list.
- **Common wrong answer:** List six labels without connecting them to assets, flows, or controls.
- **Safe principle:** Model concrete attacker goals and testable mitigations in the actual data flow.

### C05 — Prioritize a risk register
- **Correct answer / rubric:** A defensible default is (b) cross-tenant authorization failure first because it directly exposes other tenants' data; (d) unrestricted public fetcher next because internal reachability may be high impact and broad; (c) vulnerable dependency with a fix next, depending on reachability/exposure; (a) low-confidence unreachable test-only warning last. State assumptions and change order if evidence shows the dependency is actively exploited or the fetcher is tightly egress-restricted. Every item needs a mitigation, owner, verification, and residual risk.
- **Reasoning:** Impact, exploitability, reachability, and blast radius matter more than raw scanner count.
- **Common wrong answer:** Rank solely by scanner severity or CVSS number without context.
- **Safe principle:** Use transparent qualitative scoring and update it as evidence changes.

### C06 — Turn findings into testable requirements
- **Correct answer / rubric:** Examples: “Every uploaded path resolves beneath a private storage root and outside paths are rejected” tested with traversal/symlink cases; “known canary secrets never appear in captured logs/errors” tested with log capture; “fetcher connects only to approved destinations and revalidates redirects” tested with local fake endpoints plus egress-policy tests; “every object read checks tenant ownership” tested with cross-tenant IDs; “CI audits the resolved lock and blocks unapproved advisories” tested with a controlled fixture/seeded policy test. Limitations include TOCTOU/platform behavior, runtime identity/network policy, and unknown/new advisories.
- **Reasoning:** A requirement needs observable acceptance evidence and a stated residual gap.
- **Common wrong answer:** “Use a scanner” as the entire requirement.
- **Safe principle:** Define measurable behavior and test both rejection and legitimate use.

### C07 — Design a CI security gate
- **Correct answer / rubric:** On PR: format/lint and Ruff `S`, Bandit, custom Semgrep, secret scan, dependency audit of the resolved lock/environment, unit/security regression tests; upload SARIF or reviewable reports with redacted logs. Block new high-confidence/high-impact findings, confirmed secret leaks, policy violations, and unapproved vulnerable dependencies according to a documented policy. Compare against a reviewed legacy baseline so new findings fail while old ones have owners/expiry. Nightly/release scans can add broader image/IaC scans and dependency freshness. Retain reports as access-controlled artifacts and never print secret values.
- **Reasoning:** CI should provide actionable evidence and avoid leaking the very secrets it detects.
- **Common wrong answer:** Make every historical warning a permanent merge blocker or silently ignore all baseline findings.
- **Safe principle:** Fail closed on new policy violations; baseline legacy issues with ownership and deadlines.

### C08 — Write a defensible exception
- **Correct answer / rubric:** Record rule/finding ID, exact file/line/scope, why the behavior is required, threat analysis, compensating controls, tests, owner, approver, created date, expiry/review date, and removal plan. A narrow comment may identify the exact Bandit rule and reason, e.g. `# nosec B603 — fixed executable and argv allow-list; see SEC-123; expires YYYY-MM-DD`, only if that rule is truly applicable and project policy accepts the syntax. Do not use blanket `# nosec`, suppress secrets or known exploitable behavior, or omit expiry.
- **Reasoning:** Exceptions transfer an explicitly bounded residual risk; they do not make code safe.
- **Common wrong answer:** Suppress a whole file to obtain a green build.
- **Safe principle:** Minimize suppression scope, document compensating controls, and expire exceptions.

### C09 — Supply-chain review of a new dependency
- **Correct answer / rubric:** Defer pending evidence because the benefit is small and release/maintainer/build risks are unclear. Compare standard-library or existing dependencies; review maintainers, source repository, release history, package name/typosquatting, license, transitive graph, sdist build backend, provenance/signatures where available, hashes and lockfile reproducibility. Apply a documented release-age delay with an emergency exception process, automate updates through reviewed PRs, and test the exact resolved artifact. Approval may be reasonable after risk and value are demonstrated.
- **Reasoning:** Fewer lines of code may not justify a new supply-chain and maintenance dependency.
- **Common wrong answer:** Trust the highest download count or pin only a version string without reviewing the artifact source.
- **Safe principle:** Minimize dependencies and make provenance, reproducibility, and ownership explicit.

### C10 — Interpret scanner blind spots
- **Correct answer / rubric:** Examples: BOLA/authorization logic (cross-tenant integration tests/code review); runtime SSRF and DNS rebinding (local mock tests plus egress enforcement); business-logic abuse and cost exhaustion (threat model/load tests/quotas); unknown vulnerabilities (patch and vendor monitoring); secret leakage in external logs/history (repository and artifact scans plus rotation drills); unsafe deployment IAM/network exposure (configuration review/runtime policy); LLM prompt injection/tool abuse (red-team tests and least-privilege tool gates). Any five well-matched gaps earn full credit.
- **Reasoning:** Each tool sees only a portion of the system and known patterns/data.
- **Common wrong answer:** “All security issues are covered because CI is green.”
- **Safe principle:** Layer static, dependency, secret, dynamic, architecture, and operational verification.

### C11 — Define a secure artifact pipeline
- **Correct answer / rubric:** Pin source revision and build inputs; build in a controlled environment; record hashes and provenance; review license and dependency graph; sign release metadata and verify it against a trusted publisher key; scan and validate the artifact; prefer a data-only format; store immutable/versioned artifacts; gate promotion; load in an isolated low-privilege worker; validate schema and resource bounds; expose only typed IPC. Signing proves the artifact matches a key's signature, not that the publisher or artifact is benign; scanners have coverage limits.
- **Reasoning:** Controls protect different stages and do not collapse into one “signed means safe” assertion.
- **Common wrong answer:** Verify a checksum from the same untrusted download location and immediately load pickle.
- **Safe principle:** Establish provenance, restrict formats, gate promotion, and isolate execution.

### C12 — Evaluate LLM/tool trust boundaries
- **Correct answer / rubric:** Uploaded text and fetched pages may contain indirect prompt injection; user prompts can directly request misuse. Treat model output as untrusted. Authorize tools outside the model using the authenticated tenant/user, restrict URL fetch via safe HTTP/egress policy, limit export scope and fields, require human approval for high-impact actions, prevent secrets from entering prompts/logs, validate output schemas, rate-limit/token-budget, and test cross-tenant and exfiltration attempts with local fixtures.
- **Reasoning:** Prompt instructions are not a security boundary; tool permissions and data access must be enforced by deterministic application code.
- **Common wrong answer:** Add a system prompt saying “ignore malicious instructions” and grant the agent broad tools.
- **Safe principle:** Least privilege and policy enforcement must live outside model-generated text.

### C13 — Threat-model review triggers and governance
- **Correct answer / rubric:** Triggers include new public endpoints, authentication/authorization changes, new external fetch/LLM/tool integration, new data class/tenant, storage or identity changes, new dependency/build pipeline, and material incident. STRIDE organizes threat categories; PASTA emphasizes risk-centric attack analysis; LINDDUN focuses privacy; attack trees model goal paths; OWASP Top 10/API/LLM lists common categories; ATT&CK/ATLAS describe observed/adversary tactics; CWE Top 25 highlights common weakness classes. Frameworks help completeness but cannot determine the system-specific threat or prove control effectiveness. Compliance supports governance evidence but is not a security guarantee.
- **Reasoning:** Checklists improve coverage but require application to architecture and business context.
- **Common wrong answer:** Claim a completed framework checklist certifies the design as secure.
- **Safe principle:** Use frameworks as prompts, then validate threats, controls, and residual risk against the real system.

### C14 — Incident detection and recovery exercise
- **Correct answer / rubric:** Define a simulated trigger (e.g. revoked test key returns an authentication failure), expected alert and routing, on-call acknowledgement deadline, containment, evidence retention, rotation/recovery, and post-incident review. Inject the event in a non-production environment and assert the expected alert reaches a test sink/on-call simulation. Include pass/fail thresholds and ensure the test does not use production credentials or create destructive side effects.
- **Reasoning:** A documented runbook is not proven until detection and execution are exercised.
- **Common wrong answer:** Mark the exercise successful because the alert rule exists in configuration.
- **Safe principle:** Test the end-to-end detection and response path safely and repeatably.

### C15 — `vulnpy` capstone acceptance plan
- **Correct answer / rubric:** Deliver `docs/threat-model.md` with DFD/trust boundaries and at least 20 threats; a risk register and peer-reviewed revision; at least eight local exploit/fix/regression cycles; fuzz/property tests for validators and paths; top five mitigations; CI with Ruff `S`, Bandit/SARIF, `pip-audit`, secret scan, custom Semgrep, and reviewed baseline; dependency update policy/release-age handling; `SECURITY.md`; incident one-pager and key-rotation procedure; and `HARDENING_REPORT.md` with before/after findings, CWE IDs, control coverage, and residual/out-of-scope risks. Demonstrate CI failing on a deliberately seeded local test finding, then passing after the fix, preserving reports as evidence.
- **Reasoning:** Acceptance requires repeatable evidence, not only a narrative claim that code is secure.
- **Common wrong answer:** Show a green scan without proving that the gate detects a known seeded regression.
- **Safe principle:** Make controls testable, reviewable, repeatable, and explicit about residual risk.

## Required special section A — Find the vulnerability

### REV01 — SQL built with an f-string
- **Correct answer / rubric:** SQL injection: `report_id` becomes SQL syntax. Use `conn.execute("SELECT body FROM reports WHERE id = ?", (report_id,)).fetchone()` for SQLite. Allow-list any dynamic sort column from fixed identifiers. Test a quote-containing identifier and verify it cannot change query structure.
- **Reasoning:** Parameters bind values only; SQL identifiers must be selected from trusted constants.
- **Common wrong answer:** Escape quotes manually or interpolate the sort column from user input.
- **Safe principle:** Separate query structure from data.

### REV02 — Unsafe `yaml.load`
- **Correct answer / rubric:** A general loader can construct unsafe Python objects from untrusted YAML. Use `yaml.safe_load(text)` (with an appropriate maintained PyYAML version), then validate expected keys, types, ranges, and size/depth. Test malformed YAML, unexpected object-like tags, and valid expected configuration.
- **Reasoning:** Safe parsing reduces object-construction risk but does not guarantee the resulting values satisfy application policy.
- **Common wrong answer:** Trust the `.yaml` extension or rely on schema-free `safe_load` as complete validation.
- **Safe principle:** Use safe parsers and validate the resulting data model.

### REV03 — `os.path.join` with user path
- **Correct answer / rubric:** An absolute child can replace the root; `..` can traverse; symlinks can escape. Prefer server-generated IDs and a private root. For a path-based check, resolve root and candidate, then use `candidate.is_relative_to(root)` (or a compatible parent-based check), and handle errors. Do not claim this eliminates TOCTOU: use directory-relative/no-follow/exclusive operations or an isolated storage layer for hostile concurrent filesystems.
- **Reasoning:** Joining constructs a path; it does not enforce authorization or containment.
- **Common wrong answer:** Remove literal `../` or check only the unnormalized string.
- **Safe principle:** Avoid user-controlled pathnames where possible and use path-aware, race-conscious access.

### REV04 — `shell=True`
- **Correct answer / rubric:** `filename` is interpolated into a shell command and can change shell syntax; even with `shell=False`, a filename beginning with an option can change ImageMagick behavior. Prefer Pillow if it meets requirements. Otherwise use a fixed executable and argv list, allow-list format/options, use a documented `--` separator where supported, create unique temporary outputs, set timeout/environment/working directory, and run with no network and least privilege. Test shell metacharacters and option-shaped filenames as inert data.
- **Reasoning:** Shell parsing and child-program option parsing are distinct attack surfaces.
- **Common wrong answer:** Quote the string and retain `shell=True`, or trust `shell=False` alone.
- **Safe principle:** Avoid shells, constrain arguments, and sandbox complex parsers.

### REV05 — TLS verification disabled
- **Correct answer / rubric:** `verify=False` disables server certificate verification and enables interception risk. For a fixed trusted endpoint, keep default verification enabled, use an explicit timeout, check status, stream the response and stop at a byte limit, and restrict redirects/endpoint policy. If it is an SSRF-capable feature, add destination/redirect/egress controls rather than only hard-coding TLS settings. Do not log sensitive query parameters.
- **Reasoning:** TLS encryption without endpoint authentication is insufficient; TLS also does not stop SSRF to an unintended but valid TLS endpoint.
- **Common wrong answer:** Turn verification back on but leave an unrestricted URL and unbounded response.
- **Safe principle:** Verify identity and separately enforce destination and resource policy.

### REV06 — Security token generated with `random`
- **Correct answer / rubric:** `random` is not intended for unpredictable security tokens. Use `secrets.token_urlsafe(32)` or another `secrets` API with sufficient entropy. Store a hash of bearer tokens where feasible, associate them with scope/owner, expire/revoke them, and avoid logging them. Test uniqueness/format and expiry/revocation behavior; statistical tests alone do not prove cryptographic unpredictability.
- **Reasoning:** Security tokens must resist prediction, not merely look random.
- **Common wrong answer:** Increase the length while continuing to use `random`.
- **Safe principle:** Use cryptographic randomness and manage the full token lifecycle.

### REV07 — Path containment using `startswith`
- **Correct answer / rubric:** A sibling such as `/srv/app/reports-old/file` shares the string prefix but is not beneath `/srv/app/reports`. Use `root = Path(...).resolve()` and `candidate = (root / user_path).resolve()` then reject unless `candidate.is_relative_to(root)`; catch invalid/missing path errors. This is only a check-before-open and does not eliminate races. Prefer generated IDs, private storage, and OS-level directory-relative/no-follow operations when attackers can mutate the tree.
- **Reasoning:** Filesystem containment is structural, not a string-prefix property.
- **Common wrong answer:** Add a trailing slash to the prefix and declare it race-proof.
- **Safe principle:** Path-aware containment plus race-resistant access and least privilege.

### REV08 — Redirect-following fetcher without revalidation
- **Correct answer / rubric:** Automatic redirects can move the request to an unapproved host/IP after only the initial URL was checked. Disable redirects or handle each hop manually with a small cap; parse and validate scheme/host/port, resolve and classify destinations, enforce policy at connection time via a reviewed pinned transport or egress proxy, preserve TLS hostname verification, and stream under a strict byte/time limit. Test redirect to an unapproved local mock host, loops, too many hops, and oversized bodies.
- **Reasoning:** Redirects create new destination decisions; DNS may also change between validation and connection.
- **Common wrong answer:** Validate the first URL only or block only the literal loopback address.
- **Safe principle:** Revalidate every hop and enforce the final destination policy where the socket connects.

## Required special section B — Incident response

### IR01 — Secret/API key committed or leaked
- **Correct answer / rubric:** (1) Revoke/rotate the live credential immediately using the provider's control plane; disable it if safe. (2) Assign incident lead and preserve relevant logs/commit/CI evidence. (3) Identify permissions, scope, last use, and possible abuse; rotate related credentials if exposure warrants it. (4) Remove secret from active files, logs, build artifacts, caches, and repository history, remembering forks/clones may persist. (5) Notify owners/security/privacy stakeholders per policy. (6) Add scanning/pre-commit/CI, redaction tests, and a rotation drill. History rewriting alone cannot invalidate an already copied credential.
- **Reasoning:** Containment comes before repository hygiene.
- **Common wrong answer:** Delete the commit but leave the key active.
- **Safe principle:** Revoke first, preserve evidence, scope impact, then clean and prevent recurrence.

### IR02 — Malicious pickle/model artifact discovered
- **Correct answer / rubric:** Stop loading/promoting the artifact and isolate affected workers; do not execute it to test the suspicion. Preserve hash, registry metadata, logs, and provenance as evidence; identify all builds/jobs that consumed it; isolate/rebuild affected workloads from trusted sources; review possible credential/network exposure and rotate as warranted; replace with a verified data-only artifact and enforce provenance/admission/isolation controls. Notify stakeholders based on impact.
- **Reasoning:** Loading the suspected artifact can trigger the behavior under investigation.
- **Common wrong answer:** Load it in production or a developer workstation to “see what happens.”
- **Safe principle:** Contain and investigate non-executingly; assume the loader boundary may have been crossed.

### IR03 — SSRF may have reached cloud metadata
- **Correct answer / rubric:** Disable or restrict the fetch feature and apply egress/metadata endpoint blocks; preserve request/egress/identity logs and relevant workload evidence; determine which workload identity and permissions were available; revoke or rotate potentially exposed credentials/tokens and inspect their use; assess affected resources and tenant data; patch with host/redirect/IP policy plus connection-time enforcement; verify through local mocks and policy tests without repeating the metadata request. Escalate according to incident policy and record uncertainty.
- **Reasoning:** The priority is stopping further access and reducing credential blast radius, not reproducing the request against production metadata.
- **Common wrong answer:** Re-run the URL to confirm access or assume IMDSv2 alone means no impact.
- **Safe principle:** Contain, investigate evidence, rotate affected identity material, and verify controls safely.

### IR04 — Dependency or release may be compromised
- **Correct answer / rubric:** Freeze adoption and deployment of the suspect artifact; identify exact package/version/hash across lockfiles, build logs, images, SBOMs, and running workloads; preserve evidence; obtain a trusted advisory and verify known-good artifacts; roll back/pin to a verified release or rebuild from a clean environment; inspect possible execution and credential access, rotating secrets if warranted; scan/rebuild affected images, notify owners/customers as required, and document residual uncertainty. Re-enable updates only through a reviewed policy.
- **Reasoning:** A package name/version alone may not identify the exact artifact that was built or installed.
- **Common wrong answer:** Run an unreviewed automatic upgrade and assume the newest release is safe.
- **Safe principle:** Establish artifact identity, contain rollout, rebuild reproducibly, and communicate evidence and uncertainty.

---

## Scoring and completion guidance

- **Main questions:** Score each 0–3: `0` missing/unsafe, `1` partial or mostly conceptual, `2` sound answer with minor gaps, `3` correct reasoning plus concrete verification and residual-risk awareness. There are 35 main questions (A01–A08, B01–B12, C01–C15), maximum 105 points.
- **Code-review items:** Score each 0–2 for identifying the root cause and proposing a safe fix plus regression test, maximum 16 points.
- **Incident scenarios:** Score each 0–3 for containment order, evidence/scope, recovery, and prevention, maximum 12 points.
- **Suggested readiness signal:** At least 80% overall and no zero on any critical area (SQL/injection, path handling, subprocesses, cryptography/secrets, SSRF/deserialization, incident containment). This is a learning rubric, not a formal certification.
- **Required capstone evidence:** Use the roadmap's `vulnpy` acceptance criteria: DFD and trust boundaries; at least 20 STRIDE/LLM-aware threats and prioritized risk register; at least eight locally demonstrated exploit/fix/regression cycles; tests including property/fuzz cases; top mitigations; CI gate with reviewed legacy baseline; secret/dependency policy; `SECURITY.md`; incident-response one-pager and key-rotation procedure; `HARDENING_REPORT.md` with before/after findings, CWE IDs, control rationale, and residual risks; and peer review or recorded review followed by revision. All demonstrations must be local and authorized.

## Self-check against the module completion checklist

Before marking the module complete, confirm that you can:

- Identify trust boundaries and validate input with allow-lists at the edge.
- Prevent SQL, command, template, log, CSV, and path injection with safe APIs.
- Avoid unsafe deserialization and choose safer data/model formats with authenticated provenance.
- Handle files, uploads, and archives with containment, atomicity, and restrictive permissions.
- Invoke subprocesses without shell/argument injection and sandbox unavoidable parsers.
- Manage secrets, choose vetted cryptography, and respond correctly to leaks.
- Build HTTP clients with TLS verification, timeouts, size limits, and SSRF controls.
- Run SAST, SCA, secret scanning, and custom rules in CI and triage findings with documented exceptions.
- Threat-model a small service with STRIDE and convert risks into tests and controls.
- Complete and document the `vulnpy` hardening project with evidence and residual-risk statements.
