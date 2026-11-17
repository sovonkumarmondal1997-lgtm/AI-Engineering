# 09 — Environment Variables

**Module:** Operating System Fundamentals
**Roadmap reference:** Stage 0 — Module 0.2 — Operating System Fundamentals
**Concept(s) covered:** environment variables, process environment, inheritance, shell export, configuration vs. secrets
**Status:** Not Started

---

## 1. What Is It?

**Connecting to what you already know.** [Permissions](08-permissions.md) explained that every process has an identity the kernel uses to decide *what it may access*. This lesson explains a related but separate piece of a process's context: the information it's handed to help it decide *how it should behave* — its **environment**.

**Environment variable.** Simple meaning: a small, named piece of text information a running program can look up, usually used to configure how it behaves. Technical meaning: an environment variable is a name/value pair, stored as part of a process's environment (this lesson's central concept), that the process can read to obtain configuration information supplied to it from outside its own source code.

**A simple example:**

```text
APP_ENV=development
```

This is one environment variable, and it has exactly two parts:

- **Name** — `APP_ENV`, the label used to look this value up.
- **Value** — `development`, the actual information stored under that name.

**Why it's called an "environment" variable.** Just as a person's physical environment (the room they're in, the tools available to them) shapes how they act without being part of *them*, a process's environment is information surrounding it, supplied from outside, that shapes how it behaves without being part of its own source code. This lesson's whole job is making that everyday word precise.

**Where an environment variable "exists," conceptually.** It is not a file, not a database entry, and not a language-level variable inside your Python source code — it's a small piece of data attached directly to a specific running **process** (Concept 03), associated with that process for as long as it exists (the exact representation is operating-system dependent).

**Why applications can read it.** A running process can query its own environment because the operating system hands each process its own copy of this name/value data when the process is created (Section 5's inheritance model) — reading it is simply asking "what values do I have in my own environment?"

**Why environment variables are useful for configuration.** They let a program's *behavior* be adjusted without touching its *code* — the same application, unmodified, can be told to behave differently depending on what values it finds in its environment when it starts (Section 2 explains this in depth).

**One precise, easily-missed technical detail:** in the common OS/application interfaces used in this lesson, **environment values are represented as strings or string-like byte sequences** — `APP_ENV=development` and, hypothetically, `PORT=8080` are both stored as plain text. Applications interpret those values as integers, booleans, paths, URLs, and so on. If an application needs `PORT` to behave like a number, converting that text into a number is something the *application* must do — the environment itself has no concept of "this one is text, this one is a number." This detail matters directly for Section 11's Scenario 6.

---

## 2. Why Does It Exist?

**The problem environment variables solve.** Imagine an application's configuration — which server to talk to, which mode to run in, how much detail to log — was hard-coded directly into its source code. Every time that configuration needed to change, someone would have to edit the code itself, and every different situation the application needed to run in (a developer's laptop, an automated test run, a real production server) would need its own separately edited copy of the code.

```text
Requirement: the same application needs to behave differently in different situations
     ↓
Requirement: changing that behavior should not require editing and redeploying source code
     ↓
Requirement: the same, unmodified code should be safely reusable across many contexts
     ↓
Configuration needs to live OUTSIDE the application's own code
     ↓
The operating system already gives every process a place for exactly this: its environment
```

**The specific problems this solves:**

- **Separating configuration from application code.** What a program *does* (its logic) and what it's currently *configured to do* (its settings) become genuinely separate concerns.
- **Changing configuration without changing source code.** Adjusting behavior becomes a matter of changing what's supplied to the process, not editing and redeploying code.
- **Configuring the same application differently across environments.** The exact same, unmodified application can run correctly in development, testing, and production, simply by being started with different environment values:

```text
development     →  APP_ENV=development   (verbose logging, relaxed settings, local resources)
testing          →  APP_ENV=testing        (test-specific configuration, isolated resources)
production        →  APP_ENV=production      (production endpoints, stricter settings)
```

- **Passing information to processes.** Environment variables are a direct, general-purpose channel for handing a process information at the moment it starts.
- **Process configuration and deployment flexibility.** The same deployable application artifact can be reused across many different deployment contexts, configured purely through its environment.
- **Avoiding hard-coded configuration values.** Values that are likely to change (URLs, filenames, modes) don't need to be baked permanently into the code that uses them.

**An important caveat, stated now and returned to directly in Section 3 and Section 12: environment variables are not automatically secure.** They solve a *configuration* problem — making behavior adjustable without editing code — not a *security* problem. Nothing about the mechanism itself guarantees that a value placed in a process's environment is protected from being seen, logged, or otherwise exposed.

---

## 3. Why an AI Engineer Needs It

Real AI applications are configured through environment variables constantly:

```text
MODEL_NAME=gpt-x-example
MODEL_PROVIDER=example-provider
API_BASE_URL=https://api.example.com
APP_ENV=production
LOG_LEVEL=INFO
```

(**These are illustrative placeholder values only — not real endpoints, models, or providers.**)

**Realistic categories of AI-engineering configuration carried this way:**

- **API endpoint configuration** — which server a service should actually talk to.
- **Model selection and model provider configuration** — which specific model, and which backend/provider, a service should use.
- **Application mode** — `APP_ENV`-style values distinguishing development, testing, and production behavior.
- **Logging configuration** — how verbose a service's logs should be (`LOG_LEVEL`).
- **Database connection configuration** — where and how to reach a database, without hard-coding it into application code.
- **Service URLs** — addresses of other services an application depends on.
- **Feature flags, at a basic level** — simple on/off toggles for optional behavior.
- **Batch sizes and other simple runtime configuration values.**
- **Storage locations, model/cache directories** — for example, `MODEL_DIR=/tmp/models`, telling an application *where* to look for a resource on disk (Section 7 connects this directly back to Concept 07 and Concept 08).

**Configuration vs. secrets — a distinction this lesson insists on precisely.**

| | Configuration | Secret |
|---|---|---|
| **Example** | `APP_ENV=production`, `LOG_LEVEL=INFO` | An API key, a database password |
| **Sensitivity** | Generally safe to log, display, or share | Must be protected from exposure |
| **What happens if exposed** | Usually nothing serious | Can lead to unauthorized access or real harm |

**Environment variables *can* carry secrets** (many real systems do exactly this), **but the environment-variable mechanism itself is not a complete secrets-management solution.** It provides no encryption, no access auditing, no rotation, and no built-in protection against accidental exposure (Section 12 covers this precisely). **Advanced secret management — dedicated secret stores, encrypted secret injection, and similar systems — belongs to later, more advanced stages of the roadmap.** This lesson teaches only the foundational mechanism those systems are eventually built on top of.

**Why this matters for debugging production AI services.** A huge share of "why isn't my service using the right model / talking to the right endpoint / logging at the right level" problems are environment-configuration problems, not application-logic bugs (Section 11 builds this skill directly).

---

## 4. Beginner Explanation

**Analogy: a person entering a room, and what they're handed at the door.**

```text
Application            = a person entering a room
Environment              = information supplied to that person as they enter
Environment variables      = labeled pieces of information among what they were handed
```

Imagine someone arriving at a room they've never been in before. As they walk in, they're handed a short, labeled information card: "Room mode: quiet hours," "Contact desk: front desk, extension 12," "Lighting: dim." None of this information is something the person *is* — it's context supplied to them, from outside, that shapes how they behave while they're in that room: they'll speak quietly, they'll know who to call if something's needed, they'll expect dim lighting rather than being confused by it.

An **environment variable** is exactly one of these labeled pieces of information — a name (`Room mode`) paired with a value (`quiet hours`) — supplied to something (a process) as it starts, so it knows how to behave without needing to be told through any other channel.

**Where this analogy is useful:** it captures the core idea — information supplied from *outside*, at the moment something starts, shaping behavior without being baked into that thing's own inherent nature.

**Where this analogy breaks down, and must not replace the technical model:**

- A person can *choose* to ignore the information card; a process either reads its environment correctly (using the mechanisms Section 6 and Section 9 demonstrate) or it doesn't — there's no equivalent of a "process's judgment" involved.
- A person entering a room gets one card, once; a process's environment can be inherited, modified, and passed along to *further* processes it starts (Section 5's inheritance model) — a chain this simple analogy doesn't capture.
- The values on a real information card could be anything (numbers, categories, free text); a process's environment values are, in the interfaces this lesson uses, plain text (Section 1) — even a "number" like a port is really just digits stored as a string until the application itself decides to interpret it otherwise.

