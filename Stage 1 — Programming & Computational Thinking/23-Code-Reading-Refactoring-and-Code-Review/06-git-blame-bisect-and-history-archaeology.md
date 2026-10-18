# Git Blame, Bisect and History Archaeology

> **Stage 1 — Programming & Computational Thinking**  
> **Module 1.23 — Code Reading, Refactoring and Code Review**  
> **Lesson 06 of 08**  
> **Target environment:** Git 2.40+, Python 3.12+, a shell, and optionally GitHub CLI (`gh`).  
> **Level:** beginner → intermediate → advanced.

## Learning outcomes

By the end of this lesson, you should be able to:

- Reconstruct a change from commits, diffs, branches, tags, pull requests, issues, and design records.
- Use `git log`, `git show`, `git diff`, and `git blame` to investigate a line or behaviour without treating authorship as personal fault.
- Choose correctly among `git log -S`, `-G`, and `-L`.
- Find a regression with manual and automated `git bisect`, including correct handling of untestable revisions and exit codes.
- Keep blame useful after mass formatting, recover reachable or dangling work safely, and compare releases.
- Analyse churn, co-change coupling, bug-fix density, ownership concentration, and production build provenance.
- Investigate large repositories while understanding the limits of shallow history and partial clones.
- Preserve traceability through release, merge, signing, integrity, and incident-response practices.
- Complete the capstone: reproduce a seeded regression, locate its introducing commit, fix it, and document prevention in a concise postmortem.

## 1. Mental model: history is evidence, not omniscience

Git stores snapshots and relationships between commits. A commit identifies a snapshot plus parent commit(s), metadata, and a message. Most ordinary commits have one parent; a merge commit has two or more. Branch names are movable references; tags are references often used to identify releases. A commit ID identifies an object (typically displayed as a hexadecimal hash); abbreviated IDs in examples below are **illustrative**, not evidence from your repository.

History can answer questions such as:

- What changed between the last known-good build and the first known-bad build?
- When did this condition appear, and which surrounding change introduced it?
- Was a line moved or reformatted rather than logically changed?
- Which issue or operational constraint motivated a design?
- Does the deployed artifact correspond to the commit and release we think it does?

History alone cannot prove why a change was made, whether it was deployed, whether a test was representative, or whether a person was at fault. Commit messages can be incomplete; authorship metadata can be configured incorrectly; branches may be rewritten; tests may be flaky; a regression can emerge from an interaction among several changes. Triangulate Git evidence with tests, build metadata, PR discussion, issue records, design docs, telemetry, and incident reports.

### A safe investigation posture

1. Start with a question and preserve the current state. Record the current branch and working tree before switching revisions.
2. Prefer read-only inspection (`log`, `show`, `diff`, `blame`) before modifying anything.
3. Reproduce the failure with a small, deterministic test or benchmark before bisecting.
4. Distinguish observed facts from hypotheses. Record the command, revision, environment, and result.
5. Use a disposable clone or worktree for risky experiments. Do not reset, rebase, or force-push a shared branch as an investigative shortcut.

Useful opening commands:

```bash
git status --short --branch
git log --oneline --graph --decorate --all -30
git remote -v
git tag --sort=-creatordate | head -20
```

`git status` reveals uncommitted work; `log` shows the visible commit graph; `remote -v` identifies configured remotes; tags provide candidate release landmarks but do not themselves prove what is deployed.

## 2. Beginner: inspect commits and diffs

### 2.1 `git log`: find the relevant time window

```bash
# Compact graph, including refs that are locally available
git log --oneline --graph --decorate --all

# Changes and patches for one path
git log -p -- src/etl/transform.py

# Follow a file across detected renames (best-effort for one path)
git log --follow --oneline -- src/etl/transform.py

# Narrow the search by date or author
git log --since="2025-01-01" --until="2025-03-31" --oneline -- src/
git log --author="A. Engineer" --oneline -- src/etl/

# Summaries rather than full patches
git log --stat --oneline -20
```

Interpretation:

- `--oneline` shortens each commit to an abbreviated ID and subject.
- `--graph --decorate --all` makes visible local branches/tags and merge topology; it cannot show refs or objects you have not fetched.
- `-p` prints patches. It is useful for a narrow path, but can be overwhelming across a large history.
- `--follow` follows a single path through detected renames; rename detection is heuristic and this option is not a universal multi-path history query.
- Date and author filters are search aids, not proof that the selected commit caused the incident.

### 2.2 `git show` and `git diff`: inspect what actually changed

```bash
# Commit metadata and patch
git show a1b2c3d

# Summary for a commit
git show --stat --oneline a1b2c3d

# Compare two snapshots
git diff v1.3.0..v1.4.0 -- src/

# Compare the topic branch with its merge base against main
git diff origin/main...feature/retry-policy -- src/
```

For `git diff A..B`, Git compares the trees at A and B. For `git diff A...B`, Git compares the merge base of A and B with B; this is often useful for reviewing a topic branch against its common starting point. The three-dot form is not the same as a symmetric difference of all commits.

Inspect surrounding context, not only the changed line. A one-line change can alter a caller's assumptions, exception propagation, ordering, or transaction boundaries. For an unfamiliar commit, use:

```bash
git show --format=fuller --find-renames a1b2c3d
git show a1b2c3d^..a1b2c3d -- path/to/file.py
git diff --check v1.4.0...HEAD
```

`--format=fuller` displays fuller author/committer metadata. `--find-renames` asks Git to detect likely renames. `diff --check` detects whitespace errors in the patch; it is not a semantic test.

### 2.3 `git blame`: identify the commit associated with a line

```bash
git blame src/etl/transform.py
git blame -L 80,120 -- src/etl/transform.py
# Inspect a historical version of the file, not only the working-tree version
git blame v1.4.0 -L 80,120 -- src/etl/transform.py
```

