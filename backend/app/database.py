from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def db_session():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def set_tenant(db: Session, tenant_id: str):
    db.execute(text("select set_config('app.current_tenant_id', :tenant, true)"), {"tenant": tenant_id})

