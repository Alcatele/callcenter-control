import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def new_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    admin = "admin"
    supervisor = "supervisor"
    agent = "agent"


class AgentStatus(str, enum.Enum):
    offline = "offline"
    available = "available"
    paused = "paused"
    ringing = "ringing"
    in_call = "in_call"
    wrap_up = "wrap_up"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    domain_name: Mapped[str] = mapped_column(String(190), nullable=False, unique=True)
    fusionpbx_domain_uuid: Mapped[str | None] = mapped_column(String(36), nullable=True, unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    agents: Mapped[list["Agent"]] = relationship(back_populates="tenant")
    queues: Mapped[list["Queue"]] = relationship(back_populates="tenant")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(190), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    tenant: Mapped[Tenant | None] = relationship(back_populates="users")
    agent: Mapped["Agent | None"] = relationship(back_populates="user")


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("tenant_id", "extension", name="uq_agent_extension_tenant"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    extension: Mapped[str] = mapped_column(String(40), nullable=False)
    fusionpbx_agent_uuid: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), default=AgentStatus.offline)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant: Mapped[Tenant] = relationship(back_populates="agents")
    user: Mapped[User | None] = relationship(back_populates="agent")
    queues: Mapped[list["QueueMember"]] = relationship(back_populates="agent")


class Queue(Base):
    __tablename__ = "queues"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_queue_name_tenant"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    extension: Mapped[str | None] = mapped_column(String(40), nullable=True)
    fusionpbx_queue_uuid: Mapped[str | None] = mapped_column(String(36), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    tenant: Mapped[Tenant] = relationship(back_populates="queues")
    members: Mapped[list["QueueMember"]] = relationship(back_populates="queue")


class QueueMember(Base):
    __tablename__ = "queue_members"
    __table_args__ = (UniqueConstraint("queue_id", "agent_id", name="uq_queue_agent"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    queue_id: Mapped[str] = mapped_column(ForeignKey("queues.id"), nullable=False)
    agent_id: Mapped[str] = mapped_column(ForeignKey("agents.id"), nullable=False)
    tier_level: Mapped[str] = mapped_column(String(10), default="1")
    tier_position: Mapped[str] = mapped_column(String(10), default="1")

    queue: Mapped[Queue] = relationship(back_populates="members")
    agent: Mapped[Agent] = relationship(back_populates="queues")

