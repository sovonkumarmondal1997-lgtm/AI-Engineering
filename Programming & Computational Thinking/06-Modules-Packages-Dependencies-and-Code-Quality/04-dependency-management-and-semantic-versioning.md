# Dependency Management and Semantic Versioning

## Learning Objectives

By the end of this chapter you will be able to:

- Explain why dependency management is a real engineering discipline,
  not just "running pip install."
- Distinguish direct from transitive dependencies, and reason about a
  project's full dependency graph.
- Read and design version constraints (`>=`, `>`, `==`, `<=`, `<`,
  `~=`, and bounded ranges), understanding the tradeoffs between loose
  and strict constraints.
- Explain version pinning versus version ranges, and why
  `pyproject.toml` and a lock file serve different purposes in this
  regard.
- Explain Semantic Versioning (SemVer) precisely: `MAJOR.MINOR.PATCH`,
  what each segment is supposed to communicate, and why SemVer is a
  **convention**, not an enforced guarantee.
- Classify a real version bump (e.g. `1.2.3` → `1.3.0`) by what kind of
  change it's supposed to represent, and evaluate compatibility from
  the *consumer's* perspective.
- Explain pre-release versions (`alpha`, `beta`, `rc`) and the special
  compatibility considerations around `0.x` versions.
- Explain how a dependency resolver evaluates constraints across a
  whole dependency graph, and diagnose a genuine resolution conflict.
- Explain dependency drift, and why unmanaged environments diverge
  over time across developers, CI, staging, and production.
- Apply a safe, deliberate dependency-update workflow, distinguishing
  patch, minor, and major updates by risk.
- Explain when and how to roll back a dependency change safely.
- Use `uv`'s dependency workflows (`uv add`, `uv remove`, `uv sync`,
  `uv lock`, `uv run`) specifically for update, rollback, and review
  scenarios — building on, not repeating,
  [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md).
- Separate runtime, development, and optional dependencies correctly.
- Explain the different dependency strategies appropriate for
  applications versus libraries.
- Reason defensively about dependency security: vulnerable and
  outdated packages, transitive exposure, and supply-chain risk.
- Explain how Python version, package version, OS/platform, and
  architecture together determine whether a dependency actually works
  in a given environment.
- Recognize and avoid the classic dependency-management mistakes.
- Design and simulate a complete, production-oriented dependency
  update and rollback workflow for a real project.

## Prerequisites

This chapter builds directly on
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)
— `pyproject.toml`'s `[project]` table, `dependencies`,
`optional-dependencies`, `requires-python`, the resolver, `uv.lock`,
virtual environments, and the core `uv` commands
(`uv init`, `uv add`, `uv remove`, `uv sync`, `uv run`, `uv lock`) are
all assumed knowledge here and are **not** re-taught from scratch —
this chapter reuses them to teach something new: how versions
communicate compatibility (Semantic Versioning), and how to manage
dependency change safely over a project's lifetime. Where the previous
chapter's mechanics are needed, they are referenced directly rather
than repeated.

## Core Mental Model

The dependency-resolution pipeline from the previous chapter, extended
with where Semantic Versioning fits into it:

```
Project requirements
        ↓
Version constraints          ← informed by what each dependency's OWN version numbers promise (SemVer)
        ↓
Dependency resolver
        ↓
Compatible dependency graph
        ↓
Resolved versions
        ↓
Lock file
        ↓
Reproducible environment
```

And the versioning convention this chapter is centrally about:

```
MAJOR . MINOR . PATCH
  │      │      │
  │      │      └── PATCH: backward-compatible bug fixes
  │      └───────── MINOR: backward-compatible new functionality
  └──────────────── MAJOR: potentially breaking changes
```

The single sentence to hold onto through this entire chapter:
**Semantic Versioning is a compatibility *communication* convention —
a promise a package's maintainers choose to make about what a version
number change means — not a guarantee enforced by Python, by `pip`,
or by `uv`.** A well-maintained package that follows SemVer carefully
makes version constraints (§4 onward) meaningful and trustworthy; a
package that doesn't follow it (or makes a mistake) can still break
something a `MINOR` or `PATCH` bump was supposed to guarantee wouldn't
break. Every section from here builds on this one honest caveat.

## 1. What Is Dependency Management?

[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§1 already defined a **dependency** (external code a project needs
that it didn't write itself) and distinguished standard-library,
local, and third-party code. **Dependency management** is the ongoing
discipline of deciding *which* dependencies a project takes on, *which
versions* are acceptable, and *how those decisions stay correct* as
both the project and its dependencies change over time.

```
application dependency        — a package your project needs to run
direct dependency               — one your code imports and declares itself
transitive dependency             — one a direct dependency needs, pulled in automatically
dependency version                  — a specific release of a package (e.g. 2.31.0)
dependency constraint                 — a rule describing which versions are acceptable (e.g. >=2.0)
```

**Why manually installing packages is not enough**: a manual
`pip install requests`, run once, tells you nothing about *which*
version was installed, records that choice nowhere durable, and gives
you no mechanism at all for keeping that choice consistent as time
passes, as teammates set up their own environments, or as `requests`
itself releases new versions. Dependency management is precisely the
set of practices — declaring dependencies explicitly, constraining
their versions deliberately, resolving and locking them
reproducibly (per the previous chapter) — that turns "I happened to
install something" into "the project has a well-defined, reviewable,
reproducible set of dependencies." This chapter's job is to teach the
*versioning and update* half of that discipline; the previous chapter
taught the *tooling* half.

## 2. Why Dependency Management Matters

A realistic scenario, threading together every failure mode this
chapter exists to prevent:

A team ships a data-processing CLI. Six months in, with no deliberate
dependency management practice:

- **"Works on my machine"** — one developer's environment has
  `pandas` 2.1; another's has 2.8, installed at a different time with
  no record of which was "correct."
- **Incompatible versions** — two dependencies each need a different,
  conflicting version of a shared transitive package.
- **Missing packages** — a developer manually installed something to
  make a feature work locally, and never recorded it anywhere.
- **Unexpected upgrades** — a routine `pip install -r
  requirements.txt`, run again weeks later with unpinned versions,
  silently pulls in newer releases than what was originally tested.
- **Dependency conflicts** (§12–§13) — adding one new package suddenly
  makes the whole environment un-installable.
- **Broken deployments** — production, built independently, ends up
  with different dependency versions than what was actually tested
  locally.
- **Unreproducible environments** — nobody can say, with certainty,
  exactly which dependency versions are running in production *right
  now*.
- **Security vulnerabilities** (§25) — a known vulnerability in a
  dependency goes unnoticed because no one is tracking what's actually
  installed, or how old it is.
- **Dependency drift** (§16) — every one of the above compounds over
  time as different environments silently diverge further and further
  from each other.

Every one of these has the same root cause: **no deliberate, shared,
versioned record of exactly which dependency versions the project
relies on, and no deliberate process for changing that record.**
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)
gave you the *tools* to maintain that record
(`pyproject.toml`/`uv.lock`); this chapter teaches the *judgment* —
reading version numbers correctly, constraining them sensibly, and
updating them deliberately — that keeps it trustworthy over time.

## 3. Direct vs. Transitive Dependencies

A direct review of
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§9, extended into a longer chain to make the scaling problem vivid:

```
Application
    ↓  (direct dependency)
Package A
    ↓  (A's own dependency — transitive, from the application's perspective)
Package B
    ↓  (B's own dependency — also transitive)
Package C
```

The application never imports `B` or `C` directly — it depends on
`A`, and `A`'s own requirements are what pull in `B`, whose own
requirements pull in `C`. From the application's point of view, all
three (`A`, `B`, `C`) must be correctly installed and mutually
compatible for anything to work — but only `A` is something the
application's own code, and its own `pyproject.toml`, ever needs to
mention.

**Why direct dependencies should normally be declared explicitly**:
they represent a genuine, intentional choice — "my code needs this" —
and belong in `pyproject.toml`'s `dependencies` (per the previous
chapter's §7) so that choice is visible, reviewable, and versioned
alongside the code that depends on it.

**Why manually managing every transitive dependency is usually
undesirable**: `A` already declares, and maintains, exactly which
versions of `B` it needs — duplicating that knowledge in the
application's own `pyproject.toml` would be redundant busywork that
goes stale the moment `A` itself changes its own requirements in a
future release. This is precisely what the **resolver** (§12) exists
to compute automatically, and precisely what the **lock file** (§15)
exists to record once that computation is done — manual transitive
management fights against tooling that already does this reliably.

## 4. Dependency Constraints

Restating and building on
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§8 table, since this chapter's entire discussion of update safety
(§17–§19) depends on fluency with these:

| Specifier | Meaning |
|---|---|
| `>=2.0` | Minimum version — 2.0 or any newer |
| `>2.0` | Strictly newer than 2.0 |
| `==2.0` | Exactly 2.0 — an exact pin |
| `<=2.0` | 2.0 or any older |
| `<3.0` | Strictly older than 3.0 |
| `~=2.31` | "Compatible release" — allows patch/minor updates within the given segment |
| `>=2.0,<3.0` | A bounded range — combining a minimum and a maximum |

**Minimum versions** (`>=2.0`) express "I need at least this much
functionality/these fixes, and trust future releases to remain
compatible." **Maximum versions** (`<3.0`, usually paired with a
minimum) express "I don't yet trust — or haven't verified — versions
beyond this boundary." **Exact versions** (`==2.0`) express "only this
precise, verified release is acceptable," with zero flexibility.
**Compatible-release constraints** (`~=2.31`) are a concise way to
express "allow routine updates within this release line, but not a
jump to the next major/minor boundary."

**The tradeoff, stated plainly**: **very loose constraints**
(`>=2.0`, or no constraint at all) maximize flexibility but offer no
protection against a future breaking change silently entering the
project the next time dependencies are resolved. **Very strict
constraints** (exact pins everywhere) maximize predictability for that
one declaration, but — as
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§7 already noted — can make the resolver's job impossible if two
dependencies each demand a different exact version of something
shared, and generally impose a maintenance burden of manually bumping
every pin by hand, forever. A **bounded range**, informed by what
SemVer promises (§6 onward), is this chapter's central recommended
middle ground.

## 5. Version Pinning

```
package==1.4.2
```
versus
```
package>=1.4
```

