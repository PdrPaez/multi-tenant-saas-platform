# Decisions

- PostgreSQL is required because RLS is the learning objective.
- Owner/runtime DB roles are separate and runtime is `NOBYPASSRLS`.
- JWT carries identity, not authoritative tenant role.
- Explicit tenant header plus database membership validation keeps selection and authorization distinct.
- Application filtering and RLS provide defense in depth.
- Projects are the representative tenant-owned resource.
- Fixed RBAC, seeded plan tiers, controlled probes, and XYFlow keep the demo inspectable.