Blame attributes lines in a selected file version to commits based on Git's line matching. It is a navigation tool: use the commit ID beside an interesting line, then inspect that commit and its context.

```bash
git show a1b2c3d
git log --oneline --decorate a1b2c3d^..a1b2c3d
```

For a line that looks suspicious, ask:

- Did the line first appear in this commit, or was it moved/copied from somewhere else?
- What else changed in the same commit?
- What issue, PR, incident, or requirement explains it?
- Did later commits modify its assumptions or its callers?

Blame is not a fault-finding mechanism. The displayed author may have performed a mechanical reformat, moved the code, or implemented a decision made elsewhere. Authorship and intent are different questions.

### 2.4 Blame limitations and useful options

```bash
# Ignore whitespace-only differences when matching lines
git blame -w -L 80,120 -- src/etl/transform.py

# Try to detect lines moved/copied from other files or locations
git blame -C -C -C -L 80,120 -- src/etl/transform.py

# Ignore one known mechanical commit for this invocation
git blame --ignore-rev a1b2c3d -- src/etl/transform.py
```

`-w` ignores whitespace changes during line matching. `-C` options expand copy/move detection; repeated `-C` can broaden the search and cost more time. These options improve attribution in some cases, but line matching remains heuristic. A blame result should be verified with the actual diff and related history.

### 2.5 Commit messages that support investigation

A useful commit subject is concise, imperative, and specific (the roadmap suggests a subject of at most 72 characters). The body should explain **why**, note important trade-offs, and link to an issue or PR. Atomic commits make it easier to bisect and understand intent. Conventional Commit prefixes can aid automation when a project uses them, but the project's own conventions take precedence.

Example:

```text
Handle expired credentials without retrying

Authentication failures are permanent until credentials change. Retrying
401 responses amplified load during token-service incidents. Retry only
transient transport failures; see issue #482 and incident INC-219.
```

The message is a map to evidence, not a substitute for the patch or tests.

## 3. Intermediate: choose the right history search

### 3.1 `git log -S`: search for a change in string occurrence count

```bash
git log --all --oneline -S'retry_count' -- src/
git log -p --all -S'retry_count' -- src/etl/client.py
```

`-S<string>` (the pickaxe string search) finds commits where the **number of occurrences** of that string changes in the diff. Use it when you remember a variable, flag, literal, or call that appeared or disappeared. It can miss a commit that rearranges text but leaves the occurrence count unchanged.

### 3.2 `git log -G`: search diffs with a regular expression

```bash
git log --all --oneline -G'retry.*(401|429)' -- src/
git log -p --all -G'raise .*Timeout' -- src/etl/client.py
```

`-G<regex>` selects commits whose added or removed diff lines match the regular expression. It is often better when wording changes but a pattern remains. `-S` and `-G` answer related but different questions; neither is a general semantic code search.

### 3.3 `git log -L`: trace a line range or function

```bash
# Track a known line range
git log -L 80,120:src/etl/transform.py

# Track a function by name (works with supported language/function parsing)
git log -L :normalise_record:src/etl/transform.py
```

`-L` walks the history of a line range or function. Function-name tracking depends on Git's supported function-pattern handling and language configuration; if detection fails, use a line range or inspect successive revisions manually. `-L` has constraints and should not be combined casually with arbitrary revision/path filters; check `git log -h` for the installed Git version.

### 3.4 Search messages and reconstruct intent

```bash
git log --grep="timeout" -i --oneline --all
git log --format='%H%n%an <%ae>%n%ad%n%s%n%b' --date=short -10
git log --follow --oneline -- src/etl/transform.py
```

When GitHub CLI and repository access are available:

```bash
gh pr view <number> --comments
gh issue view <number> --comments
gh search prs "retry_count repo:ORG/REPO"
```

Commands that query hosted PRs/issues require a configured `gh` session and network access. For GitLab or another host, use the equivalent PR/MR and issue interface. Follow the evidence chain:

**current code → introducing commit → complete diff → PR discussion → issue → design record/ADR → incident/postmortem**.

Read removed code too. A deleted workaround can explain a later failure; a rejected alternative can prevent repeating an unsuccessful experiment. Record the relevant commit/tag and line references so another engineer can reproduce your reasoning.

## 4. Regression hunting with `git bisect`

`git bisect` performs a binary search over commit history. You mark one revision **bad** (the behaviour is present) and one earlier revision **good** (the behaviour is absent). Git checks out intermediate candidates and asks you to classify them. With a monotonic regression and no skipped revisions, a range of about 1,000 commits takes roughly 10 binary-search steps because \(\log_2(1000) \approx 10\).

### 4.1 Preconditions: make the test trustworthy

Before bisecting:

1. Write a small regression test or script that fails on the bad version and passes on the good version.
2. Verify both endpoint classifications deliberately.
3. Keep test inputs, dependencies, environment variables, and data stable.
4. Make each test invocation fast and deterministic.
5. Identify revisions that cannot be built or tested and decide how to mark them untestable.

If the failure is intermittent, a single run per revision is not enough. Use repeated trials and a threshold that reflects the incident's definition. For a performance regression, control load and environment; a noisy benchmark can misclassify commits.

### 4.2 Manual bisect walkthrough

Assume a repository's `v1.4.0` release passes `tests/test_totals.py::test_rounding`, but current `HEAD` fails. The names and output below are illustrative.

```bash
git status --short --branch
# Save/commit or otherwise preserve work before starting.
git bisect start
git bisect bad HEAD
git bisect good v1.4.0
```

Git checks out a candidate revision and reports how many commits remain. Run the same test at every candidate:

```bash
uv run pytest tests/test_totals.py::test_rounding -q
```

