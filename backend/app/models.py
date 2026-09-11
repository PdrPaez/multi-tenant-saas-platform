from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text
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
class AuditEvent(Base):
    __tablename__='audit_events'; id: Mapped[UUID] = mapped_column(primary_key=True); tenant_id: Mapped[UUID] = mapped_column(ForeignKey('tenants.id')); actor_user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id')); action: Mapped[str] = mapped_column(String); resource_type: Mapped[str] = mapped_column(String); resource_id: Mapped[UUID|None] = mapped_column(nullable=True); outcome: Mapped[str] = mapped_column(String); metadata_: Mapped[dict] = mapped_column('metadata', JSON, default=dict); trace_id: Mapped[UUID|None] = mapped_column(nullable=True)

