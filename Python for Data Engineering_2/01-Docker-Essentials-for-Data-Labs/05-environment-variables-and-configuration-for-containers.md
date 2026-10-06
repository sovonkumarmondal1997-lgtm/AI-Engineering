# Environment Variables and Configuration for Containers

**Stage 2B — Python for Data Engineering_2**  
**Gap Module G1 — Docker Essentials for Data Labs**  
**Topic 05 — Environment Variables and Configuration for Containers**  
**Phase B — Connecting and Persisting**

> **Core idea:** A container image should provide the application; runtime configuration should determine how that application behaves in a particular environment.

---

## 1. Learning Objectives

By the end of this module, you should be able to:

- Explain what application configuration is and why it matters.
- Explain what an environment variable is and how a process reads it.
- Pass configuration into a container with `docker run -e` / `--env`.
- Distinguish the host environment from the container environment.
- Read environment variables from Python applications.
- Distinguish required configuration from optional configuration.
- Convert string environment variables into validated integers and booleans.
- Configure containerized PostgreSQL, MinIO, Redis, and relevant Kafka settings.
- Understand initialization-time configuration versus ordinary runtime configuration.
- Reuse the same image across development, testing, and production by changing runtime configuration.
- Inspect the configuration actually present in a running container.
- Reason about configuration separately from networking, persistent storage, and secrets management.
- Diagnose configuration failures systematically.
- Apply production-oriented configuration hygiene without turning this module into a secrets-management or orchestration course.

### The progression

```text
Basics
   ↓
Environment variables
   ↓
Docker runtime injection
   ↓
Application configuration
   ↓
Data Engineering services
   ↓
Validation and inspection
   ↓
Security awareness
   ↓
Failure diagnosis
   ↓
Production configuration mindset
```

---

# 2. Why Configuration Matters in Data Engineering

A Data Engineering system rarely behaves the same way in every environment.

A pipeline may connect to:

- one PostgreSQL instance during development,
- another during testing,
- and a production database in production.

The application code can remain the same while the runtime configuration changes.

```text
                         Same Image
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        Development       Testing      Production
             │              │              │
       DB_HOST=...      DB_HOST=...    DB_HOST=...
       LOG_LEVEL=debug  LOG_LEVEL=info LOG_LEVEL=warn
```

This gives us an important engineering principle:

> **Do not rebuild an application image merely because its environment-specific configuration changed.**

Examples of values that commonly vary:

- database hostname
- database port
- database name
- username
- service endpoint
- log level
- worker count
- timeout
- feature flags
- environment name

The application should receive these values at runtime rather than having them permanently hard-coded into source code.

### A useful mental model

```text
Application
     ↓
Configuration
     ↓
Environment Variables
     ↓
Container Runtime
     ↓
Application Behavior
```

Configuration is therefore not an optional convenience. It is one of the mechanisms that makes a containerized application reusable and predictable.

---

# 3. What Is Configuration?

## 3.1 Simple definition

**Configuration is information that tells an application how it should behave or where it should connect.**

For example:

```text
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_NAME=analytics
```

These are configuration values.

They tell an application:

- which host to contact,
- which port to use,
- and which database to select.

## 3.2 Configuration value

A configuration value is one individual setting.

For example:

```text
LOG_LEVEL=INFO
```

Here:

- `LOG_LEVEL` is the configuration name.
- `INFO` is its value.

Another example:

```text
DATABASE_PORT=5432
```

Here:

- `DATABASE_PORT` identifies the setting.
- `5432` is the configured value.

## 3.3 Default value

A **default value** is the value an application uses when configuration was not explicitly supplied.

For example:

```python
log_level = os.getenv("LOG_LEVEL", "INFO")
```

If `LOG_LEVEL` is absent:

```text
log_level = INFO
```

Defaults can make applications easier to run, but defaults must be chosen carefully.

A default such as:

```text
LOG_LEVEL=INFO
```

is usually reasonable.

A default such as:

```text
DB_PASSWORD=password123
```

for a mandatory credential is dangerous.

## 3.4 Runtime value

A **runtime value** is configuration supplied when the application is actually started.

For example:

```bash
docker run \
  -e APP_ENV=development \
  -e LOG_LEVEL=debug \
  alpine
```

The same image can later be started with:

```bash
docker run \
  -e APP_ENV=production \
  -e LOG_LEVEL=warn \
  alpine
```

The image did not change. Its runtime configuration did.

## 3.5 Hard-coded configuration

Hard-coded configuration places a value directly in application code:

```python
database_host = "localhost"
```

This can work for a toy program, but it becomes problematic when the application must run in different environments.

A runtime-configurable version is:

```python
import os

database_host = os.getenv("DATABASE_HOST")
```

Now the application does not need to know the environment-specific hostname in advance.

---

# 4. What Is an Environment Variable?

An environment variable is a named value made available to a process through its process environment.

The basic shape is:

```text
NAME=VALUE
```

For example:

```text
APP_ENV=development
```

There are four concepts to understand:

| Concept | Meaning |
|---|---|
| Name | The identifier, such as `APP_ENV` |
| Value | The supplied value, such as `development` |
| Process environment | Values made available to a running process |
| Lookup | The application asks for a value by name |

Environment variables are fundamentally text/string values.

Even this:

```text
PORT=5432
```

is supplied as text. An application may convert it to an integer.

Likewise:

```text
DEBUG=false
```

is text. It is not automatically a native Python `False`.

---

## 4.1 Environment variables in a shell

On a Linux-style shell:

```bash
export APP_ENV=development
```

Then:

```bash
echo "$APP_ENV"
```

Expected output:

```text
development
```

You can also inspect the environment:

```bash
env
```

or:

```bash
printenv
```

The important distinction is:

```text
Host Shell
    │
    │ environment
    ▼
Docker Runtime
    │
    │ inject
    ▼
Container Process
    │
    │ read
    ▼
Application
```

A host shell environment exists on the host.

A container has its own process environment.

They are related only when you explicitly pass values into the container.

---

# 5. Environment Variables Inside Containers

The simplest demonstration is an Alpine container.

Run:

```bash
docker run \
  --name env-demo \
  -e APP_ENV=development \
  alpine \
  sh
```

Inside the container:

```bash
env
```

You should see an environment containing:

```text
APP_ENV=development
```

You can also run:

```bash
printenv APP_ENV
```

or:

```bash
echo "$APP_ENV"
```

Expected:

```text
development
```

## What did Docker actually do?

This:

```bash
-e APP_ENV=development
```

means:

> Start the container process with an environment variable named `APP_ENV` whose value is `development`.

The conceptual flow is:

```text
docker run
   │
   │ --env APP_ENV=development
   ▼
Container process environment
   │
   │ APP_ENV available
   ▼
Application can read APP_ENV
```

Docker is not changing your Python source code.

Docker is supplying runtime process configuration.

---

# 6. `docker run -e` / `--env`

The short form is:

```bash
docker run -e KEY=value image
```

The long form is:

```bash
docker run --env KEY=value image
```

They represent the same basic operation.

## 6.1 One variable

```bash
docker run \
  -e APP_ENV=development \
  alpine
```

## 6.2 Multiple variables

```bash
docker run \
  -e APP_ENV=development \
  -e LOG_LEVEL=debug \
  alpine
```

The resulting process can see both:

```text
APP_ENV=development
LOG_LEVEL=debug
```

## 6.3 Explicitly setting an empty value

You can explicitly supply an empty value:

```bash
docker run \
  -e OPTIONAL_SETTING= \
  alpine
```

The variable exists, but its value is empty.

That is different from the variable being absent.

Applications should decide whether:

```text
missing
```

and:

```text
empty
```

mean the same thing.

They do not necessarily mean the same thing.

## 6.4 Quoting values

