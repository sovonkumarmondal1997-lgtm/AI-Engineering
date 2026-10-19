-- Illustrative schema-per-tenant variant. Provision with a privileged migration role.
-- Schemas still share a PostgreSQL instance and possibly its failure domain.
CREATE SCHEMA tenant_a;
CREATE TABLE tenant_a.events (
  event_id uuid PRIMARY KEY,
  event_type text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE ROLE silo_tenant_a_runtime LOGIN NOSUPERUSER NOBYPASSRLS;
GRANT USAGE ON SCHEMA tenant_a TO silo_tenant_a_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tenant_a TO silo_tenant_a_runtime;
-- Configure default privileges and prohibit broad grants in production.
-- Never let clients choose arbitrary schema identifiers.
