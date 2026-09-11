# Threat model

| Threat | Mitigation | Residual risk |
| --- | --- | --- |
| Header tampering | Membership lookup per request | Compromised user credentials |
| Known foreign UUID / IDOR | Tenant predicate + RLS + 404 | External side effects are out of scope |
| Missing tenant filter | RLS controlled probe | Only tenant-owned tables covered |
| Role escalation | Server-side DB membership | Admin DB compromise out of scope |
| Stale JWT role | Roles never trusted from token | Token remains valid until expiry |
| SQL injection | SQLAlchemy parameters; fixed probe SQL | Future code must preserve review discipline |
| Leaked JWT | In-memory frontend token | Local demo lacks revocation/refresh |
| Audit tampering | No update/delete API | Not cryptographically immutable |
| Runtime privilege | Separate NOBYPASSRLS role | Postgres superusers still bypass |
| Quota abuse | Transactional check/usage limit | Small single-node demo strategy |

