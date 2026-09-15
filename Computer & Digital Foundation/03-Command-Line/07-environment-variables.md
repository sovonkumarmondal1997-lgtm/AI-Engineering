# Module 0.3 — Command Line

## Lesson 07 — Environment Variables

**Module:** Command Line
**Roadmap reference:** Stage 0 — Module 0.3 — Command Line
**Concept(s) covered:** environment variables, shell variables, `export`, `printenv`, `env`, `unset`, `PATH`
**Status:** Complete
**Builds on:** 01–06 (navigation, file operations, viewing, searching, text processing, pipes/redirection) and Module 0.2 (processes, shell, process lifecycle, standard input/output)

---

## 1. Learning Objectives

After completing this lesson you will be able to:

- Explain what an environment variable is.
- Explain why environment variables exist.
- Distinguish a shell variable from an environment variable.
- Explain what a process environment is.
- Explain environment inheritance and the parent/child process relationship.
- Create a shell variable.
- Export a variable so it becomes part of the environment.
- Inspect environment variables with `printenv` and `env`.
- Remove (unset) a variable.
- Understand variable scope and lifetime.
- Understand `PATH` at a foundational level.
- Understand the difference between configuration and secrets.
- Explain why environment variables are useful in applications.
- Access environment variables from Python, conceptually and practically.
- Access environment variables in PowerShell.
- Reason about WSL2 environment behavior at a foundational level.
- Diagnose a missing variable, a missing `export`, a misspelled name, or an unexpected value.
- Recognize the risk of accidental secret exposure.
- Apply safe environment-variable practices.

---

## 2. Connection to Previous Lessons

You've built up a full command-line toolkit across Lessons 01–06: navigating the filesystem, managing files, viewing content, searching, processing text, and composing commands with pipes and redirection. Every one of those lessons operated on **files and text**. This lesson is different: it's about something that belongs to the **running process itself** — a small, temporary space of named values that travels with a process and its children.

This lesson does not re-teach navigation, file operations, viewing, searching, text processing, pipes, or redirection — it uses them only where they help illustrate environment variables (for example, `printenv | grep`, echoing Lesson 04's `grep` and Lesson 06's pipe).

This lesson also leans directly on Module 0.2, which already introduced **processes**, the **shell**, **process lifecycle**, and **environment variables** at a conceptual level. This lesson turns that conceptual introduction into hands-on command-line practice — it does not re-teach Module 0.2 from scratch.

---

## 3. What Is an Environment Variable?

**WHAT:** An environment variable is a **named value** made available to a running process through that process's **environment** — a small set of `NAME=VALUE` pairs the operating system hands to a process when it starts.

**WHY it exists (preview; Section 4 goes deeper):** so that a program can be told *something about how to behave* — a setting, a path, a mode — without that information being written directly into the program's own code.

**HOW it looks conceptually:**

```text
OPERATING SYSTEM
       ↓
PROCESS
       ↓
PROCESS ENVIRONMENT
       ↓
NAME = VALUE
```

For example, a process's environment might contain:

```text
APP_ENV=development
MODEL_NAME=example-model
LOG_LEVEL=info
```

**A critical clarification, stated directly:** an environment variable is **not** a global variable magically shared by every program on your computer. It belongs to a **specific process's environment** — and, as you'll see in Sections 5 and 12, to whichever other processes that one specific process happens to hand its environment to when it starts them. There is no single shared pool that every running program automatically sees.

---

## 4. Why Environment Variables Exist

**The engineering problem, first.** Without some way to configure a program from outside its own code, applications tend to **hard-code** things like:

- service URLs
- database addresses
- model/provider choices
- logging levels
- storage paths
- feature flags
- deployment environment names ("this is development" vs. "this is production")
- batch sizes

**Why hard-coding these creates real problems:**

- Changing environments (development → staging → production) requires **editing and redeploying code**, just to change a setting.
- Development and production become **harder to separate cleanly** — the same code, with different hard-coded values, risks drifting or being edited incorrectly under pressure.
- Deployments become **less flexible** — every environment needs its own slightly different copy of the code.
- **Configuration gets mixed with application logic**, making both harder to read and reason about.

**The configuration principle this lesson teaches:**

```text
CODE
+
ENVIRONMENT-SPECIFIC CONFIGURATION
```

rather than:

```text
CODE
+
HARDCODED ENVIRONMENT-SPECIFIC VALUES
```

**Important scoping note, stated explicitly:** this lesson does **not** claim "all configuration belongs in environment variables." Environment variables are **one** configuration mechanism among several (configuration files, command-line arguments, and others exist too) — a genuinely useful one, especially for simple, process-level settings, but not a universal solution. Section 26 (Trade-offs) returns to this directly.

---

## 5. The Process Environment

Recall from Module 0.2: a running program is a **process**, and a process has associated state beyond just "the code executing." One piece of that state is its **environment** — conceptually:

```text
Process
├── program code
├── process state
├── file descriptors
└── environment
      ├── APP_ENV=development
      ├── LOG_LEVEL=info
      └── MODEL_NAME=example-model
```

