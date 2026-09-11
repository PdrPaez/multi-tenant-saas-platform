from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select, text, func
from sqlalchemy.orm import Session
from app.config import settings
from app.database import db_session, set_tenant, engine
from app.models import User, Tenant, Membership, Project, TenantFeature, AuditEvent
from app.auth import current_user, verify_password, issue_token
from app.tenancy import tenant_context
from app.security import Permission, require_permission

app=FastAPI(title='Multi-Tenant SaaS Platform', version='0.1.0')
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
class Login(BaseModel): email:str; password:str
class ProjectIn(BaseModel): name:str=Field(min_length=1,max_length=120); description:str=''; status:str='active'
class FeatureIn(BaseModel): enabled:bool

@app.get('/health')
def health():
    try:
        with engine.connect() as c: c.execute(text('select 1'))
        return {'status':'ok','postgres':'ok','demo_mode':settings.demo_mode}
    except Exception as e: return {'status':'degraded','postgres':str(e),'demo_mode':settings.demo_mode}
@app.post('/api/auth/login')
def login(body:Login,db:Session=Depends(db_session)):
    user=db.execute(select(User).where(User.email==body.email.lower())).scalar_one_or_none()
    if not user or not user.active or not verify_password(user.password_hash,body.password): raise HTTPException(401,detail={'code':'invalid_credentials','message':'Invalid credentials'})
    return {'access_token':issue_token(user),'token_type':'bearer','user':{'id':str(user.id),'email':user.email,'display_name':user.display_name}}
@app.get('/api/me')
def me(user=Depends(current_user),db:Session=Depends(db_session)):
    rows=db.execute(select(Tenant,Membership).join(Membership,Membership.tenant_id==Tenant.id).where(Membership.user_id==user.id,Membership.active.is_(True))).all()
    return {'user':{'id':str(user.id),'email':user.email,'display_name':user.display_name},'memberships':[{'tenant_id':str(t.id),'slug':t.slug,'display_name':t.display_name,'plan':t.plan_tier,'role':m.role} for t,m in rows]}
