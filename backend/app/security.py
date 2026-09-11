from enum import StrEnum
from fastapi import HTTPException

class Permission(StrEnum):
    TENANT_READ='tenant.read'; PROJECTS_READ='projects.read'; PROJECTS_CREATE='projects.create'; PROJECTS_UPDATE='projects.update'; PROJECTS_DELETE='projects.delete'; FEATURES_READ='features.read'; FEATURES_MANAGE='features.manage'; AUDIT_READ='audit.read'
MATRIX = {'owner': set(Permission), 'admin': {p for p in Permission if p != Permission.PROJECTS_DELETE}, 'member': {Permission.TENANT_READ, Permission.PROJECTS_READ, Permission.PROJECTS_CREATE, Permission.PROJECTS_UPDATE, Permission.FEATURES_READ}, 'viewer': {Permission.TENANT_READ, Permission.PROJECTS_READ, Permission.FEATURES_READ}}
def require_permission(ctx, permission: Permission):
    if permission not in ctx['permissions']: raise HTTPException(403, detail={'code':'permission_denied','message':f'Missing {permission}','trace_id':str(ctx['trace_id'])})