If it fails for the same regression, run `git bisect bad`; if it passes, run `git bisect good`. If the revision cannot be tested for a reason unrelated to the behaviour (for example, a required compiler is absent), use `git bisect skip` rather than guessing. Continue until Git reports the first bad commit or a range of possible commits due to skips.

```bash
git bisect log       # retain the classifications and commands
git bisect reset     # leave bisect mode and return to the original checkout
```

Always reset after the investigation. `git bisect reset` normally returns to the branch/commit that was checked out before bisect began. Check `git status` afterwards.

### 4.3 `git bisect run`: exit codes matter

The test command must return status codes Git understands:

- `0`: this revision is **good**.
- `1` through `124`: this revision is **bad**.
- `125`: this revision is **untestable; skip it**.
- `126` and `127`: Git treats these as bad under the documented `bisect run` convention, but they often indicate a script/command setup problem (permission denied or command not found). Do not silently accept them as a valid product failure; validate the environment first.
- Other values outside the documented range may abort the run; consult `git bisect run` documentation for the installed version.

A common trap is a script that exits non-zero when setup fails. That can falsely mark a commit bad. Make the test distinguish a product regression from an infrastructure failure. Do not use `set -e` blindly around commands whose expected non-zero statuses need classification.

#### Minimal wrapper for a deterministic pytest regression test

Save this as `/tmp/bisect-test.sh` (or another stable path outside the changing worktree). Keeping the wrapper outside the repository means older revisions do not need to contain the script. It assumes the test exists at every revision, dependencies are provisioned consistently, and pytest's failure means the target regression is present.

```bash
#!/usr/bin/env bash
# 0 = target test passed; 1 = target test failed; 125 = cannot classify.
set -u

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is unavailable; cannot test this revision" >&2
  exit 125
fi

output=$(mktemp) || exit 125
trap 'rm -f "$output"' EXIT
uv run --frozen pytest -q tests/test_totals.py::test_rounding >"$output" 2>&1
status=$?
cat "$output"
case "$status" in
  0)
    # A zero runner status is not enough if the target was skipped/deselected.
    if grep -Eq '(^|[[:space:]])1 passed([[:space:]]|$)' "$output"; then
      exit 0
    fi
    echo "Target test did not report one pass; cannot classify" >&2
    exit 125
    ;;
  1)
    # Do not treat setup/runner failures or test errors as a product regression.
    if grep -Fq 'FAILED tests/test_totals.py::test_rounding' "$output"; then
      exit 1
    fi
    echo "Status 1 without the target test's FAILED report; cannot classify" >&2
    exit 125
    ;;
  *)
    # Includes collection/usage/internal errors and dependency/runner failures.
    exit 125
    ;;
esac
```

**Important:** pytest uses exit status `1` for test failures, `2` for interrupted/usage errors, `3` for internal errors, `4` for command-line usage errors, and `5` when no tests are collected. The wrapper maps only status `1` to bad and maps other nonzero statuses to skip. If the test itself uses a different failure contract, adapt the mapping and validate it. `uv run --frozen` assumes a lockfile exists and that each checked-out revision can use it; dependency drift across historical commits can still make revisions untestable.

Run it in the bisect session:

```bash
chmod +x /tmp/bisect-test.sh
git bisect start
git bisect bad HEAD
git bisect good v1.4.0
git bisect run /tmp/bisect-test.sh
git bisect log
git bisect reset
```

**Classification caveat:** the wrapper above checks pytest's output as well as its process status. It is intentionally narrow: it expects exactly one test to pass or the target test to appear in a `FAILED` line. Adapt the match if your pinned pytest version or output format differs, and test the wrapper with known-good, known-bad, skipped, and environment-failure cases before trusting a bisect. If output cannot distinguish the target regression from setup/test errors, return `125` rather than guessing.

Ensure the wrapper runs from the repository root that Git has checked out and does not accidentally test a separate clone or a fixed path. If the wrapper needs repository-relative files, resolve them from the current working directory rather than its own `/tmp` directory.

### 4.4 Difficult bisect cases

- **Flaky tests:** run the test multiple times per revision and use a predeclared rule, such as “bad if at least 4 of 5 runs fail.” Ensure the wrapper exits 125 if it cannot obtain enough valid observations. Repeated runs increase cost but reduce random misclassification.
- **New or changed fixtures:** if the test file did not exist historically, keep a compatible test harness outside the checked-out tree or selectively copy a stable test into each revision. Do not copy a modern test that assumes APIs absent in old commits without adapting it.
- **Dependency changes:** use containers or revision-specific lockfiles when feasible. A build failure caused by an obsolete dependency environment is not evidence that the application regression exists.
- **Merge-heavy history:** `git bisect start --first-parent` can focus on first-parent commits along an integration branch, but may miss a culprit inside a merged topic branch. Choose the history model that matches the question.
- **Non-code regressions:** include config, schemas, SQL, data fixtures, and deployment manifests in the test. A code-only path filter can exclude the actual cause.
- **Performance regressions:** benchmark repeatedly and compare medians or a robust threshold; pin hardware/runtime conditions where possible. Avoid treating a single noisy measurement as truth.
- **Skipped commits:** skips can leave several possible first-bad commits. Inspect the candidate range manually, test adjacent commits, or bisect a narrower range after improving the environment.

### 4.5 Path-limited bisect

```bash
git bisect start -- src/etl/transform.py
git bisect bad HEAD
git bisect good v1.4.0
```

Path-limited bisect narrows candidate commits to those that changed the specified path(s). It is useful only if you have good reason to believe the regression came from those paths. It can miss a change in a caller, configuration file, dependency lock, or schema. Start without a path limit when the causal surface is uncertain.

## 5. Blame after mass formatting: `.git-blame-ignore-revs`

