# Real UI captures

The canonical capture is taken from the local Vite application after starting the backend. Captures in this directory must be made with a real browser against the running application and must show the scenario result, persisted trace inspector, and replay state; mockups are not accepted.

Required final capture set once PostgreSQL is available:

- `owner-read.png`
- `viewer-mutation-denied.png`
- `cross-tenant-404.png`
- `rls-unscoped-query.png`
- `quota-exceeded.png`

The UI shell was inspected in a real browser during development. Scenario-labeled captures remain intentionally gated on a local native PostgreSQL instance so that the repository never presents a backend-free screenshot as proof of security behavior.
