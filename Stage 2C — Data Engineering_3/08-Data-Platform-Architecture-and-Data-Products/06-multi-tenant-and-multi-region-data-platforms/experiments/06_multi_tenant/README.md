# Multi-Tenant Platform Lab

Educational lab aligned with Topic 06 of `roadmap-Data-Platform-Architecture-and-Data-Products.md`.

## Contents
- PostgreSQL pooled-tenancy DDL with forced RLS bound to tenant-specific authenticated database logins.
- PostgreSQL integration tests for cross-tenant reads, updates, inserts, and attempted custom-GUC spoofing.
- Local policy simulation, schema-per-tenant SQL example, quota simulation, and offboarding manifest/audit simulation.
- Regional architecture and failover checklist.

## Local-only tests (no database required)

```bash
python -m venv .venv
# activate it, then:
python -m pip install -e ".[test]"
python -m pytest -q
python run_lab.py
```

Expected without both `TEST_DATABASE_URL_A` and `TEST_DATABASE_URL_B`: five local tests pass and two PostgreSQL integration tests skip.

## PostgreSQL integration tests (Docker Compose required)

```bash
docker compose up -d --wait
# Linux/macOS:
export TEST_DATABASE_URL_A='postgresql://tenant_a_runtime:tenant_a_local_only@localhost:55432/tenant_lab'
export TEST_DATABASE_URL_B='postgresql://tenant_b_runtime:tenant_b_local_only@localhost:55432/tenant_lab'
# PowerShell equivalents:
# $env:TEST_DATABASE_URL_A = "postgresql://tenant_a_runtime:tenant_a_local_only@localhost:55432/tenant_lab"
# $env:TEST_DATABASE_URL_B = "postgresql://tenant_b_runtime:tenant_b_local_only@localhost:55432/tenant_lab"
python -m pytest -q
docker compose down -v
```

The bootstrap's `lab_admin` creates objects. Tenant A and B have distinct login roles, no membership in each other, and cannot change `session_user`; RLS maps that login to a tenant through a tightly scoped security-definer function. The function owner is non-login and non-superuser, has a fixed search path, and the mapping table is not writable by tenant roles. Review this function and its ownership in any real deployment.

**Never reuse lab credentials.** The integration test validates this lab configuration only, not production isolation or a penetration test. Per-tenant database roles are an illustrative security model; for thousands of tenants, evaluate credential/role lifecycle costs and reviewed database-proxy or signed-context alternatives. A shared-login policy based only on a client-settable custom GUC is not a defense against arbitrary SQL under that login.

## Limits

Offboarding writes a simulated manifest/audit record; it does not delete real cloud object versions, external caches, or managed backups. Noisy-neighbour logic is a deterministic quota simulation, not a benchmark. No cloud regions are provisioned or failed over.
