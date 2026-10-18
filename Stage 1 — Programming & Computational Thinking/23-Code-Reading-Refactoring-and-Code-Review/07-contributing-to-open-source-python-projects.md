# Contributing to Open-Source Python Projects

> **Stage 1 — Programming & Computational Thinking**  
> **Module 1.23 — Code Reading, Refactoring and Code Review**  
> **Lesson 07 of 08**  
> **Audience:** beginner through advanced Python engineers, with data-engineering examples  
> **Assumptions:** Python 3.12+ as a learning baseline; Git; a shell; GitHub CLI (`gh`) is optional. Always follow the target project's actual supported versions and instructions.

## Learning outcomes

By the end of this lesson, you should be able to:

- Select a contribution that is useful, appropriately scoped, and aligned with a project's direction.
- Read project policy and development instructions before changing code.
- Reproduce a reported issue and turn it into a minimal, deterministic test case.
- Fork a repository, configure remotes, create a topic branch, implement a focused change, validate it, and open a professional pull request.
- Work with project-specific formatting, linting, typing, tests, documentation, changelog, compatibility, and release requirements.
- Diagnose CI failures and respond constructively to maintainer feedback.
- Recognize licensing, DCO/CLA, security-disclosure, and AI-assistance obligations.
- Understand how maintainers balance correctness, review capacity, release risk, governance, and sustainability.
- Complete a small real contribution and record evidence of what changed and what was learned.

> **Source-alignment note:** This lesson follows the Module 1.23 roadmap's Lesson 07 sequence: start small and be useful; read project documentation; follow the fork-to-PR workflow; reproduce before fixing; run project checks; collaborate professionally; then progress to substantial contributions, CPython, maintainer practices, legal/security responsibilities, and sustained contribution. The commands below are general examples, not claims about any particular repository's rules. Repository-specific requirements must be verified in that repository.

## 1. Why contribute?

Open source is not simply code published online. It is a collaboration model with maintainers, users, contributors, review conventions, release processes, and legal and security responsibilities.

Useful motivations include:

- **Fix a problem you encountered.** You have direct evidence of the failure and can often provide a strong reproduction.
- **Improve the tools you depend on.** A small documentation clarification or regression test can help many users.
- **Learn unfamiliar engineering systems.** You practise navigating code, tests, packaging, CI, API compatibility, and review.
- **Give back and build trust.** Repeated high-quality contributions make your work visible to the community.
- **Shape a project's future.** Larger proposals can improve APIs, performance, accessibility, reliability, or developer experience.
- **Build a credible portfolio.** A merged PR is useful evidence, but the quality of your reasoning and collaboration matters more than the raw number of PRs.

Do not treat maintainers as a free implementation service. Their time is limited; a well-researched report, a clear reproduction, or a test that documents an ambiguous behaviour may be more valuable than a large patch.

## 2. Choose a contribution that can actually land

### 2.1 Start with a small, useful unit

Begin with work that is low-risk and independently reviewable:

- Fix a documentation example that does not run.
- Clarify a confusing sentence, option, exception, or migration instruction.
- Add a missing test for an already-understood behaviour.
- Reproduce and triage an issue with exact versions and a minimal example.
- Improve a type annotation when the intended contract is clear.
- Fix a small, confirmed bug with a regression test.
- Improve error messages or validation without changing unrelated behaviour.

Labels such as `good first issue`, `help wanted`, and `up-for-grabs` can be useful discovery aids, not promises that an issue is easy or available. Check whether it is still open, whether another contributor is working on it, and whether the maintainers have recently discussed the problem. Some projects run mentorship programmes; read their current application and contribution rules.

### 2.2 Evaluate project health and fit

A project is a better first target when it has clear instructions, a runnable test suite, recent maintainer activity, a respectful community, and a scope that matches your current skills. Inspect:

- Recent releases and commits, not just repository stars.
- Whether maintainers respond to issues and reviews.
- The issue tracker for duplicates and design discussions.
- CI configuration and visible status checks.
- Supported Python versions and dependency constraints.
- How contribution decisions are made and who owns the affected area.
- Whether the issue is appropriate for a first contribution or requires a design discussion.

Potential ecosystems include libraries you already use—such as `httpx`, `pydantic`, `pandas`, pytest plugins, `ruff`/`uv`, scikit-learn, FastAPI, `dbt`, Airflow providers, and integrations. These are examples to explore, not endorsements or claims about current open issues.

### 2.3 A contribution-selection scorecard

Use this scorecard as a thinking aid, not a rigid formula. Rate each item from 0 (poor/unknown) to 2 (strong). If the score is low because you lack evidence, investigate before coding.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| User impact | Unclear or cosmetic only | Some users affected | Reproducible pain or meaningful clarity improvement |
| Scope | Broad/multiple subsystems | Can be narrowed | One coherent change |
| Evidence | Guess or anecdote | Partial reproduction | Minimal reproduction or clear documentation gap |
| Project fit | Conflicts with direction | Direction unclear | Matches existing design and issue discussion |
| Validation | No clear test path | Some checks available | Specific test/check strategy known |
| Policy fit | License/security/policy unclear | Needs clarification | Contribution path and rights are understood |

**Rule of thumb:** if project direction or scope is unclear, open a concise issue/discussion first. Do not invest days in a feature that maintainers may reasonably reject because it duplicates planned work or changes the public API unexpectedly.

## 3. Read the repository's rules before editing

Treat the repository's current documentation as authoritative for that repository. A general tutorial cannot override its actual contribution policy.

### 3.1 Repository-document checklist