**Exact pinning** (`==1.4.2`) fixes a dependency to one, precise
version, with zero room for the resolver to pick anything else for
that declaration. **A minimum version** (`>=1.4`) leaves room for any
compatible newer release. Between these two extremes sits the
**bounded range** (§4), and — orthogonally — the **lock file**, which
is where the real distinction this section exists to teach becomes
sharp:

**`pyproject.toml`'s constraints and a lock file's pinned versions
serve genuinely different purposes**, extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§13/§16 directly: a *loose* constraint in `pyproject.toml`
(`package>=1.4`) expresses **intended flexibility** — "any compatible
version is fine, in principle" — while `uv.lock` still records **one
exact, specific version** actually installed right now
(`package==1.4.7`, say). The loose constraint gives *future*
resolutions room to move; the lock file gives *today's* installation
exact reproducibility. Confusing the two — believing a loose
`pyproject.toml` constraint alone guarantees reproducibility, or
believing an exact pin in `pyproject.toml` is what "locking" means —
is precisely the confusion
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§16 comparison table exists to prevent, and this chapter's update
workflows (§17 onward) depend on keeping straight.

**Reproducibility vs. flexibility vs. maintenance burden**, as a
direct three-way tradeoff: an exact pin maximizes reproducibility for
that one declaration but requires manual maintenance to ever change; a
bare minimum maximizes flexibility but sacrifices any guardrail
against an unreviewed breaking change; a bounded range, informed by
SemVer, is what lets a project receive routine, low-risk updates
automatically while still requiring a deliberate, reviewed decision to
cross a boundary that might actually break something.

## 6. What Is Semantic Versioning?

**Semantic Versioning** (commonly abbreviated **SemVer**) is a
widely-adopted **convention** for structuring version numbers so that
the number itself communicates something meaningful about
compatibility, in the form:

```
MAJOR . MINOR . PATCH
```

A concrete example: `2.7.4` — `MAJOR = 2`, `MINOR = 7`, `PATCH = 4`.

- **`MAJOR`** increments when a release contains changes that **may
  break** existing code depending on the package.
- **`MINOR`** increments when a release adds **new, backward-
  compatible functionality** — existing code should keep working
  unchanged.
- **`PATCH`** increments when a release contains **backward-compatible
  bug fixes only** — no new functionality, no intended behavior
  change beyond "the bug is now fixed."

**The general compatibility expectation**, stated as the *intended
contract*, not an ironclad law: if a package correctly follows
SemVer, you should be able to upgrade across `MINOR` and `PATCH`
releases with confidence that your existing code keeps working,
while a `MAJOR` release is your signal to actively review what
changed before upgrading. This is a **contract about intent and
communication**, not a technical guarantee any tool enforces — §6's
closing point, and this entire chapter's most important caveat,
restated: **a project can absolutely make a mistake and ship a
breaking change in a `MINOR` or `PATCH` release**, whether by accident
or through an honest disagreement about what counts as "breaking."
SemVer is valuable precisely *because* most well-maintained packages
follow it carefully — but "this package claims SemVer" is a strong
signal, not a certainty.

## 7. SemVer Examples

Walking through concrete version bumps and what each is *supposed* to
represent:

**`1.2.3` → `1.2.4`** (PATCH bump) — a bug fix release. Existing code
using this package should be entirely unaffected in terms of what
functions exist or how they behave, aside from the specific bug now
being fixed.

**`1.2.3` → `1.3.0`** (MINOR bump) — new functionality was added, in a
way that shouldn't affect existing usage. A new optional parameter, a
new function, a new class — all reasonable MINOR-bump additions,
because code that doesn't use the new feature is unaffected.

**`1.2.3` → `2.0.0`** (MAJOR bump) — something changed in a way that
*may* require consumers to update their own code: a function was
removed or renamed, a parameter's meaning changed, a previously
optional argument became required, or a fundamentally different
behavior replaced the old one.

**A realistic Python-library-flavored example**: imagine a validation
library, `strictjson`.
```
strictjson 1.4.0 → 1.4.1   # PATCH: fixed a bug where nested lists were validated incorrectly
strictjson 1.4.1 → 1.5.0   # MINOR: added a new `validate_partial()` function; nothing existing changed
strictjson 1.5.0 → 2.0.0   # MAJOR: renamed `validate()` to `check()`, and it now returns a result object instead of raising
```
A project pinned to `strictjson>=1.4,<2.0` receives the `1.4.1` and
`1.5.0` updates automatically and safely (per the SemVer contract);
the `2.0.0` release requires the project's own code to be updated
(`validate()` → `check()`, and adjusting to the new return type)
before upgrading past the `<2.0` boundary at all — exactly the
deliberate review §17–§19 formalizes.

## 8. Breaking vs. Non-Breaking Changes

The single most important skill this chapter teaches: **evaluating
compatibility from the consumer's perspective**, not just trusting a
version number in isolation.

**Examples of potentially breaking changes:**
- Removing a public function or class that existing code might call.
- Changing a function's signature incompatibly (removing a parameter,
  changing a parameter's meaning, changing its type).
- Dropping support for a Python version your project still needs
  (directly connecting to §26).
- Changing expected runtime behavior (a function that used to return
  `None` on failure now raises an exception instead).
- Changing required configuration (a setting that used to be optional
  becomes mandatory).

**Examples of generally backward-compatible changes:**
- A pure bug fix — the *intended* behavior is unchanged; only an
  incorrect implementation is corrected.
- Adding an entirely new, optional feature that doesn't alter any
  existing code path.
- Adding a new function alongside existing ones, without touching
  their behavior.

**"Compatibility must be evaluated from the consumer's perspective"**
— worked through concretely: a bug fix that corrects
`compute_total()`'s previously-wrong output *is* a breaking change for
any consumer that had (knowingly or not) come to depend on the buggy
behavior, even though the package's own maintainers correctly consider
it a PATCH-level, backward-compatible fix from their point of view.
This is not a contradiction — it's the honest, practical limit of any
versioning convention: SemVer describes the maintainer's *intent*
regarding their own public API's contract, not a guarantee that
*every possible* way a consumer might be using the package remains
unaffected. This is exactly why "review the actual changes" (§18's
step 2–3) remains part of a safe update process even for a supposedly
"safe" MINOR or PATCH bump.

## 9. Pre-Release Versions

Before a version is considered stable, a project may publish
**pre-release** versions signaling "not yet finished, use with
caution":

```
1.0.0-alpha       # early, unstable, likely to change further before release
1.0.0-beta         # more complete, still likely to have rough edges or further changes
1.0.0-rc.1          # "release candidate" — believed ready, undergoing final verification
1.0.0                # the actual stable release
```

- **Alpha** — early-stage, incomplete, and expected to change
  significantly before the final release; primarily useful for very
  early feedback, not for depending on in anything that matters.
- **Beta** — more feature-complete and stable than alpha, but still
  expected to have bugs or further changes before the final release.
- **Release candidate (`rc`)** — believed ready for release; published
  specifically to catch any remaining issues before the actual stable
  version ships.
- **Stable release** — the version with no pre-release suffix at all;
  what the SemVer compatibility contract (§6) actually applies to.

**Why production applications should treat pre-releases carefully**:
a pre-release version's entire *point* is that it might still change —
possibly significantly — before the corresponding stable release
ships; depending on one in a production system means accepting the
real possibility of a future, unplanned breaking change with no
SemVer-style warning, since pre-release versions exist specifically
*outside* the normal stability guarantees a stable release line
provides. Most dependency resolvers, including `uv`'s, will not
select a pre-release version to satisfy an ordinary constraint unless
explicitly asked to — a deliberate design choice reflecting exactly
this caution.

## 10. Development Versions and Version `0.x`

Versions in the `0.x.y` range carry a special, widely-understood
exception to the ordinary SemVer expectation: **a project below
`1.0.0` is considered to still be in initial development**, and — by
the SemVer specification's own convention — **anything may change at
any time**, even between `MINOR` bumps within the `0.x` line.

```
0.3.0 → 0.4.0    # under strict SemVer's own 0.x convention, this MAY include breaking changes,
                  # even though the same jump (e.g. 1.3.0 → 1.4.0) would NOT be expected to
```

**Why this exists**: version `1.0.0` is meant to signal "this API has
stabilized and is now making the full compatibility commitments SemVer
describes" — everything before that is understood, by convention, to
still be finding its shape, with the normal MAJOR/MINOR/PATCH
compatibility promise not yet fully in effect.

**What this means practically**: depending on a `0.x` package
requires more caution than depending on an equivalent `1.x`+ package —
a `MINOR` bump in the `0.x` range deserves the same scrutiny a `MAJOR`
bump would get in a stable `1.x`+ line, since the usual guarantee
simply doesn't apply yet. This chapter deliberately avoids
overclaiming here: **not every project treats `0.x` identically**, and
some maintainers do try to keep even `0.x` releases reasonably
stable — but the *convention*, and the safe default assumption absent
other information, is exactly as just described: treat `0.x`
compatibility as unsettled until the project reaches `1.0.0`.

## 11. SemVer and Python Packages

Connecting SemVer directly to the mechanics
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)
already taught:

```
package's OWN published version (e.g. requests 2.31.0)
        ↓
YOUR dependency constraint, informed by what that version number promises
        ↓
the resolver, evaluating your constraint against every other constraint in the project
        ↓
one specific, compatible version actually selected
```

A practical `pyproject.toml` example, reasoning through the constraint
choice explicitly:

```toml
[project]
dependencies = [
    "requests>=2.31,<3.0",   # trust MINOR/PATCH updates within the 2.x line; require review before 3.0
]
```

The `>=2.31` lower bound says "I need at least the fixes/features
available as of 2.31"; the `<3.0` upper bound says "I'm relying on
`requests`' own SemVer discipline to keep every 2.x release
backward-compatible with my code, but I want to *deliberately* review
anything before accepting a 3.0 upgrade" — this single line is a
direct, practical encoding of everything §6–§10 just established
about what a MAJOR-version boundary is supposed to mean.

## 12. Dependency Resolution

Extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§10 with a slightly richer, SemVer-flavored example:

```
Application requires:      A >=2, <4
Package B requires:          A >=2, <3
Package C requires:            A >=2.5
```

The resolver needs one version of `A` satisfying **all three**
constraints at once: `>=2, <4` (the application's own, direct
requirement), `>=2, <3` (from `B`), and `>=2.5` (from `C`). The
overlap of all three ranges is `[2.5, 3.0)` — any `A` version from 2.5
up to (but not including) 3.0 satisfies every constraint
simultaneously, so a valid resolution exists (e.g., the resolver would
typically select the latest version within that range).

