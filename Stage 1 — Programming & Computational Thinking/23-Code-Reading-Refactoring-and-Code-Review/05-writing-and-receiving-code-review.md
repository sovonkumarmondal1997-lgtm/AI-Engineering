# Writing and Receiving Code Review

> **Stage 1 — Programming & Computational Thinking**  
> **Module 1.23 — Code Reading, Refactoring and Code Review**  
> **Lesson 05 of 08**  
> **Audience:** beginner through advanced Python engineers, with data engineering examples  
> **Runtime assumptions:** Python 3.12+, Git 2.40+, pytest, Ruff, and a GitHub- or GitLab-style pull-request workflow

## Learning outcomes

By the end of this lesson, you should be able to:

- Explain the purposes of review without confusing it with style policing or a substitute for testing.
- Prepare a small, focused pull request (PR), self-review it, and provide enough context for a reviewer to make a decision.
- Review tests first, then design, then implementation details; inspect happy paths and failure paths.
- Identify and describe correctness, compatibility, security, performance, operations, dependency, and maintainability risks.
- Classify findings by impact, write actionable and respectful comments, and separate required fixes from optional suggestions.
- Receive feedback without defensiveness, resolve disagreements with evidence, and close review conversations constructively.
- Review changes to data pipelines, SQL, migrations, notebooks, ML/AI systems, infrastructure, and CI with the appropriate risk lens.
- Use automation and review policies to reduce noise while retaining human judgment for design and behavior.
- Improve team review culture through sensible SLAs, reviewer rotation, design reviews, retrospectives, and reviewable PR sizes.

## 1. What code review is—and is not

Code review is a structured examination of a proposed change before or shortly after it enters a shared codebase. It is a quality-control activity, a learning mechanism, and a way to distribute system knowledge. The goal is not to prove that the author is wrong; the goal is to increase confidence that the change is appropriate for its intended purpose and safe to maintain and operate.

### 1.1 Purposes of review

A useful review considers:

- **Correctness:** Does the change satisfy the stated requirement? Are boundaries, failure paths, and unusual inputs handled?
- **Design:** Is the change in the right layer? Does it respect architectural boundaries and public contracts?
- **Readability and maintainability:** Can another engineer understand and change it without reconstructing hidden assumptions?
- **Tests:** Do tests prove observable behavior, including regression and negative cases?
- **Security and privacy:** Are trust boundaries, authorization, secrets, personal data, and dependencies handled safely?
- **Performance and resource use:** Could the change cause an N+1 query, quadratic work, unbounded retries, memory growth, or missing timeouts?
- **Consistency:** Does it fit project conventions and APIs? Mechanical style should normally be handled by formatters and linters.
- **Knowledge sharing and bus factor:** Does review spread understanding, challenge undocumented assumptions, and reduce reliance on one person?

A review is not a substitute for automated tests, static analysis, threat modeling, performance measurement, production monitoring, or an explicit design decision. It is one control in a larger engineering system.

### 1.2 What humans should not spend review time on

Use tools such as `ruff format`, `ruff check`, type checkers, and CI to catch mechanical issues consistently. Do not use review comments to debate formatting that the repository has already delegated to automation. Human attention is scarce; spend it on semantics, contracts, risk, and design.

This does not mean every stylistic issue is irrelevant. A name that obscures a business invariant or a confusing API can be a maintainability defect. The distinction is whether the comment improves understanding or merely expresses personal preference.

### 1.3 Review is not a search for perfection

A change can be acceptable without being the only possible implementation. This is consistent with Google’s code-review guidance: the question is whether the change improves overall code health enough for its risk and context, not whether every line matches the reviewer's preferred style. A reviewer may approve with non-blocking follow-up work when the remaining imperfections are understood and the team's standards permit it. A correctness, security, data-loss, or compatibility defect is not made acceptable by calling it a nit.

---

## 2. The author's workflow: make the change reviewable

A reviewer cannot efficiently assess an unclear or sprawling change. The author is responsible for presenting the change in a form that exposes intent, evidence, and risk.

### 2.1 A repeatable preparation workflow

1. **Confirm the problem.** Read the issue or request. Write down expected behavior, constraints, and non-goals. Clarify ambiguous requirements before coding.
2. **Choose one logical change.** Separate unrelated cleanup, dependency upgrades, formatting-only changes, and feature work where practical. Aim for fewer than 400 changed lines as a useful guideline, not an absolute law. A 100-line security-sensitive migration may need more review than a 350-line generated file.
3. **Make the smallest safe change.** Avoid opportunistic rewrites. If a larger refactor is necessary, explain why and consider a preparatory PR.
4. **Add evidence.** Include regression tests and relevant boundary/failure cases. Update documentation, runbooks, changelog entries, schemas, or migration instructions when the change affects them.
5. **Run local checks.** Run focused tests first, then the project's broader checks. Record exact commands and results; never claim a check passed if it was not run.
6. **Inspect your own diff.** Review it as if someone else wrote it. Look for accidental files, debug statements, secrets, unrelated formatting, stale comments, missing tests, confusing names, and behavior changes.
7. **Inspect the diff as a reader.** Use `git diff --check`, `git diff --stat`, and a normal diff. Read moved code in context. If a PR is too large to explain clearly, split it or add a staged plan.
8. **Write the PR description.** Explain what changed, why it changed, how it was tested, what could go wrong, and how to roll it back. Link the issue, design note, dashboards, screenshots, benchmark, or migration plan as applicable.
9. **Tidy the branch.** Use meaningful commits and avoid mixing unrelated work. Keep review context when updating the branch; coordinate before force-pushing if reviewers rely on line comments.
10. **Choose the right state.** Mark the PR as a draft while work is incomplete. Request reviewers when the change is ready, the checks are available, and the description is useful.
11. **Respond to every substantive comment.** Make a change, explain why you disagree with evidence, ask a clarifying question, or explicitly record a follow-up. Do not silently leave questions unresolved.
12. **Re-run relevant checks after revisions.** Summarize what changed and which checks were rerun. Resolve threads only when the concern is addressed or a clear decision has been recorded.

### 2.2 PR size: a heuristic, not a quota

The roadmap recommends small PRs—fewer than 400 changed lines, one logical change. This is a reviewability guideline, not a guarantee of quality. Generated code, lock files, snapshots, and migrations may distort line counts. Explain such cases and separate generated noise from hand-written logic where possible. The real goal is a diff that a reviewer can understand deeply in a reasonable amount of time.

### 2.3 Self-review commands

Run these from the repository root, adapting paths and commands to the project:

```bash
git status --short
git diff --stat
git diff --check
git diff --color-moved
# Ignore whitespace only when it helps reveal moved or reformatted code:
git diff -w
# Review commits and the complete branch diff:
git log --oneline --decorate -8
git diff origin/main...HEAD
```

The `A...B` diff compares `B` against the merge base with `A`; confirm the base branch name is correct. Do not use `-w` as your only review because whitespace can be meaningful in some formats and indentation-sensitive files. In GitHub CLI workflows, `gh pr diff` and `gh pr checkout <number>` are useful; inspect the PR's base branch before comparing.

### 2.4 PR description template

Copy and adapt this template. Delete sections that truly do not apply, rather than leaving unexplained blanks.