- [ ] `README.md`: project purpose, installation, supported environments, quick start, links to contribution docs.
- [ ] `CONTRIBUTING.md` or equivalent: branch/commit conventions, local setup, test commands, formatting, changelog rules, PR process.
- [ ] `CODE_OF_CONDUCT.md`: behavioural expectations and reporting channels.
- [ ] `SECURITY.md`: supported versions and private vulnerability-reporting method.
- [ ] Issue templates and pull-request templates: required reproduction details, checklists, labels, linked issue conventions.
- [ ] Governance docs: decision process, maintainers, steering group, voting/consensus model, escalation path.
- [ ] Roadmap, milestones, discussions, and relevant issues: intended direction and whether the work is wanted.
- [ ] License file and third-party notices: permitted use, distribution obligations, attribution, and compatibility.
- [ ] `pyproject.toml`, tox/nox configuration, Makefile, CI workflows, pre-commit configuration, and test configuration.
- [ ] Changelog/release-note policy: for example, a `towncrier` fragment, `CHANGES.rst`, or no fragment for a docs-only change.
- [ ] Any AI-assistance, sign-off, CLA, employer-IP, or contributor-certification policy.

Do not assume every repository uses all these files. If a file is absent, look for an equivalent documented process; ask politely if a material requirement remains unclear.

### 3.2 Licensing, DCO, and CLA

These concepts are related but not interchangeable:

- **Project license:** states permissions and conditions for using, modifying, and redistributing the project. Common license families include MIT, BSD, Apache-2.0, GPL, and AGPL, but their obligations differ; read the actual license and relevant notices rather than inferring terms from a badge or assuming licenses are interchangeable.
- **DCO (Developer Certificate of Origin):** commonly records that a contributor certifies they have the right to submit the contribution under the project's terms. Projects using DCO may require a sign-off line, often added with `git commit -s`. A sign-off is not the same thing as a cryptographic commit signature.
- **CLA (Contributor License Agreement):** a separate agreement a project may require contributors to accept, often through a bot or web workflow. Its scope and legal effect depend on the actual agreement.
- **Employer and third-party rights:** confirm that you are allowed to contribute work created at work, code owned by an employer, or code copied from another source. Never paste proprietary code into a public issue or PR without authorization.
- **Inbound=outbound policies:** some projects describe contributions as being received under the same license as the project; others require a CLA or have other terms. Read the actual policy rather than assuming a universal rule.

If DCO sign-off is required and you are authorized to contribute, a commit can look like this:

```bash
git commit -s -m "Fix parsing of empty values"
```

This adds a sign-off line using the configured Git identity. It does **not** prove that the identity is accurate or replace a required CLA. If you forgot a sign-off, follow project guidance; amending a local, unpublished commit may be appropriate, but do not rewrite shared history casually.

### 3.3 Security issues must use private channels

If you suspect an exploitable vulnerability, do not publish exploit details, sensitive logs, credentials, or a proof-of-concept in a public issue or pull request. Read `SECURITY.md` and use the specified private advisory, security email, or other approved channel. If no process is obvious, contact the maintainers privately through a legitimate channel without disclosing the exploit publicly. Follow their coordinated-disclosure instructions and avoid making promises about timelines or severity on their behalf.

Never commit secrets to a branch and assume deleting the line is enough: secrets can remain in Git history and CI logs. Revoke/rotate exposed credentials and follow the repository's incident process.

## 4. Set up the contribution workspace

The commands in this section assume a GitHub-hosted repository and an installed Git client. GitHub CLI (`gh`) is optional; authenticate with `gh auth login` if you intend to use authenticated CLI actions. Replace `ORG/PROJECT` and paths with the actual target. Verify the target repository before running commands.

### 4.1 Fork and clone

A common GitHub workflow is:

```bash
gh auth login
gh repo fork ORG/PROJECT --clone
cd PROJECT
git remote -v
```

Typical interpretation:

- `origin` points to your fork, where you can push your topic branch.
- `upstream` points to the original project, from which you fetch current changes.

CLI defaults and prompts can vary. Inspect `git remote -v`; do not assume `upstream` was added automatically. If needed, add it explicitly:

```bash
git remote add upstream https://github.com/ORG/PROJECT.git
git fetch upstream
```

For a non-GitHub host, use that host's documented fork and review workflow. You can also clone a repository you have permission to push to directly; do not fork when the project requires another process.

### 4.2 Create a topic branch

Before branching, check whether the fork's default branch is behind the upstream project. If the repository's policy permits updating the fork's default branch, fetch and fast-forward it when safe; do not reset or force-push shared branches as a shortcut. For example, after confirming the upstream default branch is `main` and your working tree is clean:

```bash
git fetch upstream
git switch main
git pull --ff-only upstream main
git switch -c docs-clarify-timeout-example
```

If the project uses another default branch or a different synchronization policy, follow that policy. If your fork's default branch is already current, the branch-creation command alone is sufficient. Use a short descriptive branch name. Avoid making unrelated changes on `main` or a long-lived personal branch. Confirm the working tree before editing:

```bash
git status --short --branch
git log -5 --oneline --decorate
```

### 4.3 Establish the project's development environment

Read the project instructions and follow the documented environment setup. Typical commands might include:

```bash
uv sync --all-groups
pre-commit install
uv run pytest
```

But these commands are **examples only**: a repository may use `nox`, `tox`, `make test`, a devcontainer, Docker, a custom bootstrap script, or a different dependency manager. Do not blindly run every tool named in this lesson. Use the project's supported setup and avoid installing dependencies globally when an isolated environment is practical.

Before editing, run the smallest documented baseline check that demonstrates the environment works. Record failures and versions. If baseline tests already fail, distinguish them from failures introduced by your patch.

Useful reconnaissance commands:

```bash
find . -maxdepth 2 -type f | sort | head -200
git status --short
rg "the_function_or_option" .
```

