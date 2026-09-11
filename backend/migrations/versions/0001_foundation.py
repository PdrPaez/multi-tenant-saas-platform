"""foundation schema and tenant RLS"""
from alembic import op

revision = "0001_foundation"
down_revision = None

def upgrade():
    op.execute("""
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE TABLE users (id uuid PRIMARY KEY, email text UNIQUE NOT NULL, display_name text NOT NULL, password_hash text NOT NULL, active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE tenants (id uuid PRIMARY KEY, slug text UNIQUE NOT NULL, display_name text NOT NULL, plan_tier text NOT NULL CHECK(plan_tier IN ('starter','pro')), active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE memberships (user_id uuid REFERENCES users(id) ON DELETE CASCADE, tenant_id uuid REFERENCES tenants(id) ON DELETE CASCADE, role text NOT NULL CHECK(role IN ('owner','admin','member','viewer')), active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(user_id, tenant_id));
    CREATE TABLE projects (id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE, name text NOT NULL, description text NOT NULL DEFAULT '', status text NOT NULL CHECK(status IN ('active','archived')), created_by_user_id uuid NOT NULL REFERENCES users(id), created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
    CREATE INDEX projects_tenant_idx ON projects(tenant_id);
    CREATE TABLE tenant_features (tenant_id uuid REFERENCES tenants(id) ON DELETE CASCADE, feature text NOT NULL, enabled boolean NOT NULL, PRIMARY KEY(tenant_id, feature));
    CREATE TABLE tenant_usage (tenant_id uuid REFERENCES tenants(id) ON DELETE CASCADE, resource text NOT NULL, used integer NOT NULL DEFAULT 0, PRIMARY KEY(tenant_id, resource));
    CREATE TABLE audit_events (id uuid PRIMARY KEY, tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE, actor_user_id uuid REFERENCES users(id), action text NOT NULL, resource_type text NOT NULL, resource_id uuid, outcome text NOT NULL, metadata jsonb NOT NULL DEFAULT '{}', trace_id uuid, created_at timestamptz NOT NULL DEFAULT now());
    CREATE INDEX audit_tenant_idx ON audit_events(tenant_id, created_at DESC);
    CREATE TABLE request_traces (id uuid PRIMARY KEY, tenant_id uuid REFERENCES tenants(id) ON DELETE CASCADE, actor_user_id uuid REFERENCES users(id), status_code int NOT NULL, outcome text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
    CREATE TABLE request_trace_steps (id bigserial PRIMARY KEY, trace_id uuid REFERENCES request_traces(id) ON DELETE CASCADE, step_order int NOT NULL, name text NOT NULL, state text NOT NULL, metadata jsonb NOT NULL DEFAULT '{}', duration_ms float NOT NULL DEFAULT 0);
    GRANT USAGE ON SCHEMA public TO saas_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON users, tenants, memberships, projects, tenant_features, audit_events, request_traces, request_trace_steps TO saas_app;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO saas_app;
    ALTER TABLE projects ENABLE ROW LEVEL SECURITY; ALTER TABLE projects FORCE ROW LEVEL SECURITY;
    ALTER TABLE tenant_features ENABLE ROW LEVEL SECURITY; ALTER TABLE tenant_features FORCE ROW LEVEL SECURITY; ALTER TABLE tenant_usage ENABLE ROW LEVEL SECURITY; ALTER TABLE tenant_usage FORCE ROW LEVEL SECURITY;
    ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY; ALTER TABLE audit_events FORCE ROW LEVEL SECURITY;
    CREATE POLICY projects_tenant ON projects USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid);
    CREATE POLICY features_tenant ON tenant_features USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid);
    CREATE POLICY usage_tenant ON tenant_usage USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid);
    CREATE POLICY audit_tenant ON audit_events USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid) WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true),'')::uuid);
    ALTER TABLE projects OWNER TO saas_owner; ALTER TABLE tenant_features OWNER TO saas_owner; ALTER TABLE tenant_usage OWNER TO saas_owner; ALTER TABLE audit_events OWNER TO saas_owner;
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS request_trace_steps, request_traces, audit_events, tenant_usage, tenant_features, projects, memberships, tenants, users CASCADE")
