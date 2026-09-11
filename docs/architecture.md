# Architecture

The control plane contains users, tenants, and memberships. Projects, feature overrides, and tenant audit records are tenant-owned. Each request resolves an immutable context, checks the centralized role matrix, sets transaction-local PostgreSQL context, and then calls a scoped query. The UI visualizes the returned execution result; it does not authorize requests. Local PostgreSQL is installed natively; Docker is not required.