Quoting is important when a shell value contains spaces or shell-sensitive characters.

For example:

```bash
docker run \
  -e APP_MESSAGE="hello data engineering" \
  alpine
```

The application receives:

```text
APP_MESSAGE=hello data engineering
```

The shell interprets quoting before Docker receives the argument.

---

# 7. Host Environment vs Container Environment

This is one of the most important mental models in this module.

Suppose the host shell has:

```bash
export APP_ENV=development
```

Now start:

```bash
docker run alpine env
```

Do not assume `APP_ENV` is automatically available.

A container does not magically inherit every host environment variable.

## 7.1 Explicitly forward a host variable

You can use:

```bash
docker run \
  -e APP_ENV \
  alpine \
  sh
```

The form:

```bash
-e APP_ENV
```

means Docker should use the host environment's value for `APP_ENV` and provide that value to the container.

Compare it with:

```bash
-e APP_ENV=development
```

The second form explicitly supplies the value.

Conceptually:

```text
export APP_ENV=development
       │
       │ host variable
       ▼
docker run -e APP_ENV
       │
       │ explicit forwarding
       ▼
Container APP_ENV=development
```

## 7.2 The critical rule

```text
Host environment
      ≠
Container environment
```

A host variable becomes container configuration only when the runtime invocation explicitly provides it.

---

# 8. Application Configuration

Docker can supply configuration, but the application still has to consume it.

Python provides two common mechanisms:

```python
os.getenv("KEY")
```

and:

```python
os.environ["KEY"]
```

Start with:

```python
import os

app_env = os.getenv("APP_ENV", "development")
log_level = os.getenv("LOG_LEVEL", "INFO")

print(f"Environment: {app_env}")
print(f"Log level: {log_level}")
```

If nothing is supplied, the application uses:

```text
Environment: development
Log level: INFO
```

If Docker supplies:

```bash
docker run \
  -e APP_ENV=production \
  -e LOG_LEVEL=warn \
  ...
```

the application sees:

```text
Environment: production
Log level: warn
```

---

## 8.1 `os.getenv()`

```python
value = os.getenv("APP_ENV")
```

If `APP_ENV` does not exist, the result is:

```python
None
```

You can provide a default:

```python
value = os.getenv("APP_ENV", "development")
```

If the variable is absent:

```python
value == "development"
```

---

## 8.2 `os.environ[]`

```python
value = os.environ["DATABASE_HOST"]
```

This expects the variable to exist.

If it is missing, Python raises a `KeyError`.

That behavior can be useful for mandatory configuration because the application fails immediately instead of continuing with an invalid or incomplete configuration.

---

# 9. Required vs Optional Configuration

A professional application should distinguish between configuration that is optional and configuration that is required.

## 9.1 Optional configuration

For example:

```text
LOG_LEVEL
```

may reasonably default to:

```text
INFO
```

Python:

```python
log_level = os.getenv("LOG_LEVEL", "INFO")
```

## 9.2 Required configuration

A database connection may require:

```text
DATABASE_HOST
DATABASE_USER
DATABASE_PASSWORD
```

You may deliberately fail if one is absent:

```python
import os

database_host = os.environ["DATABASE_HOST"]
database_user = os.environ["DATABASE_USER"]
database_password = os.environ["DATABASE_PASSWORD"]
```

Or validate explicitly:

```python
import os

database_host = os.getenv("DATABASE_HOST")

if not database_host:
    raise RuntimeError("DATABASE_HOST is required")
```

The distinction is:

```text
Missing but acceptable
        vs
Missing and invalid
```

This matters because silent fallback can produce confusing behavior.

---

# 10. Data Types and Environment Variables

Environment variables should be treated as strings.

For example:

```text
PORT=5432
DEBUG=false
WORKERS=4
TIMEOUT=30
```

These are textual values.

Python must convert them when the application needs native types.

```python
import os

port = int(os.getenv("PORT", "8080"))
workers = int(os.getenv("WORKERS", "4"))
timeout = int(os.getenv("TIMEOUT", "30"))
```

For booleans:

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

Now:

```text
DEBUG=true
```

becomes:

```python
True
```

and:

```text
DEBUG=false
```

becomes:

```python
False
```

## 10.1 Why boolean parsing matters

Do not assume this:

```python
bool("false")
```

means:

```python
False
```

It does not. A non-empty string is truthy in Python.

Therefore:

```python
bool("false")
```

evaluates to:

```python
True
```

This is an easy configuration bug.

## 10.2 Validate numeric configuration

Do not allow invalid values to fail much later.

```python
import os

port_raw = os.getenv("DATABASE_PORT", "5432")

try:
    database_port = int(port_raw)
except ValueError as exc:
    raise RuntimeError(
        "DATABASE_PORT must be an integer"
    ) from exc
```

The application now fails with a configuration-specific error.

---

# 11. Configuring Data Engineering Services

This topic is not intended to reteach PostgreSQL, MinIO, Redis, or Kafka.

The goal is to understand:

> **How environment variables configure containerized Data Engineering services.**

The important pattern is:

```text
Docker environment variables
          ↓
Image/application startup behavior
          ↓
Service behavior
```

Common services in the lab environment include:

- PostgreSQL
- MinIO
- Redis
- Kafka

A crucial distinction:

> Docker does not define the meaning of every environment variable.

Many variables are **application/image-specific conventions**.

For example:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

have meaning because the PostgreSQL image's startup behavior recognizes them.

They are not universal Docker variables.

---

# 12. PostgreSQL Configuration

PostgreSQL is the primary configuration example because it clearly demonstrates the relationship between runtime configuration and initialization.

A common container startup pattern is:

```bash
docker run -d \
  --name postgres \
  -e POSTGRES_DB=analytics \
  -e POSTGRES_USER=analytics_user \
  -e POSTGRES_PASSWORD=dev_password \
  postgres
```

These values are conventions provided by the PostgreSQL image.

Conceptually:

```text
Docker environment
        │
        ▼
PostgreSQL image startup logic
        │
        ▼
Database initialization behavior
```

## 12.1 What the variables represent

| Variable | Purpose |
|---|---|
| `POSTGRES_DB` | Database name used by the image during initialization |
| `POSTGRES_USER` | Initial database user |
| `POSTGRES_PASSWORD` | Password associated with the initialization user |

These names should not be interpreted as universal Docker settings.

They are PostgreSQL image/application conventions.

## 12.2 Verify configuration

For a running container:

```bash
docker exec postgres printenv
```

Or inspect the container:

```bash
docker inspect postgres
```

Avoid printing credentials in shared terminals, logs, screenshots, or reports.

---

# 13. Initialization vs Runtime Configuration

This distinction is critical.

Some configuration is consumed during the **first initialization** of a service.

Other configuration is consumed every time the application starts.

PostgreSQL makes this distinction especially visible.

Suppose:

```text
POSTGRES_DB=analytics
```

is supplied when PostgreSQL initializes an empty data directory.

The database state is then persisted.

Later, you change:

```text
POSTGRES_DB=warehouse
```

and restart the same PostgreSQL container with the existing persistent data.

Do not automatically expect the existing database state to be recreated as `warehouse`.

The important model is:

```text
Environment configuration
        +
Persistent volume
        ↓
Observed application behavior
```

The environment variable may have an initialization-time role, while the persistent database state already exists.

### Key lesson

> **Changing an environment variable is not the same thing as changing already-persisted application state.**

This is why configuration and persistence must be reasoned about separately.

---

# 14. MinIO Configuration

MinIO is another useful example.

A containerized MinIO deployment can receive configuration through environment variables for values such as:

- root username
- root password
- relevant runtime settings

The exact variable names depend on the image/version and its documented startup contract, so always verify the image documentation for the version being used.

The conceptual flow is:

