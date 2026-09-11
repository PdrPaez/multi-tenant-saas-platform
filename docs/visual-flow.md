# Visual flow

The XYFlow canvas represents backend trace stages: request, authentication, tenant resolution, membership, RBAC, DB context, repository, RLS, feature, quota, mutation, audit, and response. The backend result maps to node states; denied or skipped downstream stages remain visible. Replay is a UI presentation of a completed trace and cannot change backend behavior.