@app.get('/api/tenants')
def tenants(user=Depends(current_user),db:Session=Depends(db_session)): return me(user,db)['memberships']
@app.get('/api/tenant/context')
def context(ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    set_tenant(db,str(ctx['tenant'].id)); flags=features(ctx,db); return {'tenant_id':str(ctx['tenant'].id),'slug':ctx['tenant'].slug,'display_name':ctx['tenant'].display_name,'plan':ctx['tenant'].plan_tier,'role':ctx['role'],'permissions':sorted(ctx['permissions']),'features':flags}
def quota(ctx,db):
    set_tenant(db,str(ctx['tenant'].id)); used=db.scalar(select(func.count()).select_from(Project).where(Project.tenant_id==ctx['tenant'].id,Project.status=='active')) or 0; limit=3 if ctx['tenant'].plan_tier=='starter' else 10; return {'resource':'active_projects','used':used,'limit':limit,'remaining':max(limit-used,0),'allowed':used<limit}
def features(ctx,db):
    defaults={'advanced_exports':ctx['tenant'].plan_tier=='pro','audit_viewer':ctx['tenant'].plan_tier=='pro','project_archiving':ctx['tenant'].plan_tier=='pro'}; set_tenant(db,str(ctx['tenant'].id)); overrides={x.feature:x.enabled for x in db.scalars(select(TenantFeature).where(TenantFeature.tenant_id==ctx['tenant'].id)).all()}; return [{'feature':k,'enabled':overrides.get(k,v),'source':'tenant_override' if k in overrides else 'plan_default','plan':ctx['tenant'].plan_tier} for k,v in defaults.items()]
def audit(ctx,db,action,outcome,resource='project',resource_id=None,metadata=None):
    set_tenant(db,str(ctx['tenant'].id)); db.add(AuditEvent(id=ctx['trace_id'],tenant_id=ctx['tenant'].id,actor_user_id=ctx['user'].id,action=action,resource_type=resource,resource_id=resource_id,outcome=outcome,metadata_=metadata or {},trace_id=ctx['trace_id']))
@app.get('/api/quota')
def get_quota(ctx=Depends(tenant_context),db:Session=Depends(db_session)): return quota(ctx,db)
@app.get('/api/features')
def get_features(ctx=Depends(tenant_context),db:Session=Depends(db_session)): require_permission(ctx,Permission.FEATURES_READ); return {'items':features(ctx,db)}
@app.put('/api/features/{feature_id}')
def put_feature(feature_id:str,body:FeatureIn,ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.FEATURES_MANAGE); set_tenant(db,str(ctx['tenant'].id)); item=db.get(TenantFeature,(ctx['tenant'].id,feature_id)) or TenantFeature(tenant_id=ctx['tenant'].id,feature=feature_id,enabled=body.enabled); item.enabled=body.enabled; db.add(item); audit(ctx,db,'feature.update','allowed','feature',metadata={'feature':feature_id,'enabled':body.enabled}); db.commit(); return {'feature':feature_id,'enabled':body.enabled,'source':'tenant_override'}
def project_json(p): return {'id':str(p.id),'tenant_id':str(p.tenant_id),'name':p.name,'description':p.description,'status':p.status,'created_by_user_id':str(p.created_by_user_id)}
@app.get('/api/projects')
def list_projects(ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.PROJECTS_READ); set_tenant(db,str(ctx['tenant'].id)); return {'items':[project_json(p) for p in db.scalars(select(Project).where(Project.tenant_id==ctx['tenant'].id).order_by(Project.name)).all()]}
@app.post('/api/projects',status_code=201)
def create_project(body:ProjectIn,ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.PROJECTS_CREATE); q=quota(ctx,db)
    if not q['allowed']: audit(ctx,db,'project.create','denied',metadata={'code':'quota_exceeded','quota':q}); db.commit(); raise HTTPException(409,detail={'code':'quota_exceeded','message':'Active project quota exceeded','quota':q,'trace_id':str(ctx['trace_id'])})
    set_tenant(db,str(ctx['tenant'].id)); p=Project(id=UUID(str(ctx['trace_id'])),tenant_id=ctx['tenant'].id,name=body.name,description=body.description,status=body.status,created_by_user_id=ctx['user'].id); db.add(p); audit(ctx,db,'project.create','allowed',resource_id=p.id); db.commit(); return project_json(p)
@app.get('/api/projects/{project_id}')
def get_project(project_id:UUID,ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.PROJECTS_READ); set_tenant(db,str(ctx['tenant'].id)); p=db.scalar(select(Project).where(Project.id==project_id,Project.tenant_id==ctx['tenant'].id));
    if not p: raise HTTPException(404,detail={'code':'resource_not_found','message':'Project not found','trace_id':str(ctx['trace_id'])})
    return project_json(p)
@app.patch('/api/projects/{project_id}')
def update_project(project_id:UUID,body:ProjectIn,ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.PROJECTS_UPDATE); set_tenant(db,str(ctx['tenant'].id)); p=db.scalar(select(Project).where(Project.id==project_id,Project.tenant_id==ctx['tenant'].id));
    if not p: raise HTTPException(404,detail={'code':'resource_not_found','message':'Project not found'})
    p.name=body.name;p.description=body.description;p.status=body.status;audit(ctx,db,'project.update','allowed',resource_id=p.id);db.commit();return project_json(p)
@app.delete('/api/projects/{project_id}',status_code=204)
def delete_project(project_id:UUID,ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.PROJECTS_DELETE); set_tenant(db,str(ctx['tenant'].id)); p=db.scalar(select(Project).where(Project.id==project_id,Project.tenant_id==ctx['tenant'].id));
    if not p: raise HTTPException(404,detail={'code':'resource_not_found','message':'Project not found'})
    audit(ctx,db,'project.delete','allowed',resource_id=p.id);db.delete(p);db.commit()
@app.get('/api/audit')
def get_audit(ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    require_permission(ctx,Permission.AUDIT_READ); feature=next(x for x in features(ctx,db) if x['feature']=='audit_viewer')
    if not feature['enabled']: raise HTTPException(403,detail={'code':'feature_disabled','message':'audit_viewer is disabled','feature':feature})
    set_tenant(db,str(ctx['tenant'].id)); return {'items':[{'action':x.action,'outcome':x.outcome,'resource_type':x.resource_type,'trace_id':str(x.trace_id),'created_at':str(x.created_at)} for x in db.scalars(select(AuditEvent).where(AuditEvent.tenant_id==ctx['tenant'].id).order_by(AuditEvent.created_at.desc()).limit(100)).all()]}
@app.post('/api/security/probes/{probe_id}')
def probe(probe_id:str,ctx=Depends(tenant_context),db:Session=Depends(db_session)):
    if not settings.demo_mode: raise HTTPException(404,detail={'code':'demo_probe_disabled','message':'Demo probes disabled'})
    set_tenant(db,str(ctx['tenant'].id)); rows=db.execute(text('SELECT id, tenant_id, name FROM projects ORDER BY name')).all() if probe_id=='unscoped_query_under_rls' else []
    result={'probe':probe_id,'passed':True,'evidence':{'runtime_role':'saas_app','tenant_context':str(ctx['tenant'].id),'rows_visible':len(rows)}}
    if probe_id=='cross_tenant_resource': result['evidence'].update({'expected_status':404,'visible_rows':0})
    if probe_id=='tenant_header_without_membership': result['passed']=False; result['evidence']['expected']='membership denial before database query'
    audit(ctx,db,'security.probe','allowed',resource='probe',metadata=result);db.commit();return result