The environment is simply a list of `NAME=VALUE` pairs that exists **alongside** the process, available for the process (or whatever library/language it's written in) to read. This lesson builds directly on that Module 0.2 concept — nothing here contradicts or extends it at the operating-system level; it only shows you how to actually **create, inspect, and pass along** these values from the shell.

---

## 6. Environment Variables and Processes

Every process — including your shell itself, which is a process (Module 0.2) — has its own environment. When your shell starts another program (say, `python`), that new program becomes a **child process** of your shell, and — as you'll see in detail in Section 9 and Section 12 — it can receive a copy of (some or all of) the shell's environment at the moment it starts.

This is the mechanism that makes environment variables useful for configuration: you can set a value in your shell, then start an application, and that application can read the value from *its own* environment — without you ever having edited the application's code.

---

## 7. Shell Variables vs. Environment Variables

**This distinction is required and easy to get wrong as a beginner — read this section carefully.**

### Shell variable

```bash
NAME=value
```

This creates a variable that exists **inside your current shell**, usable by the shell itself (e.g. in further commands), but — critically — **not automatically part of the environment** that gets handed to any child process the shell starts.

### Environment variable (via `export`)

```bash
export NAME=value
```

`export` marks the variable so that it **becomes part of the environment** the shell hands to child processes it starts **from that point on**.

### The diagram

```text
Current shell
    |
    | shell variable only (NAME=value, no export)
    |
    └── not automatically inherited by child processes

Current shell
    |
    | exported environment variable (export NAME=value)
    ↓
Child process
    ↓
Grandchild process
```

**A precise statement, to avoid a common vague misconception:** `export` does **not** make a variable "global." It does **not** put the variable somewhere every process on the machine can see it. It only means: *"when this shell starts a child process from now on, include this variable in the environment handed to that child."* Nothing else on the machine — no unrelated program, no other terminal window, no other shell session — is affected.

---

## 8. Creating a Shell Variable

**WHAT:** Assigning a name to a value inside your current shell.

**WHY:** To hold onto a value temporarily for use in your current session — for testing, for building up a command, or as a first step before deciding to export it.

**HOW:**

```bash
APP_ENV=development
```

No spaces are allowed around the `=` — `APP_ENV = development` (with spaces) is a syntax error in Bash, not the same assignment.

**Reading it back:**

```bash
echo "$APP_ENV"
```

Example output:
```text
development
```

**Expected behavior:** the variable exists in your current shell and can be used in further commands in that same shell — but, per Section 7, it is **not** yet part of the environment handed to child processes.

**Common mistake:** assuming this alone is enough for a program you're about to start to "see" the value — it is not, until you `export` it (Section 9).

---

## 9. Exporting an Environment Variable

**WHAT:** `export` marks a shell variable so it becomes part of the environment passed to child processes started from this shell afterward.

**WHY:** Because, as Section 7 established, a plain shell variable is not automatically inherited — `export` is the explicit step that changes that.

**HOW:**

```bash
export APP_ENV=development
```

(This single line both creates the variable and exports it. You could also do it in two steps: `APP_ENV=development` then `export APP_ENV`.)

**Expected behavior:** any child process started from this shell **after** this line runs will receive `APP_ENV=development` in its own environment.

**Common mistake:** forgetting `export` entirely, then being confused when a child process (like a Python script) doesn't see the variable — this is, by a wide margin, the single most common beginner mistake in this entire lesson, and Section 24's debugging scenarios return to it first.

---

## 10. Reading Environment Variables

Three different tools, each with a different purpose:

### `echo`

```bash
echo "$APP_ENV"
```

**WHAT:** Prints the value of one specific variable you already know the name of.
**WHY:** Quick, single-variable checks.
**Common mistake:** relying on `echo` as your primary way of inspecting a *whole* environment — it only shows you what you already knew to ask for, one variable at a time. It also does not tell you whether the variable is merely a shell variable or an actually-exported environment variable — `echo "$APP_ENV"` would print the same thing either way.

### `printenv`

```bash
printenv APP_ENV
```

**WHAT:** Prints the value of an environment variable specifically — and, importantly, this checks the actual **process environment**, not just shell variables.
**WHY:** `printenv` is the more reliable, purpose-built tool for confirming whether something is genuinely present in the environment (i.e., actually exported) — not merely a shell variable that looks the same to `echo`.

Without an argument:

```bash
printenv
```

lists **every** environment variable currently set — useful, but potentially a lot of output (Section 27 flags a safety concern here).

### `env`

```bash
env
```

**WHAT:** Also lists the current environment variables (conceptually very similar to bare `printenv`), and is additionally used as a way to run a command with a modified environment (a capability this lesson does not go deeper into, to avoid drifting into advanced usage).
**WHY:** Another standard, widely available way to inspect the environment; you'll see it used interchangeably with `printenv` in real-world examples and documentation.

**Combining with earlier lessons:**

```bash
printenv | grep APP_ENV
```

Search the full environment listing for one specific name — directly reusing Lesson 04's `grep` and Lesson 06's pipe, exactly as promised in Section 2.

---

## 11. Unsetting Variables

**WHAT:** `unset` removes a variable entirely — both as a shell variable and, if it was exported, from the environment.

**WHY:** To clean up, or to explicitly test what happens when a variable is genuinely absent (useful for the debugging exercises in Section 24).

**HOW:**

```bash
unset APP_ENV
```

**Expected behavior:** afterward, `echo "$APP_ENV"` prints nothing, and `printenv APP_ENV` produces no output (and typically a non-zero exit status, per Lesson 04's exit-status discussion — "no output" here means "not found," not "broken").

**Common mistake:** assuming a variable that "goes away" after `unset`, or after closing a shell, has been deleted from some permanent storage — it hasn't; it was never persistent to begin with (Section 14 covers this directly).

---

## 12. Environment Inheritance

**This is one of the most important concepts in this lesson.**

```text
Parent process
      |
      | environment inherited
      ↓
Child process
```

When a process starts another process (for example, your shell starting `python`), the new process is a **child** of the one that started it. At the moment the child starts, it typically receives a **copy** of the parent's exported environment variables.

**Three critical, precise statements — read carefully, because each corrects a common beginner misconception:**

1. **A child process receives a copy of the environment at the moment it starts.** It is a snapshot, not a live connection.
2. **The child normally starts with the inherited values already present** — it doesn't need to do anything special to receive them; they're just there, in its environment, from the beginning.
3. **Changing a child's environment does not modify the parent's environment.** Because the child received a *copy*, anything the child does to its own copy — changing a value, unsetting it, adding new variables — has **zero effect** on the parent shell's environment. This is the reverse of the mistake in point 1, and just as important.

**Environment inheritance happens specifically when the child process is started** — not continuously, and not retroactively. If you export a new variable in your shell *after* a child process has already started, that already-running child will **not** suddenly receive it; only processes started *after* the export will.

This connects directly to Module 0.2's process model: starting a child process, handing it a copy of the environment, and letting it run independently, is part of the same parent/child process relationship you already studied there.

---

## 13. Parent and Child Processes

Restating Section 12's model in the shape you'll actually use it:

```text
Bash shell (parent)
   |
   | export APP_ENV=development
   ↓
python application.py (child)
   |
   | receives a copy of the shell's exported environment,
   | including APP_ENV=development
```

If `python application.py` itself starts something else (a **grandchild** process), that grandchild in turn receives a copy of *its parent's* (the Python process's) environment — which, unless the Python process removed or changed it, still includes `APP_ENV=development`. This is how environment variables can flow down through several layers of started processes, each inheriting from the one that started it.

---

## 14. Scope and Lifetime

**Shell session scope:** an exported variable exists for the lifetime of the shell session it was exported in, and is available to any child process that shell starts from that point forward.

**Process lifetime:** once a process (shell or otherwise) ends, its environment — and anything only ever set as a shell variable in it — ends with it. There's nothing left over afterward.

**Why environment variables normally do not persist across unrelated shell sessions:** each new terminal window, or each new shell session, starts with its own fresh environment (typically inherited from whatever started *it* — often your operating system's default startup process, not from some other terminal window you had open). A variable you exported in one terminal window is simply **not present** in a second, separate terminal window you open afterward — they're different shell processes, each with their own independent environment.

**The important distinction to internalize:**

```text
Temporary session configuration          Persistent configuration
(what this lesson teaches)                (a different topic)

Set with plain assignment / export        Set so it survives across
in the current shell.                     new shells/sessions automatically.

Lasts only as long as this shell          Lasts across new sessions.
session (and its children).
```

**This lesson does not teach how to make configuration persistent.** You may encounter mentions of files like `.bashrc`, `.profile`, or PowerShell profiles as the mechanism real shells use for that — this lesson mentions them only by name, conceptually, as "the place persistent shell configuration eventually lives," and explicitly defers actually teaching them to later, dedicated shell-environment study. This lesson's entire scope is the *temporary, current-session* behavior described above.

---

## 15. `PATH` as an Important Environment Variable

`PATH` deserves its own section because it's one of the most consequential environment variables you'll interact with, and a frequent source of beginner confusion.

**WHAT:** `PATH` contains a list of directories that the shell searches, in order, to find the actual program file corresponding to a command name you type.

**Conceptual example:**

```text
PATH=/directory1:/directory2:/directory3
```

(On Linux/Bash, entries are separated by `:`; Section 20's PowerShell note flags that Windows uses `;` instead.)

**Command lookup, conceptually:**

```text
User types:
python

Shell searches directories in PATH, in order
        ↓
finds an executable file named "python" in one of them
        ↓
starts that program
```

**Why `PATH` matters:**

- **"command not found" errors** almost always mean: none of the directories currently listed in `PATH` contain an executable with that exact name.
- **Python installations** — which specific `python` actually runs when you type `python` depends entirely on which directory containing a `python` executable appears *first* in `PATH`.
- **Virtual environments** (a topic this lesson does not teach in depth) work, at a foundational level, partly by temporarily adjusting `PATH` so that a project-specific version of a tool is found before any other. This lesson mentions this only to connect `PATH` to something you'll encounter later — it does not teach virtual environments here.
- **Developer environments generally** — installing a new command-line tool and then getting "command not found" anyway is very often a `PATH` problem, not an installation problem (Section 24, Scenario 9, walks through this).

---

## 16. Configuration Through Environment Variables

Practical configuration examples, using only harmless placeholder values:

```text
APP_ENV=development
LOG_LEVEL=debug
MODEL_NAME=example-model
API_BASE_URL=https://example.invalid
BATCH_SIZE=32
DATA_DIR=/data/example
```

**Why this is useful:** the exact same application code can run with **different** values for these variables in different contexts — development, testing, staging, production — without the code itself needing to change at all. One environment might set `LOG_LEVEL=debug` (verbose, for local troubleshooting) and `APP_ENV=development`; another might set `LOG_LEVEL=info` (quieter) and `APP_ENV=production` — same program, different behavior, driven purely by configuration.

`API_BASE_URL=https://example.invalid` uses the reserved `.invalid` domain deliberately, precisely so this example is obviously not a real, callable address — consistent with this lesson's safety requirement never to reference real services or make real network calls.

---

## 17. Configuration vs. Secrets

**This section is required and important — read it carefully.**

**The core principle, stated directly:**

```text
Environment variable
≠
secure secret store
```

Environment variables are often used, in practice, as a *convenient way to inject* configuration — including sometimes secrets like API keys — into a running process. But being a convenient injection mechanism is **not the same thing** as being inherently secure storage.

**Concrete risks worth understanding now:**

- **Accidentally printing secrets** — running `printenv` or `env` (Section 10) to debug something can print *everything* in the environment to your screen, including anything sensitive that happens to be set.
- **Shell history exposure** — depending on how a value was set, it may end up recorded in a shell's command history, readable later.
- **Process/environment inspection** — on many systems, other tools or users with sufficient access can inspect a running process's environment.
- **Logs** — code that logs "here's my configuration" for debugging purposes can accidentally log secret values right along with harmless ones.
- **Debugging output** — the exact same accidental-printing risk as above, just during active debugging rather than routine logging.
- **Accidental inclusion in diagnostics** — an error report or diagnostic dump that includes environment details can leak secrets unintentionally.
- **Insecure CI/CD handling** — automated systems that aren't careful about how they handle environment variables can expose secrets in build logs or artifacts (this lesson does not teach CI/CD secret management in depth — only names this as a real-world risk category, per Section 42's scope boundary).
- **Inherited environments** — per Section 12, a secret set in a parent's environment flows down to every child process it starts, which is convenient but also means it's now present in more than one process's memory.

**This lesson's safety commitment, stated explicitly:** no real API key, password, token, or credential appears anywhere in this lesson's examples. Where a "secret-like" value needs to be shown at all, it uses an obvious placeholder such as:

```text
EXAMPLE_API_KEY=not-a-real-key
```

— and even this is used sparingly, since the better habit is to avoid demonstrating secret-shaped values at all when a genuinely harmless configuration example (like `APP_ENV` or `LOG_LEVEL`) makes the same teaching point.

---

## 18. Bash Environment Variable Commands — Consolidated Reference

| Command | What | Why | Example | Expected behavior | Common mistake |
|---|---|---|---|---|---|
| `NAME=value` | Create a shell variable | Hold a value temporarily in the current shell | `APP_ENV=development` | Usable in this shell; not inherited by children | Assuming it's automatically inherited |
| `export NAME=value` | Create/mark a variable as part of the environment | Make it available to child processes started afterward | `export APP_ENV=development` | Child processes started after this line receive it | Forgetting `export` entirely |
| `echo "$NAME"` | Print one known variable's value | Quick single-value check | `echo "$APP_ENV"` | Prints the value, or nothing if unset | Using it as a general environment-inspection tool |
| `printenv NAME` | Print one variable, checking the actual process environment | Confirm something is genuinely exported | `printenv APP_ENV` | Prints the value if exported; no output/non-zero exit if not | Confusing "no output" with "command failed" |
| `printenv` / `env` | List the entire current environment | Full inspection when debugging | `printenv` | Prints every current `NAME=VALUE` pair | Printing this somewhere it could be logged or shared, exposing secrets (Section 17) |
| `unset NAME` | Remove a variable entirely | Clean up, or deliberately test absence | `unset APP_ENV` | Variable is gone from both shell and environment | Assuming this deletes something "permanent" |

---

## 19. Variable Naming

Practical naming conventions, illustrated with examples used throughout this lesson:

```text
APP_ENV
LOG_LEVEL
MODEL_NAME
API_BASE_URL
DATABASE_URL
BATCH_SIZE
```

- **Uppercase** — the overwhelming convention in Unix/Linux environments for environment variables (as opposed to lowercase, often used for ordinary shell-script-local variables). **This is a convention, not a technical requirement** — lowercase names work mechanically — but breaking this convention makes your configuration harder for others (and future you) to recognize at a glance.
- **Underscores** — used to separate words, since spaces aren't allowed in variable names at all.
- **Descriptive names** — `LOG_LEVEL` tells you immediately what it controls; a name like `X` or `TMP1` does not.
- **Avoiding confusing names** — don't reuse a name that already means something specific elsewhere (like `PATH` itself) for an unrelated purpose.
- **Avoiding accidental typos** — a misspelled variable name doesn't cause an error (Section 23, Scenario 2) — it simply creates a *different*, unrelated, empty variable, which is precisely why careful, consistent naming matters.

---

## 20. Python and Environment Variables

Because this is an Applied AI Engineering roadmap, here is how Python code reads environment variables — kept strictly foundational.

```python
import os

value = os.environ.get("APP_ENV")
```

**`os.environ.get("APP_ENV")`** — returns the value of `APP_ENV` if it's present in the process's environment, or `None` if it is **not** present. No error is raised either way.

```python
value = os.environ["APP_ENV"]
```

**`os.environ["APP_ENV"]`** — expects the key to exist. If `APP_ENV` is **not** present in the environment, this raises an error (a `KeyError`) instead of quietly returning something.

**The practical difference, stated plainly:** use `.get(...)` when a variable is optional (and you're prepared to handle its absence, perhaps with a fallback value: `os.environ.get("LOG_LEVEL", "info")`); use `[...]` when a variable is genuinely required and you *want* the program to fail loudly and immediately if it's missing, rather than silently continuing with `None`.

**Scope note:** this lesson does not teach `python-dotenv`, Pydantic Settings, or any other configuration framework — those are later-stage topics (Section 42). This section's entire purpose is the two lines above, and the conceptual difference between them.

---

## 21. PowerShell Environment Variables

A concise comparison — **not** a PowerShell course.

```powershell
$env:APP_ENV
```

Reads the value of `APP_ENV` from PowerShell's environment — the `$env:` prefix is PowerShell's own syntax for accessing an environment variable, distinct from Bash's `$NAME`.

```powershell
Get-ChildItem Env:
```

Lists the current environment variables — PowerShell's rough equivalent to Bash's `printenv`/`env` (Section 10), though as noted in earlier lessons (05, 06), PowerShell's broader design is object-oriented rather than purely text-stream-oriented; this lesson does not go further into that distinction here.

**Explicit clarification:** Bash and PowerShell syntax for environment variables are **genuinely different**, not just cosmetically different — `$APP_ENV` (Bash) and `$env:APP_ENV` (PowerShell) are not interchangeable, and neither is `export` vs. whatever PowerShell's assignment/scoping equivalent would be. This lesson does not teach PowerShell's assignment or export-equivalent behavior in depth — only enough to recognize the syntax if you encounter it.

---

## 22. Git Bash

**Git Bash provides a Unix-like shell environment on Windows.** For the purposes of this lesson, Bash-style environment-variable commands — `export`, `printenv`, `env`, `unset`, `$NAME` — generally follow the same Bash model taught throughout this lesson when run inside Git Bash. This lesson does not turn this into a Git lesson, and does not cover Git Bash's specific installation, configuration, or interaction with Windows beyond this one-sentence orientation.

---

## 23. WSL2 Considerations

Foundational points worth knowing, without going deeper:

- **The Linux environment inside WSL2 has its own process/environment context** — a shell running inside WSL2 has its own environment, following exactly the Bash model taught in this lesson.
- **Windows and WSL2 are related, but they are not simply one single, identical shell environment.** A variable exported inside a WSL2 Bash session is not automatically visible to a Windows PowerShell session (or vice versa) — they are genuinely separate environments, even though WSL2 provides some interoperability between the two worlds.
- **Environment behavior can differ depending on how a process is launched** — a program started directly from within WSL2's Bash behaves according to this lesson's model; a program started via some Windows-to-WSL2 interop mechanism may involve additional considerations this lesson does not cover.

This lesson does not teach advanced WSL2/Windows interop configuration — only enough to prevent the common beginner assumption that "it's all just one environment somehow."

---

## 24. Internal Mechanics

**What happens conceptually** when you run:

```bash
export APP_ENV=development
python application.py
```

```text
Bash shell
   |
   | variable exported
   ↓
Shell environment
   |
   | child process creation (python application.py)
   ↓
Python process
   |
   | receives a copy of the shell's environment, including APP_ENV
   ↓
Python process runs, and at some point executes:
os.environ.get("APP_ENV")
   |
   ↓
"development"
```

Step by step:

1. `export APP_ENV=development` updates the **shell's own environment** (Section 9).
2. When you then run `python application.py`, the shell starts a **new child process** for Python (Module 2's process concept).
3. As part of starting that child process, the shell hands it a **copy** of its current environment — including `APP_ENV=development` (Section 12).
4. The Python process now has its own environment, containing that variable, from the moment it starts.
5. When the Python code calls `os.environ.get("APP_ENV")`, it's simply reading that value out of its **own** process's environment — the same conceptual "process environment" idea from Section 5, just from Python's side rather than the shell's.

This connects directly back to Module 0.2's process model: parent/child relationships, and each process carrying its own environment as part of its execution context. This lesson does not go deeper into kernel-level implementation of how environments are actually copied at the operating-system level — that level of detail is intentionally out of scope here.

---

## 25. Environment Variables and Process Lifecycle

Restating the flow from Module 0.2's process-lifecycle concept, now specifically with configuration in view:

```text
Shell
  ↓
starts child process
  ↓
child receives environment (Section 12)
  ↓
application starts
  ↓
application reads configuration (Section 20's os.environ)
```

**Why this specific ordering matters** in real systems:

- **Backend services** — typically read their configuration (host, port, log level, feature flags) from the environment once, near startup, before they begin actually handling requests.
- **Workers** (background processing processes) — same pattern: read configuration at startup, then run using those settings for their entire lifetime.
- **Scripts** — a script that reads `os.environ` partway through its own logic is reading whatever was present in *its* environment from the moment it started — not something that can change mid-run just because you change it in some other, unrelated shell.
- **CLI applications** — often blend environment variables with command-line arguments, using the environment for defaults and arguments for per-invocation overrides (this blending itself is not taught in depth here).
- **AI inference services** — might read `MODEL_NAME` or `MODEL_PROVIDER` once at startup, to decide which model to load or which API endpoint to call, for the service's entire running lifetime.
- **Training jobs** — might read `BATCH_SIZE`, `DATA_DIR`, or `MODEL_CACHE_DIR` once at the start of a training run, to configure that run's behavior without editing the training code itself.

---

## 26. Real-World Software Engineering Use Cases

- **Development vs. production configuration** — the same application, configured differently per environment (Section 16).
- **Service URLs** — `API_BASE_URL` pointing to a different address per environment.
- **Database configuration** — a connection string or address supplied via environment rather than hard-coded.
- **Log levels** — `LOG_LEVEL=debug` locally, `LOG_LEVEL=info` in production, controlling verbosity without a code change.
- **Feature flags** — a variable like `FEATURE_X_ENABLED=true` toggling behavior without redeploying different code.
- **Model selection** — `MODEL_NAME` determining which model an application loads or calls.
- **Storage locations** — `DATA_DIR` pointing to different physical locations in different environments.
- **Batch sizes** — `BATCH_SIZE` tuned differently for a small development machine versus a larger production one.
- **Runtime mode** — `APP_ENV=development`/`staging`/`production` as a single, simple signal the application can check.
- **Application behavior configuration generally** — any setting that should vary by environment without requiring a code change.

**When environment variables are the right tool:** simple, process-level settings — a handful of named values, each a simple string, read once (typically at startup).

**When another configuration mechanism may be better** (mentioned here only for balance, not taught in depth): configuration that's deeply **structured** (nested settings, lists, complex objects) is often awkward as flat environment-variable strings and may be better served by a configuration file; configuration that needs strong **validation** or **typed** values benefits from a dedicated configuration library; genuine **secrets at scale**, in a real production system, are usually better served by a dedicated secret-management approach rather than plain environment variables (Section 17) — though this lesson does not teach any such system in depth.

---

## 27. Applied AI Engineering Use Cases

Using only harmless placeholder values — no real provider, no real credentials, no external calls:

```text
MODEL_PROVIDER=example-provider
MODEL_NAME=example-model
LOG_LEVEL=info
APP_ENV=production
BATCH_SIZE=16
MODEL_CACHE_DIR=/models/cache
DATA_DIR=/data
API_BASE_URL=https://example.invalid
```

**What environment variables like these can control, conceptually:**

- **Model/provider selection** — which model or provider an application is configured to use, without code branching for every possibility.
- **API endpoints** — which service address to call (again, `https://example.invalid` here — never a real, callable address in this lesson).
- **Service configuration** — general operational settings for a running service.
- **Logging behavior** — how verbose the application's logs are.
- **Dataset paths** — where an application looks for input data.
- **Model artifact locations** — where a trained model or checkpoint is expected to be found.
- **Inference batch size** — how many items are processed together at inference time.
- **Feature flags** — enabling/disabling specific behaviors.
- **Runtime environment** — which broad deployment context (`development`/`staging`/`production`) the application believes it's running in.

**The core benefit, stated plainly:** the exact same application code can run in different environments with entirely different configuration values — no code change required, only different environment variables supplied at startup.

**The security risk, restated directly for this specific context:** if any of these variables held a real API key or credential (which none of this lesson's examples do), the exact same risks from Section 17 apply — accidental printing during debugging, inclusion in logs, or exposure through diagnostics. This lesson does not use real provider credentials, does not make external API calls, and does not teach any specific AI provider's SDK.

---

## 28. Common Mistakes

1. **Forgetting `export`** — the variable exists in the shell but is never actually handed to a child process (Section 9).
2. **Typing the variable name incorrectly** — a typo silently creates or reads a *different*, unrelated (usually empty) variable, with no error (Section 19).
3. **Confusing shell variables with environment variables** — assuming any `NAME=value` assignment is automatically inherited (Section 7).
4. **Assuming variables are globally available** — believing `export` shares a variable with every other process/terminal on the machine (Section 7's explicit correction).
5. **Assuming variables persist forever** — believing an exported variable survives closing the shell, or is visible in a brand-new terminal window automatically (Section 14).
6. **Expecting a child process to modify the parent's environment** — believing a change made *inside* a started child process could somehow affect the shell that started it (Section 12, point 3).
7. **Using incorrect quoting** — for example, `echo $APP_ENV` (unquoted) can behave unexpectedly if a value contains spaces or special characters; `echo "$APP_ENV"` (quoted) is the safer default, echoing the quoting discipline from Lesson 04, Section 5.
8. **Accidentally exposing secrets** — running `printenv`/`env` somewhere the output could be logged, screen-shared, or otherwise seen, when the environment contains something sensitive (Section 17).
9. **Using the wrong shell syntax** — writing PowerShell's `$env:NAME` syntax inside Bash, or vice versa (Sections 18, 21).
10. **Confusing Bash and PowerShell syntax generally** — assuming `export`/`$NAME` and `$env:NAME` are simply two spellings of the same thing, rather than genuinely different mechanisms.
11. **Assuming Windows and WSL2 environments are identical** — expecting a variable exported in one to automatically appear in the other (Section 23).
12. **Accidentally overwriting an expected value** — reassigning a variable name that some other part of your workflow was already relying on, without realizing it.
13. **Assuming an unset variable always produces an obvious error** — often it simply reads as empty/`None` (Section 20's `os.environ.get`) with no visible error at all, which can be more confusing, not less, than a hard failure.
14. **Confusing `PATH` with a general configuration variable** — treating it like any other setting, rather than recognizing its special role in command lookup (Section 15).
15. **Printing sensitive values during debugging** — the single most common way a "temporary" debugging step (like a stray `print(os.environ)` or `env` command) accidentally exposes something that shouldn't have been visible.

---

## 29. Debugging

Work through each scenario's reasoning *before* reading the corrected command/code and general lesson.

**Scenario 1 — Missing `export`**
- *Situation:* You set `APP_ENV=development` and then run `python application.py`, expecting it to see the value.
- *Intended behavior:* The Python process should read `APP_ENV` as `"development"`.
- *Broken command/code:* `APP_ENV=development` (no `export`), then `python application.py`.
- *Why it fails:* A plain shell variable is never handed to a child process (Section 7); only exported variables are.
- *How to investigate:* Check with `printenv APP_ENV` in the same shell *before* running Python — if it produces no output, it was never exported.
- *Corrected command/code:* `export APP_ENV=development`, then run the script.
- *General lesson:* Always confirm with `printenv`, not just `echo`, when you need to know whether a value is genuinely exported.

**Scenario 2 — Typo in variable name**
- *Situation:* You export `APP_ENV` but your Python code checks `os.environ.get("APP_ENVIRONMENT")`.
- *Intended behavior:* The code should read your intended value.
- *Broken command/code:* `export APP_ENV=development` in the shell; `os.environ.get("APP_ENVIRONMENT")` in the code.
- *Why it fails:* These are two different names — no relationship exists between them as far as the environment is concerned.
- *How to investigate:* Compare the exact name used in the shell against the exact name used in the code, character by character.
- *Corrected command/code:* Make both names match exactly — e.g. `os.environ.get("APP_ENV")`.
- *General lesson:* A typo doesn't produce an error here; it produces a silently different, unrelated, empty result.

**Scenario 3 — Variable not defined at all**
- *Situation:* Code expects `LOG_LEVEL` to be set, but nothing ever set it.
- *Intended behavior:* `os.environ.get("LOG_LEVEL")` should return a real value.
- *Broken command/code:* No `export LOG_LEVEL=...` was ever run in this shell session.
- *Why it fails:* There's genuinely nothing there — this isn't a typo or an inheritance problem, just an absent variable.
- *How to investigate:* `printenv LOG_LEVEL` — no output confirms it's simply not set anywhere in this environment.
- *Corrected command/code:* Export the variable before running the application, or have the code use a documented default via `os.environ.get("LOG_LEVEL", "info")`.
- *General lesson:* "Not set" and "misspelled" look identical from the code's perspective — always verify with `printenv` which one you're actually facing.

**Scenario 4 — Variable defined in one shell but not another**
- *Situation:* You export `APP_ENV` in one terminal window, then open a second terminal window and run the same application, expecting it to still see the value.
- *Intended behavior:* Consistent configuration across your work.
- *Broken command/code:* Assuming the second terminal's shell shares the first terminal's environment.
- *Why it fails:* Each terminal window runs its own separate shell process, each with its own independent environment (Section 14) — nothing links them automatically.
- *How to investigate:* Run `printenv APP_ENV` in the second terminal — if it's empty, this confirms the two shells are independent.
- *Corrected command/code:* Export the variable again in the second shell, or (for a real workflow) rely on the persistent-configuration mechanisms this lesson explicitly does not teach (Section 14's `.bashrc`/profile note).
- *General lesson:* Nothing about opening a new terminal window automatically carries over exported variables from a different, already-running shell session.

**Scenario 5 — Child process does not receive a variable**
- *Situation:* You start a long-running child process, then export a *new* variable in the same shell, and expect the already-running child to now see it.
- *Intended behavior:* The child process should pick up the new setting.
- *Broken command/code:* `export NEW_VAR=value` run *after* the child process was already started.
- *Why it fails:* Inheritance happens at the moment a child process starts (Section 12) — it is a one-time snapshot, not something that updates afterward.
- *How to investigate:* Check whether the export happened before or after the child process was actually launched.
- *Corrected command/code:* Export the variable *before* starting the child process, then start it (or restart it, if it's already running).
- *General lesson:* Order matters — a child only ever sees what was exported before it started.

**Scenario 6 — Unexpected variable value**
- *Situation:* `printenv APP_ENV` shows `production`, but you were confident you'd set it to `development`.
- *Intended behavior:* The value should match what you last set.
- *Broken command/code:* An earlier command (perhaps in a script, or a previous line you forgot about) reassigned `APP_ENV=production` after your intended assignment.
- *Why it fails:* Variable assignment simply overwrites whatever was there before — there's no built-in warning or protection against this (echoing Lesson 02's overwrite-risk theme, applied here to variables instead of files).
- *How to investigate:* Review, in order, every place in your current session (or script) that touches `APP_ENV`.
- *Corrected command/code:* Re-export the intended value last, after confirming nothing downstream will overwrite it again.
- *General lesson:* Always check for a later, overriding assignment before assuming the "wrong" value is a mysterious bug.

**Scenario 7 — Python receives `None`**
- *Situation:* `os.environ.get("MODEL_NAME")` returns `None` instead of the expected model name.
- *Intended behavior:* A real value should be returned.
- *Broken command/code:* `MODEL_NAME` was never exported (or was exported under a different, misspelled name) before Python started.
- *Why it fails:* `.get()` returns `None` for any key that simply isn't present — by design, not as an error (Section 20).
- *How to investigate:* Check `printenv MODEL_NAME` in the same shell you're about to launch Python from.
- *Corrected command/code:* `export MODEL_NAME=example-model` before running the Python process.
- *General lesson:* `None` from `.get()` is a normal, silent signal of absence — always verify the shell's actual exported environment when this happens, rather than assuming a Python-side bug.

**Scenario 8 — Python raises a missing-key error**
- *Situation:* `os.environ["DATA_DIR"]` raises a `KeyError`.
- *Intended behavior:* The code should read a real path.
- *Broken command/code:* `DATA_DIR` was never exported; the code used `os.environ["DATA_DIR"]` (the raising form) rather than `.get(...)`.
- *Why it fails:* `os.environ[...]` requires the key to exist and raises an error immediately if it doesn't (Section 20) — this is the intended, "fail loudly" behavior for genuinely required configuration.
- *How to investigate:* Confirm with `printenv DATA_DIR` whether it's actually set in the environment you're launching from.
- *Corrected command/code:* Export `DATA_DIR` before running the application, or — if this is genuinely optional — change the code to use `.get(...)` with a sensible default instead.
- *General lesson:* This particular error is the *correct, intended* behavior of `os.environ[...]` for a required variable — the fix is usually to actually provide the configuration, not to "fix" the code's error-raising behavior.

**Scenario 9 — `PATH`-related command-not-found issue**
- *Situation:* You install a new command-line tool, but running it produces "command not found."
- *Intended behavior:* The shell should locate and run the newly installed program.
- *Broken command/code:* Simply typing the tool's name, e.g. `newtool`.
- *Why it fails:* The directory containing the new tool's executable is not listed in your current shell's `PATH` (Section 15) — installation and being *findable via PATH* are two separate things.
- *How to investigate:* `printenv PATH` to see the current list of searched directories; compare against where the tool was actually installed.
- *Corrected command/code:* Either run the tool using its full path directly, or (for a genuinely permanent fix) add its directory to `PATH` — the specific, permanent mechanism for doing that safely and durably is intentionally out of this lesson's scope (Section 14's persistence note applies here too).
- *General lesson:* "Command not found" is frequently a `PATH` problem, not a "the program doesn't exist" problem.

**Scenario 10 — Accidental secret exposure**
- *Situation:* While debugging, you run `env` (or `printenv`) and paste the *entire* output into a chat message, a support ticket, or a shared screen, without checking what's actually in it first.
- *Intended behavior:* Share only the specific configuration value that's actually relevant to the problem.
- *Broken command/code:* `env` (unfiltered), shared in full.
- *Why it fails:* The full environment can contain far more than the one value you meant to show — including anything sensitive that happens to be set in that shell (Section 17).
- *How to investigate:* Before sharing anything, ask: "have I actually looked at everything in this output, or am I just assuming it's all harmless?"
- *Corrected command/code:* `printenv APP_ENV` (or `printenv | grep APP_ENV`) — share only the specific variable relevant to the issue, never the full, unfiltered environment.
- *General lesson:* Treat "dump the whole environment" as something to do carefully and privately, never as something to casually share in full.

---

## 30. Practical Demonstration

Everything below uses a **disposable, learner-created practice directory** if you want to follow along — for example, `command-line-environment-demo/`. **This lesson does not create this directory for you.** You may create it manually if you wish:

```bash
mkdir -p ~/command-line-environment-demo
cd ~/command-line-environment-demo
```

**No command below has actually been executed by this lesson.** Every result shown is explicitly labeled `Example output:` — an illustration of expected behavior, never a captured result. Nothing here modifies the real Applied AI Engineering project, uses `sudo`, or touches any system-wide configuration.

**Step 1 — create a simple shell variable**

Command: `APP_ENV=development`
Purpose: create a value in the current shell only.
Data/process flow: the value now exists in this shell's own memory.
Why: this is the baseline case Section 7 describes — not yet exported.

**Step 2 — inspect the variable**

Command: `echo "$APP_ENV"`
Example output:
```text
development
```
Purpose: confirm the shell variable exists and holds the expected value.

**Step 3 — show that a normal shell variable is not automatically inherited**

Command: `printenv APP_ENV`
Example output:
```text
(no output)
```
Why this occurs: `printenv` checks the actual process environment, and this variable was never exported into it (Section 7, Section 10) — even though `echo` (Step 2) happily showed it, because `echo` reads shell variables too, not only environment variables.

**Step 4 — export the variable**

Command: `export APP_ENV`
Purpose: mark the existing shell variable so it becomes part of the environment from now on.
Data/process flow: `APP_ENV` moves from "shell-only" to "part of this shell's environment."

**Step 5 — show that a child process can now receive it**

Command: `python3 -c "import os; print(os.environ.get('APP_ENV'))"`
Example output:
```text
development
```
Why this occurs: this starts a genuine child process (Python), which — per Section 12 — receives a copy of the shell's now-exported environment, including `APP_ENV`.

**Step 6 — inspect environment variables with `printenv`**

Command: `printenv APP_ENV`
Example output:
```text
development
```
Why this differs from Step 3: the variable is now genuinely exported, so `printenv` (which checks the real environment) finds it too.

**Step 7 — use `env`**

Command: `env | grep APP_ENV`
Example output:
```text
APP_ENV=development
```
Purpose: an alternate, equally valid way to confirm the same thing, combined with Lesson 04's `grep` to isolate just this one line from the full listing (rather than dumping everything, per Section 17's caution).

**Step 8 — unset the variable**

Command: `unset APP_ENV`
Data/process flow: the variable is removed from both the shell and its environment.

**Step 9 — observe scope/lifetime behavior**

Command: `printenv APP_ENV`
Example output:
```text
(no output)
```
Why this occurs: exactly as Section 11 described — `unset` removes it entirely; there's nothing left to find.

**Step 10 — demonstrate a simple `PATH` concept**

Command: `printenv PATH`
Example output:
```text
/usr/local/bin:/usr/bin:/bin
```
Purpose: see the actual list of directories your shell currently searches for commands (Section 15) — the real value on your system will differ from this illustrative example.

**Step 11 — read a variable from Python**

Command:
```bash
export MODEL_NAME=example-model
python3 -c "import os; print(os.environ.get('MODEL_NAME'))"
```
Example output:
```text
example-model
```
Data/process flow: shell exports `MODEL_NAME` → Python child process inherits it → Python reads it via `os.environ.get` (Section 20).

**Step 12 — briefly compare Bash and PowerShell**

Bash: `echo "$MODEL_NAME"`
PowerShell: `$env:MODEL_NAME`

Both retrieve a variable's value, but using genuinely different syntax (Section 21) — neither is a "translation" of the other; they're two separate shells' own mechanisms.

---

## 31. Safety

All practical work in this lesson is designed to be safe by construction:

- **No real API keys, passwords, credentials, or tokens** appear anywhere in this lesson.
- **No production configuration** is referenced or modified.
- **No system-wide environment variables** are modified — every example operates on the current shell session only.
- **No `sudo`** is used or suggested.
- **No secrets are exposed or printed** — where a "secret-like" example appears at all (Section 17), it uses an explicit, obvious placeholder.
- **No modification of the real Applied AI Engineering project** occurs anywhere in this lesson's demonstrations or exercises.
- All demonstrations use **disposable values** the learner sets and removes within their own current shell session.

Safe placeholder values used throughout this lesson:

```text
APP_ENV=development
LOG_LEVEL=info
MODEL_NAME=example-model
```

**Restated directly:** environment variables can contain sensitive information, and must therefore be handled carefully — never printed in full without checking their contents first, never shared in full with others, and never populated with real credentials for the purposes of practicing this lesson's material.

---

## 32. Trade-offs

**Advantages of environment variables:**
- Simple — a flat list of names and string values, easy to reason about.
- Widely supported — nearly every programming language and platform can read them.
- Easy to inject at process startup — set them, then start the process.
- Separates configuration from code (Section 4's core motivation).
- Useful across deployment environments — the same code, different values.
- Works across many programming languages without special libraries for basic use.

**Limitations of environment variables:**
- Poor structure for complex configuration — nested or list-like settings are awkward as flat strings.
- Can be difficult to validate — nothing stops you from providing a malformed value; the program has to check for itself.
- Can be accidentally exposed — as detailed throughout Section 17 and Section 29's Scenario 10.
- Values are always strings — a `BATCH_SIZE` of `"32"` needs to be explicitly converted to a number by the reading code; there's no built-in type system.
- Environment inheritance can surprise beginners — exactly the misconceptions Section 12 corrected directly.
- Debugging can be difficult — a missing export, a typo, or a stale value from an earlier session can all look identical from the outside ("the value is just wrong/missing"), as Section 29 demonstrated repeatedly.
- Not a secret-management system (Section 17) — convenient, but not inherently secure.
- Persistent configuration requires additional mechanisms this lesson does not teach (Section 14).

**When environment variables are appropriate:** simple, flat, process-level configuration, especially values that genuinely differ between environments.

**When a dedicated configuration mechanism may be better:** complex/structured settings, settings needing strong validation, or genuine secrets at real production scale — none of which this lesson teaches a specific solution for (Section 42).

---

## 33. Engineering Best Practices

- **Use descriptive variable names** — `LOG_LEVEL`, not `LL` (Section 19).
- **Use consistent naming conventions** — uppercase-with-underscores, as a recognizable signal that something is meant as an environment variable.
- **Validate required configuration** — a real application should check, at startup, that required variables are actually present, rather than discovering their absence deep inside unrelated logic later.
- **Provide safe defaults only when appropriate** — `os.environ.get("LOG_LEVEL", "info")` is reasonable for an optional setting; a genuinely required setting (like which database to use) usually should **not** silently default to something plausible-looking.
- **Distinguish required vs. optional configuration** — decide deliberately, per variable, which category it belongs to, and code accordingly (`.get()` with a default vs. `[...]`/an explicit startup check).
- **Never log secrets** — ensure logging code never accidentally includes sensitive environment values.
- **Avoid printing entire environments** — prefer targeted `printenv NAME` or `printenv | grep NAME` over bare `env`/`printenv` when you only need to check one thing (Section 17, Section 29 Scenario 10).
- **Do not hard-code environment-specific values unnecessarily** — the core motivation from Section 4, restated as a habit.
- **Document expected configuration** — someone else (or future you) should be able to find a list of what variables an application expects, without reading through all of its code to discover them.
- **Keep configuration separate from application logic** — configuration values should be read in one clear place, not scattered arbitrarily throughout code.
- **Understand process inheritance** — know, for any given child process, exactly what was exported *before* it started (Section 12, Section 29 Scenario 5).
- **Verify the environment when debugging** — reach for `printenv`, not assumption, whenever a configuration-related bug appears (the consistent theme of every Section 29 scenario).
- **Avoid accidental exposure of sensitive values** — treat any environment inspection as something to do thoughtfully, not carelessly (Section 17).

---

## 34. Practical Exercises

All Level 3–5 practical work should be done inside your own current shell session (optionally inside a disposable directory you create yourself), using only harmless placeholder values. Never use real credentials, and never modify real project or system configuration.

### Level 1 — Recognition

1. Which of these is a plain shell-variable assignment: `APP_ENV=development` or `export APP_ENV=development`?
2. Which command makes a shell variable part of the environment passed to child processes?
3. Which command removes a variable entirely?
4. Which command is the more reliable way to confirm a variable is genuinely exported: `echo` or `printenv`?
5. What does `env` (with no arguments) do?
6. What is `PATH`, in one sentence?
7. Is `os.environ.get("X")` or `os.environ["X"]` the form that raises an error if `X` is missing?
8. In `$env:APP_ENV`, which shell's syntax is this — Bash or PowerShell?

### Level 2 — Understanding

1. Explain, in your own words, what a process environment is.
2. Explain environment inheritance — what exactly does a child process receive, and when?
3. Explain the difference between a shell variable and an environment variable.
4. What does "scope" mean for a shell-session variable, and what does "lifetime" mean?
5. Explain, conceptually, how `PATH` is used when you type a command name.
6. Explain the difference between configuration and secrets, and why environment variables aren't automatically secure.
7. Why does forgetting `export` cause a child process to not see a variable, specifically?
8. Why can a missing environment variable produce `None` in Python rather than an obvious error?

### Level 3 — Application

Perform each of these in your own shell session.

1. Create a shell variable (without exporting it) and confirm it with `echo`.
2. Confirm, using `printenv`, that the same variable is *not* present in the actual environment yet.
3. Export the variable, then confirm with `printenv` that it now is present.
4. Use `env | grep` (or `printenv | grep`) to find one specific variable among the full listing.
5. `unset` a variable and confirm, via `printenv`, that it's genuinely gone.
6. Export at least three configuration-style variables (e.g. `APP_ENV`, `LOG_LEVEL`, `MODEL_NAME`) simulating a small application's configuration.
7. Start a Python one-liner (`python3 -c "..."`) that reads one of those variables via `os.environ.get(...)` and prints it.
8. Change one exported variable's value to simulate switching from a "development" to a "production" configuration, and confirm the Python one-liner now reads the new value.

### Level 4 — Debugging

For each scenario, state the likely cause and the safe fix — explain your reasoning, don't just guess a command.

1. You exported `APP_ENV` but a Python script still reports it as missing. What's the most common cause to check first?
2. `printenv MY_VAR` produces no output, but `echo "$MY_VAR"` shows a value. What does this combination of results tell you?
3. A variable you're sure you exported doesn't appear in a *second*, separately opened terminal window. Why not?
4. You export a new variable *after* starting a long-running background process, and that process doesn't seem to pick it up. What's the root cause?
5. `os.environ["SOME_VAR"]` raises an error in your Python code. What are the two most likely explanations, and how would you tell them apart?
6. After installing a new command-line tool, running it says "command not found," even though the installation seemed to succeed. What variable would you check first?
7. You run `env` to debug an issue and now realize the output may have contained something sensitive. What should you have done differently, and what should you check now?
8. A variable's value looks wrong compared to what you remember setting. What would you check to find out where the unexpected value actually came from?

### Level 5 — Integration

These combine environment variables with earlier Module 0.3 skills (navigation, pipes/redirection, text processing). Perform each in your own shell session.

1. Export a small set of configuration variables (simulating an application's settings), then use `printenv | grep` and Lesson 05's `sort` to produce a neatly sorted list of just those variables' names and values, redirecting the result to a disposable file (Lesson 06).
2. Simulate switching an application between two configurations (e.g. `development` and `production`) by changing the same set of exported variables, and explain, in your own words, what would need to happen for a *real* running application to actually notice the change (hint: Section 25's process-lifecycle discussion).
3. Deliberately create a "missing export" bug on purpose, verify the resulting Python behavior (`None` from `.get()`), then fix it and confirm the corrected behavior — narrating your diagnostic process at each step.
4. Explain the specific security risk of running `env` and redirecting its full output to a file (Lesson 06) versus running `printenv | grep` for one specific variable and redirecting only that — in terms of what could end up saved in each resulting file.
5. Design (in writing, not necessarily executing) a short conceptual plan for how you would validate, at the very start of an application's execution, that all of its required environment variables are actually present — before the application does anything else.

---

## 35. Mini-Project — Environment-Driven Application Configuration

**Objective:** demonstrate the ability to define, export, inspect, and consume environment-based configuration across a parent shell and a child process, using only harmless placeholder values — no external APIs, no real credentials, no databases, no Docker, no Kubernetes, no cloud, no AI APIs, no frameworks.

**Scenario:** You're simulating a small application that needs configuration for: an environment name, a log level, a model name, a data directory, and a batch size. You'll define this configuration entirely through environment variables, verify it's correctly inherited by a child process, read it from Python, and practice both changing configuration without touching application code and identifying what should never be printed openly.

**Setup:** No files are created automatically by this lesson. If you'd like a disposable working area, create one yourself:

```bash
mkdir -p ~/env-config-project
cd ~/env-config-project
```

**Tasks:**

1. **Define configuration variables** — choose harmless placeholder values for:
   ```text
   APP_ENV=development
   LOG_LEVEL=debug
   MODEL_NAME=example-small-model
   DATA_DIR=/tmp/example-data
   BATCH_SIZE=8
   ```
2. **Export them** — using `export`, one at a time or combined, so they become part of your shell's environment.
3. **Inspect them** — use `printenv` (or `env | grep`) to confirm each one is genuinely present and correctly valued.
4. **Start a simple child process** — for example, `python3 -c "import os; print(os.environ.get('APP_ENV'))"`.
5. **Verify inheritance** — confirm the child process's output matches what you exported, demonstrating Section 12's inheritance model directly.
6. **Read configuration from Python** — extend the one-liner (or write a short multi-line `python3 -c "..."`) to read and print all five configuration values using `os.environ.get(...)`.
7. **Change configuration without changing application code** — re-export different values (simulating switching to a "production-like" configuration: `APP_ENV=production`, `LOG_LEVEL=info`, `MODEL_NAME=example-production-model`), then re-run the *same* Python one-liner unchanged, and confirm it now reflects the new values.
8. **Identify which values should NOT be stored or printed openly** — write one sentence explaining that, in a real (non-simulated) version of this project, something like an API key or database password would belong in this configuration set too, but would need to be handled according to Section 17's caution — never casually printed with the rest.
9. **Debug at least one configuration failure** — deliberately misspell one variable name when exporting it (e.g. export `MODEL_NAME` but have your Python code check for `MODELNAME`), observe the resulting `None`, and correctly diagnose and fix it.

**Expected reasoning:** by the end, you should be able to explain exactly why the Python process saw the values it did at each step — tracing back to what was exported, and when, in your shell.

**Debugging challenge:** in addition to task 9, try *removing* `export` from just one variable (leaving it as a plain shell variable) while keeping the others exported, and predict — before checking — which single value the Python child process will fail to see.

**Security challenge:** without actually adding a real secret anywhere, write out (in a comment or plain text, not executed) what a `printenv | grep` command targeting just one specific variable name would look like, as the *safe* alternative to running bare `env` if this configuration set genuinely included something sensitive.

**Completion checklist:**
- [ ] Defined and exported all five configuration variables.
- [ ] Confirmed each with `printenv`.
- [ ] Verified a child Python process correctly inherited them.
- [ ] Read all five values from Python using `os.environ.get(...)`.
- [ ] Changed configuration values and re-ran the same code unchanged, observing the new values.
- [ ] Identified, in writing, which kind of value would need extra care if this were real.
- [ ] Deliberately broke and then correctly diagnosed and fixed a missing/misspelled export.

**Capability demonstrated:** the ability to configure an application's behavior entirely from the shell environment, understand exactly how and when that configuration reaches a child process, and reason correctly about what changed, why, and what would need extra care if the values involved were genuinely sensitive.

---

## 36. Review

**Key concepts:** environment variable, process environment, shell variable, `export`, environment inheritance, parent/child processes, scope, lifetime, `PATH`, configuration, configuration-vs-secrets, Bash commands (`printenv`, `env`, `unset`, `echo`), Python's `os.environ`/`os.environ.get`, PowerShell's `$env:`, security considerations.

**Compact mental model:**

```text
Shell variable
      ↓
export
      ↓
process environment
      ↓
child process
      ↓
application reads configuration
```

**Syntax summary:**

| Syntax | Meaning |
|---|---|
| `NAME=value` | Shell variable only, not inherited |
| `export NAME=value` | Environment variable, inherited by future child processes |
| `echo "$NAME"` | Print one known value (shell or environment) |
| `printenv NAME` | Print one value, checking the real environment specifically |
| `printenv` / `env` | List the entire current environment |
| `unset NAME` | Remove a variable entirely |
| `os.environ.get("NAME")` | Python: read a value, or `None` if absent |
| `os.environ["NAME"]` | Python: read a value, or raise an error if absent |
| `$env:NAME` | PowerShell: read a value |

**Common-mistakes checklist** (full detail in Section 28): forgetting `export`; typos creating unrelated empty variables; confusing shell and environment variables; assuming global availability; assuming permanence; expecting a child to affect its parent; quoting mistakes; accidental secret exposure; mixing up Bash/PowerShell syntax; assuming Windows/WSL2 share one environment; accidental overwrites; assuming absence always errors loudly; confusing `PATH` with ordinary configuration; printing secrets while debugging.

**Debugging checklist:** check `printenv`, not just `echo`, for the authoritative answer on whether something is truly exported; verify exact spelling on both sides (shell and code); confirm export happened *before* the relevant child process started; distinguish "misspelled" from "genuinely absent" from "overwritten later"; check `PATH` specifically for "command not found."

**Safety checklist:** no real secrets, ever; prefer targeted `printenv NAME`/`grep` over bare `env`/`printenv` dumps; never share full environment output without checking its contents first; use disposable placeholder values for all practice.

You should now be able to explain, without memorizing definitions, the difference between a **shell variable** and an **environment variable**, and the difference between **stdin/stdout/stderr** (Lesson 06) and an **environment** (this lesson) — two related, but distinct, pieces of a process's execution context.

---

## 37. Interview Questions

1. **What is an environment variable?** A named value made available to a process through its environment — a set of `NAME=VALUE` pairs the process can read.
2. **Why do applications use environment variables?** To separate configuration from code, so the same application can behave differently in different environments (development, staging, production) without code changes.
3. **What is the difference between a shell variable and an environment variable?** A shell variable exists only in the current shell and is not automatically inherited by child processes; an environment variable (created via `export`) is included in the environment handed to child processes.
4. **What does `export` do?** It marks a shell variable so that it becomes part of the environment passed to any child process the shell starts afterward — it does not make the variable globally available machine-wide.
5. **What is environment inheritance?** The mechanism by which a newly started child process receives a copy of its parent's exported environment at the moment it starts.
6. **Can a child process modify its parent's environment?** No — the child receives a *copy* of the environment; changes the child makes to its own copy have no effect on the parent's environment.
7. **What is `PATH`?** An environment variable listing directories the shell searches, in order, to locate the executable file for a typed command name.
8. **Why is `PATH` important?** Because "command not found" errors, and which specific version of a program actually runs, both depend directly on `PATH`'s contents and order.
9. **Why are environment variables not automatically secure?** Because they can be accidentally printed, logged, included in diagnostics, or inspected by other processes/users with sufficient access — being a convenient way to inject values is not the same as being a secure storage mechanism.
10. **What happens when a shell exits?** Its process ends, and its environment — along with any shell variables that were never exported and used elsewhere — ceases to exist with it; nothing is automatically saved for later sessions.
11. **How does Python access environment variables?** Through `os.environ` — most commonly `os.environ.get("NAME")` for an optional value, or `os.environ["NAME"]` for one that must be present.
12. **What is the difference between `os.environ.get()` and `os.environ[...]`?** `.get()` returns `None` (or a provided default) if the key is absent; `os.environ[...]` raises an error (`KeyError`) if the key is absent.
13. **Why might an environment variable be missing?** It was never set/exported in this shell session, it was set in a different, unrelated shell session, it was set *after* the relevant child process already started, or its name was misspelled somewhere.
14. **What are the risks of printing the environment?** Running `env`/`printenv` with no filter can display everything currently set, including anything sensitive, to a screen, a log, or a shared session — better to target the one specific variable you actually need.

---

## 38. Architecture Questions

1. **Why separate application code from environment-specific configuration?** So the same, tested code can run correctly across multiple environments (development, staging, production) without needing to be edited or redeployed differently for each one — reducing risk and duplication.
2. **How would you configure the same service for development, staging, and production?** Using the same codebase everywhere, but supplying different exported environment variables (or another configuration mechanism) per environment — e.g. different `APP_ENV`, `LOG_LEVEL`, and service-endpoint values, while the code itself never changes.
3. **What are the security risks of environment-based secret injection?** Accidental exposure through debugging output, logs, full-environment dumps, or diagnostic tooling; the environment is a convenient delivery mechanism, not an inherently protected storage layer (Section 17).
4. **When would you use environment variables versus a configuration file?** Environment variables suit simple, flat, per-environment settings; a configuration file suits more complex, structured, or deeply nested settings that are awkward to represent as flat strings.
5. **When would you use a dedicated secret-management system instead of plain environment variables?** When secrets need stronger guarantees than "a string sitting in a process's environment" can provide — auditing, rotation, tightly scoped access — at a scale or sensitivity level beyond this lesson's foundational scope.
6. **How does process inheritance influence application configuration?** Configuration exported in a parent shell only reaches processes started *after* that export, and only as a one-time snapshot at startup — meaning changing configuration later requires restarting the relevant process, not just re-exporting a value into an already-running one.
7. **What happens if required configuration is missing?** Depending on how the application was written, it may silently continue with `None`/a default (risky, if the setting was actually required) or fail loudly and immediately (safer, for genuinely required settings) — Section 20's `.get()` vs. `[...]` distinction is exactly this design choice.
8. **How should a production application validate configuration at startup?** By explicitly checking, before doing any real work, that every required environment variable is present and reasonably well-formed — failing fast with a clear message if something required is missing, rather than discovering the problem much later, deep inside unrelated logic.

---

## 39. Production Application

The concepts in this lesson remain directly relevant well beyond this beginner stage:

- **Backend services** — configuration for ports, hosts, log levels, and feature flags, supplied via environment variables at startup.
- **Python applications generally** — reading `os.environ` for exactly the kinds of settings covered in this lesson.
- **APIs** — endpoint addresses, timeouts, and mode flags, configured per environment.
- **Workers** — background processing configuration, read once at startup.
- **Deployment** — the same deployed artifact (code) configured differently per target environment via environment variables.
- **CI/CD** — automated pipelines commonly inject environment variables to control build/test/deploy behavior (this lesson does not teach CI/CD secret handling in depth — only names it as a real context where these concepts apply).
- **AI inference services** — model/provider selection, endpoint configuration, and logging behavior, read from the environment at service startup.
- **Training jobs** — dataset paths, batch sizes, and cache directories, read once at the start of a run.
- **Model configuration** — which model, and where its artifacts live, controlled without code changes.
- **Logging** — verbosity controlled per environment.
- **Storage** — which paths or locations an application reads/writes, controlled per environment.
- **Feature flags** — enabling/disabling specific behavior without a code change.

**A production-style conceptual example:**

```text
Application code
       +
environment-specific configuration
       ↓
development / staging / production
```

**Stated explicitly, one more time:** environment variables are **one part** of a real production configuration architecture — not the entire architecture. Later stages of this roadmap will introduce more capable configuration and secret-management approaches; this lesson's job is only to make sure the foundational model (process environment, inheritance, scope, configuration vs. secrets) is solid before you get there.

---

## 40. Relationship to Module 0.2

Module 0.2 (Operating System Fundamentals) already introduced, conceptually:

- **Processes**
- **Filesystems**
- **Permissions**
- **Environment variables**
- **Standard input/output**
- **Pipes**
- **Shell**
- **Process lifecycle**

This lesson turns the **environment-variable** concept specifically into practical, hands-on command-line usage — creating, exporting, inspecting, inheriting, and consuming values, exactly the way Lesson 06 turned Module 0.2's process/pipe/file-descriptor concepts into actual pipe and redirection syntax.

**The conceptual bridge:**

```text
Module 0.2:
Understand that processes have environments.

Module 0.3 (this lesson):
Learn how to inspect, create, export, inherit, and use environment
variables from the command line.

Future:
Use environment-driven configuration in software and AI systems.
```

This lesson does not re-teach Module 0.2's material — it assumes that conceptual foundation and builds the practical layer directly on top of it.

---

## 41. Relationship to Previous Module 0.3 Lessons

```text
Navigation
    ↓
File operations
    ↓
Viewing
    ↓
Searching
    ↓
Text processing
    ↓
Pipes and redirection
    ↓
Environment variables (this lesson)
    ↓
Shell scripts
    ↓
Permissions
    ↓
CLI integration
```

This lesson adds **process-level configuration** to the command-line foundation built in Lessons 01–06. It does not replace or re-teach any of them — Section 10's `printenv | grep` example, and Section 30's redirection-based exercise, both directly reuse skills from earlier lessons rather than introducing anything new about them.

---

## 42. Relationship to Next Lesson

The next lesson is `08-shell-scripts.md`. This lesson does not teach shell scripting — no loops, conditionals, functions, or script arguments appear here. The only connection worth naming: shell scripts will **use** the environment-variable concepts learned in this lesson (variables, `export`, reading configuration) as part of automating command-line workflows — this lesson builds the piece that the next lesson will put to use, without previewing shell scripting's own material here.

---

## 43. Scope Boundary

This lesson teaches only:

- environment variables and shell variables
- the process environment and environment inheritance
- `export`, `printenv`, `env`, `echo`, `unset`
- variable naming conventions
- scope and lifetime (session-level only)
- `PATH` at a foundational level
- configuration through environment variables
- configuration vs. secrets, as a security principle
- Python's `os.environ` / `os.environ.get()`
- a concise PowerShell comparison
- foundational Git Bash and WSL2 considerations
- debugging of common environment-variable mistakes

This lesson deliberately does **not** deeply teach:

- `.env` files
- `python-dotenv`
- Pydantic Settings or other configuration frameworks
- Docker environment configuration
- Kubernetes ConfigMaps or Secrets
- Vault or cloud secret managers
- CI/CD secret-management systems
- advanced shell startup files (`.bashrc`, `.profile`, PowerShell profiles) beyond naming them conceptually
- advanced Bash scripting (`08-shell-scripts.md`)
- advanced PowerShell scripting
- advanced Windows environment configuration
- service managers
- container environment internals

These are separate roadmap topics and stages, mentioned in this lesson only where necessary for context. This lesson is not a preview course for any of them.

---

## 44. Final Self-Assessment

Before moving on to `08-shell-scripts.md`, confirm you can do each of the following, ideally without checking back:

- [ ] Explain what a process environment is, in your own words.
- [ ] Explain the difference between a shell variable and an environment variable.
- [ ] State exactly what `export` does — and what it does *not* do (make something globally available).
- [ ] Explain environment inheritance, including why a child process cannot modify its parent's environment.
- [ ] Predict, correctly, what happens if you export a variable *after* a child process has already started.
- [ ] Use `printenv` (not just `echo`) to confirm whether a variable is genuinely part of the environment.
- [ ] Explain what `PATH` is and why "command not found" is so often a `PATH` issue.
- [ ] Explain the difference between `os.environ.get("X")` and `os.environ["X"]` in Python.
- [ ] Explain, in one sentence, why environment variables are not automatically a secure secret store.
- [ ] Diagnose, from a short description alone, whether a configuration problem is most likely a missing `export`, a typo, a stale/overwritten value, or a genuine `PATH` issue.

If any of these feel uncertain, revisit the relevant section above before continuing — this lesson's mental model (shell variable → export → environment → inheritance → configuration) underlies a large amount of what you'll build later in this roadmap.

---

_This lesson is complete. It covers environment variables, shell variables, `export`, `printenv`, `env`, `unset`, and `PATH` only. The remaining Module 0.3 topics are covered in subsequent lessons within this module._