```text
Environment variables
        ↓
MinIO startup
        ↓
MinIO runtime configuration
        ↓
Object-storage service behavior
```

Do not confuse:

```text
API credentials
```

with:

```text
container port
```

They are different configuration concerns.

A credential tells the application **who is authenticating**.

A port tells the network stack **where a service is listening**.

The networking mechanics belong to Topic 03; here we care about the configuration value being supplied.

---

# 15. Redis Configuration

Redis is often simpler than PostgreSQL or Kafka.

Configuration may be supplied:

- to the Redis container itself, where supported by the image/startup contract,
- or to a client application connecting to Redis.

For example, a Python client might receive:

```text
REDIS_HOST=redis
REDIS_PORT=6379
```

and consume them as:

```python
import os

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
```

The important lesson is not Redis command syntax.

It is:

```text
Containerized service
        ↑
Runtime configuration
        ↑
Application/client reads configuration
```

---

# 16. Kafka Configuration

Kafka has more configuration than a simple service.

In this module, focus only on how configuration values are supplied to a containerized Kafka service.

Examples of configuration concerns include:

- broker settings
- listener-related settings
- advertised address settings

A Kafka deployment may use environment variables to represent configuration consumed by the particular Kafka image/distribution.

The exact variable naming conventions differ between Kafka container images.

Therefore:

> **Always treat Kafka environment-variable names as image/application-specific configuration, not as universal Docker variables.**

Topic 03 covers Kafka listener/networking behavior in depth.

Here, the relevant mental model is:

```text
Environment variable
        ↓
Kafka container startup configuration
        ↓
Broker behavior
```

The objective is to understand how configuration is supplied, not to repeat the complete Kafka networking curriculum.

---

# 17. Environment-Specific Configuration

A major reason runtime configuration exists is to allow the same application to operate in multiple environments.

Consider:

```text
Development
DATABASE_HOST=localhost
LOG_LEVEL=debug

Testing
DATABASE_HOST=test-postgres
LOG_LEVEL=info

Production
DATABASE_HOST=prod-postgres
LOG_LEVEL=warn
```

The application can remain the same.

Only the runtime configuration changes.

```text
Same application
+
different runtime configuration
=
different environment behavior
```

This is especially useful in Data Engineering because pipelines frequently move between:

```text
local development
        ↓
integration testing
        ↓
staging
        ↓
production
```

The code and image should be as reusable as possible.

---

# 18. Configuration Defaults

Defaults are useful when a setting has a safe, predictable fallback.

Example:

```python
import os

log_level = os.getenv("LOG_LEVEL", "INFO")
```

If the user does not provide `LOG_LEVEL`, the application uses:

```text
INFO
```

## Good default

```python
log_level = os.getenv("LOG_LEVEL", "INFO")
```

Logging has a reasonable default.

## Dangerous default

Avoid:

```python
password = os.getenv("DB_PASSWORD", "password123")
```

when a database credential is mandatory.

A better pattern is:

```python
password = os.environ["DB_PASSWORD"]
```

or explicit validation:

```python
password = os.getenv("DB_PASSWORD")

if not password:
    raise RuntimeError("DB_PASSWORD is required")
```

The rule is:

> **Use defaults when they are safe and meaningful; require explicit configuration when silent fallback could be unsafe or invalid.**

---

# 19. Configuration Validation

Configuration should be validated as early as practical.

For example:

```python
import os

database_host = os.getenv("DATABASE_HOST")

if not database_host:
    raise RuntimeError("DATABASE_HOST is required")
```

Numeric validation:

```python
import os

port_raw = os.getenv("DATABASE_PORT", "5432")

try:
    database_port = int(port_raw)
except ValueError as exc:
    raise RuntimeError(
        "DATABASE_PORT must be an integer"
    ) from exc
```

You can also validate ranges:

```python
if not 1 <= database_port <= 65535:
    raise RuntimeError("DATABASE_PORT must be between 1 and 65535")
```

The benefit is early failure.

Without validation:

```text
Container starts
    ↓
Application starts
    ↓
Later database operation fails
    ↓
Confusing connection error
```

With validation:

```text
Container starts
    ↓
Application reads configuration
    ↓
Configuration validation
    ↓
Clear error
```

This is much easier to diagnose.

---

# 20. Environment Variable Naming

Use clear, consistent names.

For example:

```text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD

MINIO_ENDPOINT
MINIO_ACCESS_KEY
MINIO_SECRET_KEY

APP_ENV
LOG_LEVEL
```

Good naming practices include:

1. Use descriptive names.
2. Use a consistent convention.
3. Use related prefixes.
4. Avoid ambiguous names.
5. Avoid accidental collisions.

Uppercase names with underscores are a common convention:

```text
DATABASE_HOST
```

but uppercase is not technically mandatory.

A name should communicate what it means.

Compare:

```text
HOST
```

with:

```text
DATABASE_HOST
```

The second is much clearer in an environment containing many services.

---

# 21. Inspecting Runtime Configuration

Do not guess what a container received.

Inspect it.

## 21.1 Inspect container metadata

```bash
docker inspect <container>
```

This can show the container configuration Docker knows about.

## 21.2 Inspect the environment from inside the container

```bash
docker exec <container> env
```

or:

```bash
docker exec <container> printenv
```

You can inspect one value:

```bash
docker exec <container> printenv APP_ENV
```

The distinction is useful:

```text
docker inspect
    ↓
Docker/container configuration metadata

docker exec ... env
    ↓
Environment visible to a process inside the container
```

When troubleshooting, inspect the actual runtime state instead of assuming the intended configuration was successfully supplied.

### Security warning

Do not casually run:

```bash
docker exec <container> env
```

on a screen recording or shared support session if the environment contains credentials.

Inspection is powerful, but it can expose sensitive values.

---

# 22. Security and Environment Variables

## 22.1 Environment variables are not a secret vault

A professional mental model is:

```text
Configuration
     ≠
Secrets management
```

Environment variables are a configuration transport mechanism.

They can be convenient for development and many runtime settings, but sensitive values can potentially become visible through:

- shell history
- command lines
- Docker inspection
- process/container inspection
- logs
- debugging output
- source code
- accidental printing

Therefore:

> **Do not automatically treat an environment variable as a secure secret-management system.**

More secure secret mechanisms exist, but implementing a complete secrets-management platform is outside this topic.

## 22.2 Never use real credentials in learning examples

Use clearly fake development-only values such as:

```text
dev_password
local_only_password
example_secret
```

Do not place real credentials into:

- Markdown files
- Git repositories
- screenshots
- terminal recordings
- logs
- examples

---

# 23. Do Not Print Secrets

This is bad debugging:

```python
import os

print(os.environ)
```

It can expose everything available to the process.

A safer diagnostic pattern is:

```python
import os

print({
    "APP_ENV": os.getenv("APP_ENV"),
    "DATABASE_HOST": os.getenv("DATABASE_HOST"),
})
```

Even then, make sure the selected values are non-sensitive.

If you need to confirm that a credential exists, report presence rather than its value:

```python
import os

print({
    "DATABASE_PASSWORD_CONFIGURED":
        bool(os.getenv("DATABASE_PASSWORD"))
})
```

The output might be:

```text
{'DATABASE_PASSWORD_CONFIGURED': True}
```

instead of exposing the password.

---

# 24. Shell Expansion and Quoting

Shell behavior matters when passing environment variables to Docker.

Suppose:

```bash
export APP_ENV=development
```

You can explicitly pass it:

```bash
docker run \
  -e APP_ENV="$APP_ENV" \
  alpine
```

The shell expands:

```text
"$APP_ENV"
```

before Docker receives the final argument.

Compare:

```bash
-e APP_ENV=development
```

with:

```bash
-e APP_ENV="$APP_ENV"
```

The first supplies a literal value.

The second reads the value from the current shell environment.

