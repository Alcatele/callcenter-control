from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user, tenant_scope
from app.db.models import Queue, QueueMember, User
from app.db.session import get_db


router = APIRouter()


class QueueIn(BaseModel):
    tenant_id: str
    name: str
    extension: str | None = None
    fusionpbx_queue_uuid: str | None = None


class QueueMemberIn(BaseModel):
    agent_id: str
    tier_level: str = "1"
    tier_position: str = "1"


class QueueOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    extension: str | None
    active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[QueueOut])
def list_queues(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Queue]:
    stmt = select(Queue).order_by(Queue.name)
    scope = tenant_scope(user)
    if scope:
        stmt = stmt.where(Queue.tenant_id == scope)
    return list(db.scalars(stmt))


@router.post("", response_model=QueueOut)
def create_queue(
    payload: QueueIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> Queue:
    scope = tenant_scope(user)
    if scope and payload.tenant_id != scope:
        raise HTTPException(status_code=403, detail="Tenant out of scope")
    queue = Queue(**payload.model_dump())
    db.add(queue)
    db.commit()
    db.refresh(queue)
    return queue


@router.post("/{queue_id}/members")
def add_queue_member(
    queue_id: str,
    payload: QueueMemberIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    queue = db.get(Queue, queue_id)
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")
    scope = tenant_scope(user)
    if scope and queue.tenant_id != scope:
        raise HTTPException(status_code=403, detail="Tenant out of scope")
    member = QueueMember(queue_id=queue_id, **payload.model_dump())
    db.add(member)
    db.commit()
    return {"status": "ok"}

