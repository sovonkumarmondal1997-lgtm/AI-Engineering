\set ON_ERROR_STOP on
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE ROLE tenant_a_runtime LOGIN PASSWORD 'tenant_a_local_only' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE tenant_b_runtime LOGIN PASSWORD 'tenant_b_local_only' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE ROLE tenant_policy_owner NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
CREATE SCHEMA app AUTHORIZATION lab_admin;
-- Temporarily permit ownership transfer/function ownership; remove CREATE before tenant access.
GRANT USAGE, CREATE ON SCHEMA app TO tenant_policy_owner;
CREATE TABLE app.tenant_principals (
    db_role name PRIMARY KEY,
    tenant_id uuid NOT NULL UNIQUE
);
ALTER TABLE app.tenant_principals OWNER TO tenant_policy_owner;
INSERT INTO app.tenant_principals (db_role, tenant_id) VALUES
('tenant_a_runtime', '11111111-1111-1111-1111-111111111111'),
('tenant_b_runtime', '22222222-2222-2222-2222-222222222222');
REVOKE ALL ON app.tenant_principals FROM PUBLIC;
CREATE FUNCTION app.current_tenant_id() RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog, app
AS $$ SELECT tenant_id FROM app.tenant_principals WHERE db_role = session_user $$;
ALTER FUNCTION app.current_tenant_id() OWNER TO tenant_policy_owner;
REVOKE ALL ON FUNCTION app.current_tenant_id() FROM PUBLIC;
REVOKE CREATE ON SCHEMA app FROM tenant_policy_owner;
GRANT EXECUTE ON FUNCTION app.current_tenant_id() TO tenant_a_runtime, tenant_b_runtime;
CREATE TABLE app.events (
    event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    event_type text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE app.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.events FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON app.events
  USING (tenant_id = app.current_tenant_id())
  WITH CHECK (tenant_id = app.current_tenant_id());
GRANT USAGE ON SCHEMA app TO tenant_a_runtime, tenant_b_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.events TO tenant_a_runtime, tenant_b_runtime;
INSERT INTO app.events (tenant_id, event_type, payload) VALUES
('11111111-1111-1111-1111-111111111111', 'signup', '{"customer":"A"}'),
('22222222-2222-2222-2222-222222222222', 'purchase', '{"customer":"B"}');