```markdown
## What changed
- Describe the observable change in one or two bullets.

## Why
- Link the issue, incident, request, or design decision.
- State the behavior or risk this change addresses.

## How it works
- Summarize the approach and important design choices.
- Mention public API, schema, config, or compatibility impacts.

## Validation
- [ ] Focused tests: `<command>` — result
- [ ] Full relevant suite: `<command>` — result
- [ ] Lint/type/security checks: `<command>` — result
- [ ] Manual check, benchmark, or replay (if relevant): result

## Risk and rollout
- Blast radius and affected users/pipelines.
- Migration, backfill, feature flag, monitoring, rollback, or fallback.

## Data / security / operations
- Schema or data-contract changes:
- PII/secrets/authentication/authorization implications:
- Logs, metrics, alerts, runbooks, and dashboards:

## Links and evidence
- Issue / ADR / docs / benchmark / screenshots / evaluation report:

## Author checklist
- [ ] One logical change; unrelated changes separated.
- [ ] I reviewed the complete diff and removed accidental changes.
- [ ] Tests cover relevant behavior and failure cases.
- [ ] Documentation and operational instructions are updated.
- [ ] I can explain every material line, including generated or AI-assisted code.
```

### 2.5 What good testing evidence looks like

A green badge is useful but incomplete evidence. State the commands run and what they cover. For a bug fix, include a regression test that fails on the old behavior and passes with the fix. For a refactor, show behavior-preserving evidence rather than relying on the word *refactor*. For a data migration, tests may need to cover idempotency, backfill behavior, locks, transaction boundaries, and rollback. For performance claims, provide representative data sizes, environment, baseline, and measurement method.

Never paste credentials, production PII, or sensitive payloads into a PR. Redact data and follow the organization's data-handling policy.

---

## 3. The reviewer's workflow: understand, then inspect

A strong review has a sequence. Reading lines in order without understanding the goal can produce many comments and still miss the primary defect.

### 3.1 Recommended order

1. **Read the PR description and linked issue.** Identify the intended behavior, scope, and non-goals.
2. **Review tests first.** Ask what behavior is asserted, which scenarios are missing, whether tests fail without the change, and whether they are deterministic. Tests often reveal the intended contract faster than implementation code.
3. **Review the design and boundaries.** Is the change in the right module/layer? Are public APIs, schema contracts, and dependencies affected? Is a simpler approach available?
4. **Trace the main behavior.** Follow the input through validation, transformations, side effects, error handling, and outputs. For data pipelines, trace source → transform → sink and the retry/checkpoint boundaries.
5. **Inspect failure and edge paths.** Empty input, `None`, duplicates, large inputs, Unicode, time zones, invalid configuration, timeouts, permissions, partial failures, concurrency, and retry behavior as relevant.
6. **Inspect security, privacy, and operational risks.** Trust boundaries, SQL or shell construction, authorization, sensitive logs, resource bounds, metrics, alerts, rollback, and blast radius.
7. **Inspect details.** Names, function size, comments explaining *why*, public docstrings, duplication, style, and maintainability.
8. **Run checks or reproduce the concern.** If uncertainty remains, check out the branch, run focused tests, use a small reproduction, or ask for missing evidence.
9. **Write findings by impact.** Put blockers first and distinguish required changes from suggestions. Do not bury a serious defect among ten nits.
10. **Choose a decision and explain it.** Approve, request changes, or leave comments pending evidence according to the platform and team policy. Do not approve a risky change merely to clear a queue.

### 3.2 Review both happy and failure paths

The happy path is what the code does with ideal input and healthy dependencies. Production failures often live elsewhere:

- What happens when an upstream API returns `401`, `429`, `500`, malformed JSON, or times out?
- If a job retries after writing half a batch, is the operation idempotent?
- Does a duplicate event create a duplicate row?
- What happens when a partition is empty or a timestamp has a timezone offset?
- Can an unauthorized caller reach the new path?
- If a migration is interrupted, can it safely resume?
- If a queue backs up, is memory bounded and is there an alert?

The right checklist depends on the change. Do not mechanically demand every edge case in every PR; select cases based on the contract and risk.

---

## 4. Review checklist

Use this checklist as a starting point. Adapt it to your system and change type. A checked box means the reviewer considered the dimension and has sufficient evidence for this change—not that every possible risk is impossible.

### 4.1 Core checklist

- [ ] **Requirement and scope:** Does the change solve the linked problem? Are non-goals respected? Is the diff focused?
- [ ] **Correctness:** Are invariants preserved? Are empty, `None`, duplicate, large, Unicode, timezone, and boundary cases relevant here? Are off-by-one errors possible?
- [ ] **Failure behavior:** Are errors handled at the right layer? Are exceptions specific enough? Are retries limited to transient failures? Are timeouts present where needed?
- [ ] **Concurrency and idempotency:** Could work overlap? Can a retry duplicate side effects? Are locks/transactions/checkpoints correctly scoped?
- [ ] **Design and API:** Is the code in the right layer? Is the public contract compatible? Are abstractions justified? Is behavior duplicated elsewhere?
- [ ] **Tests:** Do tests verify observable behavior? Is there a regression test? Are negative and boundary cases represented? Are tests deterministic and meaningful?
- [ ] **Readability:** Are names precise? Is control flow easy to follow? Do comments explain why rather than narrate the syntax? Are public APIs documented?
- [ ] **Security and privacy:** Is untrusted input validated? Are SQL/shell/HTML contexts parameterized or safely encoded? Are authorization checks correct? Could secrets or PII enter logs, exceptions, prompts, or fixtures?
- [ ] **Performance and resources:** Is there accidental O(n²) work, an N+1 query, repeated expensive computation, unbounded memory/queues/retries, or missing timeout/close behavior?
- [ ] **Operations:** Are logs/metrics useful without leaking data? Are configuration, alerts, runbooks, migration, rollback, and feature flags addressed?
- [ ] **Dependencies:** Is a new package justified? Is it maintained, compatible, licensed appropriately, and pinned/locked according to project policy? Are dependency files updated?
- [ ] **Compatibility:** Does this affect supported Python versions, serialization formats, schema consumers, command-line behavior, or downstream APIs?
- [ ] **Documentation:** Are examples, usage docs, changelog, data contracts, and operational procedures updated where necessary?
- [ ] **Evidence:** Are checks accurately reported? Are benchmarks and evaluation claims reproducible?

### 4.2 Change-specific review lenses

| Change type | Questions to ask |
| --- | --- |
| Behavior-preserving refactor | What evidence shows behavior is unchanged? Are characterization/regression tests in place? Did a hidden semantic change slip into a “refactor”? |
| Bug fix | Is the root cause addressed? Does a regression test fail before the fix? Are related boundaries covered? |
| New feature or API | Does it fit the architecture? Are inputs, outputs, errors, defaults, compatibility, and documentation clear? |
| SQL/data migration | Is it idempotent? What is the backfill plan? Could it lock a large table? Are transaction boundaries, rollback, duplicates, schema compatibility, and restart behavior considered? |
| Notebook | Are outputs stripped or intentionally retained? Can the notebook run top-to-bottom? Are dependencies, seeds, data sources, and environment documented? Is the diff reviewable? |
| ML/AI change | Are train/evaluation splits intact? Is leakage checked? Are seeds and data versions recorded? Are metrics defined and meaningful? Are prompt/model versions, safety effects, cost/latency, licences, and PII reviewed? |
| Infrastructure/CI | What is the blast radius? Can permissions broaden? Is a secret exposed? Can deployment or rollback be performed safely? Are protected branches and checks preserved? |
| Dependency change | Is the dependency necessary? Is its maintenance and license acceptable? Does the lock file change match the manifest? What is the supply-chain and compatibility risk? |

### 4.3 Review of data and ML changes

Data engineering code can be syntactically correct and still corrupt a warehouse. Check:

- **Lineage and contracts:** Which source, schema, keys, nullability, units, timezone, and semantic definitions changed? Which downstream consumers rely on them?
- **Duplicates and ordering:** What is the deduplication key? Are late-arriving events handled? Does the watermark skip or reprocess records?
- **Idempotency and recovery:** Can the job resume after a partial write? Are retries safe? Are checkpoints committed only after durable writes?
- **Backfills and migrations:** Are historical data volumes, locks, compute cost, rollback, and old/new schema coexistence considered?
- **Reproducibility:** Are code, data, configuration, package versions, random seeds, and evaluation splits versioned appropriately?
- **Metrics:** Is the metric definition stable? Is a claimed improvement statistically and operationally meaningful? Are sample sizes and uncertainty reported when relevant?
- **Privacy and licensing:** Do datasets, prompts, logs, or artifacts contain PII or restricted content? Are data/model licenses compatible with intended use?
- **Cost and latency:** Does the change alter query scans, model calls, token usage, retries, storage, or p95 latency?

### 4.4 Architecture and maintainability

Review where responsibilities belong, not only whether individual lines work. Watch for business logic in transport layers, database code leaking into domain logic, circular dependencies, hidden global state, duplicated policy, public APIs with unclear ownership, and abstractions that add indirection without buying flexibility. Ask whether the design makes invalid states hard to represent and whether failure handling is consistent with neighboring code.

Avoid demanding an architecture rewrite in a focused PR unless the current approach creates a material risk. If a larger design problem is real but not required to safely land this change, record it as follow-up work with an owner and rationale.

---

## 5. Severity: separate risk from preference

Severity labels help authors prioritize and teams communicate consistently. The exact labels vary by repository. The scale below is an example policy; use the project's labels when they exist.

| Label | Meaning | Typical response |
| --- | --- | --- |
| **S0 — Critical** | Immediate, broad risk such as exploitable critical security exposure, irreversible large-scale data loss, or production outage likely on merge. | Stop the merge; engage the appropriate owner/security/on-call process immediately. |
| **S1 — High / blocking** | A correctness, authorization, data-integrity, compatibility, or reliability defect with material impact under plausible conditions. | Fix before merge or explicitly use the team's documented exception process. |
| **S2 — Medium** | Meaningful defect or maintainability/performance concern with limited scope or a viable mitigation. | Normally fix in this PR if it is in scope; otherwise agree and track a follow-up. |
| **S3 — Low / non-blocking** | Minor clarity, low-risk edge, or optional improvement that does not materially compromise the change. | Optional; do not block a safe change unless project policy says otherwise. |
| **Nit / suggestion** | Preference or polish with little immediate risk. | Clearly mark optional. Avoid accumulating these into a blocking review. |

Severity is about **impact × likelihood × exposure**, adjusted for reversibility and available mitigations. A low-probability issue can still be high severity if it exposes credentials or irreversibly corrupts data. A high-likelihood issue can be low severity if impact is trivial and recovery is easy. Do not assign severity solely based on how easy a fix is or how strongly you feel about it.

### 5.1 What makes a finding actionable?

A useful finding contains:

1. **Location:** the relevant line or behavior.
2. **Observed mechanism:** what the code actually does.
3. **Condition:** when the problem occurs.
4. **Impact:** what a user, system, or data contract experiences.
5. **Evidence:** a test, reproducible input, query count, code path, or documented contract.
6. **Request:** a concrete fix, alternative, or question.

Not every comment needs six paragraphs. A short comment can contain all six parts when the mechanism is clear.

### 5.2 Poor versus improved comments

**Poor:** “This is bad.”  
**Improved:** “blocking: This query interpolates `customer_id` into SQL. If the value comes from a request or file, a quote can change the query's meaning. Can we use a bound parameter (`WHERE customer_id = ?`) and add a test with a quote in the identifier?”

**Poor:** “Why did you do it this way?”  
**Improved:** “question: What constraint led us to keep this transformation in the API handler? The batch job uses the same rule, so putting it in the shared domain layer may prevent the two paths from drifting. Is there a reason the handler must own it?”

**Poor:** “Add tests.”  
**Improved:** “blocking: Could we add a regression case for an empty input batch? The current loop leaves `last_seen` unset, and the next checkpoint calculation fails for a valid empty partition.”

**Poor:** “This function is too slow.”  
**Improved:** “suggestion: This calls `fetch_customer()` once per row. With 50,000 orders that can produce 50,000 round trips. Could we bulk-fetch the distinct customer IDs and join the results in memory? A query-count test would help protect this.”

**Poor:** “Obviously this should be a dict.”  
**Improved:** “suggestion: A dictionary keyed by `order_id` would make lookups explicit and avoid scanning the list repeatedly. If preserving duplicate order IDs is intentional, let's document that contract first.”

**Poor:** “You forgot the docs.”  
**Improved:** “blocking: This changes the public `timeout` default from 5 seconds to no timeout, but the API docs still promise bounded requests. Could we update the docs and keep a finite default unless this behavior change is intentional?”

**Poor:** “LGTM” after skimming a large PR.  
**Improved:** “I reviewed the retry and checkpoint paths and ran `pytest tests/test_ingestion.py -q`. I have not reviewed the IAM policy or migration plan, so I am not the required security/operations approval for this PR.”

### 5.3 Prefix comments by intent

Use prefixes consistently when they help the team:

- `blocking:` — a required fix for a material risk; explain the risk and condition.
- `question:` — genuine uncertainty that should be resolved before the reviewer can assess the behavior.
- `suggestion:` — a proposed improvement; explicitly say if it is optional.
- `nit:` — a minor polish issue; non-blocking.
- `praise:` — specific positive feedback that reinforces good engineering practice.

Prefixes do not determine severity by themselves. A `question:` about whether authorization is enforced may be blocking; a `suggestion:` can identify a serious issue if the label is used incorrectly. Make the requested action explicit.

### 5.4 Example of a concise, high-quality finding

> **S1 / blocking:** `retry_failed_batch()` catches every `Exception`, including `PermissionError`, and immediately retries. In production this can turn a persistent authorization failure into repeated writes and noisy alerts without recovery. Can we retry only the documented transient exceptions, apply bounded exponential backoff, and test that a permission failure is raised without retry?

This comment points to a mechanism, plausible condition, impact, and a verifiable change. It does not criticize the author.

---

## 6. Worked review: a deliberately flawed Python change

This example is a small data-service change that claims to be a behavior-preserving refactor. The diff contains multiple seeded issues. The example is intentionally flawed; do not copy it into production.

### 6.1 PR context

**Title:** `Refactor order export lookup`  
**Claim:** “No behavior changes; simplify the export path.”  
**Contract:** `customer_id` comes from a request or upstream event and is not trusted. The export endpoint must return the orders for one customer, with each order's customer name attached. The database layer uses SQLite in this example, but the review principles also apply to other SQL clients.

### 6.2 Diff with seeded issues

```diff
+import pandas as pd
+
+def export_orders(conn, customer_id):
+    """Return the customer's orders with customer names."""
+    query = f"SELECT id, customer_id, total FROM orders WHERE customer_id = '{customer_id}'"
+    orders = conn.execute(query).fetchall()
+
+    result = []
+    for order in orders:
+        customer = conn.execute(
+            f"SELECT name FROM customers WHERE id = {order[1]}"
+        ).fetchone()
+        result.append({
+            "id": order[0],
+            "customer_id": order[1],
+            "total": order[2],
+            "customer_name": customer[0],
+        })
+
+    # Refactor: keep only orders that have a positive total.
+    return [row for row in result if row["total"] > 0]
```

The diff is syntactically valid Python, but syntax validity is not evidence of correctness. The comment claims a refactor while the final filter changes behavior. The code also adds an unused dependency and has data-access risks.

