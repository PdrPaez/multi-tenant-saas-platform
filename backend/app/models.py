from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'; id: Mapped[UUID] = mapped_column(primary_key=True); email: Mapped[str] = mapped_column(String, unique=True); display_name: Mapped[str] = mapped_column(String); password_hash: Mapped[str] = mapped_column(String); active: Mapped[bool] = mapped_column(Boolean, default=True); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
class Tenant(Base):
    __tablename__='tenants'; id: Mapped[UUID] = mapped_column(primary_key=True); slug: Mapped[str] = mapped_column(String); display_name: Mapped[str] = mapped_column(String); plan_tier: Mapped[str] = mapped_column(String); active: Mapped[bool] = mapped_column(Boolean, default=True)
class Membership(Base):
    __tablename__='memberships'; user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), primary_key=True); tenant_id: Mapped[UUID] = mapped_column(ForeignKey('tenants.id'), primary_key=True); role: Mapped[str] = mapped_column(String); active: Mapped[bool] = mapped_column(Boolean, default=True)
class Project(Base):
    __tablename__='projects'; id: Mapped[UUID] = mapped_column(primary_key=True); tenant_id: Mapped[UUID] = mapped_column(ForeignKey('tenants.id')); name: Mapped[str] = mapped_column(String); description: Mapped[str] = mapped_column(Text, default=''); status: Mapped[str] = mapped_column(String, default='active'); created_by_user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))
class TenantFeature(Base):
    __tablename__='tenant_features'; tenant_id: Mapped[UUID] = mapped_column(ForeignKey('tenants.id'), primary_key=True); feature: Mapped[str] = mapped_column(String, primary_key=True); enabled: Mapped[bool] = mapped_column(Boolean)
class TenantUsage(Base):
    __tablename__='tenant_usage'; tenant_id: Mapped[UUID] = mapped_column(ForeignKey('tenants.id'), primary_key=True); resource: Mapped[str] = mapped_column(String, primary_key=True); used: Mapped[int] = mapped_column(Integer, default=0)
class AuditEvent(Base):
    __tablename__='audit_events'; id: Mapped[UUID] = mapped_column(primary_key=True); tenant_id: Mapped[UUID] = mapped_column(ForeignKey('tenants.id')); actor_user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id')); action: Mapped[str] = mapped_column(String); resource_type: Mapped[str] = mapped_column(String); resource_id: Mapped[UUID|None] = mapped_column(nullable=True); outcome: Mapped[str] = mapped_column(String); metadata_: Mapped[dict] = mapped_column('metadata', JSON, default=dict); trace_id: Mapped[UUID|None] = mapped_column(nullable=True)
class RequestTrace(Base):
    __tablename__='request_traces'; id: Mapped[UUID] = mapped_column(primary_key=True); tenant_id: Mapped[UUID|None] = mapped_column(nullable=True); actor_user_id: Mapped[UUID|None] = mapped_column(nullable=True); status_code: Mapped[int] = mapped_column(Integer); outcome: Mapped[str] = mapped_column(String)
class RequestTraceStep(Base):
    __tablename__='request_trace_steps'; id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True); trace_id: Mapped[UUID] = mapped_column(ForeignKey('request_traces.id')); step_order: Mapped[int] = mapped_column(Integer); name: Mapped[str] = mapped_column(String); state: Mapped[str] = mapped_column(String); metadata_: Mapped[dict] = mapped_column('metadata', JSON, default=dict); duration_ms: Mapped[float] = mapped_column(Float, default=0)