If `rg` is unavailable, use your editor or `grep`. Read tests alongside implementation: tests often reveal edge cases, naming conventions, fixtures, and intended compatibility better than guessing from the function alone.

## 5. The complete contribution workflow

1. **Identify the gap.** Find a real user problem, test gap, documentation defect, or agreed feature. Search issues and PRs for duplicates.

2. **Check project fit.** Read the docs, roadmap, relevant design discussions, license, and contribution policy. For non-trivial work, ask before coding.

3. **Reproduce or define expected behaviour.** Record versions, exact steps, expected and actual results, and a minimal example. For docs, verify the example against the current API.

4. **Write a failing regression test when appropriate.** Confirm it fails for the reason you intend to fix, not because of a bad fixture or unrelated environment issue.

5. **Implement the smallest coherent change.** Preserve established API and compatibility unless the project has agreed to a breaking change.

6. **Add supporting material.** Update docs, type annotations, changelog/release fragment, migration notes, or tests as required by project policy.

7. **Validate locally.** Run focused tests first, then the required lint/type/docs/full-suite checks. Inspect the final diff and check for generated files, secrets, unrelated formatting, and accidental API changes.

8. **Commit clearly.** Use the repository's convention. Keep commits coherent; include a DCO sign-off only if required and truthful.

9. **Push and open a PR.** Describe the problem, solution, tests, limitations, risks, and linked issue. Complete the actual PR template.

10. **Respond to review.** Clarify intent, make requested changes, explain evidence-based disagreements respectfully, rerun relevant checks, and reply to every actionable thread.

11. **Finish cleanly.** Verify CI, required approvals, sign-off/CLA status, and release-note requirements. Let maintainers merge according to their policy. Do not claim a PR is merged until the repository shows it.

12. **Reflect.** Record what changed, feedback received, checks run, time spent, and what you would improve next time.

## 6. Reproduce a bug and write a useful report

A bug report should help another engineer observe the same behaviour without reconstructing your whole environment. Include:

- Package version, Python version, operating system, and relevant dependency versions.
- The smallest executable example or fixture that demonstrates the problem.
- Exact command or steps to reproduce.
- Expected behaviour and actual behaviour.
- Full relevant traceback or assertion diff, with secrets and private data removed.
- Whether the issue reproduces on a clean environment and on a supported version.
- A workaround, if one exists, and why you believe the behaviour is a defect rather than an undocumented contract.

### Example issue report (illustrative)

**Title:** `parse_limit` rejects zero even though zero means no rows

**Environment:** Python 3.12.4, `sample-utils` 0.8.1, Linux x86_64. Versions and package name are illustrative.

**Reproduction:**

```python
from sample_utils.pagination import parse_limit

assert parse_limit(0) == 0
```

**Expected:** `0` is accepted as a valid limit representing zero rows.

**Actual:** `ValueError: limit must be positive`.

**Evidence (illustrative, not independently executed):** The example assumes the documented contract says a limit is a non-negative integer and the shown implementation rejects zero. In a real report, include the exact command, environment, and observed output only after reproducing it; do not claim a clean-environment run unless you performed one. No production data or secrets should be included.

**Possible fix:** Accept zero while continuing to reject negative values and booleans if the API treats booleans as invalid integers. I am happy to submit a regression test first; please let me know if the intended contract differs.

This is a teaching example, not a report about an actual project or an independently verified package release.

### Minimal reproduction discipline

Start with the smallest code that still fails. Remove unrelated data, services, mocks, threads, dependencies, and configuration one at a time. Preserve the behaviour, not the incidental complexity. If the issue only appears with a particular database or OS, state that constraint instead of pretending the example is universal.

For data-engineering projects, protect privacy: use synthetic rows, redact customer identifiers, and remove secrets from SQL, logs, notebooks, and screenshots. A minimal reproduction must be safe to publish.

## 7. A focused Python bug fix with a regression test

This toy example illustrates test-first reasoning. It is not a patch for a real library; verify the target project's API and style before adapting it.

Suppose `parse_limit` accepts non-negative integers, but its first implementation rejects zero and accidentally accepts `True` because `bool` subclasses `int` in Python.

### 7.1 Initial implementation with defects

```python
# pagination.py

def parse_limit(value: int) -> int:
    if not isinstance(value, int) or value <= 0:
        raise ValueError("limit must be positive")
    return value
```

### 7.2 Define the contract in tests

```python
# test_pagination.py
import pytest

from pagination import parse_limit


@pytest.mark.parametrize("value", [0, 1, 25])
def test_parse_limit_accepts_non_negative_integers(value: int) -> None:
    assert parse_limit(value) == value


@pytest.mark.parametrize("value", [-1, -25, True, False, 1.5, "2", None])
def test_parse_limit_rejects_invalid_values(value: object) -> None:
    # The exception type is the contract under test here; the original
    # implementation uses a different message even for otherwise-correct
    # rejection cases. Do not make the pre-fix test fail only on message text.
    with pytest.raises(ValueError):
        parse_limit(value)  # type: ignore[arg-type]
```

Run the focused test against the initial implementation. The `0` case should fail; `True` should also expose the type-contract bug. A good regression test demonstrates the defect before the fix and passes afterward.

### 7.3 Minimal fix

```python
# pagination.py

def parse_limit(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("limit must be a non-negative integer")
    return value
```

The `bool` check is explicit because `isinstance(True, int)` is true. Whether booleans should be rejected is a contract decision; here it is part of the stated example contract. A project may instead use a different validation style or exception type. Match its established conventions.

### 7.4 Validate the patch

In a clean environment with pytest installed:

```bash
python -m pytest -q test_pagination.py
```

