# README, Runbooks, and Release Basics

This chapter teaches a practical production habit:

> **Working code is only one part of a usable software system.**

A professional Python project also needs enough documentation and release discipline that another competent engineer can understand it, install it, configure it, run it, test it, troubleshoot it, release it, deploy it, verify it, and recover from a failed release.

The progression in this chapter is:

```text
Code
  ↓
Documentation
  ↓
Tested operation
  ↓
Release
  ↓
Deployment
  ↓
Verification
  ↓
Troubleshooting / Recovery
  ↓
Rollback when necessary
```

The examples are intentionally small and mostly hypothetical. They are designed to teach the engineering patterns without pretending that one command or checklist is universal for every organization.

## 1. Overview

This chapter sits at the end of the production-habits sequence. Earlier topics covered configuration, logging, validation, idempotency, safe file writes, performance measurement, and dependency awareness. Here those habits are connected into a delivery and operations lifecycle.

A useful question is not only:

```text
"Can I run the program?"
```

but:

```text
"Can another engineer run it correctly?"
"Can an operator recover it safely?"
"Can we identify what version is deployed?"
"Can we verify the deployment?"
"Can we return to a known-good release?"
```

A README answers the orientation and usage questions. A runbook answers operational action questions. Release artifacts and notes answer traceability and change questions.

## 2. Learning Objectives

By the end of this chapter, you should be able to:

- define production readiness in context rather than as a universal checklist;
- write a useful README for a Python project;
- document installation, configuration, usage, inputs, outputs, tests, and troubleshooting;
- distinguish README content from comments, docstrings, runbooks, changelogs, and release notes;
- write an operational runbook with preconditions, procedure, verification, failure handling, rollback, escalation, and evidence collection;
- explain release, version, artifact, deployment, and rollback concepts;
- use Semantic Versioning as a communication convention;
- prepare a release checklist and deployment handoff;
- reason about deployment verification and rollback limits;
- apply these practices to Python, data, and Applied AI projects.

## 3. What Does “Production-Ready” Mean?

“Production-ready” does not mean “perfect” and it does not mean that every project needs a large operations team.

A small scheduled Python CLI and a multi-service AI platform have different risk profiles. A production-ready design is therefore contextual.

Common dimensions include:

| Dimension | Practical question |
|---|---|
| Correctness | Does the software produce the intended result? |
| Reproducibility | Can the expected environment be recreated? |
| Configuration | Can settings be supplied safely and predictably? |
| Observability | Can important behavior be investigated? |
| Documentation | Can another engineer understand and use it? |
| Testing | Do important normal and failure paths have coverage? |
| Deployment | Is there a defined and repeatable way to release it? |
| Recovery | Is there a known response when something fails? |
| Rollback | Is there a recovery path when a release is bad? |
| Maintainability | Can the system be changed without relying on tribal knowledge? |

The point is not to maximize documentation or process. The point is to make the level of engineering discipline appropriate to the system's risk and operational needs.

## 4. Why Documentation Is Part of Engineering

Documentation changes how software is used.

Imagine Developer A creates a batch processing application. Three months later, Developer B receives an incident involving that application. If Developer B cannot discover the startup command, configuration requirements, output location, or known recovery procedure, the software may be technically correct but operationally expensive.

Good documentation reduces:

- onboarding time;
- avoidable operator mistakes;
- repeated questions;
- dependence on tribal knowledge;
- deployment uncertainty;
- incident-response time.

Documentation also creates a written contract between the software and its users.

A useful mental model is:

```text
Code explains how the software behaves internally.
Documentation explains how people should interact with the software.
Runbooks explain how people should operate it safely.
Release information explains what changed and what version they are handling.
```

**Key Takeaway:** Documentation is not decoration around the software. It is part of the software's operational interface.

## 5. README Files

A README is normally the first document a developer or user sees when entering a repository.

A good README answers the high-value questions quickly:

```text
What is this?
Why does it exist?
Who is it for?
How do I install it?
How do I configure it?
How do I run it?
How do I test it?
Where do I find troubleshooting and deeper documentation?
```

The README should be optimized for discovery. A reader should not have to inspect ten source files to find the basic startup command.

## 6. Purpose of a README

A README provides orientation and a practical starting path.

Typical responsibilities:

1. explain the project's purpose;
2. identify prerequisites;
3. show the supported installation path;
4. document configuration;
5. demonstrate common usage;
6. explain inputs and outputs;
7. explain how to run tests;
8. point to troubleshooting and operational documentation.

The README is especially valuable for a repository that will be touched by more than its original author.

**Common Mistake:** Treating the README as a project diary. Readers usually need current, actionable information more than a narrative of every historical decision.

## 7. README Audience

The audience affects the content and ordering.

Possible audiences include:

| Audience | What they need first |
|---|---|
| New developer | setup, prerequisites, first successful run |
| Teammate | architecture orientation and usage |
| Maintainer | development workflow and tests |
| Operator | startup, status, troubleshooting, recovery links |
| Reviewer | purpose, boundaries, quality signals |
| Deployment engineer | artifact, configuration, deployment and verification |
| Future you | enough context to avoid rediscovering the system |

A library README often emphasizes installation and API usage. A CLI README emphasizes commands and inputs. A data pipeline README emphasizes data flow, schedules, schemas, and recovery. An AI application README may additionally document model configuration, evaluation, external services, and cost-sensitive operational assumptions.

## 8. README Minimum Information

A practical minimum depends on the project, but a useful baseline is:

```text
Project purpose
Prerequisites
Installation
Configuration
Usage
Examples
Input/output behavior
Testing
Troubleshooting
Project structure
Development workflow
Release information
Links to operational documentation
```

Not every project needs all of these as separate top-level headings. The principle is to make the important information discoverable.

## 9. Project Description

Start with a one- or two-paragraph description.

A strong project description states:

- what the software does;
- the problem it solves;
- the kind of input it expects;
- the kind of result it produces;
- important scope boundaries.

Example:

```markdown
# Expense Processor

Expense Processor is a Python CLI that reads validated CSV expense records,
normalizes the fields, calculates category totals, and writes a JSON summary.

It is intended for batch processing of approved input files. It does not
modify the source CSV and does not perform accounting settlement.
```

This is stronger than “A Python application for expenses” because the boundary of responsibility is visible.

## 10. Prerequisites

Prerequisites answer “What must already exist before installation or execution?”

Document only requirements that matter.

Examples:

```text
Python 3.12+
uv
Access to the project's input directory
A configured environment file for local development
```

For a project that relies on an external service, document the need for access without exposing credentials.

Good:

```text
An API credential with access to the development environment is required.
Store it in the approved secret mechanism; do not commit it to the repository.
```

Bad:

```text
Use API key: sk-real-secret-value
```

**Production Note:** A prerequisite should be verifiable. Whenever practical, provide a command or check that confirms it.

## 11. Installation

Installation instructions should be executable by the intended reader.

For a hypothetical project managed with `uv`, a clear example is:

```bash
git clone <repository-url>
cd expense-processor
uv sync
```

Then:

```bash
uv run python -m expense_processor --help
```

Because this is a hypothetical project, the names above are illustrative. A real README must use the actual project command.

A strong installation section tells the reader:

1. where to get the source;
2. which runtime is required;
3. how dependencies are installed;
4. how the environment is prepared;
5. how to verify installation succeeded.

Avoid vague statements such as “install the dependencies and run the program.”

### A small Python entry point

The documentation for a CLI is more useful when the reader can see the shape of the corresponding Python program.