### 6.3 Findings, prioritized by severity

#### Finding 1 — S1: SQL injection in `customer_id`

**Evidence:** The first query builds SQL with an f-string and embeds `customer_id` inside quoted SQL text. The value is described as untrusted. A crafted value can alter the query syntax; the exact payload depends on the database driver and statement rules.

**Impact:** An attacker may alter the query predicate and expose records outside the intended customer scope. The demonstrated statement is a `SELECT`, so this snippet establishes a confidentiality/filter-bypass risk, not arbitrary write access; other impact depends on the actual query, driver, and database permissions. Even if a particular driver blocks multiple statements, that does not make string interpolation safe.

**Suggested comment:**

> **S1 / blocking:** `customer_id` is untrusted but is interpolated directly into SQL. A crafted identifier can alter the query's meaning. Could we bind it as a parameter (`... WHERE customer_id = ?`) and add a test for an identifier containing a quote? Please parameterize the customer lookup too if it remains dynamic.

#### Finding 2 — S2 or S1 depending on data volume: N+1 database queries

**Evidence:** The code runs one query to fetch orders and then one additional query for every returned order. If there are `n` orders, the query count is `1 + n`.

**Impact:** Latency and database load grow with the number of orders. This can become a production performance incident for large customers or repeated exports.

**Suggested comment:**

> **S2:** The loop issues one customer query per order. For 20,000 orders, that is 20,001 queries even when many rows share the same customer. Can we fetch the customer data in one join or bulk query? A query-count test or representative benchmark would make the improvement measurable.

Because the query is scoped by one `customer_id`, all returned orders should ordinarily refer to that customer, so the join is likely straightforward. Still verify the actual schema and relationship before changing it.

#### Finding 3 — S1/S2: unexpected behavior change hidden inside a refactor

**Evidence:** The return statement removes rows whose `total` is zero or negative. The stated contract says the refactor should preserve behavior; no requirement justifies excluding these rows.

**Impact:** Legitimate zero-total orders, refunds, adjustments, or negative totals may disappear from exports. The severity depends on the domain contract and downstream financial reconciliation, but the behavior change must be resolved before accepting the “no behavior changes” claim.

**Suggested comment:**

> **blocking:** This final filter changes the output by dropping zero and negative totals, but the PR is described as behavior-preserving and the issue does not request this rule. Could we preserve the previous output here and handle any business-rule change in a separately specified PR with tests for refunds/adjustments?

#### Finding 4 — S1/S2: missing related customer row causes an exception

**Evidence:** `fetchone()` can return `None`; `customer[0]` then raises `TypeError`. This can happen if referential integrity is not enforced, the data is inconsistent, or a concurrent deletion is possible.

**Impact:** One orphaned or concurrently changed row can fail the entire export. Whether this should be an explicit error, a skipped row, or a nullable name is a domain decision; silently guessing is not acceptable.

**Suggested comment:**

> **question / potentially blocking:** What should the export do if the customer row is missing? `fetchone()` returns `None` in that case, so `customer[0]` crashes the whole export. Could we define the contract and test the selected behavior (explicit data-integrity error, nullable name, or another documented policy)?

#### Finding 5 — S3: unused dependency

**Evidence:** `pandas` is imported but never referenced.

**Impact:** Unnecessary import-time work and an unjustified dependency surface. If it is newly added to the project, it also increases dependency maintenance and supply-chain obligations.

**Suggested comment:**

> **nit:** `pandas` is not used in this function. Could we remove the import and avoid adding a dependency unless the implementation needs it?

If the import is already part of the module, the immediate risk may be lower. Check the actual dependency diff before assigning severity.

### 6.4 A safer implementation direction

A minimal safer direction is parameterized SQL and a single join. The exact query depends on the actual schema, database, and contract. For a SQLite-like driver:

```python
def export_orders(conn, customer_id):
    """Return all matching orders with their customer names."""
    rows = conn.execute(
        """
        SELECT orders.id, orders.customer_id, orders.total, customers.name
        FROM orders
        LEFT JOIN customers ON customers.id = orders.customer_id
        WHERE orders.customer_id = ?
        """,
        (customer_id,),
    ).fetchall()

    return [
        {
            "id": order_id,
            "customer_id": order_customer_id,
            "total": total,
            "customer_name": customer_name,
        }
        for order_id, order_customer_id, total, customer_name in rows
    ]
```

The `LEFT JOIN` makes a missing customer name representable as `None`, but whether that is the right business behavior must be decided explicitly. If the contract requires referential integrity, an explicit data-integrity error may be preferable. The parameter placeholder syntax varies by driver (`?`, `%s`, named parameters, etc.); use the driver’s supported parameter binding, never string interpolation.

This implementation preserves zero and negative totals. It does not silently introduce a new business filter. A complete fix should include tests for parameterization, missing customer behavior, zero/negative totals, duplicate orders if relevant, and query count or a benchmark appropriate to the performance requirement.

### 6.5 Example tests that express behavior

The following tests illustrate the desired assertions. They assume a SQLite connection and a schema with `orders(id, customer_id, total)` and `customers(id, name)`. Run them with `pytest`; adapt fixture management to your project.

```python
import sqlite3


def make_connection():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE customers (id TEXT PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id TEXT NOT NULL,
            total REAL NOT NULL
        );
        INSERT INTO customers VALUES ('c1', 'Ada');
        INSERT INTO orders VALUES (1, 'c1', 10.0);
        INSERT INTO orders VALUES (2, 'c1', 0.0);
        INSERT INTO orders VALUES (3, 'c1', -2.0);
        """
    )
    return conn


def test_export_preserves_zero_and_negative_totals():
    conn = make_connection()
    try:
        rows = export_orders(conn, "c1")
        # SQL row order is unspecified without ORDER BY; compare by stable ID.
        totals_by_id = {row["id"]: row["total"] for row in rows}
        assert totals_by_id == {1: 10.0, 2: 0.0, 3: -2.0}
    finally:
        conn.close()


def test_export_does_not_match_other_customer_from_quote_input():
    conn = make_connection()
    try:
        rows = export_orders(conn, "c1' OR '1'='1")
        assert rows == []
    finally:
        conn.close()
```

No `pytest` import is needed for these plain test functions: pytest discovers them by their `test_` names. The injection test verifies that the string is treated as a value, not SQL syntax. For the final implementation, add a missing-customer test consistent with the chosen contract and, where needed, a query-count test that observes database calls without coupling excessively to implementation details.

---

## 7. Feedback is a collaboration protocol

Code review comments are written communication. The reviewer has influence, the author has context, and neither person has complete information. Tone and specificity determine whether that difference becomes useful discussion or a status contest.

### 7.1 Give feedback that can be acted on

- **Critique the change, not the person.** Say “this branch permits…” rather than “you don't understand…”.
- **Explain why.** Name the contract, failure mode, performance cost, security boundary, or future maintenance burden.
- **Ask when uncertain.** “Is this intentionally allowed?” is better than declaring a defect without understanding the domain.
- **Be specific and kind.** Avoid “obviously,” “just,” “simply,” sarcasm, and public embarrassment.
- **Separate required from optional.** Mark a blocking finding and explain why it blocks; label polish as a nit or suggestion.
- **Offer an example.** A small code example or GitHub suggestion can reduce ambiguity, but do not prescribe implementation details when multiple designs are valid.
- **Praise specific good work.** For example, “praise: the duplicate-event test protects the idempotency contract we missed last quarter.” Specific praise reinforces practices worth repeating.
- **Respect time zones and response windows.** State the urgency and expected response without assuming everyone is online at the same time.
- **Use inclusive language.** Avoid assumptions about identity or pronouns; use names or they/them when unsure. Seniority does not make an author's code immune to review, and junior reviewers should be able to raise evidence-based concerns.