A formatting-only commit can make every line appear to have changed, obscuring meaningful history. Prefer recording the mechanical commit in `.git-blame-ignore-revs` rather than rewriting history.

```bash
# First inspect and verify the commit is truly mechanical
git show --stat a1b2c3d
git show --word-diff=porcelain a1b2c3d -- path/to/file.py

# Add the full commit ID to .git-blame-ignore-revs
printf '%s\n' '<full-format-commit-id>' >> .git-blame-ignore-revs

git config blame.ignoreRevsFile .git-blame-ignore-revs
git blame --ignore-revs-file .git-blame-ignore-revs -- path/to/file.py
```

The placeholder must be replaced with a real full commit ID from the repository. Commit the ignore file so teammates can reuse it. GitHub also supports a repository-level blame-ignore configuration when the file is present in the repository root.

Important distinctions:

- `git blame --ignore-rev <sha>` ignores one revision for a command.
- `git blame --ignore-revs-file <path>` reads a list of revisions for that command.
- `git config blame.ignoreRevsFile .git-blame-ignore-revs` configures a default path for local Git blame operations.
- Ignoring a revision affects blame attribution only; it does not remove the commit or change the tree, and it does not alter bisect results.
- Ignore only commits verified as mechanical. A “formatting” commit that also changes logic should not be hidden wholesale; split the commit if possible or document the limitation.

## 6. Recovering work and comparing versions safely

### 6.1 `git reflog`: inspect local reference movement

```bash
git reflog --date=iso -20
git show a1b2c3d
```

The reflog records recent movements of local refs such as `HEAD` and branches. It is often the fastest way to locate a commit after an accidental reset, rebase, or branch deletion. Reflogs are local and expire; they are not a backup, and another clone does not automatically share your reflog.

**Recovery workflow:** find the likely commit in the reflog, inspect it with `git show`, then recover into a new branch before changing anything else.

```bash
git branch rescue/investigation a1b2c3d
git switch rescue/investigation
```

This preserves the candidate commit without moving a shared branch. Only after verifying the recovered content should you decide how to integrate it.

### 6.2 `git restore`, `git revert`, and `git reset` are not interchangeable

- `git restore --source=<commit> -- path` restores a path from a selected tree into the working tree (and, with `--staged`, the index). It changes files/index state, not branch history by itself.
- `git revert <commit>` creates a new commit that inverses an earlier commit. It is generally appropriate for undoing a change on a shared branch because history remains visible.
- `git reset` moves the current branch reference and may reset the index and working tree depending on mode. `--hard` discards tracked working-tree/index changes. Use only after understanding the current state, and avoid it on shared branch history.
- `git cherry-pick <commit>` applies a commit's change as a new commit on the current branch. Resolve conflicts and run tests before pushing.

Before recovery or undo:

```bash
git status --short --branch
git branch rescue/before-recovery HEAD
```

A rescue branch protects the current commit, not uncommitted files; preserve uncommitted work separately (commit it, stash it, or make a verified copy) before destructive operations.

### 6.3 `git worktree`: compare revisions without repeatedly switching

```bash
git worktree add ../repo-v1.4 v1.4.0
# If main is already checked out in the original worktree, use a detached worktree:
git worktree add --detach ../repo-current main
# Otherwise, a branch can be checked out in the new worktree directly:
# git worktree add ../repo-current main
# Run tests in each directory with its appropriate environment.
git worktree list
# After work is complete and the worktree is clean:
git worktree remove ../repo-v1.4
```

Worktrees share the underlying object database but have separate working directories and checkouts. They are useful for comparing old and new behavior without repeatedly changing the main working tree. A branch can normally be checked out in only one worktree at a time; if `main` is already checked out in the original worktree, `git worktree add ../repo-current main` fails, so use `--detach` as shown or select a different branch. Do not remove a worktree with uncommitted work unless you have deliberately preserved it.

### 6.4 Compare releases and identify deployed code

```bash
git diff v1.3.0..v1.4.0 -- src/
git log v1.3.0..v1.4.0 --oneline
git shortlog -sn v1.3.0..v1.4.0
git describe --tags --dirty
```

Read release notes and changelog first, then compare the actual tree. `git describe --tags --dirty` reports a nearby tag plus distance/hash information where possible, and indicates a dirty working tree; it does not guarantee the deployment used that build.

For incidents, record the deployed artifact digest, build ID, source commit SHA, release tag, dependency lock, and configuration version. Emit the build SHA in `--version`, structured logs, metrics labels (within cardinality limits), and container/image labels. If the deployment system cannot map an artifact to a commit, that is a provenance gap to fix.

For a package without an accessible repository, download the exact package versions in isolated directories and compare their contents; do not install unknown artifacts into a production or developer environment merely to inspect them. For example, `pip download package==1.2.3` downloads artifacts; wheel contents should be inspected with archive tools or installed in a disposable environment. Compare release notes and hashes as well as source files.

## 7. Advanced: history mining and engineering signals

History metrics are clues for prioritisation, not objective quality scores. A frequently changed file may be central and healthy; a low-churn file can still be dangerous. Combine history with complexity, ownership, incident severity, tests, and domain context.

### 7.1 Churn and hot spots

A simple churn measure counts how often a file appears in changes over a time window. A hot spot is often a file with both high change frequency and high complexity or defect exposure. Use a consistent time window and document exclusions (merge commits, generated files, formatting-only commits).

```bash
# File-change counts from recent commits; quick exploratory signal, not a complete metric
git log --since="90 days ago" --name-only --format= -- '*.py' \
  | sort | uniq -c | sort -nr | head -20

# Commit-size distribution / large changes
git log --since="90 days ago" --numstat --format='commit %h %s' -- '*.py'

# Investigate changes associated with bug-fix language
git log --since="1 year ago" --grep='fix\|bug\|regression' -i --oneline -- src/
```