The rest of this lesson moves from this everyday intuition into the precise, technical model — the analogy is a starting point, not a substitute for it.

---

## 5. Technical Explanation

### The process environment, precisely

```text
Operating System
       ↓
Process                       (Concept 03)
       ↓
Process Environment             (a collection of name/value pairs attached to this process)
       ↓
Environment Variables             (the individual name/value pairs within it)
```

**A required distinction, stated precisely:** an environment variable is associated with a **specific process**, not shared identically, automatically, by every process on the machine. There is no single, global pool of environment variables every process magically sees — each process has *its own* environment, which it received when it was created (next subsection), and which it can modify only for itself and for any further processes it goes on to create.

### Process inheritance

**How a process actually gets its environment.** When one process creates another (a mechanism this lesson previews only conceptually — its full detail belongs to the Process Lifecycle lesson, still ahead), the new (**child**) process receives a copy of its creator's (**parent**) environment at that moment:

```text
Parent Process                (e.g., your shell)
     │
     │  creates/starts
     ▼
Child Process                 (e.g., a Python script you run)
     │
     └── inherits a copy of the parent's environment
```

**Precise points this lesson insists on:**

- The child receives a **copy** of the parent's environment **at the moment it's created** — not a live, ongoing link back to the parent. Changes the parent makes to its own environment *afterward* do not retroactively affect a child that's already running (and vice versa).
- This is a general relationship, not specific to any one kind of process: **shell → Python**, **shell → any subprocess**, and **parent process → child process** generally all work this exact same way.
- **Why child processes can receive configuration from their parent, then:** because they inherit a copy of the parent's environment at creation, a parent can prepare specific values in its own environment beforehand, and every child it subsequently starts will automatically receive them — this is *precisely* how a shell hands configuration to a program you run from it (Section 6, Section 9 demonstrate this directly).

**The exact mechanics of process creation and environment inheritance are OS/API dependent.** On Unix/Linux, `fork()` creates a child that inherits a copy of the environment, and `execve()` supplies an environment to the new program image. **This lesson does not teach the detailed internal mechanics of process creation** (the exact system calls involved, memory setup, and more) — Concept 03 and the upcoming Process Lifecycle lesson cover process creation itself; this lesson's concern is only what happens to the *environment* specifically as part of that process.

### Shell variables vs. environment variables

This is one of the most important, and most commonly confused, distinctions in this entire lesson.

**Shell variable.** A named value that exists only within the current shell session — set, used, and visible to that shell, but **not automatically passed along to processes it starts**.

```bash
APP_ENV=development
```

At this point, `APP_ENV` is a shell variable. Typing `echo "$APP_ENV"` in the *same* shell shows `development` — but a program started from this shell would **not** see it in its own environment yet.

**Environment variable (exported).** A shell variable that has been explicitly **exported**, marking it to be included in the environment of any process the shell subsequently starts.

```bash
APP_ENV=development
export APP_ENV
```