### 7.2 Receiving criticism without defensiveness

A productive author response follows this pattern:

1. Read the comment fully before replying.
2. Restate the technical concern to ensure you understand it.
3. Ask for a reproduction or clarification if the mechanism is unclear.
4. Decide whether to change the code, provide evidence, or disagree with reasons.
5. Thank the reviewer for useful findings without treating every suggestion as mandatory.
6. Make a focused commit and report what changed and which checks were rerun.
7. Resolve the thread only after the issue is addressed or a decision is recorded.

Do not assume all feedback is correct; reviewers can be wrong. The goal is not unconditional agreement but evidence-based resolution.

### 7.3 Sample exchange: accept and improve

**Reviewer:**

> blocking: The retry loop catches `Exception`, so it retries permission failures as well as timeouts. Can we limit retries to transient errors and cap attempts?

**Author, constructive response:**

> Good catch. The client raises `PermissionError` for a permanent authorization failure. I changed the handler to retry only `TimeoutError` and the client's documented transient exception, capped attempts at four with exponential backoff, and added tests proving that a permission error is raised without retry. I reran `pytest tests/test_client.py -q` and `ruff check`.

This response acknowledges the mechanism, names the change, and reports verifiable evidence.

### 7.4 Sample exchange: disagree respectfully

**Reviewer:**

> suggestion: Could we replace the list with a dictionary for faster lookups?

**Author:**

> Thanks for the suggestion. Duplicate keys are currently meaningful: the output preserves every event in source order, including repeated `customer_id` values. A dictionary would collapse those events and change the contract. I added a test for repeated IDs and a short comment explaining the ordering requirement. If we want deduplication, I think that should be a separate product decision.

**Reviewer:**

> Agreed; I missed the duplicate-event contract. The test makes it clear. Resolving this thread.

The author did not reject feedback emotionally; they explained the contract and added evidence. The reviewer changed their view when the evidence warranted it.

### 7.5 Sample exchange: clarify instead of comment-war

**Reviewer:**

> question: Why is the transformation in the route handler instead of the domain service?

**Author:**

> The handler currently applies an HTTP-specific default before calling the shared transformation. The business mapping itself is duplicated in the batch job, though. I agree that duplication is a drift risk. Would you be comfortable with a small follow-up that moves the mapping into the shared service, while this PR adds the regression test first?

**Reviewer:**

> Yes. Please track the follow-up and include the issue link here. I am comfortable with this PR once the regression test passes.

This works because both parties separate the immediate acceptance criteria from a broader design improvement.

### 7.6 When a disagreement remains

If comments repeat without progress:

1. Summarize the competing options and the concrete trade-off.
2. Identify which fact would decide the question: benchmark, API contract, incident history, test, threat model, or compatibility requirement.
3. Move broad design questions to a short call, RFC, or ADR rather than expanding a line-comment thread.
4. Record the decision and its rationale. Use an owner and follow-up issue for deferred work.
5. Escalate only when risk, policy, or decision ownership requires it—not to win a personal argument.

For reversible choices, timebox debate and often default to the author's reasonable choice. For irreversible, security-sensitive, or externally visible choices, seek the appropriate owner and evidence before proceeding.

---

## 8. Automated checks and human judgment

Automation improves consistency and saves review attention. It does not understand every requirement or production constraint.

### 8.1 Useful automated checks

- Formatters and linters: `ruff format`, `ruff check`.
- Tests and coverage: focused tests, full relevant suite, deterministic test checks, coverage thresholds where meaningful.
- Type checks: `mypy` or `pyright`, depending on the project.
- Security checks: secret scanning, static analysis, dependency vulnerability and license checks, infrastructure policy checks.
- Dependency automation: update PRs with tests and compatibility evidence.
- Repository controls: PR templates, required reviews, CODEOWNERS, branch protection, status checks, merge queue where appropriate.
- Review-noise reduction: danger-style bots for mechanical policy checks and bots that identify missing changelog or documentation entries.

The exact commands and policies belong in the repository's contribution guide and CI. A local check can pass while CI fails due to environment differences; report what actually ran.

### 8.2 What automation cannot reliably decide

Humans must still evaluate whether the code satisfies the issue, whether a test encodes the right behavior, whether a schema change breaks downstream consumers, whether a metric is meaningful, whether an abstraction belongs in a particular layer, and whether the rollout/rollback plan is safe. A security scanner may detect a pattern without understanding reachability; absence of a finding does not prove security.

### 8.3 AI-assisted review

LLM-based review can be a first pass for obvious defects, missing edge cases, suspicious code paths, and comment drafting. Treat its output as untrusted suggestions:

- Verify each claim against the actual diff, code, tests, and contracts.
- Check APIs and package names rather than trusting plausible-looking hallucinations.
- Do not use AI as the sole reviewer or approval authority.
- Follow policy before sending proprietary code, customer data, secrets, or security-sensitive material to an external service.
- Track false positives and missed issues; provide repository-specific instructions where supported.
- Ensure the author understands and can explain every material line of AI-generated code and can validate its behavior, tests, and licenses.

AI assistance changes the volume and source of suggestions, not the responsibility for the final decision.

---

## 9. Advanced review: production risk and change management

The most important review question for a risky change is: **What happens at 3 a.m. if this breaks?** A robust review considers not only whether code works, but also how it fails, how far failure spreads, and whether the team can detect and recover from it.

### 9.1 Risk-based review

Consider these dimensions:

- **Blast radius:** Which customers, jobs, tables, services, regions, or permissions can be affected?
- **Reversibility:** Can the change be rolled back safely after it has written data or changed a public contract?
- **Data loss and integrity:** Can rows be dropped, duplicated, reordered, or partially committed? Can recovery reconstruct the original state?
- **Compatibility:** Can old and new versions run together during a rolling deployment? Are readers and writers compatible with the new schema?
- **Rollout:** Is a feature flag, canary, staged migration, or bounded rollout appropriate?
- **Observability:** What metrics, logs, traces, alerts, and dashboards show success or failure? Are they useful without leaking PII?
- **Fallback:** Is there a known safe mode or rollback path? Who owns it?
- **Security-sensitive changes:** Is a second specialist review required? What changed in the threat model, trust boundaries, permissions, or data exposure?

Risk does not map directly to diff size. A two-line authorization change can be more dangerous than a 300-line isolated refactor.

### 9.2 Feature flags, migrations, and rollback

For feature-flagged changes, review default values, flag ownership, evaluation behavior, cleanup plans, and whether old and new paths remain safe. A flag is not a rollback plan if the new code has already irreversibly changed data.

For schema migrations, review expand/contract strategy where needed: introduce a compatible schema, deploy code that can coexist with old/new forms, migrate data, switch consumers, then remove old fields in a later change. Check lock duration, backfill throughput, checkpoints, idempotency, and how interrupted migrations resume. Do not promise rollback unless reverse operations are genuinely safe.

### 9.3 Security-sensitive changes

Review input validation, output encoding, authentication versus authorization, least privilege, secret handling, dependency provenance, cryptographic usage, logging, and denial-of-service potential. Think about the trust boundary and attacker-controlled inputs, not just whether a static scanner is green. For high-risk changes, request a security specialist or second reviewer according to policy and record threat-model changes.

### 9.4 Design reviews, RFCs, and ADRs before implementation

For broad or irreversible changes, use a design discussion before code review. A useful RFC includes:

- Problem statement and user/business impact.
- Goals and non-goals.
- Current state and constraints.
- Proposed design and architecture diagram where helpful.
- Alternatives considered and trade-offs.
- Compatibility and migration plan.
- Rollout, monitoring, rollback, and security risks.
- Open questions, decision owner, and success criteria.

Record durable decisions in an Architecture Decision Record (ADR). Design review prevents the team from discovering fundamental disagreements after a large implementation has been written. Timebox bike-shedding and distinguish reversible implementation choices from decisions that are expensive to undo.

### 9.5 Review effectiveness and reviewer fatigue

The roadmap highlights a practical review range of roughly 200–400 lines and under 60 minutes as a target for reviewability and attention, alongside awareness of defect-detection rates and reviewer fatigue. Treat these as heuristics, not universal scientific laws: language, change type, familiarity, generated code, and risk all affect review time and defect detection. Reviews are imperfect; use escaped defects and retrospective evidence to improve the checklist rather than assuming a fixed detection percentage. Do not optimize a metric by splitting a coherent change into meaningless fragments or approving too quickly.

Useful techniques include:

- **Two-pass review:** first design and behavior, then implementation details.
- **Review tests first:** understand the claimed contract before evaluating code.
- **Checklist review:** use a short, relevant checklist to avoid omissions.
- **Pair review:** work synchronously when the change is complex, urgent, or difficult to explain asynchronously.
- **Reviewer rotation:** spread knowledge and reduce bottlenecks while retaining specialist review for security or critical domains.
- **Commit-by-commit review:** useful when each commit represents a coherent step; also inspect the final combined diff.
- **Stacked PRs:** separate dependencies into small review units, making ordering and shared context explicit.

### 9.6 Difficult situations

**Large, unreviewable PR:** Ask the author to split it by behavior or offer to pair on a decomposition plan. If splitting is unsafe or impractical, require a design summary and review in focused passes rather than rubber-stamping.

**Repeated nits:** Agree on the convention and automate it. Repeated manual comments are process debt.

**Defensive author:** Keep the discussion on observable behavior, ask questions, and use a reproduction or contract. If communication becomes personal, pause and move to a facilitated discussion.

**Overly strict reviewer:** Ask which risk or standard makes the requested change necessary. Encourage optional improvements to be labeled as such and avoid making subjective preferences blockers.

**Urgent hotfix:** Use the team's emergency policy. Obtain the minimum appropriate review and tests for the risk, document the exception, monitor closely, and perform a post-merge review if full pre-merge review was intentionally deferred. “Urgent” should not become a permanent bypass.

**Rubber-stamp culture:** Require reviewers to state what they reviewed, rotate reviewers, inspect defect escapes, and make it safe to ask for more time. Approval count alone is not evidence of review quality.

**Junior reviewing senior:** Evaluate the claim and evidence, not seniority. Senior engineers should model receiving corrections gracefully.

---

## 10. Review culture at team scale

Good individual comments are not enough if the process creates queues, hidden expectations, or unsafe incentives.

### 10.1 Team agreements

Document:

- Expected review response time and escalation path.
- PR size guidance and exceptions.
- Which changes require CODEOWNERS, security, data, or operations approval.
- What constitutes “ready for review” and the definition of done.
- Required tests, docs, rollout evidence, and labels.
- How to handle urgent changes and post-merge reviews.
- How to resolve disagreements and record architectural decisions.
- When threads should be resolved and how follow-ups are tracked.

A response SLA is a commitment to acknowledge and communicate, not a guarantee that every PR receives a complete review within a fixed number of hours. The roadmap recommends responding within a day; teams should make that realistic across time zones, workload, and specialist availability.

### 10.2 Avoid reviewer bottlenecks

Use granular CODEOWNERS, rotate reviewers for knowledge spread, train new reviewers through pairing, and keep specialist approval for genuinely high-risk areas. Do not make one expert a mandatory reviewer for every small change unless the risk justifies the queue. Monitor the time spent waiting for review as well as active review time.

### 10.3 What to measure—and what not to optimize blindly

Useful signals include PR open-to-merge cycle time, time waiting for first response, review rounds, PR size distribution, escaped defects, revert/hotfix rates, and reviewer concentration. Interpret them together. Fast merges can indicate healthy small PRs or rubber stamps; many comments can indicate thoughtful review or noisy nitpicking. Do not use metrics to rank individual engineers or incentivize superficial approvals.

### 10.4 Review of the reviews

In retrospectives, examine a sample of merged PRs and ask:

- Which important risks did reviewers identify early?
- Which defects escaped and why?
- Were comments actionable and respectful?
- Did automation generate avoidable noise?
- Did the right people review security, schema, and operations risks?
- Were PRs too large or waiting on one reviewer?
- What single process change would improve quality next month?

The purpose is to improve the system, not shame authors or reviewers.

### 10.5 Trunk-based development, long-lived branches, and stacked changes

Small, frequent PRs often reduce integration risk and shorten feedback loops. Long-lived branches can accumulate merge conflicts and make review context stale. Stacked PRs can make large work reviewable when dependencies are explicit, but reviewers must understand the stack order and verify the final integrated result. Choose the workflow that fits deployment and release constraints; do not turn a workflow preference into a universal rule.

---

## 11. Practice lab A: review a seeded-flaw PR

This lab expands the worked example into the roadmap's required set of seeded flaws. The fragments below isolate issues that could appear in a hypothetical PR; they are not one integrated, executable diff. The scenario includes a dependency change, data lookup, retry path, and test. The PR author claims “performance refactor; behavior unchanged.” Identify issues without assuming that every suspicious line is a confirmed defect.

### 11.1 Seeded review notes

Use the following intentionally flawed fragments as a checklist exercise:

```python
# 1. Missing edge case

def newest_timestamp(records):
    return max(record["timestamp"] for record in records)


# 2. Security-sensitive SQL construction

def get_account(cursor, account_id):
    return cursor.execute(
        f"SELECT * FROM accounts WHERE id = '{account_id}'"
    ).fetchone()


# 3. N+1 query pattern

def attach_customer_names(conn, orders):
    output = []
    for order in orders:
        name = conn.execute(
            "SELECT name FROM customers WHERE id = ?", (order["customer_id"],)
        ).fetchone()[0]
        output.append({**order, "customer_name": name})
    return output


# 4. Potentially flaky test
import random

def test_retry_eventually_succeeds():
    assert random.random() > 0.1


# 5. Behavior change inside a refactor

def normalize_amounts(amounts):
    # Previous behavior preserved all values, including zero and negatives.
    return [amount for amount in amounts if amount > 0]


# 6. Poor naming obscures meaning

def f(x):
    return [i for i in x if i["s"] == "ok"]


# 7. Retry policy retries permanent failures and has no delay.
def fetch_with_retry(client, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return client.fetch()
        except Exception:
            if attempt == max_attempts - 1:
                raise
    raise RuntimeError("unreachable")
```

An eighth issue may be a new dependency used for a one-line operation that the standard library already supports. Inspect the dependency manifest and lock-file diff before deciding whether it is actually new or unjustified. The retry example is intentionally minimal: it demonstrates broad exception handling and immediate retries, not a complete production retry implementation.

### 11.2 Review tasks

1. Find at least six concrete findings. For each, record location, condition, impact, evidence, severity, and requested action.
2. Distinguish confirmed defects from questions requiring a domain contract.
3. Write one blocking comment and two non-blocking comments.
4. Identify which checks should be automated.
5. State what you would not block on, and why.
6. For the retry path, identify which exceptions are safe to retry, whether the operation is idempotent, and what attempt/backoff limits should apply. Do not assume every operation can be retried safely.

### 11.3 Worked solution