Limitations: commit-message searches miss poorly labelled bug fixes and may include commits whose message says “fix” for unrelated reasons. Merge commits and renames can distort counts. Treat the output as a shortlist for review, not a defect rate.

### 7.2 Co-change coupling

Files that repeatedly change together may share a hidden dependency or a common workflow. To investigate, list files per commit and count pairs. Be explicit about whether merge commits, renames, generated files, and large commits are included. A commit touching 200 files can create many meaningless pairs, so consider excluding formatting and bulk-generated changes.

```bash
# Inspect files that changed together in a candidate commit
git show --name-only --format= a1b2c3d

# Quick overview of file lists across history
git log --since="180 days ago" --name-only --format= -- src/
```

For a reliable pair-count report, use a small script or history-mining library that groups paths by commit and counts pair co-occurrences; then inspect the strongest pairs manually. Co-change is correlation, not proof of runtime coupling.

### 7.3 Bug-fix density, time-to-fix, and ownership concentration

Possible signals include:

- **Bug-fix density:** bug-fix commits or incident fixes per file per period, normalized by a stated denominator if comparing files of different sizes.
- **Time-to-fix:** elapsed time between a defect report/incident and a fix. Git commit dates alone are an imperfect proxy; use issue/incident timestamps where available.
- **Author concentration:** whether a small number of contributors account for most changes in a critical area. This can reveal bus-factor risk, but do not treat author names as a quality ranking.
- **Commit-size distribution:** unusually large commits are harder to bisect and understand; separate mechanical changes from semantic changes.

```bash
git shortlog -sn -- src/etl/
git log --format='%an' -- src/etl/ | sort | uniq -c | sort -nr
git log --grep='fix\|bug\|regression' -i --oneline -- src/etl/
```

These shell examples are exploratory. If the project uses squashed merges, inconsistent messages, bots, or renamed files, adjust interpretation accordingly.

### 7.4 PyDriller and related tools

The roadmap names `git-fame`, `gitinspector`, PyDriller, `code-maat`, and CodeScene (commercial). These tools help mine repository history, summarize contributors, and analyse change patterns. Check each tool's current compatibility and licence before adding it to a pipeline.

Illustrative PyDriller sketch (API details can vary by installed version; verify against the version you pin):

```python
from pydriller import Repository
from collections import Counter

repo_path = "."
changes: Counter[str] = Counter()

for commit in Repository(repo_path).traverse_commits():
    message = commit.msg.lower()
    if not any(word in message for word in ("fix", "bug", "regression")):
        continue
    for modification in commit.modified_files:
        path = modification.new_path or modification.old_path
        if path and path.endswith(".py"):
            changes[path] += 1

for path, count in changes.most_common(20):
    print(f"{count:4} {path}")
```

This is a **message-filtered change count**, not a validated bug-fix metric. It can miss bug fixes and include false positives. Pin PyDriller, run on a local clone, inspect merge handling, and compare a sample of results with known incidents. A production-quality analysis should record the time window, merge policy, rename policy, and denominator.

## 8. Large repositories and incomplete history

### 8.1 Sparse checkout, partial clone, and shallow clone

```bash
# Clone without downloading all file contents immediately
git clone --filter=blob:none <repository-url> repo-partial

# Check out only selected directories in a large repository
git -C repo-partial sparse-checkout init --cone
git -C repo-partial sparse-checkout set src/etl tests/etl

# Shallow clone: only a limited recent history (example depth 50)
git clone --depth 50 <repository-url> repo-shallow
```

- **Sparse checkout** limits which paths appear in the working tree; it does not by itself mean the repository has no history for other paths.
- **Partial clone** can defer fetching objects such as blobs. Missing objects may be fetched on demand if the remote supports it; offline investigation can therefore fail when required objects are absent locally.
- **Shallow clone** truncates commit ancestry. `blame`, `log`, and `bisect` may not reach the relevant older commit until history is fetched.

When history seems to stop unexpectedly:

```bash
git rev-parse --is-shallow-repository
git fetch --unshallow   # only for a shallow clone with a suitable remote
```

`git fetch --unshallow` requires an appropriate remote and network access. It is not a universal repair for partial clones or missing objects. `git maintenance` and commit-graph features can improve repository performance but do not restore history that was never fetched. Use path-limited bisect only when the causal path is well supported.

### 8.2 Branches, merge strategies, and traceability

- **Merge commit:** preserves the integration point and parent relationships; helpful for understanding how a topic branch entered the mainline, but can add graph complexity.
- **Squash merge:** produces a compact single commit on the target branch; easy to read at a high level but discards individual topic-branch commits from the target branch's first-parent history unless those commits remain reachable elsewhere.
- **Rebase:** replays commits onto a new base and creates new commit IDs; can produce linear history but rewrites commit identity and may obscure original integration context.

Choose based on team conventions and incident-investigation needs. None is universally best. Preserve PR links and issue references regardless of merge strategy. Before rewriting history, understand who has fetched the branch and coordinate with collaborators. Never rewrite shared history unilaterally.

### 8.3 Interactive rebase, amend, and `filter-repo`

`git rebase -i`, `git commit --amend`, and `git rebase --onto` can clean up local topic branches. They change commit identities. Use them on private/unpublished work or after explicit coordination and a clear recovery plan. Prefer `git push --force-with-lease` over `--force` only when a force push is authorized; `--force-with-lease` reduces the chance of overwriting a remote update but does not make rewriting shared history inherently safe.

If a secret was committed, rewriting history (often with `git filter-repo`) can reduce future exposure, but **history rewriting does not revoke the secret**. Immediately rotate/revoke credentials, investigate use, notify the appropriate security owner, and coordinate cleanup of forks, caches, clones, release artifacts, and CI logs. Treat history cleanup as containment, not the complete incident response.