```text
Shell variable                 (APP_ENV=development — visible only to this shell)
     ↓  export
Environment variable             (now marked for inheritance)
     ↓  inherited
Child process                      (a program started from this shell now receives it)
```

**A one-shot alternative: supplying a variable for a single command only.**

```bash
APP_ENV=development python app.py
```

This form sets `APP_ENV` in the environment of **only this one specific command's process** — it does not persist as a shell variable in the current shell afterward, and it does not require a separate `export` step, precisely because it's scoped to exactly one process invocation from the start.

**Scope and lifetime, precisely, for each form:**

| Form | Visible to the current shell? | Inherited by child processes? | Persists after this command finishes? |
|---|---|---|---|
| `APP_ENV=development` (plain assignment) | Yes | No | Yes, for the rest of the current shell session |
| `export APP_ENV` (after assignment) | Yes | Yes | Yes, for the rest of the current shell session |
| `APP_ENV=development python app.py` (one-shot) | No (not set in the shell itself) | Yes, but only for this one command's process | No — scoped to exactly this one invocation |

### Lifetime and scope, more broadly

- **Current shell/session-level configuration** — an exported variable lasts exactly as long as the shell session it was set in; closing that shell/terminal ends it.
- **Child-process lifetime** — once inherited, a child process's copy of the environment lasts exactly as long as that child process itself runs, independent of what its parent does afterward.
- **Temporary, command-specific environment** — the one-shot form above, scoped even more narrowly than a session.
- **Persistent configuration, conceptually.** Making a variable available automatically in *every future* shell session (rather than just the current one) requires it to be set in a shell startup mechanism. **This lesson mentions this only at a high level** — files like `~/.bashrc` and `~/.profile` are commonly involved, but **their detailed behavior belongs to the dedicated [Shell](13-shell.md) lesson, still ahead** — this lesson deliberately does not teach shell startup-file mechanics.

---

## 6. How It Works Internally

### Reading environment variables from Python

Python's standard library exposes the current process's environment through `os.environ`:

```python
import os

value = os.environ.get("APP_ENV")
print(value)
```

**Line by line, for a beginner:** `import os` brings in Python's standard `os` module, which includes access to process/OS-related information; `os.environ` is a dictionary-like object representing this specific Python process's own environment (inherited at creation, exactly as Section 5 described); `.get("APP_ENV")` looks up the value for that name, without raising an error if it's missing.

**Two ways to read a value, with a beginner-critical difference:**

```python
os.environ.get("NAME")    # returns the value, or None if the name doesn't exist
os.environ["NAME"]         # returns the value, or raises a KeyError if the name doesn't exist
```

**An illustration recorded in the documented environment used when this lesson was prepared:**

```python
import os
print('using .get():', os.environ.get('DEFINITELY_MISSING_VAR'))
try:
    os.environ['DEFINITELY_MISSING_VAR']
except KeyError as e:
    print('using []: raised KeyError:', e)
```

**Observed in the documented environment used when this lesson was prepared:**

```text
using .get(): None
using []: raised KeyError: 'DEFINITELY_MISSING_VAR'
```

**Why `.get()` returning `None` for a missing variable matters, precisely:** `None` is Python's own "nothing here" value — it is **not** the same as an empty string (`""`), and it is not automatically converted to any default number or setting. An application that expects a variable to always be present, and does not explicitly check for `None`, can fail later in a confusing way when that check is missing (Section 11's Scenario 1 is built directly around this).

### Reading environment variables from PowerShell

Because the roadmap explicitly includes PowerShell, here is the direct conceptual equivalent:

```powershell
$env:APP_ENV = "development"
$env:APP_ENV
```

**An illustration recorded in the documented environment used when this lesson was prepared** (via its WSL2-to-Windows interop):

```text
$ powershell.exe -NoProfile -Command "$env:APP_ENV_DEMO = 'learning'; Write-Output $env:APP_ENV_DEMO"
learning
```

This confirms the same underlying idea in PowerShell as Bash's `export`-based model: `$env:APP_ENV_DEMO = 'learning'` sets an environment variable for this PowerShell process (and anything it subsequently starts), and reading `$env:APP_ENV_DEMO` back retrieves it.

**The conceptual equivalence, side by side:**

```text
Bash:         export APP_ENV=development
PowerShell:   $env:APP_ENV = "development"
```

**The syntax differs; the underlying idea does not: provide environment information to a process, in a form its children will inherit.** This lesson does not teach PowerShell scripting beyond this direct equivalence.

### WSL2: two genuinely separate environments

**Because WSL2 runs a real, separate Linux environment (Concept 01), its processes have their own, independent process environments — entirely separate from the Windows host's own environment variables.** Setting `$env:APP_ENV` in a Windows PowerShell session does **not** automatically appear inside a WSL2 Linux shell's environment, and vice versa — these are two genuinely different operating-system environments, bridged by interoperability features (like the `powershell.exe` call demonstrated above), **not automatically synchronized**. This lesson does not claim, and you should not assume, that environment variables are ever automatically identical between a Windows process and a WSL2 Linux process unless something has explicitly been configured to pass a specific value across that boundary.

### Connecting to the kernel and system calls, precisely

The process has an environment supplied at program startup; the exact representation and management mechanism are operating-system dependent. It is associated with the process and available to its user-space code — it is part of what Concept 03 already described a process as having. **It is not "stored inside the kernel" as some separate, kernel-owned database** — it is data associated with, and readable by, the specific process it belongs to, set up at that process's creation (Concept 02's system-call model governs process creation itself, but this lesson does not claim environment variables are, by themselves, a single distinct system call — reading `os.environ` in Python is a library-level convenience built on top of how the process's environment was already made available to it at startup, not a fresh request to the kernel every time you read a value).

---

## 7. Real-World Example