| Fragment | Finding | Example severity | Why / next action |
| --- | --- | --- | --- |
| `newest_timestamp` | Empty input raises `ValueError` from `max()`; missing timestamp keys can raise `KeyError`. | S2 or S1 if empty partitions are normal and job failure is costly | Define empty-input behavior and missing-field contract; add tests. Do not invent a fallback timestamp. |
| `get_account` | Untrusted `account_id` is interpolated into SQL. | S1; potentially S0 depending on exposure and privileges | Use bound parameters and a quote-containing input test. Review authorization separately; safe SQL does not establish permission. |
| `attach_customer_names` | One query per order; `fetchone()` may return `None`. | S2 for N+1; S1/S2 for missing row depending on contract | Bulk-fetch/join and define missing-customer behavior. Measure query count for representative sizes. |
| Random test | The test passes only about 90% of runs and does not test retry behavior. | S2 | Replace randomness with a deterministic fake that fails a known number of times and then succeeds, or always fails. Assert attempt count and outcome. |
| `normalize_amounts` | Filters values despite a behavior-preserving refactor claim. | S1/S2 depending on financial/data contract | Preserve behavior in this PR or split the intentional business rule into a separately specified change. |
| `f(x)` / `i["s"]` | Names hide the business meaning of the function, input, and status field. | S3 unless ambiguity conceals a correctness or security risk | Ask for domain-revealing names such as `filter_successful_records(records)` and a named status constant/key; do not block solely for personal naming taste if context is already clear. |
| `fetch_with_retry` | Retries every `Exception`, including permanent failures, immediately and without backoff. | S1/S2 depending on side effects and downstream load | Retry only documented transient exceptions, cap attempts, use bounded backoff where appropriate, and test permanent errors are not retried. Confirm that the operation is safe to retry. |
| New dependency | Need to inspect manifest, lockfile, license, maintenance, and actual usage. | S3 or higher if supply-chain/security impact is material | Do not call it unnecessary until the dependency diff and purpose are known. Ask for justification or use standard library if appropriate. |

Severity is context-dependent. The security issue is a clear blocker when the identifier is untrusted. Missing data may be expected or prohibited by the domain contract; review should surface that decision rather than guessing.

### 11.4 Make the flaky test deterministic

A deterministic test can model a client that fails twice with a transient error and succeeds on the third attempt. The production retry function is deliberately abstracted below; adapt exception names and API to your implementation.

```python
class TransientFetchError(Exception):
    pass


class FakeClient:
    def __init__(self, failures_before_success):
        self.failures_before_success = failures_before_success
        self.calls = 0

    def fetch(self):
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise TransientFetchError("temporary failure")
        return {"ok": True}


def test_retry_succeeds_after_two_transient_failures():
    client = FakeClient(failures_before_success=2)
    result = fetch_with_retry(client, max_attempts=3)
    assert result == {"ok": True}
    assert client.calls == 3
```

This test assumes `fetch_with_retry` accepts a client and `max_attempts`, retries `TransientFetchError`, and returns the successful result. It is an illustrative contract, not a complete implementation. Add a separate test showing that permanent exceptions are not retried and that exhausting attempts raises a meaningful error.

---

## 12. Practice lab B: author a PR and respond to review

Create a small change in a practice repository. Do not use a production repository unless you have permission.

### 12.1 Author task

1. Choose a small bug or maintainability improvement with a clear expected behavior.
2. Add a regression test before or with the fix.
3. Make one logical change and keep the diff reviewable.
4. Run relevant tests, linting, and type checks that the repository supports.
5. Use the PR template in Section 2.4 and link the issue.
6. Request a reviewer and ask one focused question if a design trade-off needs input.

### 12.2 Feedback-response exercise

For each comment, choose whether to accept, clarify, or push back. Write the reply and describe what evidence you would provide.

**Comment A:** “This is terrible. Rewrite it.”  
**Comment B:** “Could this use a dictionary?”  
**Comment C:** “The new default timeout is `None`; what happens if the service never responds?”  
**Comment D:** “Please rename `x` to `orders`; this is a nit, not a blocker.”

### 12.3 Worked response examples

- **A — Ask for actionable detail:** “I want to address the concern, but I’m not sure which behavior or design risk you mean. Could you point to the specific path and expected outcome? I can then make a focused change or propose alternatives.” If the reviewer has already described a concrete security or correctness defect elsewhere, address that defect directly rather than using this response to avoid it.
- **B — Decide based on semantics:** “A dictionary would improve lookup time, but it would collapse duplicate IDs and lose source order. The contract currently preserves duplicates. I added a test for that behavior; if deduplication is desired, let's agree on the rule separately.” If duplicate preservation is not a requirement, benchmark or simplify based on evidence.
- **C — Treat as a real risk:** “Good catch. The client can wait indefinitely with `None`. I restored a finite default, added a test that verifies the timeout is passed to the client, and updated the docs. The command `pytest tests/test_client.py -q` passes.”
- **D — Accept a non-blocking improvement:** “Agreed. I renamed it to `orders` and reran the focused test. Thanks for marking it as a nit.” The author can also defer a genuine nit if the change would distract from a safe, urgent fix; communicate the decision and track it when worthwhile.

### 12.4 Retrospective

Write a short retrospective with:

- Which findings improved correctness, security, or maintainability?
- Which comments were preferences rather than risks?
- Did the PR description make the review easier?
- Were tests sufficient and deterministic?
- Was any disagreement resolved by evidence or a design decision?
- What one change would improve your next PR or review?

---

## 13. Practice lab C: review three real open-source PRs

The roadmap asks for review of three real PRs from an open-source project. Do this as a read-only exercise; do not comment on public PRs unless invited or authorized.

For each PR:

1. Read the issue and description before examining the code.
2. Inspect the tests first, then design and implementation.
3. Record findings with severity labels and evidence.
4. Separate confirmed issues from questions and optional suggestions.
5. Read maintainers' comments and decisions only after writing your own notes.
6. Compare what you found with what maintainers found. Do not assume maintainers are infallible; look for evidence and context.
7. Reflect on missed issues, false positives, and any missing domain knowledge.

Suggested review-notes format:

```markdown
## PR: <link or identifier>
**Goal:** <one sentence>
**Scope reviewed:** <files / behavior>
**Evidence available:** <tests, CI, docs, benchmark>

### Findings
- [S1] <location> — <condition, impact, evidence, request>
- [S2] <location> — <condition, impact, evidence, request>
- [S3] <location> — <optional improvement>

### Questions / unknowns
- <contract or system context needed>

### What I missed or learned
- <comparison with maintainer discussion>
```

---

## 14. Capstone: build a team review policy

Produce the following artifacts for a practice repository or a small team:

1. A `CONTRIBUTING.md` section explaining how to prepare, review, and respond to PRs.
2. A PR template containing the checklist, test evidence, risk, rollout, and rollback fields.
3. A one-page **How We Give Feedback** guide covering tone, comment prefixes, severity, disagreement, and escalation.
4. Team agreements for PR size guidance, response SLAs, required reviewers, and definition of done.
5. A short retrospective based on one reviewed PR or a sample of recent PRs.

### Acceptance criteria

- The policy distinguishes blocking defects from nits and explains severity consistently.
- It asks authors to link the issue, state what/why/how tested, identify risks, and self-review the diff.
- It asks reviewers to read the goal, review tests first, inspect design and details, and check happy/failure paths.
- It covers security, data integrity, dependencies, performance, operations, compatibility, and documentation.
- It explains when automated checks should replace manual style comments.
- It sets a realistic response expectation and a route for urgent changes or specialist review.
- It promotes inclusive, evidence-based feedback and a constructive way to resolve disagreements.
- It addresses AI-assisted code/review without outsourcing responsibility or violating data policy.
- It is short enough to use during real work, with detailed reference material linked separately.

