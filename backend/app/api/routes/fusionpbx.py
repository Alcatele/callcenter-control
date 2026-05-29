from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.models import Tenant, User
from app.db.session import get_db
from app.services.fusionpbx_repository import FusionPbxRepository


router = APIRouter()


class FusionDomainOut(BaseModel):
    domain_uuid: str
    domain_name: str


@router.get("/domains", response_model=list[FusionDomainOut])
def list_fusionpbx_domains(_: User = Depends(require_admin)) -> list[dict[str, str]]:
    repository = FusionPbxRepository()
    if not repository.enabled():
        raise HTTPException(status_code=400, detail="FusionPBX database is not configured")
    return repository.list_domains()


@router.post("/import-tenants")
def import_tenants(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    repository = FusionPbxRepository()
    if not repository.enabled():
        raise HTTPException(status_code=400, detail="FusionPBX database is not configured")

    created = 0
    updated = 0
    domains = repository.list_domains()

    for domain in domains:
        domain_uuid = str(domain["domain_uuid"])
        domain_name = str(domain["domain_name"])
        tenant = db.scalar(select(Tenant).where(Tenant.fusionpbx_domain_uuid == domain_uuid))

        if tenant:
            tenant.name = domain_name
            tenant.domain_name = domain_name
            updated += 1
            continue

        existing_by_name = db.scalar(select(Tenant).where(Tenant.domain_name == domain_name))
        if existing_by_name:
            existing_by_name.fusionpbx_domain_uuid = domain_uuid
            existing_by_name.name = domain_name
            updated += 1
            continue

        db.add(
            Tenant(
                name=domain_name,
                domain_name=domain_name,
                fusionpbx_domain_uuid=domain_uuid,
            )
        )
        created += 1

    db.commit()
    return {"created": created, "updated": updated, "total": len(domains)}