```text
Production AI Service
        ↓
Process starts
        ↓
Receives environment configuration
        ↓
APP_ENV=production
MODEL_NAME=<placeholder>
MODEL_PROVIDER=<placeholder>
MODEL_DIR=/opt/models
LOG_LEVEL=INFO
        ↓
Python application reads configuration          (os.environ, Section 6)
        ↓
Application initializes accordingly
        ↓
Loads required resources                          (e.g., a model file from MODEL_DIR)
        ↓
Serves requests
```

**What environment variables are doing here — and, just as importantly, what they are NOT doing:**

- `MODEL_DIR=/opt/models` **tells** the application *where* to look for its model file — this is purely informational, a piece of configuration.
- **Whether the process is actually *allowed* to read whatever is at that path is governed entirely by filesystem permissions (Concept 08), not by the environment variable.** The environment variable does not grant access, bypass permission checks, or interact with the permission system in any way — it is simply a string the application uses to decide *where to look*.
- **Configuration and authorization are two genuinely separate systems, working together but never substituting for each other:** an environment variable can point at a resource the process has no permission to actually read, and a perfectly permission-correct resource can go entirely unused if no environment variable ever tells the application where to find it.

| Example | What the environment variable does | What it does NOT do |
|---|---|---|
| `MODEL_DIR=/opt/models` | Tells the app where to look | Does not grant read access to that path (Concept 08 governs that) |
| `APP_ENV=production` | Tells the app which mode to run in | Does not itself change any file's permissions or the process's identity |
| `LOG_LEVEL=INFO` | Tells the app how verbose to log | Does not control where log files may be written (Concept 08 again) |
| `API_BASE_URL=...` | Tells the app which endpoint to call | Does not authenticate the app to that endpoint by itself |

---

## 8. Relationships to Other Concepts

```text
Kernel / User Space
      ↓
Process                     (owns/receives an environment — Concept 03)
      ↓
Process Environment           (this lesson)
      ↓
Environment Variables
```

| Concept | Relationship to environment variables | Prerequisite or later? | Full treatment |
|---|---|---|---|
| Kernel and User Space | The environment is supplied to a process at startup (the mechanism is OS dependent); user-space code reads it, it is not itself "kernel-internal" data (Section 6) | Prerequisite (Concept 01) | Already covered |
| System Calls | Process creation (which establishes a new process's environment) is a kernel-mediated operation, though reading `os.environ` is not a fresh system call each time (Section 6) | Prerequisite (Concept 02) | Already covered |
| Processes | A process owns and receives its environment at creation, and can pass it to any child it starts (Section 5) | Prerequisite (Concept 03) | Already covered |
| Threads | Threads within a process share that process's single environment, since they share the process's resources generally (Concept 04) | Prerequisite (Concept 04) | Already covered |
| Scheduling | Entirely independent of environment variables — governs *when* a process runs, not what configuration it has | Prerequisite (Concept 05) | Already covered |
| Virtual Memory | Independent of environment variables, though the environment itself occupies a small part of a process's memory | Prerequisite (Concept 06) | Already covered |
| Filesystems | Environment variables commonly contain paths (`MODEL_DIR=/tmp/models`), but the variable itself is only text — it is not the filesystem, and does not touch it directly | Prerequisite (Concept 07) | Already covered |
| Permissions | Governs actual access to whatever a variable's value might point at; the variable itself supplies information only, never access (Section 7) | Prerequisite (Concept 08) | Already covered |
| Signals | A separate kernel-mediated process interaction; a process's environment/configuration can indirectly shape *how* it responds when a signal affects its lifecycle, but signals and environment variables are distinct mechanisms | Later | Concept 10 |
| Standard Input/Output | A different process interface entirely — environment variables are configuration data, not a stream of input/output | Later | Concept 11 |
| Pipes | Transfer data *between* running processes; environment variables instead provide configuration/inherited context established at process creation — genuinely different purposes | Later | Concept 12 |
| Shell | The everyday tool used to set, export, and inspect environment variables (Section 6, Section 9), and the mechanism behind persistent, startup-file-based configuration (Section 5) | Later | Concept 13 |
| Process Lifecycle | Explains, in full, exactly when and how a process's environment is established as part of its creation — this lesson only previewed that moment | Later | Concept 14 |

---

## 9. Practical Observation / Commands

You are working in Ubuntu inside WSL2. All commands below are safe, session-local (affecting only the current shell and processes it starts), and require no `sudo`. No system-wide or persistent configuration is changed anywhere in this lesson. All values used are harmless placeholders (`learning`, `demo-model`, and similar) — never real credentials.

### The full practical lab, with recorded output

**Step 1 — set a plain shell variable (not yet exported):**

```bash
APP_ENV=learning
echo "$APP_ENV"
```

**Observed in the documented environment used when this lesson was prepared:**

```text
learning
```

**Step 2 — confirm it does NOT appear in a child process's environment yet:**

```bash
python3 -c "import os; print('APP_ENV in child (before export):', os.environ.get('APP_ENV'))"
```

**Observed in the documented environment used when this lesson was prepared:**

```text
APP_ENV in child (before export): None
```

This is the direct, concrete confirmation of Section 5's distinction: a plain shell variable is **not** automatically inherited.

**Step 3 — export it:**

```bash
export APP_ENV
```

**Step 4 — confirm it now appears in a child process:**

```bash
python3 -c "import os; print('APP_ENV in child (after export):', os.environ.get('APP_ENV'))"
```

**Observed in the documented environment used when this lesson was prepared:**

```text
APP_ENV in child (after export): learning
```

**Step 5 — inspect it directly with `printenv` and `env`:**

```bash
printenv APP_ENV
env | grep '^APP_ENV='
```

**Observed in the documented environment used when this lesson was prepared:**

```text
learning
APP_ENV=learning
```

`printenv <name>` looks up one specific variable; `env` (here filtered with `grep` to keep the demonstration focused, rather than showing this whole environment's full contents) prints every environment variable this shell currently has exported, one `NAME=value` line per entry. (`env | sort` works the same way, alphabetically sorted, if you want to browse a large environment more easily — this lesson does not print a full, unfiltered listing, to avoid exposing this specific environment's unrelated variable values.)

**Step 6 — override it for a single command only, without changing the shell's own value:**

```bash
APP_ENV=one_shot_override python3 -c "import os; print('one-shot override in child:', os.environ.get('APP_ENV'))"
echo "shell's own APP_ENV unchanged after that: $APP_ENV"
```

**Observed in the documented environment used when this lesson was prepared:**

```text
one-shot override in child: one_shot_override
shell's own APP_ENV unchanged after that: learning
```

This directly confirms Section 5's scope table: the one-shot form affected only that single command's process, leaving the shell's own `APP_ENV` exactly as it was.

**Step 7 — remove (`unset`) it, and confirm removal from both the shell and a new child:**

```bash
unset APP_ENV
python3 -c "import os; print('APP_ENV in child (after unset):', os.environ.get('APP_ENV'))"
printenv APP_ENV
echo "printenv exit code: $?"
```

**Observed in the documented environment used when this lesson was prepared:**

```text
APP_ENV in child (after unset): None
(printenv produced no output)
printenv exit code: 1
```

`printenv` on a variable that no longer exists produces no output and exits with a non-zero status (`1`) — a safe, scriptable way to check for a variable's absence.

**Step 8 — the missing-variable case in Python, precisely (also shown in Section 6):**

```python
import os
print(os.environ.get("DEFINITELY_MISSING_VAR"))   # None — no error
os.environ["DEFINITELY_MISSING_VAR"]               # raises KeyError
```

**Observed in the documented environment used when this lesson was prepared:**

```text
using .get(): None
using []: raised KeyError: 'DEFINITELY_MISSING_VAR'
```

### PowerShell, recorded via WSL2 interop

```powershell
$env:APP_ENV_DEMO = "learning"
Write-Output $env:APP_ENV_DEMO
```

**Observed in the documented environment used when this lesson was prepared** (run via WSL2's interoperability bridge to the Windows host's `powershell.exe`):

```text
learning
```

This confirms Section 6's Bash/PowerShell equivalence directly, with recorded output from both shells in the documented environment. (This lesson does not print a full `Get-ChildItem Env:` listing here, for the same reason as the Bash `env` command above — avoiding exposing this specific machine's unrelated environment values; the single-variable demonstration above is sufficient to confirm the concept.)

