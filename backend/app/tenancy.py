from uuid import UUID, uuid4
from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.auth import current_user
from app.database import db_session
from app.models import Tenant, Membership
from app.security import MATRIX

def tenant_context(x_tenant_id: str|None=Header(default=None), user=Depends(current_user), db: Session=Depends(db_session)):
    if not x_tenant_id: raise HTTPException(400, detail={'code':'tenant_required','message':'X-Tenant-ID is required'})
    try: tid=UUID(x_tenant_id)
    except ValueError: raise HTTPException(400, detail={'code':'tenant_required','message':'Tenant ID must be UUID'})
    tenant=db.get(Tenant,tid); membership=db.execute(select(Membership).where(Membership.user_id==user.id,Membership.tenant_id==tid,Membership.active.is_(True))).scalar_one_or_none()
    if not tenant or not tenant.active or not membership: raise HTTPException(403, detail={'code':'tenant_not_available','message':'No active membership for requested tenant'})
    return {'tenant':tenant,'user':user,'role':membership.role,'permissions':MATRIX[membership.role],'trace_id':uuid4()}

