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
        checks.append(('runtime_role_no_bypass', db.scalar(text("select not rolbypassrls from pg_roles where rolname=current_user"))))
        checks.append(('missing_context_isolated', db.scalar(text('select count(*)=0 from projects'))))
        db.execute(text("select set_config('app.current_tenant_id','00000000-0000-0000-0000-000000000001',true)"))
        checks.append(('acme_rls_rows_only', db.scalar(text("select count(*)=1 from projects where tenant_id='00000000-0000-0000-0000-000000000001'"))))
    passed=sum(bool(v) for _,v in checks)
    return {'passed': passed == len(checks), 'total': len(scenarios), 'checks':[{'name':n,'passed':bool(v)} for n,v in checks], 'scenarios':scenarios}

def main():
    report=evaluate()
    checks=[(item['name'],item['passed']) for item in report['checks']]
    passed=sum(bool(v) for _,v in checks)
    for name,ok in checks: print(f"{'PASS' if ok else 'FAIL'} {name}")
    print(f'{passed}/{len(checks)} evaluation checks passed')
    if passed != len(checks): sys.exit(1)
if __name__=='__main__': main()