### Cleanup

Every variable set during this lab (`APP_ENV`, the one-shot `APP_ENV` override, `APP_ENV_DEMO` in the PowerShell demonstration) was either automatically scoped to a single command, or explicitly `unset` in Step 7 above — no persistent shell configuration file was touched, and no variable from this lesson remains set in any lasting way.

---

## 10. Common Misconceptions

| Misconception | Why it's wrong |
|---|---|
| "Environment variables are global variables shared by the entire computer." | Every process has its *own* environment (Section 5) — there is no single, machine-wide pool every process automatically shares. |
| "Every process automatically sees every shell variable." | Only **exported** shell variables become part of a child process's environment (Section 5, Section 9's recorded "before export: None" result) — plain shell variables stay local to the shell. |
| "Setting a shell variable automatically makes it available to child processes." | It must be explicitly exported first (Section 5) — Section 9's lab demonstrated this exact distinction directly. |
| "Environment variables are always persistent." | A plain or exported variable lasts only as long as the current shell session, unless separately configured in a shell startup mechanism (Section 5's lifetime table) — most of this lesson's examples were deliberately session-local and temporary. |
| "Environment variables are always secret." | They are plain-text configuration data (Section 1) with no inherent protection — Section 3 and Section 12 explain exactly why "environment variable" and "secret" are not the same thing. |
| "Environment variables are only used by Linux." | Windows/PowerShell has its own, directly analogous mechanism (`$env:NAME`, Section 6) — the underlying idea is general, not Linux-specific. |
| "Python environment variables are Python variables." | `os.environ` entries come from the *process's* environment (inherited at creation, Section 5) — they are not Python-language variables defined in your source code. |
| "Changing an environment variable automatically changes an already-running unrelated process." | A process's environment is a *copy*, taken at creation (Section 5) — changing a value afterward, in a different process, does not retroactively reach into an already-running process's own copy. |
| "Environment variables are stored in the filesystem like normal files." | They are process state (Section 5, Section 6) — Concept 07's filesystem model and this lesson's process-environment model are genuinely different things, even though a variable's *value* can be a filesystem path. |
| "The OS magically knows what `MODEL_NAME` means." | The OS treats an environment variable as an opaque name/value pair of string data (Section 1) — giving it meaning is entirely up to whatever application chooses to read and interpret it. |
| "Environment variables can only contain numbers or predefined values." | Values are arbitrary string data in the interfaces this lesson uses (Section 1) — there is no built-in restriction to numbers or predefined values. |
| "If a variable is missing, Python always returns an empty string." | `os.environ.get(...)` returns `None` (Python's own "nothing here" value) for a missing variable, not an empty string, and `os.environ[...]` raises a `KeyError` instead of returning anything at all (Section 6, Section 9's recorded output). |
| "Environment variables eliminate the need for configuration validation." | A missing or malformed value (Section 11's Scenario 6) can still cause real problems — reading an environment variable does not, by itself, guarantee the value is present, well-formed, or usable. |
| "Using an environment variable automatically makes an application production-ready." | Environment-based configuration is one foundational building block among many (validation, secret management, deployment tooling, and more — Section 3, Section 15's scope boundaries) — it does not, by itself, constitute a complete production configuration strategy. |

---

## 11. Debugging and Troubleshooting

### A systematic reasoning workflow

```text
Reproduce
   ↓
Check whether the variable exists
   ↓
Check the exact variable name                (typos, case sensitivity)
   ↓
Check current process/shell
   ↓
Check whether it was exported                 (Section 5's shell-vs-environment distinction)
   ↓
Check child-process inheritance
   ↓
Check value                                     (is it actually what you expect?)
   ↓
Check application access                          (is the app reading the right name?)
   ↓
Check parsing/type conversion                       (Section 1's "values arrive as strings" caveat)
   ↓
Form hypothesis
   ↓
Test
   ↓
Fix
   ↓
Verify
```

**Scenario 1 — Python prints `None` for an expected environment variable.**

1. *Problem:* `os.environ.get("APP_ENV")` returns `None` when a value was clearly expected.
2. *Beginner's likely assumption:* "There must be a bug in my Python code."
3. *Correct mental model:* `None` from `.get()` specifically means "this name was not found in this process's environment" (Section 6) — the code itself is very likely working exactly as designed; the variable simply isn't present in *this specific process's* environment.
4. *Investigation approach:* check, in the *exact same shell/session* the Python process was actually started from, whether the variable is set and exported (`printenv APP_ENV`, Section 9).
5. *Expected conclusion:* the variable was either never set, never exported, or set in a different shell/session than the one that actually launched this process.

**Scenario 2 — A shell variable exists but Python cannot see it.**

1. *Problem:* `echo "$APP_ENV"` in the shell shows a value, but the Python process it starts reports `None`.
2. *Beginner's likely assumption:* "Python must not be reading environment variables correctly."
3. *Correct mental model:* this is Section 5's and Section 9's central distinction exactly: a shell variable that has not been `export`-ed is visible to the shell itself but is **not** inherited by child processes.
4. *Investigation approach:* check whether `export` was actually run for this variable.
5. *Expected conclusion:* exporting the variable resolves it — this is one of the single most common environment-related beginner issues, precisely because the shell's own behavior (showing the value with `echo`) can look identical whether or not it's exported.

**Scenario 3 — A Python application works when started manually but fails when launched another way.**

1. *Problem:* running `python app.py` directly in a terminal works; launching the same application via a different mechanism (a script, a service manager, a different shell) fails.
2. *Beginner's likely assumption:* "The application code must behave differently depending on how it's started."
3. *Correct mental model:* different launch mechanisms can easily have different environments — an interactive shell session and an automated launch mechanism are not guaranteed to have exported the same variables (Section 5, Concept 08's related Scenario 4 about service-account identity).
4. *Investigation approach:* compare the actual environment each launch mechanism provides — for example, by having the application itself print its relevant environment variables at startup, in both cases.
5. *Expected conclusion:* "works manually, fails another way, identical code" is a strong, specific signature of an environment/configuration difference between the two launch paths, not a code defect.

**Scenario 4 — The variable name is misspelled.**

1. *Problem:* the application reports a missing variable, but the developer is confident they set it.
2. *Beginner's likely assumption:* "Something deeper must be wrong with how environment variables work."
3. *Correct mental model:* environment-variable name matching depends on the operating system. On Unix/Linux, names are case-sensitive (so `APP_ENV` and `App_Env` are different names), while on Windows, environment-variable names are case-insensitive. Either way, a name that doesn't match is functionally identical to a missing one.
4. *Investigation approach:* compare the exact name used when *setting* the variable against the exact name used when *reading* it in the application code, character by character.
5. *Expected conclusion:* a silent typo in either location produces exactly the same symptom as the variable never having been set at all — always verify the literal name first.

**Scenario 5 — The variable exists but contains an unexpected value.**

1. *Problem:* the application reads a value successfully, but it's not the value the developer intended.
2. *Beginner's likely assumption:* "The application must be transforming or corrupting the value somehow."
3. *Correct mental model:* the environment simply stores whatever text was most recently set for that name in the process that started this one — an unexpected value usually means it was set incorrectly (or set in the wrong shell/session, or overridden by a later one-shot assignment, Section 5) somewhere upstream, not corrupted afterward.
4. *Investigation approach:* trace back to exactly where and how the variable was set for this specific run, rather than assuming the application altered it after reading.
5. *Expected conclusion:* environment variables are read, not silently transformed — an unexpected value points to an upstream configuration mistake.

**Scenario 6 — An integer configuration value is supplied as text and the application fails when using it numerically.**

1. *Problem:* a variable like `PORT=8080` is set correctly, but the application crashes trying to use it as a number.
2. *Beginner's likely assumption:* "The environment variable system must not support numbers."
3. *Correct mental model:* this is Section 1's precise caveat directly: **environment variable values arrive as strings** in the interfaces this lesson uses — `"8080"` is a string of four characters, not the number `8080`, until the application explicitly converts it (for example, with Python's `int(...)`).
4. *Investigation approach:* check whether the application code actually converts the string value to the expected type before using it numerically.
5. *Expected conclusion:* this is not a limitation of environment variables — it's a direct, expected consequence of values arriving as text, and the fix belongs in the application's own parsing/conversion logic, not in "fixing" the environment variable itself.

**Scenario 7 — A child process does not receive an expected variable.**

1. *Problem:* a parent process clearly has a variable set, but a process it starts doesn't see it.
2. *Beginner's likely assumption:* "Inheritance must be broken."
3. *Correct mental model:* inheritance (Section 5) only carries **exported** variables, and only reflects the parent's environment **at the moment the child was created** — a variable set or exported *after* the child already started will not retroactively appear in it.
4. *Investigation approach:* confirm the variable was exported *before* the child process was actually launched, not afterward.
5. *Expected conclusion:* inheritance is a snapshot taken at creation time, not a live, ongoing connection — timing matters.

**Scenario 8 — A developer accidentally logs a sensitive environment variable.**

1. *Problem:* a service's logs are found to contain what looks like a real secret value.
2. *Beginner's likely assumption:* "Environment variables must have some kind of built-in leak."
3. *Correct mental model:* nothing about the environment-variable mechanism itself caused this — some application code (a debug print, a broad "log all configuration at startup" routine, or similar) explicitly wrote that value somewhere it shouldn't have (Section 12).
4. *Investigation approach:* find exactly where in the application's own code a sensitive value was written to a log, rather than looking for a flaw in the environment-variable mechanism itself.
5. *Expected conclusion:* this class of exposure is an application-logic and process-hygiene issue — a direct, practical reason Section 3 and Section 12 insist environment variables are not, by themselves, a secrets-management solution.

---

## 12. Exercises

Work through these in your own words. No answer key exists for this lesson — the goal is reasoning ability, not matching a memorized phrase.

### Level 1 — Recognition

1. What is an environment variable? Identify the name and value in `MODEL_NAME=demo-model`.
2. What is the difference between a shell variable and an (exported) environment variable?
3. What does `export` actually do?
4. What does process inheritance mean, in the context of this lesson?
5. What does `os.environ.get("X")` return if `X` is missing?
6. What does `os.environ["X"]` do if `X` is missing?
7. What command lets you look up a single environment variable's value from the shell?
8. What command removes a shell/environment variable?

### Level 2 — Understanding

9. Explain, in your own words, why a plain shell variable is not automatically visible to a child process.
10. Explain why a one-shot `VAR=value command` assignment does not persist in the shell afterward.
11. Explain why "the OS knows what `MODEL_NAME` means" is inaccurate.
12. Explain why environment variables are not automatically secrets.
13. Explain why changing a variable in one process does not affect an already-running, unrelated process.
14. Explain the difference between configuration and a secret, using your own example.
15. Explain why environment variable values arrive as strings (in the interfaces this lesson uses), even when they "look like" numbers.
16. Explain why inheritance is described as a snapshot taken at process-creation time, not a live connection.

### Level 3 — Application

17. In your own terminal, set a plain (non-exported) shell variable and confirm, using a Python one-liner, that it is *not* visible to that child process.
18. Export the same variable and re-run the same Python one-liner. Confirm it is now visible.
19. Use the one-shot form (`VAR=value command`) to supply a variable to a single Python invocation, and confirm the shell's own environment is unaffected afterward.
20. Use `printenv` to check a variable both before and after `unset`-ing it, recording both results including exit status.
21. Write a Python snippet demonstrating the difference between `os.environ.get("MISSING")` and `os.environ["MISSING"]` for a variable you know doesn't exist.
22. If you have access to PowerShell (via WSL2 interop or a Windows machine), set and read back a variable using `$env:NAME`, and compare the syntax to the Bash equivalent.
23. Set a variable representing a port number as text (e.g., `PORT=8080`) and write a small Python snippet that correctly converts it to an integer before using it.
24. Demonstrate, using `env | grep` or similar, that only *exported* variables appear in a child process's full environment listing.

### Level 4 — Debugging

25. Python reports `None` for an expected variable. Using Scenario 1 from Section 11, describe your investigation steps.
26. A shell variable clearly has a value (`echo` shows it) but a Python child process reports it missing. Using Scenario 2, explain the likely cause.
27. A script works when run manually but fails when launched a different way. Using Scenario 3, explain what you'd compare between the two launch methods.
28. An application reports a missing variable despite the developer being sure they set it. Using Scenario 4, explain what to check first.
29. A variable is present but contains an unexpected value. Using Scenario 5, explain how to trace the actual source of the value.
30. An application crashes trying to use a numeric-looking environment variable as a number. Using Scenario 6, explain the root cause and the correct fix location.
31. A child process doesn't receive a variable the parent clearly has set. Using Scenario 7, explain the most likely timing-related cause.
32. A service's logs are found to contain a sensitive configuration value. Using Scenario 8, explain where the actual problem lies, and why it isn't a flaw in the environment-variable mechanism itself.

### Level 5 — Integration

33. Design the environment-variable configuration for a small AI inference service that needs: an application mode (`APP_ENV`), a model name, a model directory path, a log level, and an API base URL for an external service it calls. For each, briefly justify why it belongs in the environment rather than hard-coded in the application.
34. A friend claims, "Since I put my database password in an environment variable, it's now secure." Using Section 3 and Section 12, explain what's incomplete about this claim, with at least two concrete risks that remain.
35. Explain how this lesson's inheritance model (Section 5) and Concept 08's permission model together explain why a service could have `MODEL_DIR` set correctly and still fail to load its model.
36. A production deployment process starts a Python service under a dedicated service account, in a script that does not `export` a required variable before invoking it. Using Section 5, Section 9, and Scenario 7 from Section 11, explain what would happen and how you'd diagnose it.
37. Using everything in this lesson, explain to a beginner (in your own words, as if teaching them) why "the variable is set in my terminal" is not the same claim as "the process that actually needs it will see it" — and why that distinction is the single most practically useful thing this lesson teaches.

---

## 13. Expected Results

**Expected conceptual results — these should hold regardless of your specific machine:**

- Correctly distinguish a shell variable from an exported environment variable, in your own words.
- Correctly predict whether a child process will see a given variable, based on whether it was exported and when the child was started.
- Correctly explain the difference between `os.environ.get(...)` and `os.environ[...]` for a missing key.
- Explain why environment variable values arrive as strings (in the interfaces this lesson uses), and why that matters for numeric configuration.
- Correctly identify, for several of this lesson's fourteen misconceptions, why each is wrong and what the accurate idea is instead.

**What the practical observations should generally demonstrate, regardless of the exact values:**

- A plain (non-exported) shell variable should be invisible to a child process (`os.environ.get(...)` returning `None`), while the same variable, after `export`, should become visible.
- A one-shot `VAR=value command` assignment should be visible inside that one command's process, while leaving the shell's own environment unaffected afterward.
- `unset` should remove a variable such that both the shell (`printenv`, which will exit with a non-zero status and no output) and any new child process no longer see it.
- `os.environ.get("MISSING")` should return `None`; `os.environ["MISSING"]` should raise `KeyError`.

**Possible environment-dependent results — these will vary by machine and are expected to vary:**

- The full contents of `env`/`printenv` (beyond the specific demonstration variable) will differ entirely between machines and sessions — this lesson deliberately filtered its own `env` output rather than showing this specific environment's full, unrelated variable set.
- Whether `powershell.exe` is reachable via WSL2 interop (as it was in this lesson's documented environment) depends on your specific WSL2/Windows configuration — this lesson's PowerShell example was recorded in the documented environment, but your own environment may or may not have this interop path available.
- Exact process IDs, timing, and shell session details will differ across runs and machines.

---

## 14. Review Questions

Answers are intentionally not provided directly below these questions.

### Foundational knowledge

- What is an environment variable?
- What is a process environment?
- What is the difference between a shell variable and an environment variable?
- What does `export` do?

### Reasoning

- Why isn't a plain shell variable automatically visible to a child process?
- Why does a variable's value arrive as a string, even when it represents a number?
- Why doesn't changing a variable in one process affect an already-running, different process?
- Why is an environment variable not, by itself, a secret?

### OS relationships

- **How does a running Python service actually receive its environment-based configuration, from process creation through reading `os.environ`?**
- How does process inheritance (Concept 03) relate to environment variables specifically?
- Why does an environment variable pointing at a file path (like `MODEL_DIR`) not, by itself, guarantee access to that path?

### Practical Linux/PowerShell

- What is the difference between what `printenv NAME` and plain `echo "$NAME"` each tell you?
- What does `os.environ.get("X")` return for a missing `X`? What does `os.environ["X"]` do instead?
- What is the Bash equivalent of PowerShell's `$env:NAME = "value"`?
- Why shouldn't you assume a Windows PowerShell environment variable is automatically visible inside a WSL2 Linux shell?

### AI engineering

- Give three examples of AI-service configuration commonly supplied through environment variables.
- Why is `MODEL_DIR=/opt/models` not sufficient, by itself, to guarantee a service can actually read the model there?
- Why is it inaccurate to say "using environment variables makes my application production-ready"?

---

## 15. Production Relevance

At this point, you understand what an environment variable is, how the process environment relates to a process, how inheritance works, the precise difference between shell variables and exported environment variables, how Python and PowerShell each read them, and why they are configuration — not automatically secrets. You are not yet expected to know shell startup-file mechanics, dedicated secrets-management systems, or container/orchestration configuration — those remain later topics.

For a production Applied AI Engineer, this lesson's mental model shows up constantly:

- **Development vs. test vs. production configuration.** The exact same, unmodified application code commonly runs in all three, distinguished purely by what's in its environment at startup (Section 2).
- **Service, runtime, model, and database configuration.** All commonly supplied this way — Section 3's and Section 7's examples are not hypothetical; they reflect how real services are configured every day.
- **Logging configuration.** `LOG_LEVEL`-style variables are a direct, everyday example of adjusting behavior without touching code.
- **Deployment configuration and process startup.** Understanding that a process's environment is fixed at the moment it's created (Section 5) is essential for reasoning about deployment scripts, service managers, and any tooling that launches your application.
- **Containerized applications, at a conceptual level.** Modern deployment systems (containers, and beyond) commonly inject configuration into a process's environment at startup — **this lesson does not teach Docker's environment-injection mechanics or Kubernetes ConfigMaps/Secrets in any depth**, but everything they do, at the foundation, is exactly the process-environment model this lesson just taught: a process receiving name/value configuration when it starts.

**Where this lesson stops, deliberately.** This lesson does not teach `.env` file libraries (like `python-dotenv`), configuration libraries (like Pydantic Settings), Docker's environment-injection mechanics, Kubernetes ConfigMaps or Secrets, cloud provider configuration/secret systems, dedicated secret managers (like Vault), CI/CD secret stores, or advanced shell startup configuration — **every one of these is a genuinely important, later-roadmap topic, and every one of them is built directly on top of the process-environment foundation this lesson just established.** Trying to reason about a Kubernetes Secret or a cloud IAM policy without first understanding what a process's environment actually is, and how inheritance actually works, would be building on nothing.

**What comes next**, building directly on this lesson:

```text
Environment Variables            ← this lesson
  → Signals                       (a separate kernel-mediated process interaction)
  → Standard Input/Output           (a different process interface — streams, not configuration)
  → Pipes                            (data transfer between processes, not inherited configuration)
  → Shell                             (the everyday tool for setting/exporting variables, and
                                        the mechanism behind persistent, startup-file configuration)
  → Process Lifecycle                  (exactly when and how a process's environment is
                                         established as part of its creation)
```

None of these are taught here — this section exists only to show where this lesson sits within the larger Module 0.2 sequence you are building, one concept at a time.

---

_This file is the completed lesson for Concept 09 of Module 0.2. It intentionally does not teach `.env` file libraries, `python-dotenv`, Pydantic Settings, Docker environment-injection internals, Kubernetes ConfigMaps or Secrets, cloud provider configuration/secret systems, Vault or other advanced secret managers, CI/CD secret stores, advanced shell startup-file configuration, advanced process-environment internals, kernel source code, or enterprise configuration platforms in depth — those remain the subject of later, more advanced curriculum, not this beginner-level foundation._