## 24.1 Why quoting matters

Suppose:

```bash
export APP_MESSAGE="hello data engineering"
```

Use:

```bash
docker run \
  -e APP_MESSAGE="$APP_MESSAGE" \
  alpine
```

Quoting protects the value from being split by normal shell word parsing.

Be especially careful with:

- spaces
- quotes
- `$`
- shell metacharacters
- empty values
- values that contain shell-sensitive characters

The important mental model is:

```text
Shell parsing
      ↓
Docker CLI receives arguments
      ↓
Docker starts container
      ↓
Application reads environment
```

Docker does not perform the same shell expansion that your host shell performs.

---

# 25. Configuration Precedence

Applications can receive configuration from several sources.

A useful conceptual model is:

```text
Application defaults
        ↓
Image-defined defaults
        ↓
Runtime environment
        ↓
Application command-line configuration
```

However, do not treat this as a universal Docker precedence specification.

There are two different questions:

### Docker question

What configuration does the Docker runtime provide to the container?

### Application question

When the application has several configuration sources, which source does the application prefer?

These are not the same thing.

For example:

```text
Docker runtime
    └── provides APP_PORT=8080

Application
    ├── has internal default 5000
    ├── reads APP_PORT=8080
    └── may also accept --port
```

The final behavior depends on the application's own configuration design.

Therefore:

> **Always distinguish Docker runtime behavior from application-specific configuration precedence.**

---

# 26. Image Defaults and Runtime Configuration

An image can contain default environment configuration.

Conceptually:

```text
Image
 └── default configuration
          ↓
Container runtime
 └── runtime configuration can influence behavior
```

The important idea is that an image can provide a baseline while runtime configuration supplies environment-specific values.

This module does not teach Dockerfile authoring.

It does not cover:

- Dockerfile syntax
- image building
- multi-stage builds
- image optimization
- advanced BuildKit

Those belong to other curriculum areas.

You only need the conceptual model:

> **An image can provide defaults; runtime configuration can influence how the resulting container behaves.**

---

# 27. Configuration vs Command Arguments

Applications may receive configuration through different mechanisms.

For example:

```text
APP_PORT=8080
```

could be supplied through an environment variable.

Another application may support:

```bash
--port 8080
```

as a command-line argument.

Conceptually:

```text
Environment variable
        ↓
Application configuration input

Command-line argument
        ↓
Application configuration input
```

These mechanisms are not identical.

The application decides how to interpret them and, when multiple mechanisms exist, which one takes precedence.

For this module, the important lesson is simply:

> **Configuration can enter an application through more than one channel.**

---

# 28. Configuration vs Volumes

Topic 04 covered storage and persistence.

Keep these concepts separate.

## Environment variable

Usually provides:

```text
configuration value
```

For example:

```text
DATABASE_HOST
DATABASE_USER
DATABASE_PASSWORD
```

## Volume

Provides:

```text
persistent filesystem data
```

For example:

```text
/var/lib/postgresql/data
```

The difference:

```text
DATABASE_HOST
DATABASE_USER
DATABASE_PASSWORD
        │
        └── configuration

/var/lib/postgresql/data
        │
        └── persistent application data
```

A volume stores application state.

An environment variable tells the application how to behave or where to connect.

### Critical rule

```text
Configuration
      ≠
Persistent application data
```

---

# 29. Configuration vs Networking

Suppose a Python application receives:

```text
DATABASE_HOST=postgres
DATABASE_PORT=5432
```

Those are configuration values.

But whether:

```text
postgres:5432
```

is actually reachable depends on networking.

The relationship is:

```text
Configuration
      +
Networking
      =
Successful connection
```

Therefore, these are different failure categories.

### Wrong configuration

```text
DATABASE_HOST=wrong-service
```

### Network failure

```text
DATABASE_HOST=postgres
```

but the network path to `postgres:5432` is unavailable.

This distinction prevents wasted troubleshooting.

If the hostname is wrong, changing Docker networking may not solve the problem.

If the hostname is correct but the service is unreachable, changing the environment variable may not solve the problem.

---

# 30. Configuration and Persistent Data

PostgreSQL demonstrates why configuration and persistent state must be considered together.

Conceptually:

```text
Container configuration
        +
Persistent volume
        ↓
Application state
```

Suppose an initialized PostgreSQL volume already contains database state.

You then change:

```text
POSTGRES_DB
```

Changing the environment variable does not automatically erase, recreate, or transform the existing database state.

The observed behavior depends on:

1. what configuration the image consumes,
2. when it consumes it,
3. whether the data directory is empty,
4. what persistent state already exists.

The operational lesson is:

> **Always ask whether a configuration value is initialization-time configuration, runtime configuration, or both.**

---

# 31. Hands-On Data Engineering Lab

## Lab objective

Build a configurable PostgreSQL + Python client environment.

You will:

1. provide PostgreSQL initialization configuration,
2. inspect it,
3. connect to PostgreSQL,
4. create test data,
5. build a Python configuration reader,
6. run the Python application in a container,
7. pass configuration through Docker,
8. change configuration without changing the image,
9. demonstrate missing configuration,
10. demonstrate invalid numeric configuration,
11. demonstrate a safe default,
12. demonstrate safe debugging without printing secrets.

---

## 31.1 Prerequisites

Verify Docker:

```bash
docker --version
```

Check that Docker is running:

```bash
docker info
```

You should have a working Docker environment.

---

## 31.2 Step 1 — Start PostgreSQL

Use clearly fake development credentials:

```bash
docker run -d \
  --name postgres-config-lab \
  -e POSTGRES_DB=analytics \
  -e POSTGRES_USER=analytics_user \
  -e POSTGRES_PASSWORD=dev_password \
  -p 127.0.0.1:5432:5432 \
  postgres:16
```

The important configuration values are:

```text
POSTGRES_DB=analytics
POSTGRES_USER=analytics_user
POSTGRES_PASSWORD=dev_password
```

---

## 31.3 Step 2 — Inspect the configuration

Inspect metadata:

```bash
docker inspect postgres-config-lab
```

Inspect the environment from inside:

```bash
docker exec postgres-config-lab printenv
```

For a focused check:

```bash
docker exec postgres-config-lab printenv POSTGRES_DB
```

Expected:

```text
analytics
```

Do not paste the full environment into a public report because it may contain credentials.

---

## 31.4 Step 3 — Connect with `psql`

If the PostgreSQL client is installed on your host:

```bash
psql \
  -h 127.0.0.1 \
  -p 5432 \
  -U analytics_user \
  -d analytics
```

Enter the fake development password when prompted.

Alternatively, use a client environment appropriate to your Docker lab.

---

## 31.5 Step 4 — Create test data

Inside PostgreSQL:

```sql
CREATE TABLE pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL
);
```

Insert test data:

```sql
INSERT INTO pipeline_runs (pipeline_name, status)
VALUES
    ('daily_orders', 'success'),
    ('customer_snapshot', 'success'),
    ('inventory_refresh', 'running');
```

Verify:

```sql
SELECT * FROM pipeline_runs;
```

This proves the service is usable; the learning objective remains configuration.

---

## 31.6 Step 5 — Write a Python configuration reader

Example:

```python
import os

host = os.environ["DATABASE_HOST"]
port = int(os.getenv("DATABASE_PORT", "5432"))
database = os.environ["DATABASE_NAME"]
user = os.environ["DATABASE_USER"]

print(f"Database host: {host}")
print(f"Database port: {port}")
print(f"Database name: {database}")
print(f"Database user: {user}")
```

Notice that the password is intentionally not printed.

---

## 31.7 Step 6 — Run the application in a container

A lightweight demonstration can use Python directly:

```bash
docker run --rm \
  -e DATABASE_HOST=postgres \
  -e DATABASE_PORT=5432 \
  -e DATABASE_NAME=analytics \
  -e DATABASE_USER=analytics_user \
  python:3.12 \
  python -c 'import os; print(os.environ["DATABASE_HOST"]); print(int(os.getenv("DATABASE_PORT", "5432"))); print(os.environ["DATABASE_NAME"]); print(os.environ["DATABASE_USER"])'
```

If the Python container is not on the same Docker network as PostgreSQL, the hostname `postgres` will not necessarily be reachable.

That is intentional: this demonstrates why configuration and networking are separate concerns.

---

## 31.8 Step 7 — Pass configuration through Docker

You can configure a generic Python application with:

```bash
docker run --rm \
  -e DATABASE_HOST=postgres \
  -e DATABASE_PORT=5432 \
  -e DATABASE_NAME=analytics \
  -e DATABASE_USER=analytics_user \
  python:3.12 \
  python -c 'import os; print("host=", os.environ["DATABASE_HOST"]); print("port=", int(os.getenv("DATABASE_PORT", "5432"))); print("database=", os.environ["DATABASE_NAME"]); print("user=", os.environ["DATABASE_USER"])'
```

The same image can receive different values:

```bash
docker run --rm \
  -e DATABASE_HOST=test-postgres \
  -e DATABASE_PORT=5432 \
  -e DATABASE_NAME=test_analytics \
  -e DATABASE_USER=test_user \
  python:3.12 \
  python -c 'import os; print(os.environ["DATABASE_HOST"]); print(os.environ["DATABASE_NAME"])'
```

No image rebuild is required.

---

## 31.9 Step 8 — Change configuration without changing the image

Run the same Python image twice.

Development:

```bash
docker run --rm \
  -e APP_ENV=development \
  -e LOG_LEVEL=debug \
  python:3.12 \
  python -c 'import os; print(os.getenv("APP_ENV")); print(os.getenv("LOG_LEVEL"))'
```

Production-like:

```bash
docker run --rm \
  -e APP_ENV=production \
  -e LOG_LEVEL=warn \
  python:3.12 \
  python -c 'import os; print(os.getenv("APP_ENV")); print(os.getenv("LOG_LEVEL"))'
```

The image remains the same.

The runtime configuration changes.

---

## 31.10 Step 9 — Demonstrate missing required configuration

Run:

```bash
docker run --rm \
  python:3.12 \
  python -c 'import os; print(os.environ["DATABASE_HOST"])'
```

You should see a `KeyError`.

This is an example of explicit required configuration.

---

## 31.11 Step 10 — Demonstrate invalid numeric configuration

Run:

```bash
docker run --rm \
  -e DATABASE_PORT=abc \
  python:3.12 \
  python -c 'import os; print(int(os.environ["DATABASE_PORT"]))'
```

The application should fail because:

```text
abc
```

cannot be converted into an integer.

A production application should turn this into a clear configuration error.

---

## 31.12 Step 11 — Demonstrate a safe default

Run:

```bash
docker run --rm \
  python:3.12 \
  python -c 'import os; print(os.getenv("LOG_LEVEL", "INFO"))'
```

Expected:

```text
INFO
```

This is a good example of a safe default.

---

## 31.13 Step 12 — Demonstrate safe secret debugging

Instead of:

```python
print(os.environ)
```

use:

```python
import os

print({
    "APP_ENV": os.getenv("APP_ENV"),
    "DATABASE_HOST": os.getenv("DATABASE_HOST"),
    "DATABASE_PASSWORD_CONFIGURED":
        bool(os.getenv("DATABASE_PASSWORD"))
})
```

This tells you whether a password was configured without displaying it.

---

# 32. Break/Fix Configuration Lab

Use the following exercises deliberately.

For every failure, follow:

```text
Symptom
   ↓
Hypothesis
   ↓
Inspection
   ↓
Root Cause
   ↓
Fix
   ↓
Verification
```

---

## Failure 1 — Missing `DATABASE_HOST`

### Symptom

The application raises:

```text
KeyError: 'DATABASE_HOST'
```

### Hypothesis

The required environment variable was not supplied.

### Inspection

Check the container environment:

```bash
docker exec <container> printenv DATABASE_HOST
```

### Root cause

The variable was never injected.

### Fix

Supply it:

```bash
-e DATABASE_HOST=postgres
```

### Verification

```bash
docker exec <container> printenv DATABASE_HOST
```

---

## Failure 2 — Wrong database hostname

Configuration:

```text
DATABASE_HOST=wrong-postgres
```

### Symptom

The application cannot connect.

### Hypothesis

The hostname may be wrong.

### Inspection

Verify:

```bash
docker exec <container> printenv DATABASE_HOST
```

Then reason about whether that hostname exists and is reachable on the relevant Docker network.

### Root cause

Configuration points to the wrong service name.

### Fix

Use the correct service hostname.

### Verification

Test the connection after correcting the configuration.

---

## Failure 3 — Wrong database port

Configuration:

```text
DATABASE_PORT=9999
```

### Symptom

Connection fails.

### Hypothesis

The application has the wrong port.

### Inspection

```bash
docker exec <container> printenv DATABASE_PORT
```

### Root cause

Incorrect runtime configuration.

### Fix

Supply the correct port.

### Verification

Retry the connection.

---

## Failure 4 — Wrong database name

Configuration:

```text
DATABASE_NAME=wrong_database
```

### Symptom

The PostgreSQL server may be reachable, but the requested database does not exist.

### Important distinction

This is not necessarily a networking failure.

The server may be reachable while the selected database is wrong.

### Fix

Correct:

```text
DATABASE_NAME
```

and verify.

---

## Failure 5 — Missing PostgreSQL initialization variable

Suppose you expect:

```text
POSTGRES_DB=analytics
```

to create or select a database, but the existing PostgreSQL data directory has already been initialized.

### Hypothesis

The learner may be confusing initialization configuration with current persistent state.

### Inspection

Check the configuration and the existing database state.

### Root cause

Initialization-time settings do not automatically recreate existing persistent database state.

### Fix

Reason about whether the desired change is:

- runtime configuration,
- initialization,
- or persistent application-state management.

Do not delete persistent data casually.

---

## Failure 6 — Invalid integer

Configuration:

```text
DATABASE_PORT=abc
```

### Symptom

Integer conversion fails.

### Fix

Supply a numeric value:

```text
DATABASE_PORT=5432
```

### Better application behavior

Validate the value at startup and report:

```text
DATABASE_PORT must be an integer
```

rather than allowing an obscure downstream failure.

---

## Failure 7 — Incorrect boolean parsing

Bad pattern:

```python
debug = bool(os.getenv("DEBUG"))
```

If:

```text
DEBUG=false
```

the string is non-empty, so Python treats it as truthy.

A safer simple pattern is:

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

### Professional takeaway

Boolean configuration needs explicit parsing semantics.

---

## Failure 8 — Host variable not passed into container

Host:

```bash
export APP_ENV=development
```

Then:

```bash
docker run alpine printenv APP_ENV
```

If the value is absent, the host variable was not automatically forwarded.

### Fix

```bash
docker run \
  -e APP_ENV \
  alpine \
  printenv APP_ENV
```

---

## Failure 9 — Spaces or special characters passed incorrectly

Suppose:

```bash
export APP_MESSAGE="hello data engineering"
```

Use:

```bash
docker run \
  -e APP_MESSAGE="$APP_MESSAGE" \
  alpine \
  printenv APP_MESSAGE
```

Verify the complete value.

---

## Failure 10 — Credentials printed during debugging

Bad:

```python
print(os.environ)
```

### Root cause

The developer chose maximum diagnostic visibility without considering data exposure.

### Fix

Print only safe fields:

```python
print({
    "APP_ENV": os.getenv("APP_ENV"),
    "DATABASE_HOST": os.getenv("DATABASE_HOST"),
    "DATABASE_PASSWORD_CONFIGURED":
        bool(os.getenv("DATABASE_PASSWORD"))
})
```

### Verification

No credential value should appear in output.

---

# 33. Real-World Data Engineering Scenarios

## Scenario 1 — Same image, different environments

A pipeline service connects to PostgreSQL in development, testing, and production.

### Questions

Should the image change?

**Normally, no.**

What should change?

**Runtime configuration.**

Examples:

```text
Development:
DATABASE_HOST=localhost
LOG_LEVEL=debug

Testing:
DATABASE_HOST=test-postgres
LOG_LEVEL=info

Production:
DATABASE_HOST=prod-postgres
LOG_LEVEL=warn
```

The application image remains reusable.

---

## Scenario 2 — PostgreSQL credentials in Python source

A developer writes:

```python
username = "analytics_user"
password = "real-password"
host = "production-db"
```

### Why is this problematic?

Because configuration is now coupled to source code.

This can cause:

- accidental credential commits,
- difficult environment changes,
- code/image rebuilds for configuration changes,
- poor separation of application and deployment concerns.

A better conceptual design is:

```text
Source code
    ↓
expects configuration

Runtime
    ↓
provides configuration
```

For sensitive production credentials, environment variables should not automatically be considered the final security mechanism; a proper secret-management solution may be appropriate.

---

## Scenario 3 — Missing configuration

A pipeline container starts successfully but fails when connecting to PostgreSQL.

The application may be missing:

```text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
```

### Diagnosis

First inspect the configuration:

```bash
docker exec <container> printenv DATABASE_HOST
docker exec <container> printenv DATABASE_PORT
docker exec <container> printenv DATABASE_NAME
docker exec <container> printenv DATABASE_USER
```

Then determine whether the failure is:

```text
missing configuration
```

or:

```text
incorrect configuration
```

or:

```text
network reachability
```

Do not jump directly to changing the network.

---

## Scenario 4 — Wrong hostname: `localhost`

Suppose a Python application inside a container uses:

```text
DATABASE_HOST=localhost
```

and PostgreSQL is running in a different container.

The conceptual issue is that:

```text
localhost
```

inside the application container refers to that container's own network namespace, not automatically to the PostgreSQL container.

The relevant hostname in a user-defined Docker network may instead be the PostgreSQL container/service name.

This connects to Topic 03:

```text
Configuration:
DATABASE_HOST=postgres

Networking:
Can this container reach postgres:5432?
```

Both must be correct.

---

## Scenario 5 — Persistent PostgreSQL database

The learner changes:

```text
POSTGRES_DB
```

but the PostgreSQL volume already contains initialized data.

They expect the database state to change immediately.

### Why this can fail

The image's initialization behavior may only use that variable when the data directory is empty.

The existing persistent state remains.

### Lesson

```text
Runtime configuration
        +
Persistent state
        ↓
Actual behavior
```

Changing configuration does not automatically rewrite persistent state.

---

# 34. Configuration Design Principles

## Principle 1 — Keep configuration outside application code when appropriate

Prefer:

```python
database_host = os.environ["DATABASE_HOST"]
```

over hard-coding:

```python
database_host = "production-db"
```

This makes the application reusable.

---

## Principle 2 — Make required configuration explicit

If an application cannot work without:

```text
DATABASE_HOST
```

fail clearly when it is absent.

---

## Principle 3 — Provide safe defaults where appropriate

For example:

```python
log_level = os.getenv("LOG_LEVEL", "INFO")
```

Avoid unsafe defaults for mandatory credentials.

---

## Principle 4 — Validate configuration early

Convert and validate:

```text
DATABASE_PORT
WORKERS
TIMEOUT
```

before the application performs expensive work.

---

## Principle 5 — Use consistent naming

Prefer:

```text
DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
```

over vague names such as:

```text
HOST
PORT
NAME
```

---

## Principle 6 — Do not print secrets

Never use:

```python
print(os.environ)
```

as a routine debugging strategy.

---

## Principle 7 — Do not commit credentials to source control

Do not put real credentials in:

- Python files,
- Markdown files,
- shell scripts,
- Git repositories,
- Docker commands committed to source,
- documentation examples.

---

## Principle 8 — Separate development credentials from real credentials

A learning lab can use:

```text
dev_password
```

A real production environment should use its approved credential mechanism.

---

## Principle 9 — Inspect actual runtime configuration when debugging

Do not assume the configuration you intended to pass is the configuration the application received.

---

## Principle 10 — Keep configuration separate from persistent application state

```text
DATABASE_NAME
```

is configuration.

```text
/var/lib/postgresql/data
```

is persistent state.

They interact, but they are not the same thing.

---

## Principle 11 — Keep configuration separate from network reachability

```text
DATABASE_HOST=postgres
```

does not prove that:

```text
postgres:5432
```

is reachable.

---

## Principle 12 — Prefer reproducible runtime configuration

A team should be able to explain:

```text
Which image?
Which configuration?
Which environment?
Which services?
```

without relying on undocumented manual changes.

---

# 35. Common Mistakes

## 1. Assuming host variables automatically enter containers

**Why it happens:** The learner thinks the container is simply another shell process.

**Avoid it:** Explicitly pass required values with `-e`.

---

## 2. Forgetting `-e`

**Symptom:** Application reports missing configuration.

**Fix:**

```bash
-e KEY=value
```

---

## 3. Using the wrong variable name

For example:

```text
DATABASE_HOSTNAME
```

when the application expects:

```text
DATABASE_HOST
```

Environment variables are names. A nearly-correct name is still wrong.

---

## 4. Typographical errors

```text
DATABSE_HOST
```

instead of:

```text
DATABASE_HOST
```

Inspect the actual environment.

---

## 5. Treating all values as native booleans or numbers

This is wrong:

```python
debug = bool(os.getenv("DEBUG"))
```

Use explicit parsing.

---

## 6. Forgetting string-to-number conversion

This:

```python
port = os.getenv("PORT")
```

produces text.

If arithmetic or a numeric API is required:

```python
port = int(port)
```

with validation.

---

## 7. Using unsafe default credentials

Avoid:

```python
password = os.getenv("DB_PASSWORD", "password123")
```

for mandatory credentials.

---

## 8. Printing the entire environment

Avoid:

```python
print(os.environ)
```

It can expose sensitive configuration.

---

## 9. Hard-coding credentials

Do not embed real credentials in application source code.

---

## 10. Confusing configuration with networking

A correct:

```text
DATABASE_HOST
```

does not guarantee network reachability.

---

## 11. Confusing configuration with persistence

A configuration value does not represent a persistent data directory.

---

## 12. Assuming configuration changes rewrite database state

Initialization-time settings may not affect an already-initialized persistent database.

---

## 13. Using `localhost` incorrectly

Inside a container:

```text
localhost
```

usually refers to that container itself.

It is not automatically another container.

---

## 14. Passing shell variables without understanding expansion

Understand the difference between:

```bash
-e KEY=value
```

and:

```bash
-e KEY="$KEY"
```

---

## 15. Assuming Docker environment variables have universal meaning

For example:

```text
POSTGRES_DB
```

has meaning because of the PostgreSQL image/application contract.

Docker itself does not universally define it.

---

## 16. Forgetting that many environment variables are image/application-specific conventions

Always consult the documentation for the exact image/version when a service expects particular variables.

---

# 36. Mental Models

## Mental Model 1 — Image = Application Template

```text
Image
=
Application template
```

The image contains the application environment needed to run it.

---

## Mental Model 2 — Environment Variable = Runtime Configuration Input

```text
Environment variable
=
Runtime configuration input
```

It gives the application information at runtime.

---

## Mental Model 3 — Host Environment ≠ Container Environment