---

## 15. Common mistakes and their corrections

### Mistake 1: Reviewing only style

**Why it fails:** Formatting is easy to notice, but correctness, security, data loss, and architecture are often more consequential.  
**Correction:** Automate style checks and use a checklist that starts with behavior and risk.

### Mistake 2: Leaving vague or harsh comments

**Why it fails:** “This is bad” does not tell the author what is wrong, when it fails, or how to validate a fix. Personal wording makes technical disagreement harder.  
**Correction:** Identify the mechanism, condition, impact, evidence, and requested action. Critique code, not people.

### Mistake 3: Letting giant PRs through with “LGTM”

**Why it fails:** Reviewers cannot reliably understand large unrelated changes under time pressure; important defects are hidden in noise.  
**Correction:** Ask for logical splits, review in focused passes, and record scope and evidence. Do not equate approval with line-count compliance.

### Mistake 4: Treating every comment as a blocker

**Why it fails:** It makes review slow and discourages collaboration.  
**Correction:** Label severity and intent; explain what must change before merge and what is optional.

### Mistake 5: Assuming CI green means safe

**Why it fails:** CI can prove only the checks it runs. Tests may omit the broken contract; scanners may miss context-specific risks.  
**Correction:** Read the tests, assess missing scenarios, and examine architecture and rollout risks.

### Mistake 6: Approving because the author is senior or the change is urgent

**Why it fails:** Seniority and urgency do not remove technical risk.  
**Correction:** Evaluate evidence, follow the documented hotfix policy, and perform post-merge review when pre-merge review was deliberately constrained.

### Mistake 7: Taking feedback personally—or accepting it without thinking

**Why it fails:** Defensiveness blocks learning; unconditional acceptance can introduce a new bug or break a contract.  
**Correction:** Separate the person from the code, ask questions, provide evidence, and make a reasoned decision.

### Mistake 8: Letting comments become design debates

**Why it fails:** Line-by-line threads are poor venues for broad architecture choices.  
**Correction:** Summarize options, move to an RFC/ADR or short discussion, record the decision, and return to concrete acceptance criteria.

### Mistake 9: Treating AI review output as proof

**Why it fails:** AI may hallucinate APIs, miss project context, or confidently propose an incorrect fix. It can also expose confidential code if used against policy.  
**Correction:** Verify each suggestion and preserve human accountability.

---

## 16. Self-check questions

Answer without looking back, then compare with the answer guide.

1. What do you review first, and why?
2. Name at least five purposes of code review other than enforcing style.
3. What makes a PR reviewable? Explain the roadmap's fewer-than-400-changed-lines guidance and why it is a heuristic.
4. Rewrite three harsh or vague comments into constructive, actionable comments.
5. What is the difference between a blocking finding, a suggestion, a nit, and a question?
6. Which edge cases should be considered for a data pipeline? Give at least four and explain their relevance.
7. Why is a green CI badge insufficient evidence for a security-sensitive change?
8. How should a reviewer evaluate a refactor that changes output behavior?
9. What should be checked for SQL migrations, notebooks, and ML/AI changes?
10. How can an author disagree with a reviewer without becoming defensive?
11. When should a broad design disagreement move to an RFC or ADR?
12. What are the limitations of AI-assisted code review?
13. How can a team reduce reviewer bottlenecks without removing necessary specialist review?
14. How should an urgent hotfix be reviewed when full pre-merge review is not feasible?
15. Review the seeded-flaw example and list findings by severity within a 20-minute timebox.

### Answer guide

1. Read the PR description and linked issue to understand the goal; then review tests, design, and implementation details.
2. Correctness, design, maintainability, tests, security, performance, consistency, knowledge sharing, and reducing bus-factor risk.
3. One logical change, clear description, test evidence, self-reviewed diff, and focused scope. The <400-line guideline helps limit cognitive load but does not account for every kind of file or risk.
4. A good rewrite identifies the code path, condition, impact, evidence, and action. Example: “blocking: this path retries `PermissionError`, which is permanent; can we retry only documented transient exceptions and add a test that permission failures are not retried?”
5. Blocking means a material issue must be resolved or handled through a documented exception; suggestion is optional improvement; nit is low-impact polish; question requests missing context. A question can become blocking if it concerns a critical contract or risk.
6. Examples: empty partition, duplicate events, late-arriving data, timezone offsets, partial writes, retries, schema drift, malformed upstream payloads, large batches, and permission failures. Select based on the pipeline contract.
7. CI proves only the checks that ran; scanners and tests may not cover the actual threat model, authorization, data exposure, or rollout risk.
8. Ask for behavior-preserving evidence and compare outputs. If behavior change is intended, it needs an explicit requirement, tests, and documentation rather than being hidden inside a refactor.
9. Migrations: idempotency, backfill, locks, compatibility, rollback. Notebooks: outputs, reproducibility, dependencies, data versions. ML/AI: leakage, splits, seeds, metric definitions, model/data/prompt versions, cost/latency, safety, PII, and licences.
10. Restate the concern, explain the contract or evidence, add a test or reproduction, and propose an alternative. Thank the reviewer and resolve the thread when both sides agree on the outcome.
11. When the question spans multiple modules, has significant compatibility or rollout consequences, is difficult to reverse, or cannot be resolved with a local code change. Record the decision and rationale.
12. AI may hallucinate APIs, miss domain context, produce false positives, overlook defects, and expose confidential code if used improperly. Verify suggestions and retain human responsibility.
13. Rotate reviewers, make CODEOWNERS granular, train through pairing, and reserve specialist review for changes whose risk justifies it.
14. Follow the emergency policy, obtain the minimum appropriate review and tests, document the exception, monitor the deployment, and conduct a post-merge review when needed.
15. Strong answers identify SQL injection as a high-priority blocker, N+1 query growth, missing customer-row behavior, the hidden behavior change, a flaky test, broad/immediate retry behavior, unclear naming, and the conditional dependency concern—while stating where severity depends on the domain contract or actual dependency diff.

---

## 17. Completion checklist

Before considering this lesson complete, confirm that you can:

- [ ] Explain the purpose of review and why style should largely be automated.
- [ ] Prepare a focused PR with an issue link, clear description, tests, documentation, risks, and rollback considerations.
- [ ] Self-review a diff using Git and inspect both the complete diff and relevant commits.
- [ ] Review tests first, then design, behavior, failure paths, and details.
- [ ] Use the core checklist and adapt it to SQL, data, notebook, ML/AI, dependency, and infrastructure changes.
- [ ] Write evidence-based comments with explicit intent and severity.
- [ ] Identify seeded issues and distinguish confirmed defects from unresolved contracts.
- [ ] Receive feedback, disagree respectfully, and resolve or escalate discussions constructively.
- [ ] Explain how automated checks and AI review help—and where human judgment remains necessary.
- [ ] Describe team policies for review SLAs, reviewer rotation, design decisions, hotfixes, and review retrospectives.
- [ ] Complete the three-PR practice and the team-policy capstone.

## Further reading and tools

Use these as starting points and confirm the current documentation for your repository and tool versions:

- [GitHub pull request reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests)
- [GitHub suggested changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/commenting-on-a-pull-request)
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Google Engineering Practices: Code Review Developer Guide](https://google.github.io/eng-practices/review/)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

---

**Lesson principle:** Review the change, its contracts, and its risks—not the author's worth. Be rigorous about evidence, explicit about severity, respectful in tone, and honest about what has and has not been verified.
