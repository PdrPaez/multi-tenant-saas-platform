# Authorization

`backend/app/security.py` is the inspectable permission matrix. `require_permission` is called by each protected route. `401` means authentication failed, `403` means a valid member lacks permission, and `404` means a tenant-owned resource is not visible in the current tenant scope, including a known foreign UUID.