**Now a genuine conflict**, changing only `B`'s requirement:
```
B requires:    A < 3
C requires:      A >= 3
```
No version of `A` can simultaneously be `< 3` and `>= 3` — the ranges
`[..., 3.0)` and `[3.0, ...)` share no overlap at all. This is
precisely
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§11 conflict scenario, revisited here specifically to connect it to
SemVer: `B`'s `<3` constraint is very likely there *because* `B`'s own
maintainers know (or suspect) that `A`'s upcoming `3.0.0` will be a
MAJOR, potentially breaking release for their own code — the version
boundary in `B`'s constraint is a direct, practical reflection of
SemVer's own MAJOR-version meaning.

## 13. Dependency Conflicts

A systematic troubleshooting workflow, directly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§11:

**Problem** → the resolver reports it cannot find a compatible set of
versions.

**Root cause, in order of likelihood:**
1. **Incompatible constraints** — two dependencies (direct or
   transitive) genuinely require mutually exclusive version ranges of
   a shared package (§12's second example).
2. **A conflicting Python version requirement** — one dependency's own
   `requires-python` (§26) is incompatible with another's, or with the
   project's own declared minimum.
3. **A transitive conflict several levels deep** — the actual
   conflicting packages are not your own direct dependencies at all,
   but something two of them each pull in transitively.
4. **An overly strict constraint of your own** (§4–§5) — one of your
   *own* project's version constraints is more restrictive than
   actually necessary, and relaxing it (safely, per §17–§19) would
   allow a valid resolution.

**Possible solutions, with their tradeoffs:**
- **Upgrade one of the conflicting dependencies** to a version whose
  own transitive requirement has relaxed — the cleanest fix when
  available, but requires reviewing that upgrade for its *own*
  compatibility implications (§18).
- **Relax one of your own version constraints** — appropriate if your
  constraint was more conservative than genuinely necessary, but
  reduces the guardrail that constraint was providing.
- **Replace one of the conflicting dependencies** with an alternative
  package serving the same purpose — a larger, more disruptive change,
  appropriate when the conflict is fundamentally unresolvable
  otherwise.
- **Accept that two specific dependencies genuinely cannot coexist**
  in this project as currently designed, and reconsider whether both
  are truly needed together.

**Diagnosing the dependency graph**: read the resolver's own error
message carefully (per
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§11) to identify exactly which packages and constraints are in
conflict *before* attempting any fix — guessing at a fix without first
understanding precisely which requirement conflicts with which is how
one conflict gets "fixed" into a different, equally broken state.
**Never blindly force a version** past an unresolved conflict (§11's
warning, restated) — an environment that "installs" despite ignoring
the resolver's own determination that no valid set exists is not
actually a correctly working environment; it's one with a real,
unaddressed incompatibility hidden inside it.

## 14. `pyproject.toml` and Dependency Management

This section deliberately does not re-teach
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
full `[project]`/`dependencies` mechanics — only how this chapter's
versioning judgment applies to writing them well.

```toml
[project]
dependencies = [
    "requests>=2.0,<3.0",
    "pydantic>=2.0,<3.0",
]
```

**What the project declares**: for each dependency, a version range
whose lower bound reflects "the earliest version with the features/
fixes I actually need" and whose upper bound reflects "the version
boundary beyond which I want a deliberate review before upgrading" —
almost always chosen to align with that dependency's own next expected
MAJOR-version boundary (§6, §11), since that's precisely the boundary
SemVer signals as the one worth being cautious about.

**Why version ranges are useful, restated in this chapter's own
terms**: a range lets the project automatically receive every
PATCH and MINOR update within it — the updates SemVer's own contract
says should be safe — without requiring a manual `pyproject.toml` edit
for each one, while still requiring a deliberate, reviewed decision
(§17–§19) to cross into a new MAJOR version.

**Relationship to the resolver and the lock file**: exactly
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§10/§13 — these ranges are what the resolver evaluates (§12); the
*specific* version it picks, right now, is what gets recorded in
`uv.lock` (§15) for reproducible installation, until a future update
deliberately changes either the constraint or the lock file.

## 15. Lock File vs. Dependency Declaration

Restating
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
core distinction one final time, as this chapter's own load-bearing
foundation:

```
pyproject.toml   =   project-level dependency REQUIREMENTS   (what's acceptable, a range)
uv.lock            =   RESOLVED dependency STATE               (exactly what's installed, one version each)
```

The four distinct operations this chapter's update workflows (§17
onward) constantly move between:

- **Declaration** — writing/editing a constraint in `pyproject.toml`.
- **Resolution** — the resolver computing one valid, compatible set of
  exact versions satisfying every current declaration.
- **Locking** — recording that resolved set into `uv.lock`.
- **Installation/synchronization** — actually installing the locked
  versions into the environment (`uv sync`).

**A realistic workflow**, walking all four steps through concretely:
a developer edits `pyproject.toml` to loosen `requests`'s upper bound
from `<2.32` to `<3.0` (**declaration**); runs `uv lock` (or `uv add`/
`uv sync`, depending on the exact change), which **resolves** a new
compatible version (potentially a newer `requests` release than
before) and **locks** it into an updated `uv.lock`; then runs `uv
sync`, which **installs** that newly-locked version into the actual
environment. Each of these four steps is a genuinely separate action
— exactly why
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§26 warned that editing `pyproject.toml` alone does *not*
automatically perform the remaining three.

## 16. Dependency Drift

**Dependency drift** is what happens when different environments that
*should* be running the same dependencies slowly diverge, absent
deliberate management:

```
Today:               Later (no deliberate management):
A 2.1                   A 2.9
B 4.0                     B 4.8
```