```text
Host environment
      ≠
Container environment
```

Explicit injection creates the relationship.

---

## Mental Model 4 — Configuration ≠ Persistent Application Data

```text
DATABASE_HOST
DATABASE_USER
DATABASE_PASSWORD
      │
      └── configuration

/var/lib/postgresql/data
      │
      └── persistent state
```

---

## Mental Model 5 — Configuration ≠ Network Connectivity

```text
DATABASE_HOST=postgres
```

tells the application where it expects the service.

It does not guarantee that the service is reachable.

---

## Mental Model 6 — Persistence ≠ Configuration

```text
Persistence
=
keeping application state

Configuration
=
telling the application how to behave
```

---

## Mental Model 7 — Same Image + Different Runtime Configuration

```text
Same image
     +
different runtime configuration
     =
different environment behavior
```

This is one of the most important containerization principles.

---

## Mental Model 8 — Configuration Lifecycle

```text
Configuration supplied
        ↓
Application reads it
        ↓
Application validates it
        ↓
Application behaves accordingly
```

A robust application makes each step explicit.

---

# 37. ASCII Diagrams

## Docker environment injection

```text
                    Docker Host
                         │
                         │ docker run -e
                         ▼
                 ┌───────────────┐
                 │   Container   │
                 │               │
                 │ APP_ENV=dev   │
                 │ DB_HOST=pg    │
                 │ DB_PORT=5432  │
                 │               │
                 │ Application   │
                 └───────────────┘
```

## Host-to-container flow

```text
Host Shell
    │
    │ environment
    ▼
Docker Runtime
    │
    │ inject
    ▼
Container Process
    │
    │ read
    ▼
Application
```

## Same image, different environments

```text
                    Same Image
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           Dev         Test       Production
             │           │           │
        runtime       runtime      runtime
       configuration configuration configuration
```

## Configuration plus other concerns

```text
             Runtime Configuration
                      │
                      ▼
                 Application
                  /        \
                 /          \
                ▼            ▼
          Network path    Persistent state
                │            │
                ▼            ▼
          Reachability     Existing data
```

A successful system requires the application to reason about all three independently.

---

# 38. Command Reference

| Command | Purpose | Example | Expected behavior | Warning |
|---|---|---|---|---|
| `export KEY=value` | Define a shell environment variable | `export APP_ENV=dev` | Shell can reference `APP_ENV` | Does not automatically inject it into containers |
| `echo "$KEY"` | Display a shell variable | `echo "$APP_ENV"` | Prints its value | Do not echo secrets |
| `docker run -e KEY=value image` | Supply explicit runtime environment | `docker run -e APP_ENV=dev alpine` | Container process sees `APP_ENV` | Value is visible as runtime configuration |
| `docker run --env KEY=value image` | Long form of `-e` | `docker run --env APP_ENV=dev alpine` | Same basic effect | Same security considerations |
| `docker run -e KEY image` | Forward current shell value | `docker run -e APP_ENV alpine` | Container receives current host value | Requires the host variable to exist as intended |
| `docker exec <container> env` | Inspect environment inside container | `docker exec env-demo env` | Prints process environment | May expose secrets |
| `docker exec <container> printenv` | Inspect environment | `docker exec env-demo printenv` | Prints variables | May expose secrets |
| `docker exec <container> printenv KEY` | Inspect one variable | `docker exec env-demo printenv APP_ENV` | Prints one value | Do not use on secret values in shared output |
| `docker inspect <container>` | Inspect Docker container metadata | `docker inspect postgres-config-lab` | Shows configuration details | Output can contain sensitive values |

---

# 39. Python Configuration Reference

## `os.getenv()`

```python
import os

value = os.getenv("KEY")
```

Returns `None` when the variable is absent.

## `os.getenv()` with a default

```python
value = os.getenv("KEY", "default")
```

Returns the configured value when present, otherwise the default.

## `os.environ[]`

```python
value = os.environ["KEY"]
```

Requires the variable to exist.

If it does not exist, Python raises `KeyError`.

### Comparison

| Expression | Missing variable |
|---|---|
| `os.getenv("KEY")` | `None` |
| `os.getenv("KEY", "default")` | `"default"` |
| `os.environ["KEY"]` | `KeyError` |

## Safe integer conversion

```python
port = int(os.getenv("PORT", "5432"))
```

For production-style validation:

```python
import os

port_raw = os.getenv("PORT", "5432")

try:
    port = int(port_raw)
except ValueError as exc:
    raise RuntimeError("PORT must be an integer") from exc

if not 1 <= port <= 65535:
    raise RuntimeError("PORT is outside the valid range")
```

## Simple boolean conversion

```python
debug = os.getenv("DEBUG", "false").lower() == "true"
```

If your application accepts additional forms such as `1`, `yes`, or `on`, define those semantics explicitly rather than relying on Python truthiness.

---

# 40. Practice Questions

## Beginner

1. What is an environment variable?
2. Why do applications need configuration?
3. What does `docker run -e` do?
4. Is a host environment variable automatically available inside a container?
5. What is the difference between a variable name and its value?
6. Why are environment variables fundamentally string values?

## Intermediate

1. What is the difference between `-e KEY=value` and `-e KEY`?
2. Why should environment variables generally be treated as strings?
3. How do you inspect a container's environment?
4. What is the difference between required and optional configuration?
5. Why should applications validate configuration at startup?
6. What is the difference between `os.getenv()` and `os.environ[]`?
7. Why can `bool(os.getenv("DEBUG"))` be dangerous?
8. Why is `DATABASE_HOST=postgres` configuration rather than proof of network connectivity?
9. Why can changing `POSTGRES_DB` fail to change an already-initialized PostgreSQL database?

## Advanced

1. Why should the same image be reusable across environments?
2. How can configuration and persistent state interact?
3. Why is `localhost` often incorrect as a database hostname inside a container?
4. Why are environment variables not automatically a complete secrets-management solution?
5. How would you design configuration for a PostgreSQL-based Data Engineering pipeline?
6. How would you diagnose an application that has the correct image but incorrect runtime behavior?
7. How would you separate a configuration problem from a networking problem?
8. How would you make configuration failures easy to diagnose?
9. Why should image-specific environment variables not be treated as universal Docker variables?
10. How would you safely inspect configuration without exposing credentials?

These questions test reasoning rather than command memorization.

---

# 41. Interview Practice

## 1. What are environment variables?

**Strong answer:**

Environment variables are named string values made available to a process. Applications can read them at runtime to obtain configuration such as environment names, service endpoints, ports, log levels, and other settings.

---

## 2. Why are environment variables useful in Docker?

**Strong answer:**

They allow the same container image to run with different runtime configuration. Instead of embedding environment-specific values into application code or rebuilding the image, Docker can provide configuration when the container starts.

---

## 3. How do you pass environment variables to a container?

**Strong answer:**

Use `docker run -e KEY=value image` or the equivalent `--env` form. A host variable can also be explicitly forwarded with `-e KEY`.

---

## 4. What is the difference between host and container environment variables?

**Strong answer:**

The host and container have separate process environments. A host variable does not automatically become a container variable. It must be explicitly provided to the container runtime.

---

## 5. How do applications read environment variables?

**Strong answer:**

The application uses its programming language's process-environment API. In Python, common mechanisms are `os.getenv()` and `os.environ[]`.

---

## 6. What is the difference between `os.getenv()` and `os.environ[]`?

**Strong answer:**

`os.getenv("KEY")` returns `None` if the key is missing, while `os.environ["KEY"]` raises `KeyError`. `os.getenv()` can also accept a default value.

---

## 7. How should required configuration be validated?

**Strong answer:**

Read the required values explicitly, validate that they exist, convert them to the expected types, and fail early with a clear configuration-specific error if they are missing or invalid.

---

## 8. Why are environment variables generally strings?

