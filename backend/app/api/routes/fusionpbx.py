from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.models import Agent, Queue, Tenant, User
from app.db.session import get_db
from app.services.fusionpbx_repository import FusionPbxRepository


router = APIRouter()


class FusionDomainOut(BaseModel):
    domain_uuid: str
    domain_name: str


class FusionImportResult(BaseModel):
    created: int
    updated: int
    total: int


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


@router.post("/import-queues", response_model=FusionImportResult)
def import_queues(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    repository = FusionPbxRepository()
    if not repository.enabled():
        raise HTTPException(status_code=400, detail="FusionPBX database is not configured")

    created = 0
    updated = 0
    tenants_by_domain_uuid = {
        tenant.fusionpbx_domain_uuid: tenant
        for tenant in db.scalars(select(Tenant).where(Tenant.fusionpbx_domain_uuid.is_not(None)))
    }

    for fusion_queue in repository.list_queues():
        tenant = tenants_by_domain_uuid.get(str(fusion_queue["domain_uuid"]))
        if not tenant:
            continue

        queue_uuid = str(fusion_queue["call_center_queue_uuid"])
        queue_name = str(fusion_queue["queue_name"])
        queue_extension = fusion_queue["queue_extension"]

        queue = db.scalar(select(Queue).where(Queue.fusionpbx_queue_uuid == queue_uuid))
        if queue:
            queue.name = queue_name
            queue.extension = str(queue_extension) if queue_extension else None
            queue.active = str(fusion_queue["queue_enabled"]).lower() == "true"
            updated += 1
            continue

        existing = db.scalar(
            select(Queue).where(Queue.tenant_id == tenant.id, Queue.name == queue_name)
        )
        if existing:
            existing.fusionpbx_queue_uuid = queue_uuid
            existing.extension = str(queue_extension) if queue_extension else None
            existing.active = str(fusion_queue["queue_enabled"]).lower() == "true"
            updated += 1
            continue

        db.add(
            Queue(
                tenant_id=tenant.id,
                name=queue_name,
                extension=str(queue_extension) if queue_extension else None,
                fusionpbx_queue_uuid=queue_uuid,
                active=str(fusion_queue["queue_enabled"]).lower() == "true",
            )
        )
        created += 1

    db.commit()
    return {"created": created, "updated": updated, "total": created + updated}


@router.post("/import-agents", response_model=FusionImportResult)
def import_agents(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    repository = FusionPbxRepository()
    if not repository.enabled():
        raise HTTPException(status_code=400, detail="FusionPBX database is not configured")

    created = 0
    updated = 0
    tenants_by_domain_uuid = {
        tenant.fusionpbx_domain_uuid: tenant
        for tenant in db.scalars(select(Tenant).where(Tenant.fusionpbx_domain_uuid.is_not(None)))
    }

    for fusion_agent in repository.list_agents():
        tenant = tenants_by_domain_uuid.get(str(fusion_agent["domain_uuid"]))
        if not tenant:
            continue

        agent_uuid = str(fusion_agent["call_center_agent_uuid"])
        agent_name = str(fusion_agent["agent_name"])
        extension = extract_extension(fusion_agent)

        agent = db.scalar(select(Agent).where(Agent.fusionpbx_agent_uuid == agent_uuid))
        if agent:
            agent.name = agent_name
            agent.extension = extension
            updated += 1
            continue

        existing = db.scalar(
            select(Agent).where(Agent.tenant_id == tenant.id, Agent.extension == extension)
        )
        if existing:
            existing.fusionpbx_agent_uuid = agent_uuid
            existing.name = agent_name
            updated += 1
            continue

        db.add(
            Agent(
                tenant_id=tenant.id,
                name=agent_name,
                extension=extension,
                fusionpbx_agent_uuid=agent_uuid,
            )
        )
        created += 1

    db.commit()
    return {"created": created, "updated": updated, "total": created + updated}


def extract_extension(fusion_agent: dict[str, str | None]) -> str:
    for key in ("agent_id", "agent_name", "agent_contact"):
        value = fusion_agent.get(key)
        if not value:
            continue
        cleaned = str(value).replace("user/", "").replace("sofia/internal/", "")
        cleaned = cleaned.split("@", maxsplit=1)[0]
        cleaned = "".join(character for character in cleaned if character.isdigit())
        if cleaned:
            return cleaned
    return str(fusion_agent["call_center_agent_uuid"])