This is a minimal, hypothetical application:

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process an expense CSV file."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    print(f"Would process: {args.input}")
    print(f"Would write: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The important documentation lesson is that the README and the program should agree about the interface. If the CLI later changes from `--output` to `--destination`, the code change should trigger a documentation review.

**Common Mistake:** Showing a command in the README that was invented while writing the document instead of verifying that the application actually accepts it.

## 12. Configuration

Configuration documentation should make required and optional settings obvious.

A simple table works well:

| Setting | Required? | Default | Purpose |
|---|---|---|---|
| `LOG_LEVEL` | No | `INFO` | Controls application logging |
| `INPUT_DIR` | Yes | — | Location of input files |
| `OUTPUT_DIR` | Yes | — | Location for generated output |
| `TIMEOUT_SECONDS` | No | `30` | External operation timeout |

Explain where configuration comes from, such as environment variables or a config file, and link to the deeper configuration guidance already established elsewhere in the project.

Do not copy real credentials into the README. Use placeholders and describe the approved way to provide secrets.

## 13. Environment Variables

Environment-variable documentation should identify name, requirement, default, and meaning.

Example:

```text
INPUT_DIR=/data/input
OUTPUT_DIR=/data/output
LOG_LEVEL=INFO
```

For secrets:

```text
SERVICE_API_KEY=replace-with-your-development-key
```

The placeholder communicates shape without becoming a credential.

A useful `.env.example` pattern is:

```text
INPUT_DIR=./data/input
OUTPUT_DIR=./data/output
LOG_LEVEL=INFO
SERVICE_API_KEY=replace-with-your-key
```

The README should explain whether an `.env` file is loaded automatically, loaded by the shell, or replaced by another configuration mechanism. Do not assume every application behaves the same way.

## 14. Usage

Usage documentation should show the normal path first.

A hypothetical CLI might be documented as:

```bash
python -m expense_processor --input data/expenses.csv --output build/summary.json
```

Then explain the inputs and outputs in plain language:

```text
--input   path to an input CSV
--output  destination for the generated JSON summary
```

Show at least one minimal successful example and, when useful, one representative failure.

A usage section should answer not only “what command?” but also “what should happen?”

## 15. CLI Examples

CLI examples should be realistic, small, and copy-pasteable.

Example:

```bash
python -m expense_processor --help
python -m expense_processor --input data/expenses.csv --output build/summary.json
```

For validation behavior:

```bash
python -m expense_processor --input missing.csv --output build/summary.json
```

Then document the expected class of outcome, such as a clear error on `stderr` and a non-zero exit status.

Do not invent project commands in a real README. The chapter examples are deliberately labeled as hypothetical.

## 16. Input and Output

Users need to know the contract around data.

For CSV input, document:

```text
Encoding: UTF-8
Required columns: expense_id, amount, category
amount: decimal number greater than 0
category: non-empty text
```

For JSON output, document the shape that matters:

```json
{
  "total_amount": 1250.50,
  "record_count": 42,
  "categories": {
    "travel": 900.50,
    "food": 350.00
  }
}
```

The goal is not to document every internal object. Document the stable external contract.

## 17. Examples

Examples are executable documentation.

A good example should:

- start from a known state;
- use realistic names;
- avoid unnecessary options;
- show expected results where useful;
- remain synchronized with the actual software.

Example:

```bash
python -m expense_processor   --input examples/expenses.csv   --output build/example-summary.json
```

Then:

```text
Expected:
- command exits successfully;
- output file is created;
- record count matches the input;
- summary JSON can be parsed.
```

When documentation is changed, re-run examples or otherwise verify them. An example that no longer works damages trust faster than an omitted example.

## 18. Testing

A README should make the test entry point easy to discover.

Example:

```bash
pytest
```

For a `uv` project, another possible project-specific form is:

```bash
uv run pytest
```

Again, the correct command is whatever the actual repository supports.

Document prerequisites for tests when applicable, such as test data or environment variables. Make clear whether the suite includes only unit tests or also integration tests that require external services.

## 19. Troubleshooting

Troubleshooting is most useful when it connects:

```text
Symptom
→ likely cause
→ diagnostic step
→ resolution
→ verification
```

Example:

### `ModuleNotFoundError`

**Likely cause:** the command is using a Python environment that does not contain the project's dependencies.

**Diagnosis:**

```bash
python --version
python -c "import sys; print(sys.executable)"
```

**Resolution:** use the project's documented environment and dependency-sync command.

**Verification:**

```bash
python -c "import expense_processor; print('import ok')"
```

A troubleshooting entry should help the reader reason about a failure, not merely give them a command to copy.

## 20. Project Structure

Document the meaningful structure of the project.

Example:

```text
expense-processor/
├── src/
│   └── expense_processor/
├── tests/
├── docs/
├── examples/
├── pyproject.toml
├── README.md
└── uv.lock
```

Explain important entries:

```text
src/       application package
tests/     automated tests
docs/      deeper technical or operational documentation
examples/  example inputs and usage assets
pyproject.toml  project metadata and dependency declarations
uv.lock    resolved dependency state for the uv workflow
```

Do not produce a giant listing of every file. The purpose is orientation.

## 21. Common README Mistakes

Common failures include:

- only describing what the project does;
- omitting prerequisites;
- omitting the exact installation flow;
- hiding configuration requirements in source code;
- using examples that no longer work;
- documenting commands that do not match the current CLI;
- failing to mention output locations;
- putting secrets into examples;
- having no troubleshooting section;
- linking to documents that no longer exist;
- allowing screenshots to replace essential text instructions.

**Production Lesson:** A README should minimize the number of reasonable guesses a new engineer must make.

## 22. README Quality Checklist

Review a README with four questions:

```text
Correct?
Complete?
Discoverable?
Actionable?
```

A reader should be able to move from zero context to the first successful run without opening implementation files.

A stronger review also asks:

```text
Can I tell what this system does?
Can I reproduce the documented setup?
Do examples match the real interface?
Are secrets excluded?
Can I find troubleshooting quickly?
Can I find operational and release documentation?
```

## 23. Writing a Production-Quality README

A useful README is concise at the top and progressively deeper below.

A practical ordering is:

```text
Project purpose
→ quick start
→ prerequisites
→ configuration
→ normal usage
→ examples
→ tests
→ troubleshooting
→ project structure
→ development/release links
```

Use tables for compact reference information and code blocks for commands.

Avoid writing everything as prose. A reader in the middle of an incident wants a procedure they can scan.

## 24. Documentation vs Code Comments vs Docstrings

These artifacts answer different questions.

| Artifact | Main purpose | Typical scope |
|---|---|---|
| README | Understand and use project | Repository |
| Comment | Explain a non-obvious implementation decision | Local code |
| Docstring | Explain function/class/module interface | Code API |
| Runbook | Operate or recover the system | Operational task |
| Changelog | Record historical changes | Project/release history |
| Release notes | Explain one release | Specific version |
| Deployment handoff | Communicate deployment requirements | Change/deployment event |

A comment should not become the only place that explains how to run the program. A runbook should not be the only place that explains how to install the project.

## 25. Operational Documentation

Operational documentation explains how to operate a running or deployed system safely.

Examples:

```text
Start a batch job
Check whether a scheduled job completed
Investigate a failed output
Retry a job
Verify generated data
Perform a rollback
Escalate an unknown failure
```

Operational documentation should be written for the person who must act under time pressure.

That means:

- clear prerequisites;
- explicit commands or actions;
- expected results;
- safe stopping conditions;
- failure handling;
- evidence collection;
- escalation boundaries.

## 26. What Is a Runbook?

A runbook is a step-by-step operational procedure for a known task or failure mode.

A runbook is not simply “more README.”

A README says:

```text
How do I use this project?
```

A runbook says:

```text
What do I do right now when condition X occurs?
```

Example runbook tasks:

```text
Deploy release
Investigate failed batch job
Recover missing output
Rollback release
Validate a scheduled pipeline
```

The defining quality is operational actionability.

## 27. Why Runbooks Exist

Runbooks reduce decision-making under stress.

Without a runbook, an operator may ask:

```text
What should I check first?
What commands are safe?
What state should I expect?
When should I stop?
Can I retry?
How do I know it worked?
When do I escalate?
```

A well-written runbook turns these questions into an ordered procedure.

The runbook is not a substitute for engineering judgment. It provides a safe default path for situations the team has already understood.

## 28. Runbook Audience

The audience may be:

- on-call engineer;
- operations engineer;
- deployment engineer;
- data engineer;
- service maintainer;
- developer supporting a production workload.

Write for the reader's likely context. Avoid assuming that the person who operates the system is the person who wrote it.

## 29. Runbook vs README

A side-by-side comparison makes the distinction clear.

| README | Runbook |
|---|---|
| Project orientation | Operational procedure |
| Installation and usage | Action during a task/incident |
| Broad audience | Usually narrower operational audience |
| Explains the normal path | Explains a known procedure and failure path |
| Stable onboarding content | Often condition/task-specific |
| Usually repository entry point | Usually linked from operations documentation |

They are complementary.

## 30. Runbook Structure

A strong runbook can use:

```markdown
# Runbook: <Task>

## Purpose
## When to Use
## Required Access
## Preconditions
## Expected Initial State
## Procedure
## Verification
## Failure Handling
## Rollback
## Escalation
## Evidence to Collect
## Related Documentation
```

The structure helps the operator answer “am I allowed to do this?”, “what do I do?”, and “how do I know whether it worked?”

## 31. Preconditions

Preconditions prevent unsafe execution.

Examples:

```text
Correct environment selected
Correct release identified
Required access is available
No conflicting deployment is active
Known backup or recovery path exists
Input data is identified
```

A precondition should be verifiable.

Weak:

```text
Make sure everything is okay.
```

Better:

```text
Confirm the deployed version is the release identified in the incident record.
Confirm no other deployment is currently in progress.
```

## 32. Expected System State

The operator needs to know what “normal before the procedure” looks like.

For example:

```text
Expected:
- job status = FAILED
- no active worker for job_id
- output file from the failed attempt is incomplete
- last successful release = 1.4.1
```

This matters because a runbook can otherwise be applied to the wrong situation.

**Production Note:** If a precondition is not satisfied, the procedure may need to stop and escalate rather than continue.

## 33. Procedure

A procedure should be ordered, explicit, and bounded.

Bad:

```text
Restart the job and check the logs.
```

Better:

```text
1. Record the job ID.
2. Check the current job status.
3. Inspect the latest error logs.
4. Confirm the failure matches the conditions listed in this runbook.
5. Verify the retry is safe.
6. Start one retry using the approved command.
7. Wait for completion.
8. Verify output and final job status.
```

Each step should ideally have one clear purpose.

## 34. Verification

Every operational action needs a verification method.

```text
Action
  ↓
Expected observable result
```

Examples:

```bash
python -m expense_processor --health-check
```

or:

```text
Confirm job status = COMPLETED.
Confirm expected output file exists.
Confirm output can be parsed.
Confirm logs contain completion event.
```

Do not write “deployment succeeded” merely because a deployment command returned.

## 35. Failure Handling

A runbook should explain what to do when a step fails.

Use a bounded pattern:

```text
If verification fails:
1. Stop further changes.
2. Preserve evidence.
3. Inspect logs and status.
4. Determine whether the documented recovery path applies.
5. Roll back or escalate according to the runbook.
```

The purpose is to prevent improvisation from becoming the default failure mode.

## 36. Rollback

Rollback should be part of the procedure, not an afterthought.

A generic sequence is:

```text
Deploy release N
  ↓
Verify
  ↓
Failure
  ↓
Stop rollout
  ↓
Rollback to known-good release N-1
  ↓
Verify N-1
  ↓
Record evidence
```

The exact commands depend on the environment. The important engineering property is that a previous known-good state is identifiable and recoverable.

## 37. Escalation

A runbook should state when the operator should stop.

Escalation is appropriate when:

- the observed state is outside the documented assumptions;
- the operation could cause data loss;
- security concerns arise;
- rollback fails;
- the issue repeats after the documented recovery path;
- required access is missing;
- the operator cannot establish what version or state is active.

A safe runbook explicitly defines its boundary.

## 38. Evidence and Logs

Useful evidence may include:

```text
Timestamp
Job ID / request ID
Current version
Relevant command and result
Relevant error message
Important log lines
Input/output identifiers
Configuration context that is safe to share
```

Never instruct an operator to paste secret values into an incident channel.

A good runbook makes evidence collection part of the workflow so that later diagnosis does not depend on memory.

## 39. Troubleshooting Runbooks

A troubleshooting runbook can be organized as a decision path:

```text
Symptom
  ↓
Confirm scope
  ↓
Check system state
  ↓
Inspect logs
  ↓
Classify failure
  ↓
Apply known recovery
  ↓
Verify
  ↓
Escalate if outside scope
```

This connects to previous chapters:

```text
configuration
+ validation
+ logging
+ idempotency
+ safe writes
+ dependency management
+ documentation
```

The value comes from integrating these habits rather than repeating each lesson.

## 40. Deployment Runbooks

A deployment runbook normally has three phases.

### Before deployment

```text
Verify release version
Verify tests
Verify dependency state
Verify configuration
Verify rollback path
```

### During deployment

```text
Deploy artifact
Observe deployment status
Verify startup
```

### After deployment

```text
Run health check
Run smoke test
Inspect logs
Verify expected behavior
Record result
```

### Failure

```text
Stop
Collect evidence
Rollback when appropriate
Verify previous release
Escalate
```

## 41. Batch Job Runbooks

For a batch job, document:

```text
How to start the job
How to identify the job instance
How to inspect status
How to inspect logs
How to determine partial completion
Whether retry is safe
How to verify outputs
How to avoid duplicate processing
How to escalate
```

Example:

```text
Job:
Daily transaction normalization

Input:
transactions-YYYY-MM-DD.csv

Output:
normalized-YYYY-MM-DD.json

Recovery:
Use the documented rerun procedure only after confirming the job is idempotent for the same input date.
```

This connects directly to the previous idempotency chapter.

## 42. Data Pipeline Runbooks

A data pipeline runbook should reflect the data flow:

```text
Source
  ↓
Extraction
  ↓
Transformation
  ↓
Validation
  ↓
Load
  ↓
Verification
```

For each stage, document important failure symptoms.

Example:

```text
Symptom: output count is unexpectedly zero.

Check:
1. Input partition exists.
2. Extraction completed.
3. Validation did not reject all rows.
4. Transformation produced expected records.
5. Load completed.
```

Avoid turning the runbook into a complete data-engineering architecture document. Focus on operational action.

## 43. AI/LLM Pipeline Runbooks

AI pipelines often combine multiple dependencies and expensive processing.

A provider-neutral batch inference workflow may be:

```text
Input dataset
  ↓
Input validation
  ↓
Preprocessing
  ↓
Model/API calls
  ↓
Output validation
  ↓
Persistence
  ↓
Evaluation / reporting
```

Operational cases include:

- external API failure;
- rate limiting;
- malformed response;
- partial completion;
- retry;
- duplicate inference;
- invalid structured output;
- unexpected processing cost.

The runbook should point to the source of truth for each response procedure rather than inventing provider-specific commands.

## 44. Safe Operational Procedures

Operational procedures should minimize ambiguity and destructive surprises.

Avoid:

```text
Delete the old files.
```

Prefer:

```text
1. Confirm the file belongs to the failed job ID.
2. Confirm no process is currently writing it.
3. Confirm the path matches the documented temporary-output location.
4. Remove only the temporary artifact identified by the failed run.
5. Verify the expected source file remains untouched.
```

The more destructive the action, the more explicit the preconditions should be.

## 45. Release Basics

A release is a specific, identifiable version of software prepared for users or deployment.

A useful lifecycle is:

```text
Source code
  ↓
Tests
  ↓
Version
  ↓
Build artifact
  ↓
Release
  ↓
Deployment
  ↓
Verification
```

A release is not automatically the same thing as a deployment. A release can be published before it is deployed everywhere.

## 46. What Is a Software Release?

A release is a deliberate statement that a particular software state is ready to be consumed or deployed.

A release should be identifiable.

Example:

```text
Expense Processor 1.4.2
```

The identifier helps people discuss the same thing.

A good release process can answer:

```text
What changed?
What code is included?
What dependencies changed?
What configuration changed?
How do we verify it?
How do we roll it back?
```

## 47. Source Code vs Release

These are related but different.

```text
Source code
= human-maintained implementation

Commit
= recorded source-control state

Build artifact
= output produced from source/build process

Release
= identifiable version/change package made available for use

Deployment
= placing a particular build/release into a target environment
```

A production engineer should avoid saying “we deployed commit X” when the system actually deploys a built artifact. The exact mapping should be traceable.

## 48. Versioning

Version identifiers allow humans and systems to distinguish states over time.

Examples:

```text
1.0.0
1.1.0
1.1.1
```

Versions are useful for:

- traceability;
- compatibility communication;
- debugging;
- release notes;
- rollback;
- support conversations.

Choose a clear project policy and apply it consistently.

## 49. Semantic Versioning

Semantic Versioning uses:

```text
MAJOR.MINOR.PATCH
```

The intended communication is:

- **MAJOR** for incompatible or breaking changes;
- **MINOR** for backward-compatible functionality;
- **PATCH** for backward-compatible fixes.

However:

> Version numbers are promises made by a project's release policy, not physical laws.

Some projects do not follow SemVer strictly. A consumer should inspect the project's compatibility policy and release notes rather than trusting the number alone.

## 50. Major/Minor/Patch

For a project that follows SemVer-like conventions:

```text
1.4.2
│ │ └── patch
│ └──── minor
└────── major
```

Illustrative changes:

```text
1.4.2 → 1.4.3
Bug fix without intended breaking behavior

1.4.3 → 1.5.0
New backward-compatible feature

1.5.0 → 2.0.0
Breaking interface or behavior change
```

These are examples of intended communication, not guarantees about a package's real behavior.

## 51. Pre-release Versions

Pre-release versions communicate that a version is not yet a normal stable release.

Examples:

```text
1.2.0-alpha
1.2.0-beta
1.2.0-rc.1
```

Typical intent:

```text
alpha → early development/testing
beta  → broader testing
rc    → release candidate
```

Teams may define more specific policies, but the reader should recognize these suffixes as signals that extra caution may be appropriate.

## 52. Changelogs

A changelog is a historical record of meaningful project changes.

Example:

```markdown
# Changelog

## 1.3.0

### Added
- Added batch processing support.

### Changed
- Improved validation error messages.

### Fixed
- Corrected a CSV parsing edge case.

## 1.2.1

### Fixed
- Fixed timeout handling for input files.
```

Changelogs are useful because a reader can compare what changed across versions without reading every commit.

## 53. Release Notes

Release notes communicate the important information about one specific release.

A release note may include:

```text
Release version
Summary
Important changes
Breaking changes
Migration requirements
Operational impact
Known issues
Upgrade instructions
Rollback notes
```

A changelog answers “what changed over time?” A release note answers “what should I know about this specific version?”

## 54. Release Preparation

A practical release-preparation sequence is:

```text
1. Confirm the scope of change.
2. Confirm source is committed.
3. Run tests.
4. Run linting/type checks as applicable.
5. Verify dependency state.
6. Verify configuration documentation.
7. Select/version the release.
8. Update changelog.
9. Write release notes.
10. Build artifact.
11. Verify artifact.
12. Tag or otherwise identify the release.
13. Prepare deployment.
14. Verify rollback.
```

Do not blindly automate every step. The important habit is that release work follows a deliberate sequence.

## 55. Release Checklist

A release checklist is a pre-flight control.

Example:

```text
[ ] Intended changes are present
[ ] Functional tests pass
[ ] Lint/type checks pass where required
[ ] Dependency state is verified
[ ] Configuration changes are documented
[ ] Version identifier is correct
[ ] Changelog is updated
[ ] Release notes are ready
[ ] Artifact builds successfully
[ ] Artifact is identifiable
[ ] Deployment procedure is known
[ ] Verification procedure is known
[ ] Rollback procedure is known
```

Checklists are particularly valuable for repetitive, high-consequence work.

## 56. Testing Before Release

Testing should prove more than “the package builds.”

Consider:

```text
Unit tests
Integration tests
CLI tests
Data validation tests
Configuration tests
Smoke tests
Critical workflow tests
```

For a data or AI pipeline, important end-to-end workflows may matter more than adding large numbers of tiny tests.

A release candidate should pass the project's defined quality gates before deployment.

## 57. Configuration Before Release

Configuration is part of release readiness.

Review:

- newly added settings;
- removed settings;
- changed defaults;
- required values;
- environment-specific values;
- migration requirements;
- secret handling.

A release that requires a new environment variable is operationally incomplete until the deployment handoff and runbook explain it.

## 58. Dependency Verification

Before release, verify that the dependency state is intentional.

Useful questions:

```text
Are direct dependencies declared?
Is the resolved dependency state reproducible?
Did an upgrade introduce unexpected transitive dependencies?
Do tests run against the intended environment?
Are known dependency concerns reviewed?
```

This connects to the previous dependency-management chapter. The release process should consume dependency state rather than discovering surprises during deployment.

## 59. Documentation Verification

Documentation should be reviewed as part of the release, especially when behavior changes.

Check:

```text
README usage examples
Configuration documentation
CLI options
Troubleshooting steps
Runbooks
Release notes
Migration guidance
Rollback instructions
```

A practical rule:

> If a code change changes how a user or operator interacts with the system, ask whether the documentation must change too.

## 60. Build Artifacts

A build artifact is the output produced from source code that can be delivered or deployed.

Examples include:

```text
Python wheel
Source distribution
Packaged application
Container image
```

The release process should make the artifact identifiable and verifiable.

At Stage 1 level, the key concept is:

```text
source
→ build
→ artifact
```

The exact build system is a later specialization.

## 61. Release Artifacts

A release artifact should be attributable to a specific release.

Examples:

```text
expense-processor-1.4.2.whl
```

or:

```text
my-image:1.4.2
```

The artifact naming scheme is project-specific.

The important property is traceability:

```text
release identifier
→ artifact identifier
→ deployment record
```

An operator should be able to determine what artifact is running.

## 62. Deployment Handoff

A deployment handoff communicates the facts the deployment/operations team needs.

A useful template:

```text
Release: 1.4.2
What changed: Improved input validation and output aggregation
Configuration changes: Added LOG_LEVEL documentation; no new secret
Dependency changes: Updated two runtime dependencies
Data changes: None
Known issues: None
Deployment procedure: <link to runbook>
Verification: Health check + smoke test
Rollback: Return to 1.4.1 artifact
Owner/contact: <team or role>
```

A handoff should reduce unanswered questions before deployment begins.

## 63. Deployment Verification

### A tiny verification command

A Python program can expose a deliberate health or verification path. This example is intentionally small and hypothetical:

```python
def verify_output(path: str) -> int:
    from pathlib import Path

    output = Path(path)
    if not output.is_file():
        print(f"Output not found: {output}")
        return 1

    print(f"Output exists: {output}")
    return 0
```

The operational documentation should then explain how this check is invoked and what result means success or failure. The exact interface belongs to the real application.

Verification asks whether the deployed system is actually behaving as expected.

Examples:

```text
Confirm deployed version
Run health check
Run smoke test
Inspect startup logs
Execute a representative operation
Confirm expected output
```

For a batch job:

```text
Start job
→ check status
→ verify output
→ verify completion
```

For a CLI:

```text
python -m app --help
→ successful response
→ expected exit status
```

Verification should be explicit rather than inferred from the deployment tool's success message.

## 64. Post-Deployment Verification

A deployment can succeed mechanically while the application remains unhealthy.

Post-deployment checks may include:

- process startup;
- configuration load;
- dependency initialization;
- health checks;
- representative user flow;
- output validation;
- error log review;
- performance sanity check.

The exact checks should be proportional to risk.

**Production Note:** Define verification before deployment so “success” is not redefined after the fact.

## 65. Rollback

Rollback means returning to a previously known-good release or state.

A simple conceptual flow:

```text
Release N
  ↓
Problem detected
  ↓
Stop rollout
  ↓
Deploy/restore known-good Release N-1
  ↓
Verify
```

Rollback requires more than knowing a version number. Consider:

```text
Artifact availability
Configuration compatibility
Data/schema changes
State changes
External interfaces
Operational dependencies
```

Some releases are easy to roll back. Others require a forward fix or a data migration strategy.

## 66. Release Failure Scenarios

Common release failures include:

```text
Application fails to start
Configuration key missing
Dependency conflict
CLI behavior changed unexpectedly
Data format changed
Performance regression
External dependency incompatible
Artifact is not the expected version
Rollback artifact is unavailable
```

For each class of failure, the release process should help answer:

```text
How do we detect it?
How do we stop further damage?
How do we collect evidence?
Can we roll back?
How do we verify recovery?
```

## 67. Hotfix Basics

A hotfix is a focused change released to address an urgent production issue.

Good hotfix discipline still includes:

```text
Define exact problem
Keep change scope narrow
Test the fix
Version or identify the fix
Record the change
Deploy deliberately
Verify
Document follow-up work
```

“Urgent” should not mean “skip every safety control.”

## 68. Release Traceability

Traceability connects the change to what users actually run.

```text
Requirement / issue
  ↓
Commit
  ↓
Version
  ↓
Build artifact
  ↓
Release
  ↓
Deployment
  ↓
Observed behavior
```

This allows an incident investigator to ask:

```text
What changed?
Which release introduced it?
What artifact is deployed?
Can we return to the previous artifact?
```

Traceability is one of the most useful properties of a mature release process.

## 69. Git Tags and Releases

Git tags can identify a particular source-control state.

Example:

```bash
git tag v1.2.0
```

A tag is useful for source traceability, but it does not automatically prove which built artifact was deployed. The release process must maintain the relationship:

```text
Git tag
→ build
→ artifact
→ deployment
```

Some organizations use a CI/CD platform or release system to enforce and record this mapping.

## 70. Production Readiness Checklist

A contextual readiness review can be grouped like this:

| Area | Questions |
|---|---|
| Code | Is the intended behavior tested? |
| Configuration | Are required settings documented and safe? |
| Dependencies | Is the environment reproducible? |
| Logging | Can important failures be investigated? |
| README | Can a new engineer get started? |
| Runbook | Can known operational tasks be executed safely? |
| Release | Is the release identifiable? |
| Deployment | Is there a defined handoff and verification path? |
| Recovery | Is rollback or another recovery strategy documented? |
| Ownership | Is there a clear team/role responsible for operating it? |

A checklist does not magically make software production-ready. It is a way to make important readiness questions visible.

## 71. Applied AI Engineering Examples

AI systems benefit strongly from explicit operational documentation because they frequently combine software, data, configuration, external APIs or models, storage, evaluation, and batch processing.

### CLI AI data processor

Document:

```text
Installation
Model/configuration inputs
Input dataset requirements
Execution command
Output location
Validation behavior
Failure handling
Retry procedure
Release/version
Rollback
```

### RAG application

Document:

```text
Environment requirements
Embedding configuration
Indexing procedure
Query procedure
Expected input/output
Common retrieval failures
Deployment verification
Rollback considerations
```

### LLM batch inference

Document:

```text
Input schema
Batch identity
Model/configuration settings
Execution procedure
Partial completion behavior
Retry rules
Result location
Validation
Release notes
Operational recovery
```

### Data engineering pipeline

Document:

```text
Source → extract → transform → validate → load
```

Then write the runbook around failure at each meaningful boundary.

Keep provider-specific statements out unless the project itself establishes them.

## 72. Complete Production Example

### Minimal release metadata exposed by Python

A project can expose its version for diagnostics. One simple pattern is:

```python
__version__ = "1.4.2"


def application_version() -> str:
    return __version__
```

In a real project, the authoritative version should be defined by the chosen packaging/release strategy rather than duplicated carelessly across many files. The example is only illustrating the idea that runtime diagnostics can expose release identity.

## Production-Ready Python Batch Processing Application

Consider a hypothetical application called `expense_processor`.

### What it does

It reads a CSV file, validates each expense record, calculates a summary, and writes a JSON result.

### Example structure

```text
expense-processor/
├── src/
│   └── expense_processor/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       └── processing.py
├── tests/
├── docs/
│   └── runbooks/
├── examples/
├── pyproject.toml
├── README.md
└── uv.lock
```

### README outline

```markdown
# Expense Processor

## Overview
## Prerequisites
## Installation
## Configuration
## Usage
## Input Format
## Output Format
## Testing
## Troubleshooting
## Project Structure
## Operations
## Release
```

### Installation

The following is a hypothetical project command:

```bash
uv sync
```

### Configuration

```text
INPUT_DIR=./data/input
OUTPUT_DIR=./data/output
LOG_LEVEL=INFO
```

### Usage

```bash
python -m expense_processor   --input data/input/expenses.csv   --output data/output/summary.json
```

### Testing

```bash
pytest
```

### Troubleshooting entry

```markdown
## Batch job failed

1. Record the job ID.
2. Inspect the latest error logs.
3. Confirm the input file exists.
4. Confirm the configuration matches the documented environment.
5. Determine whether partial output exists.
6. Follow the retry guidance only if rerunning is safe.
7. Verify the final output.
```

### Deployment handoff

```text
Release: 1.4.2
Artifact: expense-processor-1.4.2
Configuration changes: none
Data changes: none
Verification: startup check + representative batch
Rollback: previous known-good artifact 1.4.1
Runbook: Batch Deployment Runbook
```

### Deployment sequence

```text
Confirm release
→ verify artifact
→ deploy
→ health/startup check
→ smoke test
→ representative job
→ inspect result
→ record verification
```

### Failure sequence

```text
Deployment
→ verification fails
→ stop
→ capture evidence
→ rollback if compatible
→ verify previous release
→ document incident
```

The example integrates earlier Stage 1 practices without re-teaching them. Validation protects the input boundary. Logging records evidence. Idempotency makes reruns safer. Safe file writes protect outputs. Dependency management makes the environment reproducible. This chapter adds the documentation and release interface around those engineering habits.

## 73. Debugging Scenarios

### Scenario 1 — New developer cannot run the project

**Problem:** The README only says “install dependencies and start the app.”

**How to think:** The setup path is incomplete.

**Diagnosis:** Look for missing Python-version requirements, dependency installation command, configuration instructions, and actual execution command.

**Solution:** Replace vague setup text with a tested quick-start path.

**Production lesson:** A setup instruction is useful only when a reader can execute it.

### Scenario 2 — Deployment succeeded but the application is unhealthy

**Problem:** Deployment tooling reported success, but requests or jobs fail.

**How to think:** Deployment completion is not application-health verification.

**Diagnosis:** Check deployed version, startup logs, configuration, health checks, and representative behavior.

**Solution:** Add explicit post-deployment verification.

**Production lesson:** “Deployed” and “healthy” are different states.

### Scenario 3 — Batch job failed halfway through

**Problem:** An operator does not know whether retrying is safe.

**Diagnosis:** Identify completed work, job identity, output state, and documented retry semantics.

**Solution:** Provide a runbook that uses idempotency and partial-failure handling.

**Production lesson:** A retry procedure must be backed by an understood failure model.

### Scenario 4 — New release causes unexpected behavior

**Diagnosis:** Determine active version, compare release notes, inspect deployment history and logs.

**Solution:** Roll back if the recovery path is valid; otherwise follow the incident/recovery procedure.

**Production lesson:** Traceability makes diagnosis faster.

### Scenario 5 — Operator does not know what command to run

**Diagnosis:** The procedure likely depends on tribal knowledge.

**Solution:** Put the supported operational command in a runbook, with preconditions and verification.

**Production lesson:** Known procedures should not live only in someone's memory.

### Scenario 6 — Rollback is attempted but fails

**Diagnosis:** Check artifact availability, configuration compatibility, state/data changes, and current system state.

**Solution:** Stop repeated attempts if the system is outside the documented rollback assumptions and escalate.

**Production lesson:** A rollback plan must include its own preconditions and failure boundary.

### Scenario 7 — README is correct but unusable

**Diagnosis:** The information may be technically true but hard to find, out of order, or missing an executable example.

**Solution:** Optimize for reader flow: purpose → quick start → configuration → usage → troubleshooting → deeper details.

**Production lesson:** Correctness without discoverability is not enough.

## 74. Exercises

The following exercises progress from beginner documentation work to release and operations design. Every exercise includes an objective, problem, constraints, expected output, solution, explanation, and common mistakes.


### Exercise 1 — Write a Useful README

**Objective:** Practice turning a vague project description into actionable documentation.

**Problem:** You have a CLI that reads `input.csv` and writes `output.json`.

**Constraints:** Do not invent external services or secrets.

**Expected output:** A README containing purpose, prerequisites, installation, configuration, usage, inputs/outputs, and tests.

**Solution:**

```markdown
# CSV Summary Tool

## Overview

CSV Summary Tool reads a validated CSV file and writes a JSON summary.

## Prerequisites

- Python 3.12+
- Project dependency environment

## Installation

```bash
uv sync
```

## Usage

```bash
python -m csv_summary --input input.csv --output output.json
```

## Testing

```bash
pytest
```
```

**Explanation:** The README now answers the first operational questions without exposing implementation details.

**Common mistakes:** vague installation instructions, missing input contract, and no test command.

### Exercise 2 — Add a Configuration Table

**Objective:** Make environment variables discoverable.

**Problem:** The application needs `INPUT_DIR`, `OUTPUT_DIR`, and `LOG_LEVEL`.

**Constraints:** `LOG_LEVEL` defaults to `INFO`.

**Expected output:** A clear table.

**Solution:**

```markdown
| Setting | Required | Default | Purpose |
|---|---|---|---|
| INPUT_DIR | Yes | — | Input location |
| OUTPUT_DIR | Yes | — | Output location |
| LOG_LEVEL | No | INFO | Logging verbosity |
```

**Explanation:** Tables are compact and easy to scan.

**Common mistakes:** listing variable names without meaning or default behavior.

### Exercise 3 — Document a CLI

**Objective:** Write a reproducible usage example.

**Problem:** The command accepts `--input`, `--output`, and `--verbose`.

**Expected output:**

```bash
python -m app --input data/input.csv --output build/output.json
```

Explain each option and show a help command:

```bash
python -m app --help
```

**Explanation:** The reader can discover the interface and run the common path.

**Common mistakes:** failing to explain required arguments.

**Constraints:** Use only the documented `--input`, `--output`, and `--verbose` options; do not invent unsupported behavior.

**Solution:** Show the normal command first, then show `--help`, and explain what each argument controls.

### Exercise 4 — Write a Troubleshooting Entry

**Objective:** Separate symptom from diagnosis.

**Problem:** A developer sees `ModuleNotFoundError`.

**Solution:**

```markdown
### ModuleNotFoundError

**Symptom:** Import fails when starting the application.

**Likely causes:**
- wrong Python environment;
- dependencies not synced.

**Diagnosis:**
```bash
python -c "import sys; print(sys.executable)"
```

**Resolution:** Use the project's documented environment and dependency-sync command.

**Verification:** Re-run the documented import/start command.
```

**Common mistakes:** saying “reinstall everything” without diagnosis.

**Constraints:** Do not treat the exception message itself as proof of one specific root cause; show a diagnostic path.

**Explanation:** The exercise teaches the difference between a symptom, a likely cause, a diagnostic check, and a resolution.

**Expected output:** A troubleshooting entry that separates symptom, likely causes, diagnosis, resolution, and verification.

### Exercise 5 — README Review

**Objective:** Identify documentation gaps.

**Problem:** A README contains only:

```text
This project processes data.
Run app.py.
```

**Expected reasoning:** It lacks purpose detail, prerequisites, installation, configuration, input/output contract, tests, troubleshooting, and supported execution method.

**Solution:** Expand the README around the reader's actual workflow.

**Common mistake:** adding a huge file listing instead of missing operational information.

**Constraints:** Improve discoverability without turning the README into an exhaustive implementation document.

**Explanation:** The original README leaves the reader with too many unanswered operational questions.

**Common mistakes:** Adding decorative prose while leaving installation, configuration, usage, or testing undocumented.

**Expected output:** A revised README outline that fills the important documentation gaps.

### Exercise 6 — Build a Runbook

**Objective:** Turn vague operational advice into a procedure.

**Problem:** “Restart the failed batch job.”

**Solution:**

```markdown
# Runbook: Retry Failed Batch Job

## Purpose
Retry a failed batch only after confirming the failure matches the documented retry conditions.

## Preconditions
- Job is not currently running.
- Input identity is known.
- Retry is idempotent for the same input/job ID.

## Procedure
1. Record the job ID.
2. Inspect the latest logs.
3. Confirm failure class.
4. Verify the input.
5. Start one retry.
6. Monitor status.

## Verification
Confirm final status is `COMPLETED` and output validates successfully.

## Escalation
Escalate if the observed state falls outside documented conditions.
```

**Explanation:** The operator now has a bounded decision path.

**Constraints:** The retry path must be conditional on the job state and documented idempotency assumptions.

**Common mistakes:** Retrying blindly, skipping evidence collection, or deleting output before understanding the failed run.

**Expected output:** A runbook with purpose, preconditions, procedure, verification, and escalation/recovery.

### Exercise 7 — Deployment Verification

**Objective:** Define observable success.

**Problem:** Deployment command returned success.

**Expected output:** A verification checklist.

**Solution:**

```text
Confirm deployed version
Run health check
Run smoke test
Inspect startup logs
Execute representative operation
Verify expected result
```

**Common mistake:** treating deployment-tool success as application-health success.

**Constraints:** Verification must use observable application behavior rather than only the deployment tool's status.

**Explanation:** A verification checklist converts deployment completion into a testable application-health decision.

**Common mistakes:** Checking only that the process started or assuming a successful deployment command means the feature works.

### Exercise 8 — Release Checklist

**Objective:** Create release discipline.

**Solution:**

```text
[ ] Tests pass
[ ] Documentation updated
[ ] Version selected
[ ] Changelog updated
[ ] Release notes ready
[ ] Artifact built
[ ] Artifact identified
[ ] Rollback path verified
[ ] Deployment runbook ready
[ ] Verification ready
```

**Explanation:** The list creates a repeatable release gate.

**Problem:** Prepare a reusable checklist that controls release quality before deployment.

**Constraints:** Include verification and rollback readiness without pretending the checklist covers every organization's controls.

**Common mistakes:** Treating the checklist as a substitute for testing or as a universal production-readiness guarantee.

**Expected output:** A release checklist that can be reviewed before deployment.

### Exercise 9 — Changelog Entry

**Objective:** Record meaningful historical changes.

**Solution:**

```markdown
## 1.4.0

### Added
- Added CSV batch processing.

### Changed
- Improved validation messages.

### Fixed
- Fixed incorrect handling of empty categories.
```

**Problem:** Record the meaningful changes introduced by release 1.4.0.

**Constraints:** Describe user/developer-relevant changes rather than every internal commit.

**Explanation:** A changelog is a historical record, so entries should remain understandable after the original release work is forgotten.

**Common mistakes:** Writing vague entries such as 'various fixes' or copying raw commit messages without context.

**Expected output:** A concise changelog entry for version 1.4.0.

### Exercise 10 — Release Notes

**Objective:** Communicate a specific release.

**Solution:**

```markdown
# Release 1.4.0

## Summary
Adds CSV batch processing.

## Important Changes
- New batch CLI flow.
- Improved validation diagnostics.

## Operations
No new required environment variables.

## Verification
Run the documented smoke test.

## Rollback
Return to the previously deployed 1.3.x artifact if compatibility conditions permit.
```

**Common mistake:** copying the entire changelog instead of highlighting the current release.

**Problem:** Communicate what users and operators need to know about release 1.4.0.

**Constraints:** Focus on this release and clearly call out operational or migration impact.

**Explanation:** Release notes are communication about a specific version, not a complete repository history.

**Common mistakes:** Hiding breaking changes, omitting upgrade instructions, or pasting the entire changelog unchanged.

**Expected output:** Release notes focused on version 1.4.0 and its operational impact.

### Exercise 11 — Deployment Handoff

**Objective:** Transfer release context.

**Solution:**

```text
Release: 1.4.0
Artifact: example-artifact-1.4.0
Changes: CSV batch support
Dependencies: none
Configuration: no new required settings
Verification: smoke test + sample batch
Rollback: previous known-good artifact
Owner: Data Processing Team
```

**Problem:** Prepare a concise deployment handoff for release 1.4.0.

**Constraints:** Do not include secrets or undocumented destructive actions.

**Explanation:** The handoff transfers the context the deployment team needs to execute and verify the change.

**Common mistakes:** Omitting artifact identity, verification, configuration impacts, or rollback.

**Expected output:** A deployment handoff containing release identity, changes, verification, and rollback.

### Exercise 12 — Rollback Reasoning

**Objective:** Understand why rollback can be unsafe.

**Problem:** Version 2.0 changes the persisted data format.

**Expected reasoning:** Returning to version 1.x may fail if 1.x cannot read the new format.

**Solution:** Check compatibility before rollback. Use a forward-compatible migration or restore strategy when code rollback alone is insufficient.

**Constraints:** Reason about compatibility before recommending a rollback.

**Explanation:** Code rollback is only safe when the previous version can operate with the current configuration, data, and state.

**Common mistakes:** Assuming every deployment is reversible by simply redeploying the previous code version.

**Expected output:** A safe rollback decision with compatibility considerations.

### Exercise 13 — Documentation Drift

**Objective:** Detect stale instructions.

**Problem:** README says `python app.py`, but the supported interface is `python -m app`.

**Solution:** Update the documentation to the supported invocation and review all linked examples for related drift.

**Production lesson:** Documentation changes belong in the same change workflow as behavior changes.

**Constraints:** Update the current supported command and check related examples for the same documentation drift.

**Explanation:** Documentation is part of the product surface and should change with user-visible interface changes.

**Common mistakes:** Fixing one command while leaving contradictory examples elsewhere.

**Expected output:** Updated usage documentation that matches the supported CLI invocation.

### Exercise 14 — AI Pipeline Runbook

**Objective:** Apply the method to Applied AI.

**Problem:** A batch inference job stops after partial completion.

**Solution outline:**

```text
Identify batch/job ID
→ inspect status
→ identify processed portion
→ inspect logs
→ verify result state
→ decide whether retry is safe
→ retry according to idempotency design
→ validate outputs
→ record final status
```

**Constraints:** Keep the procedure provider-neutral and rely on the pipeline's idempotency and validation design.

**Explanation:** The goal is to connect operational recovery to batch identity, partial completion, validation, logs, and safe retry.

**Common mistakes:** Retrying every failed batch without determining what already completed or ignoring invalid model output.

**Expected output:** A provider-neutral recovery procedure for a partially completed batch inference job.

**Solution:** Use the solution outline shown in the exercise and require job identity, state inspection, safe retry, output validation, and escalation outside the documented assumptions.

### Exercise 15 — Production Readiness Review

**Objective:** Evaluate whether a small Python CLI is operationally ready.

**Problem:** The code has tests, but no README, configuration guide, rollback path, or release identifier.

**Solution:** Treat the project as incomplete from an operational-readiness perspective. Add the missing artifacts in proportion to the CLI's risk and deployment context.

**Constraints:** Judge readiness relative to the CLI's actual risk and deployment context.

**Explanation:** Automated tests are necessary but do not replace operational documentation, release identity, and recovery planning.

**Common mistakes:** Declaring a project production-ready solely because all tests pass.

**Expected output:** A readiness decision and a list of the missing operational artifacts.

### Exercise 16 — Trace an Incident

**Objective:** Practice release traceability.

**Problem:** Users report behavior that began after a recent deployment.

**Solution:**

```text
Observed incident
→ identify deployed version
→ identify artifact
→ inspect release notes
→ inspect deployment history
→ inspect relevant logs
→ compare with previous release
→ choose rollback/recovery path
```

**Constraints:** Use only evidence that can be traced to source, release, artifact, deployment, and runtime behavior.

**Explanation:** Traceability narrows an incident from a vague 'recent change' to an identifiable release path.

**Common mistakes:** Guessing which commit caused the problem without first identifying the deployed artifact.

**Expected output:** A traceability path from the incident to the deployed release/artifact and recovery decision.

### Exercise 17 — Safe Operational Wording

**Objective:** Remove dangerous ambiguity.

**Problem:** A runbook says “clean old output files.”

**Solution:** Replace it with bounded steps that identify the exact job, path, state, and conditions before deleting anything.

**Constraints:** Actions must be tightly scoped to the confirmed job, path, and state.

**Explanation:** Operational safety comes from explicit preconditions and bounded actions, especially before deletion.

**Common mistakes:** Using broad wildcard deletion or assuming a filename alone proves ownership of an artifact.

**Expected output:** A bounded operational procedure that identifies exactly which temporary artifacts may be removed.

### Exercise 18 — Review a Runbook

**Objective:** Find missing operational controls.

**Problem:** A runbook has procedure steps but no verification, rollback, or escalation.

**Solution:** Add all three. The operator must know what success looks like, what recovery path exists, and when to stop.

**Constraints:** Keep the original procedure but add only the controls needed to make it verifiable and safely bounded.

**Explanation:** Verification, rollback, and escalation are distinct controls that answer success, recovery, and stopping-boundary questions.

**Common mistakes:** Adding more steps without defining what evidence proves completion.

**Expected output:** A revised runbook containing verification, rollback, and escalation controls.

### Exercise 19 — AI Release Handoff

**Objective:** Apply release discipline to an AI pipeline.

**Expected output:** Document version, model/configuration change, dependency change, input/output impact, verification method, known issues, rollback limitations, and owner.

**Problem:** Prepare a release handoff for an AI pipeline whose model/configuration behavior changed.

**Constraints:** Document the change without exposing credentials or making provider-specific claims that the project does not establish.

**Solution:** Include release/version identity, model and configuration change, dependency change, input/output impact, verification, known issues, rollback limitations, and owner.

**Explanation:** AI systems combine software, configuration, data, and external dependencies, so the handoff must communicate all relevant change surfaces.

**Common mistakes:** Documenting only Python-code changes and ignoring model/configuration or operational impact.

### Exercise 20 — Documentation Acceptance Test

**Objective:** Verify documentation is actually usable.

**Procedure:**

1. Give the README to someone who did not write the application.
2. Ask them to install and run the documented command.
3. Do not answer questions verbally.
4. Record each point where they get stuck.
5. Update documentation.
6. Repeat until the main path is reproducible.

**Production lesson:** One of the strongest documentation tests is whether another competent engineer can use it without tribal knowledge.

**Problem:** Create a test that reveals whether a README and its instructions are actually usable by a new engineer.

**Constraints:** Do not provide verbal assistance during the first trial.

**Solution:** Have an uninvolved engineer follow the README from a clean environment, record every point of confusion, update the documentation, and repeat.

**Explanation:** This turns documentation quality into an observable usability test rather than an author opinion.

**Common mistakes:** Testing only with the original author or correcting the reader verbally instead of fixing the documentation.

**Expected output:** A repeatable documentation usability test and a list of findings to feed back into the README.

## 75. Mini-Project

# Production Readiness Documentation Pack

Create, conceptually, a documentation pack for a Python application named `expense_processor`.

## Project scenario

The application is a batch CLI that reads CSV expenses, validates rows, produces a JSON summary, and runs on a daily schedule.

## Required artifacts

```text
README
Runbook
Release checklist
Changelog
Release notes
Deployment handoff
Rollback procedure
Troubleshooting guide
```

## Acceptance criteria

The documentation pack must allow a new engineer to answer:

```text
What is the system?
How do I install it?
How do I configure it?
How do I run it?
How do I test it?
What can fail?
How do I recover a failed batch?
How do I release it?
How do I verify deployment?
How do I roll back?
```

## Scenario A — Normal operation

Document the successful workflow.

## Scenario B — Batch failure

Document how to inspect state, logs, and output, then decide whether retry is safe.

## Scenario C — Release

Prepare a version, changelog entry, release notes, artifact identifier, deployment handoff, verification steps, and rollback.

## Scenario D — Documentation review

A reviewer must be able to follow the README and runbook without needing an undocumented verbal explanation.

## Production improvements

After completing the basic pack, consider:

- automated documentation checks;
- tested command examples;
- release templates;
- ownership information;
- links between README and runbooks;
- incident evidence requirements;
- deployment version traceability.

## 76. Interview Questions

## Beginner

### Question
What is a README?

### How to Think
Think about the first document a new engineer sees in a repository.

### Answer
A README is the primary project entry point that explains what the project does and how to get started, configured, run, tested, and understood.

### Why It Matters
Without it, basic project knowledge becomes tribal knowledge.

---

### Question
What is a runbook?

### How to Think
Think about an operator handling a known task or failure.

### Answer
A runbook is a step-by-step operational procedure for performing a known task or responding to a known situation safely.

### Why It Matters
It reduces ambiguity during routine operations and incidents.

---

### Question
What is a release?

### How to Think
Separate source code from the identifiable version made available for use.

### Answer
A release is a specific software version prepared and identified for users or deployment.

### Why It Matters
Release identity enables traceability and communication.

---

### Question
What is the difference between a release and deployment?

### Answer
A release identifies a version of software made available for use. Deployment is the act of placing a particular artifact/release into a target environment.

### Why It Matters
A release can exist before it is deployed, and one release may be deployed to multiple environments.

---

## Intermediate

### Question
What should a production README contain?

### Answer
At minimum, enough information to explain purpose, prerequisites, installation, configuration, usage, inputs/outputs, testing, troubleshooting, and where to find deeper operational/release documentation.

### Why It Matters
The README should reduce the need for guessing.

---

### Question
Why is a runbook different from a README?

### Answer
The README is project-oriented. A runbook is task- or incident-oriented and provides explicit operational steps, verification, failure handling, and escalation.

### Why It Matters
Different readers need different information under different conditions.

---

### Question
Why is post-deployment verification necessary?

### Answer
Because a deployment mechanism can report a successful operation even when the application itself is unhealthy or misconfigured.

### Why It Matters
Verification tests the actual system behavior that matters.

---

### Question
Why is rollback harder when data changes are involved?

### Answer
Old application code may not be compatible with new data or schema state.

### Why It Matters
Rollback design must include state and data compatibility, not just code version.

---

### Question
What is Semantic Versioning?

### Answer
A versioning convention using MAJOR.MINOR.PATCH to communicate intended compatibility and change magnitude.

### Why It Matters
It gives humans a shared vocabulary for releases, but still requires release-note and compatibility review.

---

## Advanced

### Question
How would you make a deployment safely reversible?

### Answer
Identify immutable or otherwise traceable artifacts, define a known-good previous version, document rollback prerequisites, execute controlled deployment, verify after deployment, and define what to do if rollback itself fails. Include data/configuration compatibility in the recovery design.

### Why It Matters
Rollback is a recovery mechanism, not merely a Git operation.

---

### Question
How would you document a production AI pipeline?

### Answer
Document system purpose, prerequisites, configuration, input/output contracts, model or external-service dependencies, execution procedure, validation, failure/retry behavior, idempotency, persistence, operational symptoms, release process, verification, and rollback considerations.

### Why It Matters
AI pipelines combine multiple failure boundaries, so hidden assumptions become expensive.

---

### Question
What should deployment handoff contain?

### Answer
Release identity, summary of changes, configuration and dependency changes, data impacts, known issues, deployment procedure, verification, rollback path, and responsible team or role.

### Why It Matters
It transfers the context needed to operate the change safely.

## 77. Architecture Questions

### 1. How would you design documentation for a production AI service?

**Structured answer:** Provide a concise README for project orientation and developer setup, dedicated operational runbooks for known failure modes and deployment/recovery tasks, and release documentation for versioned changes. Link them together around stable identifiers, configuration, dependencies, and verification.

**Simplified assumption:** The service has a separate operational ownership model.

### 2. What information should be available to an on-call engineer?

**Answer:** Current version, health/status, important logs, safe configuration context, known failure symptoms, diagnostic steps, retry policy, rollback procedure, escalation boundary, and evidence requirements.

### 3. How would you design a runbook for a failed batch inference job?

**Answer:** Start with a symptom and scope check, identify job and input IDs, inspect logs and output state, determine partial completion, verify whether retry is safe, execute the documented retry or recovery path, validate outputs, and escalate outside the documented assumptions.

### 4. How would you make a deployment safely reversible?

**Answer:** Build traceable release artifacts, retain a known-good version, define rollback preconditions, verify deployment, and treat data/configuration changes as first-class rollback concerns.

### 5. How would you ensure the deployed artifact can be identified?

**Answer:** Use a release/version identifier and maintain traceability from source state through build artifact to deployment record.

### 6. How would you connect releases to production incidents?

**Answer:** Record the deployed release/artifact identifier and correlate incident timestamps, deployment history, logs, and release notes.

### 7. How would you design deployment handoff?

**Answer:** Use a standard template containing version, change summary, dependency/configuration impacts, verification, rollback, and ownership.

### 8. How would you document an AI pipeline with external model/API dependencies?

**Answer:** Document configuration and dependency boundaries explicitly, including inputs, outputs, failure behavior, retries, validation, and operational verification while keeping provider-specific assumptions tied to actual project documentation.

### 9. How would you design rollback when data schema changes are involved?

**Answer:** First establish whether the old application version can safely consume the new state. If not, use a forward-compatible recovery or data migration strategy rather than assuming code rollback is safe.

### 10. What documentation should be mandatory before a service is considered production-ready?

**Answer:** At minimum: project README, tested setup instructions, configuration documentation, operational procedures for known critical failures, deployment verification, release identification, and recovery/rollback guidance appropriate to the system's risk.

## 78. Knowledge Check

### Conceptual Questions

1. Why is “the code works” not enough to call a project production-ready?
2. What are the primary questions a README should answer?
3. Why does audience matter when writing documentation?
4. What makes a runbook different from a README?
5. Why should a runbook include verification?
6. Why should a runbook define escalation?
7. Why is a release different from a deployment?
8. Why do version identifiers matter?
9. What does MAJOR.MINOR.PATCH communicate?
10. Why does a version number not guarantee compatibility?
11. Why is a changelog different from release notes?
12. Why is deployment verification necessary?
13. Why can rollback fail?
14. Why is release traceability useful?

### Answers

1. Because another engineer must be able to reproduce, operate, troubleshoot, release, and recover the system.
2. Purpose, prerequisites, installation, configuration, usage, tests, inputs/outputs, and troubleshooting or links to it.
3. Different readers need different information in different orders.
4. A runbook is a bounded operational procedure for a task or known situation.
5. Without verification, the operator may assume an action succeeded.
6. To define when the documented self-service procedure no longer safely applies.
7. A release identifies software made available; deployment places an artifact into a target environment.
8. Versions create a shared identity for changes and support rollback and debugging.
9. Intended compatibility/change magnitude under the project's versioning convention.
10. Because compatibility is a property of actual behavior and policy, not merely numbering.
11. A changelog is historical; release notes focus on a specific release and its implications.
12. Mechanical deployment success does not prove application health.
13. Artifact, configuration, data, schema, or state compatibility may prevent a simple reversal.
14. It allows engineers to connect incidents and behavior back to a specific source/release/artifact/deployment.

### README Analysis

**Question:** A README says “Run the application” but does not name Python version, install command, environment variables, or startup command. Is it complete?

**Answer:** No. It leaves critical guesses to the reader.

### Runbook Analysis

**Question:** A runbook says “restart the service,” but has no preconditions or verification. What is missing?

**Answer:** Scope checks, safe procedure detail, expected result, and failure/escalation handling.

### Release Reasoning

**Question:** A release build succeeded, but a required environment variable was not added to deployment configuration. Is the release operationally ready?

**Answer:** Not necessarily. The software may be built correctly but fail at startup or runtime. Release readiness includes configuration and deployment requirements.

### Architecture Scenario

**Question:** An AI service was deployed successfully but returns malformed model output. Where should you look first?

**Answer:** Verify the deployed version, inspect release notes for behavioral changes, inspect configuration, inspect logs around response parsing/validation, and compare against the previous known-good release before deciding whether rollback is appropriate.

## 79. Completion Checklist

## Completion Checklist

### Production Fundamentals

- [ ] I understand what production-ready means in context.
- [ ] I understand why documentation is part of engineering.
- [ ] I can distinguish project usability from internal code correctness.

### README

- [ ] I can explain the purpose of a README.
- [ ] I can identify the primary audience.
- [ ] I can document prerequisites.
- [ ] I can document installation.
- [ ] I can document configuration.
- [ ] I can document environment variables safely.
- [ ] I can document CLI usage.
- [ ] I can document input/output contracts.
- [ ] I can provide useful examples.
- [ ] I can document testing.
- [ ] I can write troubleshooting guidance.
- [ ] I can document meaningful project structure.
- [ ] I understand README vs comments vs docstrings.

### Runbooks

- [ ] I understand operational documentation.
- [ ] I can explain what a runbook is.
- [ ] I can define when a runbook should be used.
- [ ] I can write preconditions.
- [ ] I can define expected initial state.
- [ ] I can write ordered procedures.
- [ ] I can define verification.
- [ ] I can define failure handling.
- [ ] I can write rollback steps.
- [ ] I can define escalation conditions.
- [ ] I can define required evidence.
- [ ] I can write a deployment runbook.
- [ ] I can write a batch/data pipeline runbook.
- [ ] I can write an AI/LLM operational runbook.

### Release

- [ ] I understand release vs deployment.
- [ ] I understand source vs commit vs artifact vs release.
- [ ] I understand versioning.
- [ ] I understand Semantic Versioning.
- [ ] I understand pre-release versions.
- [ ] I can maintain a changelog.
- [ ] I can write release notes.
- [ ] I can prepare a release checklist.
- [ ] I can verify dependencies and configuration before release.
- [ ] I can identify a release artifact.
- [ ] I can prepare a deployment handoff.
- [ ] I can define post-deployment verification.
- [ ] I understand rollback limitations.
- [ ] I understand hotfix basics.
- [ ] I understand release traceability.
- [ ] I understand Git tags conceptually.

### Production Readiness

- [ ] I can connect documentation, logging, validation, idempotency, safe writes, dependency management, and release discipline.
- [ ] I can design recovery procedures for known failure modes.
- [ ] I can apply these practices to data engineering.
- [ ] I can apply these practices to Applied AI systems.

## Final Self-Review

Before calling this chapter complete, confirm:

- beginner concepts come before advanced terminology;
- commands are clearly labeled as shell commands;
- Python examples are clearly labeled;
- hypothetical project commands are identified as examples;
- no real secrets are included;
- README, runbook, changelog, release notes, and deployment handoff are distinguished;
- release and deployment are distinguished;
- rollback limitations are explained;
- documentation drift is explained;
- production readiness remains contextual;
- no unnecessary DevOps/SRE/Kubernetes material has replaced the requested Stage 1 scope.


---

# Final File-Scope Verification

This chapter is intended to be the only artifact created or changed for this task:

```text
08-readmes-runbooks-and-release-basics.md
```

No other Markdown, Python, project, configuration, or directory should be modified by the chapter-generation process.

The `/mnt/data` working area used for the downloadable artifact is not assumed to be the user's Git repository. Where no repository is mounted, an actual Git working-tree diff cannot be truthfully reported. The important scope control for this task is that this generation step writes only the requested target artifact.

## Final quality summary

The completed chapter includes:

```text
README
→ setup/configuration
→ usage
→ testing
→ troubleshooting
→ runbooks
→ deployment
→ verification
→ release
→ versioning
→ changelog
→ release notes
→ handoff
→ rollback
→ AI/data production examples
```

The intended learner outcome is:

> **“I can document how the project works, create operational procedures, prepare a release, hand it off for deployment, verify the deployment, and provide a safe rollback path.”**