**Strong answer:**

The process environment is a string-based interface. Applications must interpret the text as integers, booleans, durations, URLs, or other types and validate those conversions.

---

## 9. How would you configure PostgreSQL using Docker environment variables?

**Strong answer:**

Use the environment variables defined by the PostgreSQL image's startup contract, such as `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`, while understanding that these are image/application-specific conventions and can have initialization-time semantics.

---

## 10. Why might changing `POSTGRES_DB` not change an already-initialized PostgreSQL database?

**Strong answer:**

Because the PostgreSQL image may use that variable during first initialization when the data directory is empty. If persistent data already exists, changing the environment variable does not automatically recreate or transform that existing state.

---

## 11. How do you inspect environment variables inside a running container?

**Strong answer:**

Use `docker exec <container> env`, `docker exec <container> printenv`, or inspect a specific variable with `printenv KEY`. `docker inspect` can also show container configuration metadata.

---

## 12. Why should secrets not be printed during debugging?

**Strong answer:**

Environment variables can contain sensitive credentials, and printing the entire environment can expose them through terminals, logs, recordings, support tickets, or monitoring systems. Diagnostics should reveal only the non-sensitive information required.

---

## 13. Why is configuration different from persistence?

**Strong answer:**

Configuration tells an application how to behave or where to connect. Persistent storage holds application state. An environment variable such as `DATABASE_HOST` is configuration, while PostgreSQL's data directory on a persistent volume contains database state.

---

## 14. Why is configuration different from networking?

**Strong answer:**

Configuration can tell an application to use `postgres:5432`, but networking determines whether that endpoint is actually reachable. Correct configuration and network reachability are separate requirements.

---

## 15. How would you design runtime configuration for development, testing, and production?

**Strong answer:**

Keep the application image consistent and supply environment-specific configuration at runtime. Required settings should be explicit and validated, optional settings should have safe defaults where appropriate, credentials should not be hard-coded, and diagnostics should avoid exposing secrets.

---

# 42. Final Knowledge Check

You should now be able to answer these questions in your own words:

1. What is configuration?
2. What is an environment variable?
3. How does Docker pass environment variables into containers?
4. Why does a host environment variable not automatically appear inside a container?
5. How does Python read environment variables?
6. Why should environment variables be treated as strings?
7. How do you validate required configuration?
8. How do PostgreSQL environment variables influence initialization?
9. Why is configuration different from persistent storage?
10. Why is configuration different from networking?
11. Why is configuration different from secrets management?
12. How can the same image run across multiple environments?
13. How do you inspect a container's actual runtime environment?
14. How would you troubleshoot a container whose application is receiving the wrong configuration?

A strong learner should be able to explain not only the commands, but the underlying reasoning.

---

# 43. Module Completion Checklist

Mark each item only when you can perform it without following a tutorial.

## Configuration fundamentals

- [ ] I can define configuration in simple terms.
- [ ] I understand hard-coded versus runtime configuration.
- [ ] I understand defaults and runtime values.
- [ ] I can explain why the same image should work across environments.

## Environment variables

- [ ] I understand names and values.
- [ ] I understand process environments.
- [ ] I can set a host variable with `export`.
- [ ] I can inspect it with `echo`.
- [ ] I understand that environment variables are strings.

## Docker

- [ ] I can use `docker run -e`.
- [ ] I can use `docker run --env`.
- [ ] I can pass multiple variables.
- [ ] I understand `-e KEY` versus `-e KEY=value`.
- [ ] I understand shell expansion and quoting.
- [ ] I can inspect a container's environment.

## Python

- [ ] I can use `os.getenv()`.
- [ ] I can use `os.getenv()` with a default.
- [ ] I understand `os.environ[]`.
- [ ] I can validate required configuration.
- [ ] I can convert numeric configuration.
- [ ] I can parse simple boolean configuration safely.

## Data Engineering services

- [ ] I understand PostgreSQL environment-variable conventions.
- [ ] I understand initialization versus runtime configuration.
- [ ] I can explain MinIO configuration at a conceptual level.
- [ ] I can explain Redis client configuration at a conceptual level.
- [ ] I understand that Kafka configuration is image/distribution-specific.
- [ ] I do not confuse application variables with universal Docker variables.

## Operational reasoning

- [ ] I can distinguish configuration from networking.
- [ ] I can distinguish configuration from persistence.
- [ ] I can distinguish configuration from secrets management.
- [ ] I can inspect actual runtime configuration instead of guessing.
- [ ] I can diagnose missing configuration.
- [ ] I can diagnose invalid configuration.
- [ ] I can diagnose incorrect configuration.
- [ ] I can avoid exposing credentials while debugging.

---

# 44. Roadmap Coverage Audit

This module intentionally covers the Topic 05 curriculum from foundational concepts through production-oriented operational reasoning.

| Roadmap requirement | Covered |
|---|---:|
| What is configuration | Yes |
| Environment variables from first principles | Yes |
| `docker run -e` / `--env` | Yes |
| Host vs container environment | Yes |
| Application configuration | Yes |
| Required vs optional configuration | Yes |
| String/type conversion | Yes |
| PostgreSQL configuration | Yes |
| Initialization vs runtime configuration | Yes |
| MinIO configuration | Yes |
| Redis configuration | Yes |
| Kafka configuration | Yes |
| Environment-specific configuration | Yes |
| Safe defaults | Yes |
| Configuration validation | Yes |
| Naming conventions | Yes |
| Runtime inspection | Yes |
| Security awareness | Yes |
| Do-not-print-secrets hygiene | Yes |
| Shell expansion and quoting | Yes |
| Configuration precedence concepts | Yes |
| Image defaults concept | Yes |
| Configuration vs command arguments | Yes |
| Configuration vs volumes | Yes |
| Configuration vs networking | Yes |
| Configuration vs persistent data | Yes |
| Hands-on Data Engineering lab | Yes |
| Break/fix exercises | Yes |
| Real-world scenarios | Yes |
| Configuration design principles | Yes |
| Common mistakes | Yes |
| Mental models | Yes |
| ASCII diagrams | Yes |
| Command reference | Yes |
| Python configuration reference | Yes |
| Practice questions | Yes |
| Interview practice | Yes |
| Final knowledge check | Yes |
| Module completion checklist | Yes |

---

# 45. Scope Boundary

This module deliberately does **not** become a complete course on:

- Docker networking
- ports
- DNS
- Kafka listener architecture
- volumes
- bind mounts
- Docker Compose
- general container troubleshooting
- resource limits
- cleanup
- Docker Desktop
- WSL2
- Dockerfile authoring
- image building
- Kubernetes ConfigMaps
- Kubernetes Secrets
- full cloud secret-management platforms

Those subjects belong to other modules or later curriculum.

This module may reference those concepts when required to explain configuration, but it does not replace their dedicated curriculum.

---

# 46. Final Professional Takeaway

The practical skill is not merely knowing:

```bash
docker run -e KEY=value image
```

The real Data Engineering skill is understanding the complete chain:

```text
Configuration
      +
Correct runtime injection
      +
Application validation
      +
Correct networking
      +
Correct persistent state
      =
Predictable containerized application behavior
```

A strong engineer can look at a containerized pipeline and ask:

1. **What configuration does the application require?**
2. **Where does each value come from?**
3. **Did Docker actually inject it?**
4. **Did the application parse and validate it correctly?**
5. **Is the configured endpoint reachable?**
6. **Is persistent state affecting the observed behavior?**
7. **Could the diagnostic process expose credentials?**
8. **Can the same image be reused in another environment?**

Once you can answer those questions confidently, environment variables stop being a Docker command to memorize and become what they really are:

> **A runtime configuration mechanism that helps make containerized Data Engineering applications portable, reproducible, diagnosable, and environment-aware.**
