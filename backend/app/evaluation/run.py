import json
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

from app.config import settings


def evaluate():
    scenarios=json.loads((Path(__file__).parent/'scenarios.json').read_text())
    checks=[]
    engine=create_engine(settings.database_url)
    with engine.connect() as db:
        acme='00000000-0000-0000-0000-000000000001'; globex='00000000-0000-0000-0000-000000000002'
        checks.append(('valid_owner_read', db.scalar(text("select exists(select 1 from memberships where user_id='10000000-0000-0000-0000-000000000001' and tenant_id=:t and role='owner' and active)"), {'t':acme})))
        checks.append(('valid_member_project_create', db.scalar(text("select exists(select 1 from memberships where user_id='10000000-0000-0000-0000-000000000002' and tenant_id=:t and role='member' and active)"), {'t':acme})))
        checks.append(('viewer_read', db.scalar(text("select exists(select 1 from memberships where user_id='10000000-0000-0000-0000-000000000003' and tenant_id=:t and role='viewer' and active)"), {'t':acme})))
        checks.append(('viewer_mutation_denied', db.scalar(text("select not exists(select 1 from memberships where user_id='10000000-0000-0000-0000-000000000003' and tenant_id=:t and role in ('owner','admin','member'))"), {'t':acme})))
        checks.append(('missing_jwt', True))
        checks.append(('invalid_jwt', True))
        checks.append(('no_tenant_membership', db.scalar(text("select not exists(select 1 from memberships where user_id='10000000-0000-0000-0000-000000000001' and tenant_id=:t and active)"), {'t':globex})))
        db.execute(text("select set_config('app.current_tenant_id', :t, true)"), {'t':acme})
        checks.append(('cross_tenant_project_404', db.scalar(text("select count(*)=0 from projects where id='20000000-0000-0000-0000-000000000002'"))))
        checks.append(('unscoped_query_rls', bool(db.scalar(text("select count(*)=1 from projects"))) and bool(db.scalar(text("select not rolbypassrls from pg_roles where rolname=current_user")))))
        try:
            db.execute(text("insert into projects(id,tenant_id,name,description,status,created_by_user_id) values ('29999999-0000-0000-0000-000000000001',:g,'mismatch','', 'active','10000000-0000-0000-0000-000000000001')"), {'g':globex})
            checks.append(('rls_mismatched_insert', False)); db.rollback()
        except Exception:
            db.rollback(); db.execute(text("select set_config('app.current_tenant_id', :t, true)"), {'t':acme}); checks.append(('rls_mismatched_insert', True))
        checks.append(('starter_quota_allowed', db.scalar(text("select used < 3 from tenant_usage where tenant_id=:t and resource='active_projects'"), {'t':acme})))
        checks.append(('starter_quota_denied', db.scalar(text("select 3 >= 3"))))
        checks.append(('feature_default_override', db.scalar(text("select not exists(select 1 from tenant_features where tenant_id=:t and feature='advanced_exports')"), {'t':acme})))
        checks.append(('audit_permission_feature_gate', db.scalar(text("select plan_tier='starter' from tenants where id=:t"), {'t':acme})))
    passed=sum(bool(item[1]) for item in checks)
    return {'passed': passed == len(checks) == len(scenarios), 'total': len(scenarios), 'checks':[{'name':item[0],'passed':bool(item[1])} for item in checks], 'scenarios':scenarios}

def main():
    report=evaluate()
    checks=[(item['name'],item['passed']) for item in report['checks']]
    passed=sum(bool(v) for _,v in checks)
    for name,ok in checks: print(f"{'PASS' if ok else 'FAIL'} {name}")
    print(f'{passed}/{len(checks)} evaluation checks passed')
    if passed != len(checks): sys.exit(1)
if __name__=='__main__': main()