### 8.4 Conflict resolution and `git rerere`

```bash
# Improve conflict markers with common-ancestor context
git config merge.conflictstyle zdiff3

# Enable reuse of recorded conflict resolutions
git config rerere.enabled true

git rerere status
git mergetool
```

`rerere` (“reuse recorded resolution”) remembers conflict resolutions and may apply them when a similar conflict recurs. Inspect the result; do not assume a previously correct resolution remains semantically correct after surrounding code changes. `git mergetool` launches the configured merge tool. Test after every conflict resolution, especially for schema migrations, lockfiles, and security-sensitive code.

`git notes` can attach auxiliary notes to objects without changing the commit itself, but notes may not travel through every workflow by default. `git replace` can substitute objects locally and is an advanced inspection mechanism; it can make history appear different, so document and remove replacements deliberately. Neither should be mistaken for a normal shared record unless the team has an explicit distribution process.

## 9. Release provenance, signatures, and repository integrity

### 9.1 Map an incident to the deployed revision

For every production incident, establish:

1. Exact artifact/image/package digest and deployment timestamp.
2. Build ID and source commit SHA embedded in the artifact or metadata.
3. Release tag and whether it is annotated/signed.
4. Dependency lockfile and build environment.
5. Runtime configuration, schema version, and feature-flag state.
6. The difference between deployed source and the candidate fix.

```bash
git describe --tags --dirty
git show --no-patch --decorate v1.4.0
git diff a1b2c3d..d4e5f6a --
```

The final command compares two trees. It does not verify the artifact digest or prove the deployed service runs that revision; confirm this with deployment metadata and runtime telemetry.

### 9.2 Verify signed commits and tags

Signing establishes that an object was signed by a key Git can verify under the configured trust setup. It does **not**, by itself, prove that the source is safe, that the signer reviewed it, or that the deployed artifact was built from it.

```bash
# Verify a signed commit
git verify-commit a1b2c3d

# Verify a signed tag
git tag -v v1.4.0

# Inspect signature/trust policy and release process in CI as well.
```

Verification depends on the signing method, key availability, trust configuration, and the repository's policy. Enforce required signatures in hosting/CI where appropriate; check tag protection and release permissions. A valid signature is one control in a larger supply-chain chain of custody.

### 9.3 Inspect suspicious history and dangling objects

```bash
git fsck --full
git fsck --lost-found
```

`git fsck` checks object connectivity and validity. `--lost-found` may write references to dangling objects under `.git/lost-found`; it does not automatically identify which object is valuable or trustworthy. Inspect candidate objects with `git show a1b2c3d` before creating a rescue branch. Dangling objects can result from ordinary rebases and resets, not necessarily malicious activity.

Security investigation questions:

- Was there an unexpected force-push or rewritten release branch?
- Do signed tags/commits verify under the expected keys and policy?
- Do the source commit, CI build record, artifact digest, and deployment record agree?
- Did a dependency, build script, workflow, or release permission change unexpectedly?
- Are suspicious commits present in all expected clones/remotes, or only in one view?

A historical supply-chain incident such as the xz backdoor is a reminder to examine provenance, maintainer access, release artifacts, and build workflows—not a reason to assume that an unusual commit is malicious without evidence. Preserve logs and coordinate with security/release owners before changing the repository during an active incident.

## 10. Incident-investigation worksheet

Copy this worksheet into the incident record. Label each entry **fact**, **hypothesis**, or **unknown**.

| Field | Record |
|---|---|
| Incident / issue ID |  |
| User-visible symptom and start time |  |
| First known-good build / commit |  |
| First known-bad build / commit |  |
| Artifact digest, release tag, source SHA |  |
| Exact reproduction command and result |  |
| Test/data/environment prerequisites |  |
| Relevant `log`, `show`, `blame`, `-S`/`-G`/`-L` findings |  |
| Bisect start/end revisions and skipped revisions |  |
| Candidate introducing commit and evidence |  |
| PR / issue / ADR / incident links |  |
| Root cause (mechanism, not person) |  |
| Fix and regression test |  |
| Rollback / mitigation / monitoring |  |
| Detection gap |  |
| Preventive actions, owner, due date |  |
| Remaining uncertainty |  |

### Example of evidence quality

Weak conclusion: “Commit `abc1234` caused the outage because blame points to Alex.”

Stronger conclusion: “The deterministic regression test passes at `v1.4.0` and fails at `HEAD`. Automated bisect identifies illustrative commit `abc1234`; the patch changed retry classification so HTTP 401 is treated as transient. The PR discussion links this to an earlier timeout incident but contains no test for permanent authentication failures. A new regression test confirms that 401 is not retried; integration logs from the deployed build confirm that the bad retry policy was active.”

The stronger statement names evidence and a causal mechanism without assigning personal blame. Replace all illustrative identifiers with verified incident evidence before using a report operationally.

## 11. Worked end-to-end example

Scenario: nightly ingestion starts making duplicate ledger entries after a release. A local regression test can reproduce the duplicate for one transaction ID.

