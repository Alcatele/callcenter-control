from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.models import Tenant, User
from app.db.session import get_db


router = APIRouter()


class TenantIn(BaseModel):
    name: str
    domain_name: str
    fusionpbx_domain_uuid: str | None = None


class TenantOut(TenantIn):
    id: str
    active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[TenantOut])
def list_tenants(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[Tenant]:
    return list(db.scalars(select(Tenant).order_by(Tenant.name)))


@router.post("", response_model=TenantOut)
def create_tenant(
    payload: TenantIn,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = Tenant(**payload.model_dump())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

