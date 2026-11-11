# Concept 09 — Environment Variables

**Module:** Operating System Fundamentals
**Stage:** 0 — Module 0.2

**Main idea:** Environment variables allow programs to receive configuration from outside their source code.

---

## 1. What Are Environment Variables?

An **environment variable** is a named piece of text information attached to a running process. Applications read these values to decide how they should behave.

Example:

```bash
APP_ENV=development
```

It has two parts:

- **Name:** `APP_ENV`
- **Value:** `development`

Environment variables are not Python variables, files, or database entries. They belong to a specific process's environment. Their values are represented as strings, even when they look like numbers (e.g., `PORT=8080`). The application must convert them into the required data type.

---

## 2. Why Are They Needed?

They separate application configuration from application code.

The same application can run in different environments without changing its source code:

- **Development:** `APP_ENV=development`
- **Testing:** `APP_ENV=testing`
- **Production:** `APP_ENV=production`

They also provide deployment flexibility and avoid hard-coding frequently changing values such as URLs, file paths, and logging settings.

---

## 3. Why AI Engineers Need Them

AI applications commonly use environment variables for:

- Model names and providers.
- API endpoints and service URLs.
- Database connections.
- Application modes.
- Logging levels.
- Feature flags and batch sizes.
- Model and cache directories.

**Configuration vs. secrets:** Configuration such as `LOG_LEVEL=INFO` is generally safe to display. API keys and database passwords are sensitive. Environment variables can carry secrets, but they do not automatically secure them: they provide no built-in encryption, auditing, rotation, or protection against accidental exposure.

---

## 4. How Processes Receive Environment Variables

Every process has its own environment. When a parent process creates a child, the child receives a **copy** of the parent's environment at creation time.

Important points:

- Changes made by the parent afterward do not automatically affect an already-running child.
- Changes made by a child do not automatically affect its parent.
- Shells pass exported variables to programs they launch.

### Shell variables vs. environment variables

```bash
APP_ENV=development
```

This creates a **shell variable**. The current shell can read it, but child processes cannot automatically inherit it.

```bash
export APP_ENV
```

This **exports** it, allowing subsequently launched child processes to receive it.

For a single command:

```bash
APP_ENV=development python app.py
```

This supplies the variable only to that command's process.

---

## 5. Reading Variables in Python and PowerShell

Python uses `os.environ`:

```python
import os

value = os.environ.get("APP_ENV")
print(value)
```

Two lookup methods:

- `os.environ.get("NAME")` returns `None` if missing.
- `os.environ["NAME"]` raises `KeyError` if missing.

PowerShell equivalent:

```powershell
$env:APP_ENV = "development"
$env:APP_ENV
```

Bash equivalent:

```bash
export APP_ENV=development
```

**WSL2 note:** Windows PowerShell and WSL2 Linux have separate process environments. Variables are not automatically synchronized between them.

---

## 6. How It Works in an AI Application

For example, a production AI service may receive:

```bash
APP_ENV=production
MODEL_DIR=/opt/models
LOG_LEVEL=INFO
API_BASE_URL=https://api.example.com
```

Python reads these values and initializes the application accordingly.

Crucially, `MODEL_DIR` only tells the application where to look. It does not grant permission to read that directory. Filesystem permissions still control access.

---

## 7. Practical Linux Commands

| Command | Purpose |
|---|---|
| `echo "$APP_ENV"` | Display a shell variable |
| `export APP_ENV` | Export a variable |
| `printenv APP_ENV` | Display one environment variable |
| `env` | Display exported environment variables |
| `env \| grep '^APP_ENV='` | Find a specific variable |
| `unset APP_ENV` | Remove a variable |

The lesson's lab demonstrates setting, exporting, inheriting, overriding for one command, inspecting, and removing variables. It also demonstrates missing-variable behavior in Python and PowerShell.

---

## 8. Debugging and Common Misconceptions

The lesson covers eight debugging scenarios:

1. **Python returns `None`:** variable missing from that process.
2. **Shell sees it, Python does not:** variable was not exported.
3. **Manual launch works, automated launch fails:** environments differ.
4. **Variable missing despite being set:** check spelling and case.
5. **Unexpected value:** trace where it was set or overridden.
6. **Numeric value causes errors:** convert the string (e.g., `int()`).
7. **Child cannot see variable:** check export and creation timing.
8. **Secret appears in logs:** application code exposed it.

Other important misconceptions: variables are not global, automatically persistent, inherently secret, filesystem files, or understood by the OS. They also do not eliminate configuration validation.

---

## 9. Exercises, Expected Results and Review

The file includes 37 exercises across five levels: recognition, understanding, application, debugging, and integration. It also includes expected practical results and review questions covering process inheritance, Python lookup methods, Bash/PowerShell, permissions, and AI-service configuration.

Expected results include:

- Unexported variables are invisible to child processes.
- Exported variables are inherited by subsequently created children.
- One-shot assignments affect only the specified command.
- `unset` removes the variable.
- Missing Python environment values produce `None` with `.get()` and `KeyError` with bracket access.

---

## 10. Production Relevance and Scope

Environment variables are fundamental to development/testing/production configuration, model and database settings, logging, deployment, and containerized applications.

The lesson deliberately does not cover `.env` files, `python-dotenv`, Pydantic Settings, Docker injection internals, Kubernetes ConfigMaps/Secrets, Vault, cloud secret management, or CI/CD secret stores. These are later topics built on this foundation.

**Next concepts:** Signals → Standard Input/Output → Pipes → Shell → Process Lifecycle.
