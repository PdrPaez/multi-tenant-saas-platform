from uuid import UUID
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.config import settings
from app.models import User, Tenant, Membership, Project, TenantFeature
from app.auth import hash_password

IDS={
 'acme':UUID('00000000-0000-0000-0000-000000000001'),'globex':UUID('00000000-0000-0000-0000-000000000002'),'umbra':UUID('00000000-0000-0000-0000-000000000003'),
 'alice':UUID('10000000-0000-0000-0000-000000000001'),'bob':UUID('10000000-0000-0000-0000-000000000002'),'vera':UUID('10000000-0000-0000-0000-000000000003'),'carol':UUID('10000000-0000-0000-0000-000000000004'),'sam':UUID('10000000-0000-0000-0000-000000000005'),
 'acme-project':UUID('20000000-0000-0000-0000-000000000001'),'globex-project':UUID('20000000-0000-0000-0000-000000000002')}
def main():
    engine=create_engine(settings.database_admin_url)
    with Session(engine) as db:
        db.execute(text('TRUNCATE request_trace_steps, request_traces, audit_events, tenant_features, projects, memberships, tenants, users CASCADE'))
        users=[('alice','alice@demo.local','Alice Owner'),('bob','bob@demo.local','Bob Member'),('vera','vera@demo.local','Vera Viewer'),('carol','carol@demo.local','Carol Owner'),('sam','sam@demo.local','Sam Admin')]
        for key,email,name in users: db.add(User(id=IDS[key],email=email,display_name=name,password_hash=hash_password('demo-password')))
        tenants=[('acme','acme','Acme Labs','starter'),('globex','globex','Globex Cloud','pro'),('umbra','umbra','Umbra Studio','starter')]
        for key,slug,name,plan in tenants: db.add(Tenant(id=IDS[key],slug=slug,display_name=name,plan_tier=plan))
        for user,tenant,role in [('alice','acme','owner'),('bob','acme','member'),('vera','acme','viewer'),('carol','globex','owner'),('sam','acme','admin'),('sam','globex','member')]: db.add(Membership(user_id=IDS[user],tenant_id=IDS[tenant],role=role))
        for key,tenant,name in [('acme-project','acme','Acme Control Plane'),('globex-project','globex','Globex Analytics')]: db.add(Project(id=IDS[key],tenant_id=IDS[tenant],name=name,description='Seeded tenant-owned project',created_by_user_id=IDS['alice' if tenant=='acme' else 'carol']))
        db.commit()
        print('Seeded 3 tenants, 5 users, memberships, and deterministic projects. Password: demo-password')
if __name__=='__main__': main()

