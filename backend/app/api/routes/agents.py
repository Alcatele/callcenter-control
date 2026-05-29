from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user, tenant_scope
from app.db.models import Agent, AgentStatus, User
from app.db.session import get_db


router = APIRouter()


class AgentIn(BaseModel):
    tenant_id: str
    name: str
    extension: str
    fusionpbx_agent_uuid: str | None = None


class AgentStatusIn(BaseModel):
    status: AgentStatus


class AgentOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    extension: str
    status: AgentStatus
    active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[AgentOut])
def list_agents(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Agent]:
    stmt = select(Agent).order_by(Agent.name)
    scope = tenant_scope(user)
    if scope:
        stmt = stmt.where(Agent.tenant_id == scope)
    return list(db.scalars(stmt))


@router.post("", response_model=AgentOut)
def create_agent(
    payload: AgentIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Agent:
    scope = tenant_scope(user)
    if scope and payload.tenant_id != scope:
        raise HTTPException(status_code=403, detail="Tenant out of scope")
    agent = Agent(**payload.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.patch("/{agent_id}/status", response_model=AgentOut)
def update_agent_status(
    agent_id: str,
    payload: AgentStatusIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Agent:
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    scope = tenant_scope(user)
    if scope and agent.tenant_id != scope:
        raise HTTPException(status_code=403, detail="Tenant out of scope")
    agent.status = payload.status
    db.commit()
    db.refresh(agent)
    return agent