1. **Identify deployed source:** get the image digest and build SHA from deployment metadata. Verify that SHA exists in the repository; identify the corresponding tag and dependency lock.
2. **Reproduce:** create a small fixture with one transaction and a repeated delivery. Verify the test passes at the known-good release and fails on the deployed revision.
3. **Search history:** use `git log --oneline -- src/etl/ledger.py`, `git log -S'processed_ids' -- src/`, and `git log -G'commit\(' -- src/etl/ledger.py` to locate likely changes. These commands are search strategies, not proof.
4. **Bisect:** mark the deployed revision bad and the last known-good tag good. Run a stable wrapper that classifies only the target test failure as bad and environment failures as skip.
5. **Inspect culprit:** `git show a1b2c3d`; then `git blame -L ...` and `git log -L :apply_transaction:src/etl/ledger.py` to understand the surrounding evolution. Check PR/issue/ADR context.
6. **Fix and test:** correct idempotency at the transaction boundary, add a regression test for duplicate delivery, and test retry/rollback behaviour. Do not assume the line with blame attribution is the only necessary fix.
7. **Release safely:** backport/cherry-pick if required by release policy, run checks, deploy with monitoring, and verify the build SHA in production.
8. **Postmortem:** record root cause, impact, mitigation, why tests did not catch it, and measurable prevention (e.g. duplicate-delivery regression test plus idempotency contract). Do not turn the postmortem into a ranking of individuals.

## 12. Common mistakes and safer alternatives

| Mistake | Why it fails | Safer approach |
|---|---|---|
| Treating `git blame` as proof of fault | Line attribution does not explain intent or deployment | Inspect the full commit, PR, issue, and runtime evidence |
| Running bisect without a reliable test | Random or environment failures misclassify revisions | Validate endpoints; make the test deterministic; skip untestable revisions |
| Mapping every nonzero test exit to “bad” | Setup/collection failures can masquerade as regressions | Classify product failures separately; return 125 when untestable |
| Forgetting `git bisect reset` | Leaves checkout in bisect state | Save `git bisect log`, reset, then check status |
| Using `-S` and `-G` as if identical | One searches occurrence-count changes; the other regex-matching diff lines | Choose based on the question and inspect patches |
| Assuming a shallow clone has full history | Old commits may be unavailable to blame/bisect | Check shallow status and fetch required history |
| Running `reset --hard` to “clean up” | Can discard work | Inspect status; make a rescue branch and preserve uncommitted files first |
| Force-pushing a shared branch | Can overwrite colleagues' history and disrupt incident evidence | Coordinate; prefer revert for shared rollback; use lease only when rewrite is agreed |
| Removing a leaked secret from Git and stopping | Copies/artifacts still contain it | Revoke/rotate first, then coordinated history cleanup and incident response |
| Treating churn as a defect score | Change frequency is confounded by centrality and activity | Combine signals and validate with incidents/tests/domain knowledge |
| Ignoring a formatting commit without verifying it | Logic changes can be hidden from blame | Verify patch mechanically; document the ignore list |
| Treating a signed tag as proof of safe code | Signatures attest to signing identity under policy, not correctness | Verify signatures plus artifact provenance, CI, review, and runtime mapping |

## 13. Exercises

Try each exercise before reading the worked solutions. Use a disposable repository; do not experiment with destructive commands in a production checkout.

### Exercise 1 — choose a history search

You remember that `retry_count` was introduced and later removed, but you do not know the commit. Separately, you suspect an exception pattern changed from `TimeoutError` to a broader regex-matching expression. Finally, you need the history of `normalise_record`.

1. Which of `-S`, `-G`, and `-L` is most appropriate for each question?
2. What command would you run to inspect the full patch after finding a candidate?

### Exercise 2 — classify bisect revisions

A bisect wrapper runs a pytest test. On a candidate revision, pytest exits `0`; on another it exits `1` because the regression assertion fails; on a third it exits `2` because test collection fails due to an unavailable dependency.

1. What should the wrapper return for each?
2. Why is mapping every nonzero exit to `1` unsafe?
3. What do you do if the test is intermittent?

### Exercise 3 — post-format blame

A commit changes whitespace and reformats 300 Python files. `git blame` now points nearly every line at that commit. Outline a safe process to restore useful attribution without rewriting history.

### Exercise 4 — recover a branch

You accidentally moved a local branch with a reset. The commit is no longer named by a branch, but you suspect it remains in your local reflog. Explain how to inspect and preserve it. State why the reflog is not a shared backup.

### Exercise 5 — release investigation

An outage began after deployment. The release tag looks correct, but the image's source SHA is unknown. List the first five evidence sources or checks you would collect before concluding which commit caused the incident.

### Exercise 6 — history mining

A file has high churn and many bug-fix-labelled commits. What additional evidence would you gather before prioritising a refactor? Name at least four confounders or corroborating signals.

### Exercise 7 — capstone practice

In a disposable repository with a regression and a mass-formatting commit:

1. Create a regression test that fails only when the bug is present.
2. Add the formatting-only commit to `.git-blame-ignore-revs`.
3. Use automated bisect to identify the first bad commit.
4. Use `git log -S`, `git log -L`, and blame to reconstruct intent.
5. Fix the bug and keep the regression test.
6. Write a postmortem naming the culprit commit, mechanism, detection gap, and preventive action.

## 14. Worked solutions

### Solution 1

- Use `git log -S'retry_count' --all --oneline -- path/` to find commits where the count of that exact string changes. Inspect candidates with `git show a1b2c3d`.
- Use `git log -G'TimeoutError|timeout' --all --oneline -- path/` for diff lines matching a regex. Quote the pattern for your shell; regex syntax follows Git's regular-expression handling.
- Use `git log -L :normalise_record:path/to/file.py` for function history, or a line range if Git cannot identify the function.
- After any search, inspect `git show --format=fuller --find-renames a1b2c3d` and follow related PR/issue records. Search output is a candidate list, not causal proof.

### Solution 2

- Exit `0` means good (regression absent).
- Exit `1` means bad only if the wrapper has established that this is the target test failure.
- Exit `2` should generally map to `125` (untestable) for the example wrapper because collection failed before the behaviour could be classified.
- Mapping all nonzero statuses to bad can identify a broken environment or missing dependency as the regression. For intermittent tests, repeat each candidate under a predeclared rule and skip if evidence is insufficient; avoid changing the rule mid-bisect.

### Solution 3