Expected interpretation: all parameterized cases pass. Also run the project's lint/type checks and any broader tests required by its instructions. Tests that pass locally do not prove that the whole project is correct; CI may cover additional Python versions, operating systems, optional dependencies, or documentation builds.

### 7.5 Review the diff like a maintainer

```bash
git diff --check
git diff --stat
git diff -- pagination.py test_pagination.py
git status --short
```

Ask: Is the change limited to the reported contract? Does the test fail on the old implementation? Are invalid types covered? Does the error message need a docs update? Is a changelog fragment required? Did generated files or local environment artifacts enter the patch?

## 8. Tests, style, typing, docs, and compatibility

Follow the repository's prescribed checks rather than creating a competing style system.

### 8.1 Testing strategy

- Start with the narrowest relevant test to get fast feedback.
- Add a regression test for a bug so the old failure remains covered.
- Cover boundary values and failure paths, not only the happy path.
- Use existing fixtures and factories where appropriate; avoid building a parallel test framework.
- Avoid flaky tests that depend on wall-clock timing, uncontrolled network services, mutable shared state, or random seeds without control.
- For data pipelines, test schema and nullability, duplicate and empty inputs, ordering assumptions, timezone boundaries, idempotency, and error handling when relevant.
- Do not weaken or delete a test just to make CI green. If behaviour is intentionally changing, document the contract change and obtain maintainer agreement.

### 8.2 Formatting, linting, and types

Inspect the project's configuration for tools such as Ruff, Black, mypy, pyright, pre-commit, or project-specific checks. Avoid introducing a new tool or reformatting unrelated files unless maintainers have asked for it.

Typical examples, only when configured by the project:

```bash
pre-commit run --all-files
ruff check .
ruff format --check .
mypy src/
```

Use the project's exact command, version, and configuration. A command that is valid in one project may be irrelevant or wrong in another.

### 8.3 Documentation and changelog

Documentation is executable in many projects. Run doctests or documentation builds when applicable; verify code snippets in the supported environment. Check whether the project requires a changelog fragment (for example, a `towncrier` entry), release note, migration guide, or no entry for certain changes. Never invent a required filename or category—read the local policy and inspect recent accepted PRs.

### 8.4 Supported versions and API stability

A patch that works only on your newest local Python may break the project's supported matrix. Inspect `requires-python`, CI matrices, dependency constraints, and deprecation policy. Public API changes may require a proposal, deprecation period, feature flag, migration note, or a major release. Consider Windows/macOS/Linux differences, CPU architecture, optional dependencies, and free-threaded Python compatibility when relevant to the project.

## 9. Commits and pull requests that are easy to review

### 9.1 Small, coherent commits

Use commit messages that explain the change. Many projects prefer imperative subjects and concise bodies explaining why; others use Conventional Commits or another format. Follow local convention rather than enforcing a universal template.

Examples of clear subjects:

- `Fix zero limit validation`
- `Document retry timeout precedence`
- `Add regression test for empty batch`

Avoid a commit history containing unrelated formatting, a dependency upgrade, a broad refactor, and the reported bug fix all mixed together. Atomic commits make review, backporting, and regression investigation easier. If maintainers prefer squash merges, they may preserve only the final PR-level message; ask before rewriting commits when review context matters.

### 9.2 Example PR description

Use the repository's template first. This generic example shows useful content without asserting that a real PR was submitted.

```markdown
## Summary
Allow `parse_limit(0)` and reject boolean values, matching the documented
non-negative integer contract.

## Motivation
The previous validation rejected zero and accepted `True` because `bool`
is a subclass of `int`.

## Changes
- Accept non-negative integers, including zero.
- Reject booleans and other invalid input types.
- Add parameterized regression tests for boundary and invalid values.

## Validation
- `python -m pytest -q test_pagination.py` — passed
- `git diff --check` — passed
- [Add project-required lint/type/docs checks here, with actual results]

## Compatibility and risk
No public signature change. The accepted input domain changes to match the
stated contract; callers relying on zero being rejected should be checked.

## Related issue
Fixes #123
```

The command results in this example are illustrative. In your own PR, report only checks you actually ran and their actual outcomes. Link the relevant issue if one exists; do not invent an issue number or use `Fixes #123` as a literal placeholder.

### 9.3 GitHub CLI example

After pushing the branch, a common workflow is:

```bash
git push -u origin fix-zero-limit
gh pr create --base main --title "Fix zero limit validation" --body-file pr-description.md
```

Replace `main` with the project's actual target branch. If the project uses another host or PR workflow, use its instructions. Review the proposed title, base branch, template, labels, linked issues, and diff before submitting.

## 10. CI failures: diagnose evidence, not symptoms

A failing CI job is information. Do not immediately change code to silence it.

### 10.1 Triage sequence

1. Identify the failing job, exact command, Python/runtime version, OS, and dependency set.
2. Read the first meaningful failure, not just the final “job failed” line.
3. Determine whether it is a test assertion, lint/type error, build/package error, docs failure, network/service issue, timeout, or infrastructure failure.
4. Reproduce the same command and relevant environment locally if possible.
5. Compare against the target branch's baseline and inspect the changed lines.
6. Fix the root cause or document evidence that the failure is unrelated/flaky; do not hide it by skipping tests without agreement.
7. Re-run the focused check, then the required broader checks.
8. Update the PR with concise evidence and any remaining limitations.

### 10.2 CI troubleshooting exercise

A hypothetical PR passes on Python 3.12 locally but CI fails on Python 3.9 with:

```text
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
  File "src/sample_utils/parser.py", line 18, in <module>
    def parse(value: str | None) -> str | None:
```

