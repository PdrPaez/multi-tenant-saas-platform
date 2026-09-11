# PostgreSQL row-level security

`saas_owner` owns schema/migrations. `saas_app` is the runtime role and has `NOBYPASSRLS`. Tenant-owned tables use `FORCE ROW LEVEL SECURITY` and policies checking `current_setting('app.current_tenant_id', true)`. `set_config(..., true)` is transaction-local. Both `USING` and `WITH CHECK` protect reads and writes. The unscoped probe is fixed SQL and demonstrates that a missing application predicate cannot reveal another tenant.