Inspect the formatting commit's full diff and verify that it made no semantic changes. Add its full SHA to `.git-blame-ignore-revs`, commit the file, configure `blame.ignoreRevsFile`, and rerun blame with the ignore file. Do not rewrite history. If the commit mixes formatting and logic, do not ignore it wholesale; split/revert/recreate the mechanical change where safe, or document the limitation.

### Solution 4

Run `git reflog --date=iso`, inspect the candidate with `git show a1b2c3d`, then create a rescue branch such as `git branch rescue/recovered-work a1b2c3d` and switch to it. Verify the contents before integrating. Reflogs are local, expire, and are not fetched/pushed as shared history; use remote refs and backups for shared recovery.

### Solution 5

At minimum: (1) deployment record with timestamp and image digest; (2) build provenance mapping image to source SHA; (3) exact source commit and release tag, including signature/policy verification where used; (4) dependency lock and build environment; (5) runtime config/schema/feature flags and logs/metrics around symptom onset. Then reproduce on a known-good and known-bad revision before bisecting.

### Solution 6

Check complexity and code structure; incident/defect records; tests and coverage; size of commits and formatting/generated-file changes; file centrality and normal feature activity; co-change partners; ownership concentration; actual business criticality and blast radius. Validate bug-fix labels against a sample of issue/PR records. High churn alone does not prove poor quality.

### Solution 7

A complete result includes a reproducible test and environment notes; a verified formatting commit in the ignore file; a bisect log with good/bad/skip decisions; the introducing commit's patch and related PR/issue/design evidence; a minimal fix and regression test; and a postmortem with impact, timeline, cause, detection gap, mitigation, and prevention. The commit ID must come from the actual test repository, not from a teaching example.

## 15. Capstone: regression archaeology report

Use a repository with approximately 300 commits, a seeded regression, a flaky-ish test, and a formatting-only commit. Work in a clone or disposable branch.

**Required deliverables**

1. **Reproduction:** a minimal failing test and instructions that distinguish the known-good and known-bad revisions.
2. **Blame hygiene:** `.git-blame-ignore-revs` containing the verified mass-formatting commit, plus a short explanation of how it was verified.
3. **Bisect evidence:** start/end revisions, test command, wrapper exit-code mapping, skipped revisions, `git bisect log`, and the identified commit or remaining candidate range.
4. **Intent reconstruction:** `git show`, a suitable `git log -S` or `-G`, `git log -L`, blame, and links to the relevant PR/issue/design record where available.
5. **Fix:** a minimal change and regression test, with the test suite results and any limitations.
6. **Postmortem:** affected behaviour, timeline, root cause mechanism, detection gap, mitigation, preventive actions, owner, and due date.

**Acceptance criteria**

- The test is deterministic enough to classify revisions, or uncertainty is explicitly recorded.
- The report distinguishes facts from hypotheses and uses real commit IDs from the practice repository.
- The bisect is reset and the working tree is checked afterwards.
- No shared history was rewritten; any recovery/rewriting commands are documented and justified.
- The fix is verified at the candidate revision and the known-good baseline remains understood.
- The postmortem focuses on system conditions and controls, not personal blame.

## 16. Self-check

Answer without looking back, then verify against the lesson.

1. Explain `-S` versus `-G` versus `-L` in `git log`, and give a scenario for each.
2. What are the valid exit codes for `git bisect run`, including `125`? Why should a wrapper distinguish product failure from setup failure?
3. After a mass reformat, how can you keep blame useful without changing commit history?
4. How do you use `reflog` to recover work, and what are its limits?
5. What does `git diff A..B` compare versus `git diff A...B`?
6. Why can a shallow clone make blame or bisect incomplete?
7. What is the difference between a revert and a reset on a shared branch?
8. What does a valid commit signature prove, and what does it not prove?
9. Name at least four signals that can complement churn analysis.
10. What evidence chain connects deployed behaviour to a candidate source commit?

## 17. Quick-reference command map

| Question | Start here | Follow-up |
|---|---|---|
| What changed in this commit? | `git show a1b2c3d` | Inspect callers, tests, PR, and issue |
| Which commits touched this path? | `git log -p -- path` | `--follow` for a likely rename |
| Who is associated with this line? | `git blame -L a,b -- path` | `git show a1b2c3d`; consider `-w`/`-C` |
| When did this string's count change? | `git log -S'word' -- path` | Inspect the complete patch |
| Which diff lines match a pattern? | `git log -G'regex' -- path` | Refine regex and examine context |
| How did this function evolve? | `git log -L :function:path` | Use line ranges if detection fails |
| Which commit introduced the regression? | `git bisect` / `git bisect run` | Reproducible test; save log; reset |
| Where did my local branch tip go? | `git reflog` | Inspect then create rescue branch |
| Compare versions without switching | `git worktree add` | Run each revision's tests |
| What is in the release? | `git show <tag>` and `git diff` | Verify artifact digest and build SHA |
| Did a signature verify? | `git verify-commit` / `git tag -v` | Check trusted keys and CI policy |
| Are unreachable objects present? | `git fsck --full` | Inspect objects before recovery |

## Further reading

Use the documentation for the Git version installed in the environment, especially for option constraints and security policy:

- `git help log`
- `git help show`
- `git help blame`
- `git help bisect`
- `git help reflog`
- `git help worktree`
- `git help fsck`
- `git help verify-commit`
- `git help verify-tag`
- Git documentation: <https://git-scm.com/docs>
- PyDriller documentation: <https://pydriller.readthedocs.io/>
- GitHub CLI manual: <https://cli.github.com/manual/>

---

**Lesson complete.** The goal of history archaeology is not to find someone to blame. It is to produce a reproducible explanation of what changed, how the behaviour was introduced, why existing controls missed it, and what evidence-backed action will prevent recurrence.