This is an illustrative failure for Python 3.9 when annotations are evaluated normally: the parser accepts `|` as an expression, but Python 3.9 does not implement the PEP 604 type-union operation for `type` objects, so evaluating the annotation can raise `TypeError` during module import. With `from __future__ import annotations`, evaluation is postponed, so the immediate failure can differ; tools that later evaluate type hints may still need version-aware handling. Python 3.10+ supports PEP 604 unions. More importantly, inspect the actual traceback, source, interpreter version, and annotation settings rather than blindly changing the line. If the project supports Python 3.9, use the project's compatible typing style, such as `Optional[str]` with `from typing import Optional`, where appropriate. If the actual failure is a `SyntaxError`, identify the syntax that Python 3.9 truly cannot parse rather than attributing it to `str | None` alone.

**Worked troubleshooting path:**

- Check the traceback line and surrounding function.
- Check `requires-python` and the CI matrix to confirm Python 3.10 is supported (and whether 3.9 is also supported).
- Decide whether the code is an annotation or a runtime expression.
- If it is a type annotation and compatibility includes Python 3.9, use the project's compatible typing style, for example `Optional[str]` with `from typing import Optional`, if consistent with project conventions.
- Add or run the relevant test/type check on the oldest supported interpreter, not only the newest local interpreter.
- Report the actual diagnosis and checks in the PR.

Do not edit CI to remove a supported Python version merely to make the PR pass. If the support policy itself should change, that is a separate design/release decision.

### 10.3 Distinguish product failures from infrastructure failures

A timeout, unavailable external service, rate limit, or flaky test may be unrelated to your patch, but “flaky” is a hypothesis requiring evidence. Compare reruns and baseline results, inspect logs, and follow maintainer policy. If a rerun is permitted, state that the result is a rerun and do not claim the first failure never happened. Avoid repeatedly rerunning expensive jobs without a reason.

## 11. Responding to maintainer feedback

Maintainers may ask for a narrower scope, different tests, a design discussion, a changelog entry, or no change at all. Respond to the technical point rather than treating the review as a judgment of you.

### 11.1 A reliable response pattern

1. Read the whole comment and surrounding discussion.
2. Identify whether it is a blocking correctness issue, a request for clarification, a preference, or a design disagreement.
3. Ask a concise question if the requested change is ambiguous.
4. Make the change and point to the commit/line, or explain the trade-off with evidence.
5. Re-run relevant checks and report the result.
6. Reply to every actionable thread and resolve threads only when the project convention permits it—do not resolve another reviewer's thread prematurely.

### 11.2 Constructive response examples

**Maintainer:** “Please add a regression test for `None`; the current test only covers integers.”

**Good response:** “Agreed. I added a `None` case in `test_parse_limit_rejects_invalid_values` and verified that it raises the documented `ValueError`. The focused test passes.”

**Maintainer:** “This helper seems unnecessary; can we keep the validation inline?”

**Good response:** “That makes sense for this single call site. I removed the helper and kept the test at the public API boundary. If another caller appears later, we can extract it with evidence of reuse.”

**Maintainer:** “I don't think zero should be accepted.”

**Good response:** “Thanks for clarifying. I based the patch on the current docs saying ‘non-negative’. Is the intended contract actually positive-only? If so, I can update the test and docs accordingly; I wanted to confirm before changing the public behaviour.”

**You disagree with a requested change:** “I see the concern about complexity. I kept the explicit boolean check because `bool` is an `int` subclass and the documented contract excludes booleans. I added a focused test demonstrating the edge case. If the project prefers to accept booleans, I can adjust the implementation and docs.”

**You cannot continue:** “I’m sorry, I won’t be able to finish this contribution this month. The current branch contains only the reproduction and test draft; I’ll leave a concise summary here so another contributor can continue.”

Avoid sarcastic replies, silent abandonment, repeated pings, or statements such as “this is obvious.” Maintainers may take days or weeks; follow stated response expectations and be patient. A respectful “no” is a normal part of open-source work.

### 11.3 Updating a PR safely

Make the requested change on the same topic branch and push it. New commits preserve review context; some projects prefer squashing before merge. If maintainers ask you to rebase, understand whether the branch is shared before rewriting commits. Do not force-push over another contributor's work. If force-pushing your own PR branch is appropriate, prefer `--force-with-lease` over `--force`, and communicate first when others may be using the branch.

## 12. Contributing to documentation and tests

Documentation contributions can be technically significant. A broken example can teach the wrong API; an ambiguous migration guide can create production incidents.

Before editing docs:

- Check whether the documentation is generated from docstrings, Markdown, reStructuredText, notebooks, or another source.
- Verify the example against the target project's supported version.
- Preserve terminology, headings, links, and accessibility conventions.
- Run the documented docs build or link checker where available.
- Avoid committing generated output unless the repository expects it.

Before adding tests:

- Learn the project's fixture strategy and test naming conventions.
- Determine whether the test belongs at unit, integration, property, regression, or compatibility level.
- Use deterministic inputs and isolate external services.
- Ensure the test would fail against the buggy implementation.
- Avoid asserting incidental implementation details when a stable public contract is what matters.

Reviewing others' PRs and triaging issues are also contributions. Reproduce a reported problem, identify a duplicate, run a proposed patch in a disposable environment, or use history investigation (`git log`, `git blame`, `git bisect`) to narrow the likely regression. Share findings respectfully and avoid presenting speculation as fact.

## 13. Advanced contributions: design, releases, and maintainability

### 13.1 Discuss substantial changes before implementation

Features that alter public APIs, architecture, dependency footprint, performance, security posture, or compatibility deserve a proposal before a large implementation. Use the project's preferred issue/discussion/RFC/PEP-like process. A useful proposal states:

- User problem and evidence.
- Desired behaviour and non-goals.
- Alternatives considered and why they were rejected.
- Public API and backward-compatibility implications.
- Testing and benchmark plan.
- Documentation, migration, and release-note plan.
- Rollout, feature flag, deprecation, and rollback strategy where relevant.

Implement in stages. For a risky feature, first land tests or a narrow internal change, then add the API, documentation, and migration guidance as agreed. Do not smuggle a public behaviour change into a “refactor” PR.

### 13.2 Performance and benchmark changes

Performance claims need reproducible evidence. Use the project's benchmark tooling (for example, `asv` or `pytest-benchmark` if already adopted), document hardware/runtime conditions, compare against a meaningful baseline, and consider variance. Do not add brittle CI thresholds without maintainers' agreement. Include regression tests for correctness even when the change is motivated by speed.

### 13.3 CPython and the standard library

CPython has a distinct contribution process. Read the current Python Developer's Guide, issue/PR conventions, CLA requirements (including any PSF contributor agreement that applies), test instructions, news-entry rules, and backport guidance before attempting a code change. Language or standard-library changes may need a PEP or prior discussion on the appropriate Python Discourse category; consult the current process rather than assuming every change needs a PEP. Core mentorship and newcomer-friendly issues can help you find an appropriately scoped task. For changes requiring a news entry, CPython commonly uses `blurb` and its configured news-fragment workflow; verify the current Developer's Guide and branch policy. The current CPython guide also asks contributors to include the issue identifier in the PR title in its `gh-NNNNN` style when an issue exists, and provides `make patchcheck` as a Unix/macOS pre-submission checklist; follow the guide for platform-specific equivalents and exceptions (for example, docs-only changes may not need a NEWS entry). Avoid force-pushing or rewriting a CPython PR's reviewed commit history unless maintainers explicitly ask, because reviewers may rely on individual commits. Start with documentation, tests, or a small bug. A debug build may use:

```bash
./configure --with-pydebug
make -j2                              # bounded parallelism; adjust to available memory/cores
./python -m test test_some_module -v  # targeted test; replace with a real test name
./python -m test -j0                 # broad test-suite run; can take substantial time
make patchcheck                       # Unix/macOS patch checklist; follow current guide
```

These commands are platform/build-system dependent and can require build tools and libraries. `make -j` without a job limit can start an unbounded number of jobs on GNU make, so this example uses `-j2` as a conservative baseline; adjust deliberately for your machine. Follow the current Developer's Guide for your platform; do not assume the commands work unchanged everywhere. PEPs, discussions, tests, and implementation comments can explain design intent. For language or standard-library changes, expect more scrutiny around semantics, compatibility, portability, and long-term maintenance.

### 13.4 Packaging and release engineering

A code fix may need more than a green unit test. Understand the project's release workflow:

- Does it use a changelog fragment or curated release notes?
- Are wheels and source distributions built in CI?
- Are supported Python versions and platforms tested?
- Are dependencies pinned, ranged, or resolved from a lock file?
- Are API deprecations tied to a release schedule?
- Are releases signed or published through trusted publishing?
- Does a maintenance branch need a backport label or separate PR?

Do not publish a package or cut a release unless you have the authority and the project has assigned that responsibility. Contributor PRs should not add credentials, tokens, or unapproved publishing steps. Maintainers may need to verify provenance, signatures, artifacts, and release notes separately from the code review.

### 13.5 Maintainer perspective and sustainability

Maintainers do much more than review code: issue triage, release management, CI maintenance, dependency updates, governance, security response, community moderation, documentation, and burnout prevention. Governance varies: a project may have a BDFL-style model, a steering council, or a foundation-backed structure (for example, PSF, NumFOCUS, Linux Foundation, or Apache governance). Learn the target project's actual decision and escalation process rather than assuming one model. Maintainers also protect release credentials and accounts with controls such as 2FA and trusted publishing where supported. A patch that seems small to a contributor can create long-term support cost.

As a contributor:

- Make review easier by supplying evidence and keeping scope coherent.
- Respect the project's code of conduct and escalation process.
- Avoid demanding a deadline from volunteer maintainers.
- Accept that a project may decline a contribution due to direction, capacity, maintenance cost, or licensing.
- Consider funding and sustainability mechanisms when appropriate (for example, project sponsorship programmes), without making support conditional on accepting your patch.

As you gain experience, help improve issue templates, contributor docs, CI reliability, onboarding, and review culture—not just application code.

### 13.6 AI-assisted contributions

Use AI tools only in ways permitted by the project's policy and your employer's rules. Do not upload confidential code, security-sensitive reports, personal data, or licensed material to an unapproved service. You remain responsible for every line you submit.

Verify generated code, tests, API names, citations, licenses, and claimed test results. Check for hallucinated functions, unnecessary dependencies, copied code with unclear provenance, and tests that merely restate the implementation. Disclose AI assistance when the project requires it. Never claim you ran a check you did not run, and do not submit a patch you cannot explain.

### 13.7 Forks and vendoring as a last resort

If upstream cannot address a necessary fix, a temporary fork or vendored patch may be justified, but it creates an ongoing maintenance obligation. Before doing so, check license compatibility, security updates, divergence, patch ownership, and an exit condition. Prefer contributing upstream where practical; track the upstream issue and remove the fork/patch when the supported fix is available. Do not copy code under incompatible license terms.

## 14. Security and responsible disclosure

Security work requires a different communication path from ordinary bug reports.