Without a lock file (or with one that isn't consistently used), every
environment that independently re-resolves — a new developer's laptop
set up months later, a CI run against unpinned requirements, a staging
server rebuilt from scratch — can legitimately arrive at a *different*
resolved version than an environment set up earlier, simply because
newer package releases became available in the meantime. None of these
environments did anything "wrong" — each correctly resolved the
project's own declared (loose) constraints at the moment it happened
to run — but they no longer agree with each other, and nothing
recorded *when* or *why* they diverged.

**Across the full deployment lifecycle**: a **developer's machine**
set up today might already differ from one set up three months ago;
**CI**, if it re-resolves independently rather than installing from a
committed lock file, might test against yet another combination
entirely; **staging**, rebuilt on its own schedule, drifts again; and
**production**, deployed independently of all of the above, may end up
running a fourth, entirely different combination than what was ever
actually tested anywhere. This is exactly the scenario
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§15 lock-file discussion was designed to eliminate — dependency drift
is the *disease*; a committed, consistently-used `uv.lock`, installed
via `uv sync` at every stage, is the *cure*. This chapter's remaining
sections assume that cure is in place, and focus on how to change the
locked state *deliberately*, rather than letting it drift.

## 17. Dependency Updates

Four genuinely different situations, worth distinguishing before
adopting any single "update strategy":

- **No update** — the locked version remains unchanged; the safest
  state, but one that accumulates risk over time if maintained
  indefinitely (§20, §25).
- **Patch update** — a `PATCH`-level bump (§6) within an already-
  accepted range; per SemVer's own contract, the lowest-risk kind of
  change, but "lowest risk" is not "zero risk" (§8's honest caveat).
- **Minor update** — a `MINOR`-level bump within an already-accepted
  range; per SemVer, should add functionality without removing or
  changing existing behavior — still worth a lighter review.
- **Major update** — a `MAJOR`-level bump, crossing a version boundary
  the project's own constraint was deliberately guarding (§4, §11);
  should always be treated as a change requiring active review, not a
  routine update.

**Why updates should be intentional, not automatic and unreviewed**:
even a PATCH update changes *something* about the exact code actually
running — SemVer's promise reduces the *likelihood* of a surprise, but
§8 already established that promise is a convention, not a guarantee.
An intentional update process — reading what actually changed,
reviewing the lock-file diff, running tests — catches the cases where
that convention didn't hold, *before* they reach production, rather
than discovering them there.

**What a deliberate review considers**: the dependency's own
**changelog or release notes** (does the described change match what
SemVer's segment would suggest?); **compatibility** with the project's
own actual usage of that dependency; whether the project's **tests**
still pass; exactly **what else changed** in the resulting
`uv.lock` diff (an update to one direct dependency can cascade into
transitive version changes too, per
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§36 debugging scenario 10).

## 18. Safe Update Strategy

A concrete, ten-step workflow, with each step's purpose stated
explicitly:

1. **Identify the update** — know specifically which dependency, and
   which version, you're considering updating to (not just "update
   everything").
2. **Read release information** — the dependency's changelog or
   release notes, to see what actually changed, not just the version
   number.
3. **Review compatibility** — compare what changed against how your
   own project actually uses that dependency; does anything you rely
   on appear in the list of changes?
4. **Update the dependency** — adjust the constraint in
   `pyproject.toml` if needed (§14), or use the appropriate `uv`
   command (§22).
5. **Resolve dependencies** — let the resolver compute the new,
   updated resolved set (§12, §15).
6. **Review lock changes** — inspect the resulting `uv.lock` diff
   (since it's version-controlled, per
   [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
   §14) to see exactly what actually changed, including any transitive
   dependency shifts.
7. **Run tests** — the project's own automated test suite, to catch
   any regression the update introduced.
8. **Run lint/type checks where applicable** — this module's own
   later chapters cover these tools; running them after a dependency
   update catches issues an update might introduce even without a
   failing test (e.g. a changed function signature a type checker
   flags before a test happens to exercise it).
9. **Review application behavior** — for anything a test suite might
   not fully cover, a manual or exploratory check that the application
   still behaves as expected.
10. **Commit the change** — `pyproject.toml` and `uv.lock` together,
    as one atomic, reviewable change (per
    [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
    §32 mistake 4), with a commit message describing *what* was
    updated and *why*.

**Why each step matters**: skipping steps 2–3 turns "safe update"
into "blind update" regardless of how careful the remaining mechanical
steps are; skipping steps 6–9 means discovering a real regression only
after it's already shipped, rather than before; skipping step 10's
"together, atomically" discipline reintroduces exactly the
inconsistent-file problem
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§32 warned against.

## 19. Patch/Minor/Major Update Strategy

Applying §17–§18's workflow with intensity calibrated to risk, per
SemVer's own signal — while never treating the version number alone as
a safety guarantee:

**PATCH updates** — usually lower-risk, per SemVer's own contract
(§6), but still: run the test suite, and at least skim the release
notes for anything unexpected (§8's caveat — a "bug fix" can still
change behavior something in your code was inadvertently depending
on).

**MINOR updates** — usually backward-compatible under SemVer, but
review behavior more actively: check whether any newly-added
functionality overlaps with something your code does differently
(rare, but possible), and confirm the full test suite still passes.

**MAJOR updates** — treat as potentially breaking by default. Read the
dependency's own migration guide or changelog specifically for
breaking-change notes; expect to need actual code changes in your own
project; budget real time for this, rather than treating it as a
routine dependency bump; run the full review workflow (§18) with
extra scrutiny, and consider testing in a non-production environment
first.

**The one point worth restating one final time, because it's the
single most common misunderstanding this chapter corrects**: **the
version number alone never *guarantees* safety** — it's the
dependency maintainers' stated *intent*, which is usually reliable for
a well-maintained package, but is never a substitute for actually
running your own tests after any update, regardless of which segment
changed.

## 20. Dependency Rollback

**Why rollback may be necessary**: a dependency update — even one that
passed local tests and review — occasionally surfaces a problem only
under conditions the pre-deployment review didn't cover (a specific
production data pattern, a load characteristic, an interaction with
another part of the system). When that happens, the fastest, safest
response is often to **restore the previous, known-good dependency
state**, not to attempt a fix under pressure.

**Restoring a previous known-good state**: because `uv.lock` is
committed to version control (per
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§14), rolling back is, in principle, as simple as reverting to the
previous commit's `pyproject.toml`/`uv.lock` pair and re-running `uv
sync` — the exact same reproducibility guarantee that makes forward
updates safe also makes rollback safe and precise, rather than a
guessing game about which older version to reinstall.

```bash
git revert <the commit that updated the dependency>
uv sync
```

**Emergency rollback vs. forward-fix**: a **rollback** restores a
previously-verified-working state immediately, buying time to
investigate calmly; a **forward-fix** instead pushes a *new* change
that addresses the problem while keeping the update in place. Rollback
is generally the safer, faster choice under real production pressure
— it returns to a state you already know worked, rather than
introducing a *new*, unverified change while already under incident
pressure. A forward-fix becomes appropriate once there's time to
properly diagnose and address the actual problem, potentially
re-applying the update (with the fix) deliberately afterward.

**A simple production scenario**: a team updates a data-validation
library from `2.4.1` to `2.5.0` (a MINOR bump). Tests pass locally and
in CI. Days after deployment, a specific, rare input pattern in
production triggers a subtly different validation result than before —
something the test suite's coverage didn't happen to include. The
team reverts the commit that updated `pyproject.toml`/`uv.lock`,
runs `uv sync` in production, confirming the previous behavior is
restored, and then investigates the actual discrepancy calmly, without
ongoing production impact, before deciding whether to report it
upstream, patch around it, or re-attempt the update later with
additional test coverage for the case that broke.

## 21. `uv` and Dependency Management

This section connects (not repeats)
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
own command coverage to this chapter's versioning concerns
specifically.

| Command | What it does, in this chapter's terms |
|---|---|
| `uv add package` | Declares a new dependency (with your chosen version constraint, §4) and immediately resolves + locks + syncs |
| `uv remove package` | Removes a declaration and re-resolves/re-locks/re-syncs accordingly |
| `uv lock` | Re-runs resolution and updates `uv.lock`, without touching the installed environment — the "resolution + locking" steps of §15, in isolation |
| `uv sync` | Installs/aligns the environment to match the current lock file — the "installation" step of §15, in isolation |
| `uv run ...` | Runs a command inside the project's correctly-resolved environment (§18's steps 7–9 should always be run this way) |

Every one of these is exactly the command
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)
already taught in full — this chapter's contribution is knowing
*when*, in a deliberate update or rollback workflow (§18, §20, §22),
each one is the right tool.

**A reminder worth repeating from the previous chapter, because this
chapter's update workflows depend on it**: exact flags and finer
command behavior can vary by installed `uv` version. Verify current,
specific behavior with:
```bash
uv --help
uv add --help
```
rather than assuming a flag exists just because it seems like it
should.

## 22. Updating Dependencies with `uv`

Three genuinely distinct operations, easy to conflate, restated in
this chapter's own update-workflow terms:

- **Change the requirement** — edit the version constraint a
  dependency must satisfy (either by hand in `pyproject.toml`, or via
  `uv add "package>=2.5"` specifying a new constraint directly).
- **Resolve/update the lock** — have the resolver compute a new
  resolved set reflecting the changed requirement, recorded into
  `uv.lock` (via `uv lock`, or automatically as part of `uv add`/
  `uv remove`).
- **Sync the environment** — actually install the newly-locked
  versions (`uv sync`).

```bash
# Example: deliberately widen requests' accepted range to allow a newer release
uv add "requests>=2.32,<3.0"
```
This single command changes the requirement, resolves, updates
`uv.lock`, and syncs the environment — but it's worth mentally
separating what it accomplished into these three steps, because §18's
review steps (6–9) specifically target the *resolve/lock* step's
*output* (the `uv.lock` diff) before trusting the *sync* step's result
in anything beyond a local, disposable environment.

**Reviewing changes**: after any update command, `git diff
pyproject.toml uv.lock` (an ordinary version-control diff, not a
`uv`-specific command) is how you actually perform §18's step 6 —
inspecting exactly what the resolver changed, including any transitive
dependency shifts that came along with the direct change you asked
for.

This chapter does not introduce or assume any specific flag for "check
for available updates without applying them" beyond what
`uv --help`/`uv lock --help` documents for your installed version —
per this chapter's stated commitment not to invent `uv` behavior,
verify any such workflow against your own installed CLI's current
documentation before relying on it.

## 23. Dependency Groups

Restating and lightly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§21–§22 distinction, specifically for this chapter's update-strategy
purposes:

| Group | Purpose | Example | Update risk consideration |
|---|---|---|---|
| **Runtime** | Needed for the application to actually run | `requests` | Directly affects production; follow §18's full workflow |
| **Development** | Needed only while developing/testing | `pytest`, `ruff` | Never reaches production; still worth reviewing, but with lower stakes |
| **Optional** | Needed only for specific, opt-in features | a feature-specific package (e.g. `openpyxl` for Excel export) | Only affects users who actually enable that feature |

```toml
[project]
dependencies = ["requests>=2.31,<3.0"]     # runtime

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.5"]          # development
excel = ["openpyxl>=3.0"]                    # optional feature
```

**Why this separation matters for update strategy specifically**: a
runtime dependency update carries direct production risk and warrants
§18's full workflow without shortcuts; a development-tool update
(a new `pytest` release, say) carries essentially zero production risk
by definition — it never ships with the application at all — so a
lighter-weight review (does the test suite still run correctly?) is
generally proportionate; an optional-feature dependency's update only
matters to whichever consumers actually enable that specific feature,
narrowing the review's necessary scope accordingly.

## 24. Application vs. Library Dependencies

Extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§30 specifically into this chapter's versioning judgment.

**Application**:
- Controls its own deployment environment entirely.
- Reproducibility (via a committed lock file) is highly valuable —
  there's exactly one consumer (the deployed application itself), so
  pinning down an exact, tested set of versions carries no downside.
- Version constraints in `pyproject.toml` can reasonably be **tighter**
  (bounded ranges close to what's actually been tested), since the
  application's own maintainers are the only ones who'll ever need to
  loosen them.

**Library**:
- Consumed by *other* projects, each resolving the library's
  dependencies alongside their own, independently-chosen other
  requirements.
- Dependency constraints should generally **avoid unnecessary
  restriction** — a library declaring an overly tight range on a
  common dependency can make it *impossible* for a consumer to satisfy
  both the library's constraint and some unrelated constraint from a
  completely different dependency they also use (exactly the conflict
  shape from §12, now caused by the library's own over-caution rather
  than a genuine incompatibility).
- Consumers resolve their **own** full dependency graph, including the
  library's declared ranges as just one more input — the library's own
  lock file (if it has one) never travels with it to consumers at all.

**The tradeoff, stated once more without ranking one as universally
correct**: an application optimizes for *its own* reproducibility and
safety, since it's the only consumer that matters; a library optimizes
for *not constraining its consumers unnecessarily*, since being overly
cautious on the library's part can create conflicts for downstream
projects the library's own maintainers will never see coming. Both are
legitimate, sensible defaults for the situation each is actually in.

## 25. Dependency Security

Directly extending
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§31, now with more concrete defensive vocabulary:

- **Vulnerable dependencies** — a package (direct or transitive) with
  a publicly known security flaw; simply having it installed and
  reachable can be a real exposure, whether or not your code happens
  to call the specific vulnerable code path.
- **Outdated packages** — dependencies that haven't been reviewed or
  updated in a long time may be carrying vulnerabilities discovered
  and fixed upstream long ago, simply because no one applied the fix
  locally.
- **Transitive vulnerabilities** — a flaw several levels deep in the
  dependency graph (§27) is just as real a risk as one in a directly-
  chosen package, and easy to overlook precisely because it was never
  a deliberate choice.
- **Dependency review**: before adding a new dependency, it's
  reasonable to consider how actively maintained it is, how widely
  trusted and used it is, and how large a transitive footprint it
  brings — not every convenience justifies the added exposure.
- **Supply-chain risk**: the risk that a dependency itself (or one of
  *its* dependencies) is compromised — maliciously, or through a
  maintainer's own account being compromised — such that installing it
  introduces harmful code, not merely a bug.
- **Malicious packages and typosquatting, conceptually**: a
  "typosquatting" package deliberately uses a name very close to a
  popular, legitimate package (e.g. a one-character misspelling),
  hoping developers will install it by mistake; the defense is simple
  and mechanical — double-check package names carefully before adding
  a new dependency, especially one typed by hand rather than copied
  from a trusted source.
- **Why dependency sources matter**: installing from a well-established,
  widely-trusted package index (the default `uv`/`pip` behavior,
  pointing at the official Python Package Index) is a meaningfully
  different trust situation than installing from an arbitrary,
  unverified source — this chapter does not teach configuring
  alternative package sources, but the underlying principle (know
  where your dependencies actually come from) applies regardless.

**Defensive practices, gathered together:**
- Use trusted, well-established package sources.
- Review new dependencies before adding them, not just after
  something goes wrong.
- Prefer actively maintained packages over abandoned ones where a
  reasonable choice exists.
- Update deliberately (§17–§19) — not never, and not blindly.
- Use reproducible environments (§13–§16) so you always know precisely
  what's actually installed, everywhere, at all times.
- Pay attention to published security advisories for dependencies your
  project actually uses, and treat a genuine advisory as a priority
  update, following §18's workflow with appropriate urgency.

This section is deliberately **defensive**, consistent with this
entire course's approach to security topics — the goal is
recognizing and mitigating risk, not constructing an attack.

## 26. Compatibility and Python Versions

Dependency compatibility is not purely about package version numbers
— it also depends on:

```
Python version
    +
package version
    +
OS/platform
    +
architecture
```

A package can genuinely work correctly on one environment and fail on
another for reasons that have nothing to do with the version
constraints this chapter has focused on so far: a package with
compiled, platform-specific components might not have a pre-built
version available for a given OS or CPU architecture at all; a
package might drop support for an older Python version in some future
release, exactly the "removing supported Python versions" breaking
change §8 already named.

**Connecting directly to `requires-python`**: your own project's
`requires-python = ">=3.12"` declaration (from
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§6) interacts with every dependency's *own* Python-version support —
if a dependency you need drops support for Python 3.12 in some future
release, that release becomes effectively incompatible with your
project (unless you also raise your own minimum) — precisely the
"conflicting Python version requirements" conflict cause named in
§13. Checking a dependency's own supported Python versions (visible in
its own published metadata) before both adding it and before updating
it across a MAJOR boundary is a genuinely useful habit this section
recommends explicitly.

## 27. Dependency Graph Thinking

A habit of mind worth deliberately cultivating: viewing a project's
dependencies as a **graph**, not a flat list.

```
Application
├── A
│   ├── B
│   └── C
└── D
    └── C
```

Here, `C` is a **shared transitive dependency** — both `A` and `D`
depend on it, independently. This is exactly the shape that makes
version constraints genuinely important: if `A` requires `C<2.0` and
`D` requires `C>=2.0`, the resolver faces exactly §12's conflict
scenario, even though neither `A` nor `D` has any direct relationship
with each other at all — the conflict is purely a consequence of both
happening to share `C` as a transitive dependency.

**Why dependency management becomes harder as projects grow**: each
additional direct dependency doesn't just add one node to this graph —
it potentially adds an entire subtree of its own transitive
dependencies, any of which might overlap (and conflict) with anything
already present anywhere else in the graph. A project with five
direct dependencies might easily have thirty or more nodes once every
transitive dependency is counted — and every one of those thirty is a
potential source of a version conflict, a security consideration
(§25), or a compatibility question (§26). This is precisely why
manual, by-hand dependency tracking (§3's closing point) stops scaling
almost immediately, and why a real resolver (§12) computing this
entire graph automatically, backed by a lock file (§13–§16) recording
the answer reproducibly, is a genuine engineering necessity rather
than a convenience.

## 28. Common Mistakes

1. **Installing globally.** *Why:* pollutes the system Python and
   defeats per-project isolation (per
   [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
   §32 mistake 1). *Fix:* always work within the project's own managed
   environment (`uv sync`/`uv run`).
2. **Not declaring dependencies.** *Why:* an undeclared, manually
   installed package silently disappears for anyone else running `uv
   sync` (§2, §16). *Fix:* always use `uv add` for anything genuinely
   needed.
3. **Manually pinning every transitive dependency.** *Why:* duplicates
   information the resolver already computes automatically, and goes
   stale the moment an upstream dependency changes its own
   requirements (§3, §9). *Fix:* declare only your own direct
   dependencies' constraints; trust the resolver/lock file for the
   rest.
4. **Blindly upgrading everything.** *Why:* skips §17–§19's review
   entirely, risking an unreviewed breaking change or newly-introduced
   vulnerability reaching production with no warning. *Fix:* update
   deliberately, one considered change at a time, following §18's
   workflow.
5. **Never upgrading anything.** *Why:* leaves known vulnerabilities
   unpatched indefinitely (§25), and eventually forces a much larger,
   riskier "catch-up" update across many MAJOR-version boundaries at
   once. *Fix:* review and update deliberately and periodically, not
   never.
6. **Confusing SemVer with a guarantee.** *Why:* §6/§8's central
   caveat — a version number describes maintainer *intent*, not a
   technical guarantee any tool enforces; trusting it blindly, with no
   testing at all, can let a mistaken PATCH/MINOR release ship an
   actual breaking change unnoticed. *Fix:* always run tests after any
   update, regardless of which SemVer segment changed.
7. **Ignoring pre-release versions' special status.** *Why:* depending
   on an alpha/beta/rc in production accepts real instability risk
   with none of SemVer's usual guarantees applying yet (§9). *Fix:*
   reserve pre-release dependencies for genuinely experimental,
   non-production use.
8. **Ignoring Python-version compatibility.** *Why:* a dependency
   update that drops support for your project's own minimum Python
   version becomes silently incompatible (§26). *Fix:* check a
   dependency's own supported Python versions before updating across a
   MAJOR boundary especially.
9. **Ignoring lock-file changes during review.** *Why:* skipping §18's
   step 6 means an update's full impact — including transitive
   version shifts — goes unreviewed. *Fix:* always inspect the
   `uv.lock` diff, not just the `pyproject.toml` change.
10. **Modifying lock files manually.** *Why:* `uv.lock` is a generated
    artifact — hand-editing it risks an internally inconsistent state
    (per
    [03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
    §32 mistake 3). *Fix:* change `pyproject.toml` and re-run the
    appropriate `uv` command instead.
11. **Resolving locally but never testing.** *Why:* a successful
    resolution only proves the versions are *compatible with each
    other's declared constraints* — it says nothing about whether your
    *own* code still behaves correctly against the updated dependency
    (§8's consumer-perspective caveat). *Fix:* always run the test
    suite (§18's step 7) after any update, resolution success alone is
    not sufficient.
12. **Ignoring security updates.** *Why:* a known vulnerability left
    unpatched is an active, growing risk the longer it's ignored
    (§25). *Fix:* treat a genuine security advisory as a priority
    update, following §18's workflow with appropriate urgency rather
    than deferring it indefinitely.
13. **Using overly strict constraints.** *Why:* can make the resolver's
    job impossible when combined with another dependency's own
    requirements, and imposes ongoing manual-maintenance burden (§4,
    §7). *Fix:* prefer bounded ranges informed by SemVer's own
    MAJOR-version boundaries over blanket exact pins.
14. **Using overly loose constraints.** *Why:* offers no protection at
    all against an unreviewed future breaking change silently entering
    the project the next time dependencies are resolved (§4). *Fix:*
    bound the upper end of a constraint at the next MAJOR-version
    boundary you haven't yet reviewed.
15. **Assuming minor/patch updates are always risk-free.** *Why:*
    directly contradicts §6/§8's central caveat — SemVer describes
    intent, not a guarantee. *Fix:* always run the test suite, even
    for a "safe," low-risk-looking update.

## 29. Progressive Coding/Configuration Examples

**1. The dependency concept**
```python
import requests   # a direct dependency; requests' own dependencies are transitive
```

**2. A version constraint**
```toml
dependencies = ["requests>=2.0"]
```

**3. An exact pin**
```toml
dependencies = ["requests==2.31.0"]
```

**4. A version range**
```toml
dependencies = ["requests>=2.31,<3.0"]
```

**5. Interpreting a SemVer bump**
```
requests 2.31.0 → 2.32.0   # MINOR: new functionality, existing usage should be unaffected
```

**6. A breaking vs. non-breaking change, read from a changelog entry**
```
v2.31.1: "Fixed a bug where redirects were not followed for PUT requests."  → PATCH, non-breaking
v3.0.0:  "Removed the deprecated `Session.request_hook` parameter."         → MAJOR, breaking
```

**7. A `pyproject.toml` dependency declaration, reasoned through**
```toml
[project]
dependencies = [
    "pydantic>=2.0,<3.0",   # trust pydantic's own 2.x SemVer discipline; review before 3.0
]
```

**8. A dependency conflict, written out**
```
Application requires:  A >= 2, < 4
Package B requires:      A < 3
Package C requires:        A >= 3
# No version of A satisfies both B's and C's requirements — a genuine conflict.
```

**9. A lock-file workflow**
```bash
uv add "pydantic>=2.0,<3.0"   # declares + resolves + locks + syncs, in one step
git diff pyproject.toml uv.lock   # review exactly what was declared and resolved
```

**10. A safe dependency update, step by step**
```bash
# 1-3: read pydantic's changelog, confirm the 2.5.0 release is a MINOR, backward-compatible bump
uv add "pydantic>=2.5,<3.0"    # 4-5: update the requirement; resolver re-locks
git diff uv.lock                 # 6: review exactly what changed
uv run pytest                      # 7: run tests
git add pyproject.toml uv.lock       # 10: commit together
git commit -m "Update pydantic to >=2.5,<3.0 (MINOR update, tests pass)"
```

**11. An `uv`-managed update, isolating resolve vs. sync**
```bash
uv lock      # resolve + record the new state, without touching the environment yet
git diff uv.lock   # review BEFORE installing anything
uv sync        # only now, install the reviewed, locked versions
```

**12. A rollback scenario**
```bash
git log --oneline -- pyproject.toml uv.lock   # find the commit that made the problematic update
git revert <that commit>
uv sync
```

**13. An application dependency strategy**
```toml
# an application — tight, reviewed ranges; a committed uv.lock guarantees reproducibility
dependencies = ["httpx>=0.27,<0.28"]
```

**14. A production dependency workflow, end to end**
```bash
uv sync                    # install exactly what's locked
uv run pytest                # verify correctness
uv run ruff check .            # additional quality gate
git push                         # deploy from this exact, reviewed, tested state
```

## 30. Mini Project — Production Dependency Management and Upgrade Workflow

**Scenario:** `orders-report` (the same CLI from
[02-project-layout-and-package-structure.md](02-project-layout-and-package-structure.md)
and
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)),
now simulated through a full dependency lifecycle: initial setup, an
addition, a patch update, a minor update, a major update, a conflict,
a rollback, a security update, and CI/CD synchronization.

**Project tree:**
```
orders-report/
├── src/
│   └── orders_report/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── validation.py
│       └── processing.py
├── tests/
│   ├── test_validation.py
│   └── test_processing.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

**Initial `pyproject.toml`:**
```toml
[project]
name = "orders-report"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0,<3.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.5"]
```

**Step 1 — Initial dependency setup**
- **WHAT:** run `uv sync` right after cloning.
- **WHY:** establish a working, reproducible baseline environment
  before any code is written.
- **COMMAND:** `uv sync`
- **EXPECTED EFFECT:** `pydantic`, `pytest`, and `ruff` (plus every
  transitive dependency) installed exactly per `uv.lock`.
- **RISK/TRADE-OFF:** none yet — this is the safe, reproducible
  starting point every later step measures against.

**Step 2 — Adding a dependency**
- **WHAT:** the team needs to make HTTP requests to fetch exchange
  rates for multi-currency orders.
- **WHY:** a genuine new runtime capability.
- **COMMAND:** `uv add "httpx>=0.27,<0.28"`
- **EXPECTED EFFECT:** `httpx` (and its transitive dependencies) added
  to `pyproject.toml`, resolved, and locked.
- **RISK/TRADE-OFF:** a tightly bounded range (`<0.28`) minimizes
  surprise but means a deliberate future update is needed even for a
  routine `0.27.x` → `0.28.0` bump — appropriate caution given `httpx`
  is still pre-1.0 (§10).

**Step 3 — Locking/resolving dependencies**
- **WHAT:** confirm the resolution succeeded and review it.
- **WHY:** §18's step 5–6, performed explicitly before trusting the
  result.
- **COMMAND:** `git diff pyproject.toml uv.lock`
- **EXPECTED EFFECT:** a clear, reviewable diff showing exactly
  `httpx` and its transitive dependencies newly added.
- **RISK/TRADE-OFF:** none — this is a pure review step, adding
  confidence at no cost.

**Step 4 — A patch update**
- **WHAT:** `pydantic` releases `2.5.1`, a PATCH fix for a validation
  edge case.
- **WHY:** low-risk, but still reviewed per §19.
- **COMMAND:** `uv lock` (or `uv sync`, if the range already covers
  it), followed by `uv run pytest`
- **EXPECTED EFFECT:** `uv.lock` now records `pydantic==2.5.1`; tests
  still pass.
- **RISK/TRADE-OFF:** minimal — a PATCH bump within an already-trusted
  range, verified by the existing test suite.

**Step 5 — A minor update**
- **WHAT:** `pydantic` releases `2.6.0`, adding new, optional
  validation helpers.
- **WHY:** the team wants the new functionality for a future feature.
- **COMMAND:** `uv add "pydantic>=2.6,<3.0"`, then `uv run pytest`
- **EXPECTED EFFECT:** `pydantic` resolves to `2.6.0`; existing
  behavior unaffected per SemVer's MINOR contract; tests pass.
- **RISK/TRADE-OFF:** slightly more review warranted than a patch
  (§19) — confirmed here by an unchanged, passing test suite.

**Step 6 — A major update**
- **WHAT:** `pydantic` eventually releases `3.0.0`, with documented
  breaking changes to its validation error format.
- **WHY:** the team wants newer features/fixes only available in 3.x.
- **COMMAND:** read `pydantic`'s migration guide first; update
  `validation.py`'s error-handling code to match the new format;
  *then* `uv add "pydantic>=3.0,<4.0"`; `uv run pytest`
- **EXPECTED EFFECT:** `pydantic` resolves to `3.0.0`; the project's
  own code has been updated *before* the dependency bump lands, so
  tests pass against the new behavior.
- **RISK/TRADE-OFF:** the highest-risk update in this whole
  simulation, by design (§19) — treated with a full migration review,
  not a routine bump.

**Step 7 — A dependency conflict**
- **WHAT:** the team tries to add a new package, `fx-rates-extra`,
  which itself requires `httpx>=0.28,<0.29` — conflicting with the
  project's own `httpx>=0.27,<0.28` (from step 2).
- **WHY (the conflict occurs):** two constraints on `httpx` share no
  overlapping range (§12–§13).
- **COMMAND:** `uv add fx-rates-extra` → resolver reports a conflict.
- **EXPECTED EFFECT:** resolution fails with a clear error naming both
  conflicting `httpx` constraints.
- **RESOLUTION:** since `httpx` 0.27 and 0.28 are both pre-1.0 and the
  team has already verified 0.28 works fine with their own code
  (having just reviewed it for step 6's neighboring work), they widen
  their own constraint: `uv add "httpx>=0.27,<0.29"`, then re-attempt
  `uv add fx-rates-extra`.
- **RISK/TRADE-OFF:** widening a constraint always trades away some of
  the guardrail it was providing (§13) — justified here specifically
  because the team verified compatibility directly, not by assumption.

**Step 8 — A rollback**
- **WHAT:** two days after deploying step 6's `pydantic` 3.0 update, a
  rare production input triggers an unexpected validation error the
  test suite didn't cover.
- **WHY:** restore known-good behavior immediately, rather than
  debugging under production pressure (§20).
- **COMMAND:**
  ```bash
  git revert <the commit for step 6>
  uv sync
  ```
- **EXPECTED EFFECT:** `pydantic` (and `validation.py`'s corresponding
  code) return to the pre-3.0 state; the earlier issue is resolved
  immediately.
- **RISK/TRADE-OFF:** temporarily loses the 3.0 features the team
  wanted, in exchange for immediate production stability — the correct
  trade under incident pressure, per §20.

**Step 9 — A security update**
- **WHAT:** a security advisory is published for a transitive
  dependency of `httpx`.
- **WHY:** treat this as a priority update regardless of where it sits
  in the normal update cadence (§25).
- **COMMAND:** `uv lock` (to pick up the fixed version, assuming the
  advisory's fix is already available upstream within the existing
  constraint range), `git diff uv.lock`, `uv run pytest`
- **EXPECTED EFFECT:** the vulnerable transitive version is replaced
  with the patched one; tests confirm nothing broke.
- **RISK/TRADE-OFF:** minimal risk, high urgency — security fixes are
  prioritized ahead of routine update scheduling.

**Step 10 — CI/CD synchronization**
- **WHAT:** every one of the above changes is pushed through CI before
  merging.
- **WHY:** confirm the exact same reviewed, locked dependency state
  that passed locally also passes in a clean, independent environment
  (§16, §28 of the previous chapter).
- **COMMAND:**
  ```bash
  uv sync
  uv run pytest
  uv run ruff check .
  ```
- **EXPECTED EFFECT:** CI installs from the committed `uv.lock`
  exactly, runs the same tests, and either confirms the change is safe
  to merge or catches something the local review missed.
- **RISK/TRADE-OFF:** none — this step exists specifically to catch
  exactly the kind of drift or oversight §16 warns about, before it
  reaches production.

## 31. Exercises + Answer Key

**Beginner**

1. Given `myapp` imports `pandas`, and `pandas` itself needs `numpy`,
   identify which is direct and which is transitive.
2. Classify each version change as PATCH, MINOR, or MAJOR:
   `4.2.1 → 4.2.2`, `4.2.2 → 4.3.0`, `4.3.0 → 5.0.0`.
3. Read `"requests>=2.28,<3.0"` and explain, in plain language, what
   versions are and aren't acceptable.
4. Explain, in your own words, the difference between what
   `pyproject.toml` and `uv.lock` each record.

**Intermediate**

5. Design a version range for a dependency currently at `1.9.4`, where
   you want routine updates but explicit review before any future
   MAJOR release.
6. Given `A` requires `X>=1,<2` and `B` requires `X>=1.5,<2.5`,
   determine the valid range for `X`, or state that no valid range
   exists.
7. A teammate ran `pytest` after updating a dependency and it passed;
   they conclude the update is completely safe. What's missing from
   their reasoning?
8. Distinguish which of these belongs in `dependencies` vs. a `dev`
   optional group: `requests`, `pytest`, `mypy`, `pydantic`.
9. Write the `uv` command to update a dependency's constraint to
   `>=3.1,<4.0` and explain what it changes.

**Advanced**

10. Design a safe upgrade plan for moving a dependency from `1.x` to a
    newly-released `2.0.0`, including what you'd check before touching
    any code.
11. Given the graph `Application → A → C` and `Application → D → C`,
    with `A` requiring `C<2.0` and `D` requiring `C>=2.0`, propose two
    different possible resolutions to this conflict and state the
    tradeoff of each.
12. Design a rollback plan for a production application that just
    discovered a regression from a dependency update deployed one hour
    ago.
13. Your team is deciding on a version-constraint policy for a
    library you're about to publish to the public. Design that policy
    and justify it against the policy you'd use for an internal
    application.
14. Explain, with a concrete example, why a package following SemVer
    perfectly can still break a consumer's code with a MINOR release,
    and what practice protects against this regardless.

**Answer key**

1. `pandas` is direct (imported by `myapp` itself); `numpy` is
   transitive (needed only because `pandas` depends on it) (§3).
2. `4.2.1 → 4.2.2` — PATCH; `4.2.2 → 4.3.0` — MINOR; `4.3.0 → 5.0.0` —
   MAJOR (§6–§7).
3. Any `requests` version 2.28 or newer is acceptable, up to but not
   including version 3.0 — versions before 2.28, or 3.0 and beyond,
   are not acceptable (§4).
4. `pyproject.toml` records what the project *requires* (often a
   flexible range); `uv.lock` records the *exact, specific* version
   actually resolved and installed, for reproducibility (§15).
5. `>=1.9,<2.0` — allows routine PATCH/MINOR updates within the 1.x
   line, requires deliberate review before a 2.0 release (§4, §11).
6. The overlap of `[1, 2)` and `[1.5, 2.5)` is `[1.5, 2.0)` — any `X`
   version from 1.5 up to (but not including) 2.0 satisfies both
   (§12).
7. Passing tests confirms the *covered* behavior still works — it says
   nothing about behavior the test suite doesn't exercise, and doesn't
   substitute for reading the actual release notes/changelog to
   understand what changed (§8, §18's steps 2–3, §28 mistake 11).
8. `requests` and `pydantic` are runtime `dependencies` (the
   application needs them to run); `pytest` and `mypy` belong in a
   `dev` optional group (needed only for development/testing) (§23).
9. `uv add "package>=3.1,<4.0"` — this changes the declared constraint
   in `pyproject.toml`, re-resolves, updates `uv.lock`, and syncs the
   environment, all in one command (§22).
10. A reasonable plan: read the 2.0.0 changelog/migration guide first;
    identify every place in your own code that uses the affected
    dependency; update that code to match the new 2.0 behavior/API
    *before* actually bumping the dependency constraint; then update
    the constraint, resolve, review the lock diff, run the full test
    suite, and review application behavior manually where tests don't
    fully cover the change — following §18's full workflow with the
    extra migration step §19 specifies for MAJOR updates.
11. One resolution: upgrade whichever of `A`/`D` has a newer release
    whose own `C` requirement has relaxed, removing the conflict at
    its source — the tradeoff is needing to review that upgrade's own
    compatibility implications. A second resolution: replace one of
    `A`/`D` with an alternative package serving the same purpose — a
    larger, more disruptive change, appropriate only if no compatible
    version of either exists (§13).
12. A reasonable plan: identify the exact commit that introduced the
    dependency update (via `git log` on `pyproject.toml`/`uv.lock`);
    `git revert` that commit; run `uv sync` in the affected
    environment; confirm the regression is resolved; only then
    investigate the root cause calmly, without ongoing production
    impact, before considering a forward-fix or a re-attempted, better-
    tested update later (§20).
13. A reasonable policy: for the published library, favor loose,
    minimally-restrictive version ranges on its own dependencies
    (avoiding unnecessary conflicts for consumers, §24) and a
    conservative, actively-maintained `requires-python`; for the
    internal application, favor tighter, well-reviewed bounded ranges
    and a committed, consistently-used lock file, since reproducibility
    for the one deployment that actually matters is more valuable than
    flexibility for consumers that don't exist (§24).
14. Example: a package's maintainers fix a bug in a MINOR release,
    believing the fix is purely corrective and therefore backward-
    compatible — but a consumer's code had (knowingly or not) come to
    rely on the old, buggy behavior, so the "fix" breaks that consumer
    even though the maintainers followed their own SemVer discipline
    in good faith (§8). The practice that protects against this
    regardless of SemVer: always run your own test suite after any
    update, and review actual behavior, rather than trusting the
    version number alone (§18's steps 6–9, §28 mistake 15).

## 32. Debugging Lab

**1. Dependency conflict**
```
error: no solution found: package-a requires X<2, package-b requires X>=2
```
*Diagnosis:* read the exact conflicting constraints from the error.
*Root cause:* two dependencies genuinely require incompatible ranges
of a shared package (§12–§13). *Fix:* check for newer releases of
`package-a`/`package-b` with relaxed requirements; if none exist,
reconsider whether both are truly needed together. *Prevention:*
review a new dependency's own transitive requirements before adding
it to an already-large dependency graph (§27).

**2. Package missing from a clean environment**
Works on a developer's machine; a fresh `uv sync` on a new machine is
missing something. *Diagnosis:* check whether the missing package was
ever actually declared, or only manually installed once. *Root
cause:* §28 mistake 2 — an undeclared dependency. *Fix:* `uv add` the
missing package properly. *Prevention:* never rely on a manually
installed, undeclared package.

**3. Unexpected package upgrade**
A routine `uv sync` unexpectedly installs a newer version of something
than what was running yesterday. *Diagnosis:* check whether
`pyproject.toml` or `uv.lock` changed recently (via `git log`).
*Root cause:* either a teammate's recent, legitimate update (check the
commit history), or a constraint that's looser than intended,
combined with a fresh `uv lock` run picking up a newer release.
*Fix:* if unintended, revert to the previous `uv.lock`; if intended,
confirm it was reviewed per §18. *Prevention:* always commit
`pyproject.toml`/`uv.lock` changes with a clear, descriptive commit
message explaining the update.

**4. Lock file changed unexpectedly**
`git status` shows `uv.lock` modified, but nobody intentionally ran an
update command. *Diagnosis:* check exactly what changed in the diff.
*Root cause:* often, simply running a command that happens to trigger
re-resolution (some `uv` operations may refresh the lock as a side
effect) against a `pyproject.toml` whose ranges now resolve slightly
differently than before (e.g., a new compatible release became
available upstream). *Fix:* review the diff like any other dependency
change (§18's step 6) before committing it. *Prevention:* treat any
`uv.lock` diff as a real, reviewable change, never something to
commit reflexively without looking at it.

**5. Package requires an incompatible Python version**
```
error: package-x requires-python >=3.13, but the project requires >=3.12
```
*Diagnosis:* check the specific package's own `requires-python`
against your project's declared minimum. *Root cause:* the
dependency's newest release has raised its own minimum Python version
past what your project supports (§26). *Fix:* either pin that
dependency to an older release still supporting your project's Python
version, or raise your project's own `requires-python` (and verify
every *other* dependency, and your own code, still works under the
newer minimum). *Prevention:* check a dependency's Python-version
support before updating across a MAJOR boundary.

**6. Major upgrade breaks the application**
Tests fail immediately after a MAJOR version update. *Diagnosis:* read
the dependency's migration guide/changelog for the specific breaking
changes in that release. *Root cause:* §19 — a MAJOR update, by
definition, may require code changes on your side. *Fix:* update your
own code to match the new API/behavior (per §30's step 6 example)
before considering the update complete. *Prevention:* always budget
real review/migration time for MAJOR updates; never treat them as
routine.

**7. Transitive dependency conflict**
The direct dependency you just added resolves fine on its own, but
adding it to the *existing* project fails to resolve. *Diagnosis:*
identify the transitive package both the new addition and an existing
dependency share, and their respective constraints on it (§27).
*Root cause:* a shared transitive dependency's version ranges don't
overlap. *Fix:* per §13 — check for compatible releases of either
side, or reconsider the new dependency if no resolution exists.
*Prevention:* dependency-graph thinking (§27) before assuming a new
addition is "isolated."

**8. Development dependency missing**
CI fails with `ModuleNotFoundError: No module named 'pytest'` even
though local development works fine. *Diagnosis:* check whether `uv
sync` in CI installs the `dev` group, or only the base runtime
dependencies. *Root cause:* CI configuration syncing only production/
runtime dependencies, while the CI job itself needs the development
group to actually run tests. *Fix:* ensure CI's sync step includes the
development dependency group where test/lint tooling is genuinely
needed for that specific CI stage. *Prevention:* be explicit, in CI
configuration, about which dependency groups each stage actually
needs.

**9. Rollback required after deployment**
A dependency update passed all checks but causes a production issue.
*Diagnosis:* confirm the issue correlates with the recent dependency
change (via deployment/commit timing). *Root cause:* an edge case the
test suite didn't cover (§8's honest SemVer caveat, realized in
practice). *Fix:* follow §20's rollback procedure — revert the commit,
`uv sync`, confirm resolution. *Prevention:* add test coverage for the
specific case that broke, before re-attempting the update.

**10. Works locally, fails in CI**
*Diagnosis:* compare what each environment actually installed —
`uv.lock`'s committed state vs. whatever CI actually synced from.
*Root cause:* most commonly, CI isn't actually using `uv sync` against
the committed `uv.lock` (perhaps re-resolving fresh, or using a cached,
stale environment) — precisely
[03-pyproject-lock-files-and-uv.md](03-pyproject-lock-files-and-uv.md)'s
§36 scenario 6, revisited. *Fix:* ensure CI's dependency-installation
step genuinely runs `uv sync` against the exact committed `uv.lock`.
*Prevention:* treat "CI installs exactly what's locked" as a
non-negotiable pipeline requirement, verified explicitly if ever in
doubt.

## 33. Interview + Architecture Questions

1. What is dependency management, and why isn't manual `pip install`
   sufficient for a real project?
2. Distinguish direct and transitive dependencies with an example.
3. Explain the tradeoff between loose and strict version constraints.
4. What is Semantic Versioning, and what does each of
   `MAJOR.MINOR.PATCH` represent?
5. Is SemVer enforced by Python tooling? What does that mean
   practically?
6. Give an example of a change that could be a MAJOR bump versus a
   PATCH bump, and explain why.
7. Why should compatibility be evaluated from the *consumer's*
   perspective, not just the maintainer's stated intent?
8. What is a pre-release version, and why should production code avoid
   depending on one?
9. What's special about the `0.x` version range under SemVer's own
   convention?
10. Explain how a dependency resolver evaluates constraints across
    multiple dependencies, with an example.
11. Describe a genuine dependency conflict and explain why forcing a
    version past it is dangerous.
12. Precisely distinguish `pyproject.toml` from `uv.lock`.
13. What is dependency drift, and how does a lock file prevent it?
14. Describe a safe dependency-update workflow, step by step.
15. Why should PATCH, MINOR, and MAJOR updates be treated with
    different (but never zero) levels of scrutiny?
16. When and why would you roll back a dependency instead of
    forward-fixing?
17. What are `uv add`, `uv remove`, `uv sync`, `uv lock`, and
    `uv run` each responsible for?
18. Distinguish runtime, development, and optional dependencies.
19. Explain the different version-constraint strategies appropriate
    for an application versus a library.
20. What is a supply-chain risk in the context of dependencies, and
    name one defensive practice against it.
21. How does Python version compatibility interact with dependency
    updates?
22. Why does dependency-graph thinking matter as a project scales?

**Answer key**

1. Dependency management is the ongoing discipline of choosing,
   constraining, resolving, and updating a project's dependencies
   deliberately and reproducibly; manual installs record no durable,
   shared decision about which versions are used, leading to drift and
   unreproducible environments (§1–§2).
2. A direct dependency is one your own code imports and declares
   (e.g. `requests`); a transitive dependency is one your direct
   dependency itself needs (e.g. `urllib3`, needed by `requests`) (§3).
3. Loose constraints maximize flexibility but offer no protection
   against a future breaking change; strict constraints (exact pins)
   maximize predictability for that one declaration but can make
   resolution impossible when combined with another dependency's own
   requirements, and impose ongoing manual maintenance (§4).
4. SemVer is a version-numbering convention; `MAJOR` signals
   potentially breaking changes, `MINOR` signals new backward-
   compatible functionality, `PATCH` signals backward-compatible bug
   fixes (§6).
5. No — it's a convention maintainers choose to follow, not something
   Python, `pip`, or `uv` enforces; practically, this means version
   numbers are a strong, useful signal, but never a substitute for
   actually testing after an update (§6, §8).
6. A PATCH bump: fixing a bug without changing any function's
   signature or documented behavior. A MAJOR bump: removing or
   renaming a public function, or changing what a function returns —
   changes that could require consumers to update their own code (§7).
7. Because a change a maintainer considers purely corrective (and
   therefore non-breaking, per their own intent) can still break code
   that had come to depend — knowingly or not — on the previous,
   incorrect behavior; true compatibility is about whether *existing
   consumer code* keeps working, not just about the maintainer's
   stated intent (§8).
8. A pre-release (alpha/beta/rc) signals a version still likely to
   change before the stable release ships; production code should
   avoid depending on one because it accepts real instability risk
   with none of SemVer's usual post-1.0 stability guarantees yet
   applying (§9).
9. Under SemVer's own convention, a project below `1.0.0` is
   considered still in initial development, and compatibility may
   change even between MINOR bumps within the `0.x` line — the usual
   MAJOR/MINOR/PATCH guarantee doesn't fully apply until `1.0.0` (§10).
10. The resolver treats every dependency's version constraint (direct
    and transitive) as one condition in a larger constraint-
    satisfaction problem, and searches for one specific version per
    package that satisfies every condition simultaneously — succeeding
    when a valid overlap exists across all constraints, failing when it
    doesn't (§12).
11. Example: one dependency requires `X<3`, another requires `X>=3` —
    no version satisfies both. Forcing an install past this produces
    an environment that violates a real, declared constraint somewhere,
    risking subtle runtime failures instead of a clear, upfront
    resolution error (§13).
12. `pyproject.toml` is human-authored and declares acceptable version
    ranges (intent); `uv.lock` is machine-generated and records the
    exact, specific versions actually resolved, for reproducible
    installation (§15).
13. Dependency drift is the gradual divergence of dependency versions
    across different environments (developer machines, CI, staging,
    production) that should ideally match; a lock file prevents it by
    giving every environment one exact, shared, reproducible record to
    install from, rather than each independently re-resolving (§16).
14. Identify the update, read release notes, review compatibility,
    update the dependency, resolve, review the lock diff, run tests,
    run lint/type checks, review application behavior, then commit the
    change atomically (§18).
15. Because SemVer's segments correspond to *decreasing* likelihood of
    a breaking change (PATCH lowest, MAJOR highest) but never *zero*
    likelihood (§8's caveat) — scrutiny should scale with that
    likelihood, but never drop to none (§19).
16. Roll back when a fast, reliable return to a known-good state is
    more valuable than investigating under pressure — typically in an
    active production incident; forward-fix once there's time to
    properly diagnose and address the actual problem without ongoing
    impact (§20).
17. `uv add`/`uv remove` declare a dependency change and immediately
    resolve/lock/sync; `uv lock` re-resolves and updates the lock file
    only, without touching the environment; `uv sync` installs/aligns
    the environment to match the current lock file; `uv run` executes
    a command inside the project's correctly-resolved environment
    (§21–§22).
18. Runtime dependencies are needed to actually run the application;
    development dependencies are needed only while developing/testing
    and never ship to production; optional dependencies support
    specific, opt-in features, installed only when those features are
    actually needed (§23).
19. An application, controlling its own single deployment, benefits
    from tighter, well-reviewed ranges and a committed lock file for
    maximum reproducibility; a library, consumed by many different
    downstream projects each with their own other requirements,
    benefits from looser ranges to avoid creating unnecessary
    conflicts for consumers it will never see (§24).
20. Supply-chain risk is the risk that a dependency (or one of its own
    dependencies) is itself compromised — maliciously, or through a
    compromised maintainer account — introducing harmful code rather
    than merely a bug; one defensive practice is reviewing a new
    dependency's maintenance activity and trustworthiness before
    adding it (§25).
21. A dependency's own `requires-python` can change (typically
    increase) in a future release; if that new minimum exceeds your
    project's own declared `requires-python`, that release becomes
    incompatible with your project unless you also raise your own
    minimum and verify everything else still works under it (§26).
22. Because each additional direct dependency can bring an entire
    subtree of its own transitive dependencies, any of which might
    overlap (and conflict) with something already present elsewhere in
    the graph — the number of potential conflict points grows much
    faster than the number of direct dependencies alone would suggest
    (§27).

## 34. Knowledge Check

**Conceptual**
1. In your own words, why is "the version number says MINOR" not
   sufficient justification to skip testing after an update?
2. Why does a library's ideal dependency strategy differ from an
   application's?

**Version interpretation**
3. Classify this change and justify your classification:
   `"Deprecated the `old_parse()` function (still works, but now emits
   a warning); added `new_parse()` as its replacement."` released as
   `3.4.0` from `3.3.2`.

**Dependency graph questions**
4. Given `Application → A → C (C>=1,<2)` and
   `Application → B → C (C>=1.5,<3)`, what is the valid range for `C`?

**`pyproject.toml` questions**
5. What's the practical difference between declaring
   `"httpx"` (no constraint) versus `"httpx>=0.27,<0.28"` for a
   pre-1.0 dependency, in terms of risk?

**Debugging**
6. `uv sync` in CI fails with a resolution error that never occurs
   locally, even though both claim to use the same `uv.lock`. What
   would you check first?

**Scenario-based**
7. Your team depends on a library still at version `0.9.3`. It
   releases `0.10.0` with a change the changelog describes as "minor
   improvement." How cautious should you be, and why?

**Design**
8. Design the version-constraint policy for a project's single most
   critical dependency (say, a data-validation library everything else
   depends on), balancing safety and maintenance burden.

---

**Answer key**

1. Because SemVer describes the maintainer's *intent*, not a
   technically enforced guarantee — a MINOR release can still contain
   an unintentional breaking change, or break code that depended on
   previously-buggy behavior; testing is what actually verifies your
   own project still works, regardless of what the version number
   claims (§6, §8, §19).
2. Because a library's dependencies get resolved *inside* many
   different downstream projects, each with their own other
   requirements — overly tight constraints risk creating unnecessary
   conflicts for consumers; an application controls its own single
   deployment entirely, so tight, well-reviewed constraints carry no
   such downside (§24).
3. This should be classified as MINOR (matching the actual `3.4.0`
   bump) — a deprecation warning and a new, additional function are
   both backward-compatible: existing code using `old_parse()` still
   works (with a warning), and nothing existing was removed or changed
   incompatibly (§6–§8).
4. The overlap of `[1, 2)` and `[1.5, 3)` is `[1.5, 2)` — any `C`
   version from 1.5 up to (but not including) 2.0 (§12, §27).
5. An unconstrained `"httpx"` accepts any future release, including an
   eventual breaking change with zero warning, especially risky since
   `httpx` is pre-1.0 and its own compatibility promise is looser by
   convention (§10); the bounded range accepts only versions already
   verified to work, requiring a deliberate, reviewed decision to move
   past `0.28` (§4, §11).
6. Confirm CI is actually running `uv sync` against the exact,
   committed `uv.lock` file from the same commit being tested — not a
   stale cached environment, a different branch's lock file, or an
   accidental fresh re-resolution instead of an install from the lock
   file (§16, §32 scenario 10).
7. Meaningfully cautious — under SemVer's own `0.x` convention (§10),
   even a change described as "minor" may not carry the same backward-
   compatibility guarantee a `1.x`+ MINOR bump would; treat it with
   the same scrutiny you'd give a MAJOR update in a stable dependency,
   including a careful read of the actual changes and a full test run
   before accepting it.
8. A reasonable policy: a bounded range aligned to the dependency's
   current MAJOR version (e.g. `>=2.4,<3.0`) to receive its own
   PATCH/MINOR updates automatically while requiring deliberate review
   before any MAJOR bump; given its criticality, pair this with extra
   test coverage specifically around how the project uses it, and
   treat any update to it — even PATCH-level — with the fuller review
   §18's full workflow describes, rather than the lighter treatment a
   less-critical dependency might reasonably receive (§4, §18–§19).

## 35. Production Checklist

**Declarations**
- [ ] Every runtime dependency the code actually uses is explicitly
      declared in `pyproject.toml`.
- [ ] Version constraints are intentional — bounded ranges informed by
      each dependency's own SemVer MAJOR-version boundary, not left
      unconstrained and not blindly exact-pinned everywhere.
- [ ] Direct and transitive dependencies are understood as distinct;
      only genuine direct dependencies are declared explicitly.

**Lock file and reproducibility**
- [ ] `uv.lock` is committed and kept in sync with `pyproject.toml` at
      every change.
- [ ] Every environment (developer, CI, staging, production) installs
      via `uv sync` against the same committed lock file — no
      independent, drifting resolutions.

**Updates**
- [ ] Dependency updates follow a deliberate review workflow (release
      notes, compatibility review, lock-diff review, tests) — never
      applied blindly.
- [ ] PATCH, MINOR, and MAJOR updates receive scrutiny proportional to
      their risk, with MAJOR updates always treated as a real migration
      task.
- [ ] Tests are run after every update, regardless of which SemVer
      segment changed.

**SemVer literacy**
- [ ] The team correctly interprets `MAJOR.MINOR.PATCH` and treats it
      as a strong signal, not an absolute guarantee.
- [ ] `0.x` and pre-release dependencies are treated with extra
      caution, not assumed to follow the same stability contract as a
      stable `1.x`+ release.

**Compatibility**
- [ ] `requires-python` is checked against every dependency's own
      supported Python versions, especially before a MAJOR update.
- [ ] Breaking changes are assessed from the consumer's perspective,
      not assumed safe purely because a version bump "should" be
      backward-compatible.

**Rollback readiness**
- [ ] A clear, tested rollback path exists (revert the relevant
      commit, `uv sync`) for any dependency update that reaches
      production.
- [ ] The team distinguishes when to roll back versus when to
      forward-fix, and defaults to rollback under active incident
      pressure.

**Dependency groups**
- [ ] Runtime, development, and optional dependencies are kept
      separate, with production installs excluding development-only
      tooling.

**Security**
- [ ] Dependencies are reviewed for maintenance activity and
      trustworthiness before being added.
- [ ] Security advisories affecting current dependencies are monitored
      and treated as priority updates.
- [ ] Dependencies are neither indefinitely frozen nor blindly
      mass-updated without review.

**Dependency graph awareness**
- [ ] The project's transitive dependency footprint is understood, not
      just its direct dependency list — especially before adding a new
      dependency to an already-large graph.

**CI/CD**
- [ ] CI installs dependencies via `uv sync` against the exact
      committed lock file, guaranteeing the same dependency versions
      are tested and deployed.
