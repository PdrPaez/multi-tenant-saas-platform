# Tenant resolution

JWT authentication identifies the user. `X-Tenant-ID` is only a selector. The API parses it, loads an active tenant, loads active `(user_id, tenant_id)` membership, derives the role from the database, and constructs a request-scoped context. Missing headers are `400`; absent/inactive memberships are `403`. No process-global tenant state is used.