- Read `SECURITY.md` and use the project's private reporting mechanism.
- Avoid public details that enable exploitation before a fix or coordinated disclosure.
- Share only the minimum information needed with the authorized security team.
- Do not include real customer data, tokens, private keys, or internal hostnames in a public reproduction.
- Follow coordinated-disclosure instructions and applicable legal/employer policies.
- If you accidentally expose a secret, rotate or revoke it immediately and follow the incident process; removing it in a later commit is insufficient.
- Do not test against systems you do not own or have permission to assess.

A public issue can say that you found a potential security problem and are using the documented private channel, but do not include the exploit or sensitive details there. Follow the project's policy on when a public advisory or CVE is appropriate; coordinate any CVE request with the authorized project/security team rather than self-assigning or unilaterally disclosing before coordination.

## 15. Licensing, attribution, and provenance in practice

Before copying code, a test fixture, an algorithm implementation, or documentation from elsewhere:

1. Identify its source and license.
2. Check whether the source license is compatible with the destination project's license and contribution policy.
3. Preserve required notices and attribution.
4. Confirm that your employer permits the contribution.
5. Do not assume that a short snippet, an online answer, or AI-generated text is automatically free of obligations.
6. If the status is unclear, ask the project's maintainers or your legal/compliance contact before submitting it.

This lesson is educational, not legal advice. DCO and CLA terms vary. Read the actual text and ask for qualified advice when the rights or obligations are material.

## 16. Inner-source and cross-team contributions

The same habits apply to internal repositories: read contribution docs, find owners, use CODEOWNERS and issue templates, make a small change, add tests, document risk, and request review from the correct team. Inner-source can reduce platform-team bottlenecks, but access controls, data classifications, internal security policies, and release approvals still apply. Do not treat an internal repository as permission to expose secrets or proprietary code externally.

## 17. Common mistakes and how to avoid them

| Mistake | Why it hurts | Better approach |
|---|---|---|
| Starting a large feature without discussion | May conflict with roadmap or impose unwanted maintenance cost | Ask about direction and propose a narrow design first |
| Ignoring `CONTRIBUTING.md` | Wastes review time and creates avoidable CI failures | Read the instructions and inspect recent accepted PRs |
| Reporting “it doesn't work” | Maintainers cannot reproduce it efficiently | Include versions, minimal code, expected/actual behaviour, and traceback |
| Fixing without a regression test | The bug can return silently | Demonstrate failure before the fix and pass after it |
| Changing unrelated code | Increases review burden and regression risk | Keep the diff focused; separate follow-up work |
| Skipping CI failures | Can hide real compatibility or correctness defects | Diagnose, reproduce, and report evidence |
| Adding a new dependency casually | Adds supply-chain, packaging, and maintenance cost | Prefer existing tools; justify the dependency and obtain agreement |
| Posting vulnerability details publicly | May expose users before a fix exists | Use `SECURITY.md` and private reporting channels |
| Assuming DCO equals CLA | Can leave legal requirements unmet | Follow the exact project policy and agreement |
| Force-pushing without coordination | Can discard review context or collaborators' work | Coordinate; use safe branch practices and `--force-with-lease` only when appropriate |
| Treating review as personal criticism | Makes collaboration harder | Ask questions, respond to evidence, and accept project decisions professionally |
| Claiming tests passed without running them | Damages trust and can mislead maintainers | Report exact commands and actual results |
| Submitting AI-generated code you cannot explain | Increases correctness, provenance, and licensing risk | Verify, understand, test, and follow disclosure policy |
| Abandoning silently | Leaves maintainers uncertain whether work is active | Send a concise status update if you cannot continue |

## 18. Practical lab: contribute a documentation or test fix

This lab can be completed against a real project or a private practice repository. For a real upstream contribution, use the project's current policies and do not claim success until the host confirms the PR state.

### Part A — Discovery

1. Pick a Python project you use or understand.
2. Read its README, `CONTRIBUTING.md`, code of conduct, security policy, license, PR template, and relevant roadmap/issues.
3. Identify a small docs/test gap that is clearly within scope.
4. Search issues and PRs to avoid duplication.
5. Write down the expected behaviour and why the contribution is useful.

### Part B — Reproduction

For a bug, create a minimal reproduction and capture environment versions. For a documentation issue, run the example or docs build and record the mismatch. Remove private data and secrets before sharing anything.

### Part C — Implementation

1. Fork/clone and configure remotes.
2. Create a descriptive topic branch.
3. Set up the documented environment.
4. Add a focused test or docs correction.
5. Run focused checks, then the repository-required checks.
6. Inspect `git diff --check`, `git diff --stat`, and the full diff.
7. Add a changelog fragment or other release material if required.
8. Commit using the repository's convention and any required sign-off.

### Part D — PR and review

1. Open a PR using the actual template.
2. Describe the problem, solution, tests, limitations, and related issue.
3. Wait for CI and review; respond to each actionable comment.
4. If you disagree, state the contract, evidence, and trade-off calmly.
5. If you cannot continue, leave a concise status note.
6. Record the final state honestly: opened, revised, accepted, merged, or declined.

### Deliverable

A link to the PR or private practice change, a concise reproduction or documentation-gap statement, test/check evidence, a short retrospective, and a note about maintainer feedback. If the contribution is not submitted or merged, say so explicitly.

## 19. Three-contribution capstone

The roadmap's capstone is to complete three contributions to an actively maintained Python project—or, if network/time limits prevent upstream submission, run the workflow in a private mirror with a mentor.

### Contribution 1: documentation or test improvement

- Select a real gap.
- Follow project conventions.
- Run the relevant docs/test checks.
- Submit the PR if appropriate.

### Contribution 2: triaged bug with minimal reproduction and history evidence

- Search for duplicates.
- Reproduce the bug and capture exact versions.
- Use history investigation (`git log`, `git blame`, and, when a reliable good/bad test is available, `git bisect`) to identify a likely offending change; record the bisect result and tested revisions. If bisect is not reliable or feasible, document why rather than inventing a result. Treat history as evidence, not proof of intent.
- Add a regression test or clear triage report.
- Submit the findings or PR through the documented process.

### Contribution 3: small bug fix

- Confirm the expected contract with existing docs/tests or maintainer discussion.
- Write a regression test, implement the minimal fix, and update docs/changelog as required.
- Run the project's checks and compatibility matrix where available.
- Submit a focused PR and respond to review.
- The target outcome is maintainer acceptance, including the required regression test and changelog entry. Do not describe this contribution as accepted or merged until the project confirms that status. If it is declined or remains pending, record that outcome honestly and capture the reason/next step; a private-mirror exercise is practice evidence, not upstream acceptance.

### Retrospective and portfolio entry

For each contribution, record:

- Project and PR/issue link (if public and appropriate).
- Problem and user impact.
- Your approach and relevant alternatives.
- Tests/checks actually run and their results.
- Review rounds, feedback, and how you responded.
- Time spent and the biggest lesson learned.
- Final status, without implying acceptance if it was not accepted.

The goal is not to accumulate PR counts. It is to demonstrate sound engineering judgement, reproducible evidence, maintainable changes, and respectful collaboration.

## 20. Self-check questions with worked answers

### Q1. List the steps from finding a library bug to having a fix merged.

**Worked answer:** Read the project docs and policies; search issues/PRs; reproduce with versions and a minimal example; ask for direction if scope is unclear; write a failing regression test; implement the smallest fix; update docs/changelog as required; run local checks and inspect the diff; commit and push a topic branch; open a PR with evidence; respond to review and CI; satisfy policy and approval requirements; verify the merge state on the hosting platform. The merge is controlled by project maintainers and policy, not guaranteed by submitting a PR.

### Q2. What makes a bug report maintainers appreciate?

**Worked answer:** A concise title; exact versions/platform; a minimal, safe reproduction; expected versus actual behaviour; relevant traceback/logs; evidence that the issue is reproducible; duplicate search; and no secrets or private data. A suggested fix can help, but should be labelled as a hypothesis unless confirmed.

### Q3. A project requires DCO sign-off. Is `git commit -s` the same as signing a commit with GPG or SSH?

**Worked answer:** No. `-s` adds a sign-off trailer to the commit message. Cryptographic signing uses a signing key and is verified differently. A project may require one, both, or neither; follow its actual policy.

### Q4. CI fails only on an older supported Python version. What should you do first?

**Worked answer:** Read the first meaningful traceback, confirm Python 3.9 is supported, inspect the relevant source and CI command, reproduce on that interpreter if possible, and determine whether the failure is syntax, runtime behaviour, dependency resolution, or infrastructure. Fix the root cause and test the oldest supported version. Do not remove a supported CI job merely to get a green check.

### Q5. A maintainer declines your feature because it does not fit the roadmap. What is the professional response?

**Worked answer:** Thank them for explaining, ask a clarifying question only if it will help, and accept the decision. You may ask whether a smaller alternative would be useful, but do not pressure maintainers or continue expanding the PR against their stated direction.

### Q6. You discover a possible remote-code-execution vulnerability. What do you post publicly?

**Worked answer:** Do not post exploit details or a proof-of-concept publicly. Read `SECURITY.md` and report through the documented private channel. Share only the necessary information with authorized maintainers and follow their coordinated-disclosure process.

### Q7. You copied a helper from another repository. What should you verify?

**Worked answer:** Source and license, compatibility with the destination project's license and contribution policy, required attribution/notices, employer rights, and any project rules on third-party or AI-generated code. If unclear, stop and ask before submitting.

### Q8. Your local tests pass but CI fails on documentation. What is the next safest step?

**Worked answer:** Identify the exact docs job and command, reproduce the build or link check locally, inspect whether the changed docs example or link caused the failure, fix it, and rerun the docs check. Do not claim the PR is fully validated based only on unit tests.

## 21. Final submission checklist

- [ ] The contribution solves a real, scoped problem and fits project direction.
- [ ] I read the repository's current contribution, conduct, security, licensing, and PR instructions.
- [ ] I checked for duplicate issues/PRs and asked before making a substantial change.
- [ ] The bug or documentation gap is reproducible and described with evidence.
- [ ] The change is focused and follows established project conventions.
- [ ] Tests demonstrate the intended behaviour; regression tests fail before and pass after the fix where appropriate.
- [ ] Required docs, changelog, type annotations, compatibility, and release material are updated.
- [ ] I ran and reported the checks I actually ran.
- [ ] The final diff contains no secrets, private data, unrelated changes, or unapproved generated files.
- [ ] Licensing, attribution, DCO/CLA, employer, and AI-policy requirements are satisfied.
- [ ] Security concerns were reported privately.
- [ ] The PR description explains the problem, solution, validation, risks, and links.
- [ ] I responded to review comments respectfully and did not rewrite shared history carelessly.
- [ ] I recorded the real final state and a short retrospective.

## Further reading

Use the current, project-specific source of truth first:

- The target repository's `README`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, license, issue/PR templates, governance documents, and CI configuration.
- The official Python Developer's Guide for CPython and standard-library contributions: <https://devguide.python.org/>.
- Git documentation for branching, commits, remotes, and history: <https://git-scm.com/docs>.
- GitHub CLI manual and PR workflow documentation: <https://cli.github.com/manual/>.
- The project's current issue discussions, design proposals, release notes, and accepted PRs for local conventions.

**Core principle:** contribute evidence, not assumptions; make the smallest useful change; follow the project's actual rules; and treat review as collaborative engineering.
