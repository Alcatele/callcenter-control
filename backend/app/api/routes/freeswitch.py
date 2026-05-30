from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.models import Agent, AgentStatus, User
from app.db.session import get_db
from app.services.freeswitch_esl import FreeSwitchEslClient


router = APIRouter()


@router.post("/sync-agent-status")
def sync_agent_status(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    client = FreeSwitchEslClient()
    try:
        freeswitch_agents = client.list_callcenter_agents()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    updated = 0
    for freeswitch_agent in freeswitch_agents:
        name = freeswitch_agent.get("name") or freeswitch_agent.get("agent") or ""
        contact = freeswitch_agent.get("contact") or ""
        extension = extract_extension(name, contact)
        if not extension and not name:
            continue

        stmt = select(Agent)
        if extension:
            stmt = stmt.where(Agent.extension == extension)
        else:
            stmt = stmt.where(Agent.name == name)

        for agent in db.scalars(stmt):
            agent.status = map_agent_status(
                freeswitch_agent.get("status", ""),
                freeswitch_agent.get("state", ""),
            )
            updated += 1

    db.commit()
    return {"updated": updated, "found": len(freeswitch_agents)}


def extract_extension(name: str, contact: str) -> str:
    for value in (contact, name):
        cleaned = value.replace("user/", "").replace("sofia/internal/", "")
        cleaned = cleaned.split("@", maxsplit=1)[0]
        cleaned = "".join(character for character in cleaned if character.isdigit())
        if cleaned:
            return cleaned
    return ""


def map_agent_status(status: str, state: str) -> AgentStatus:
    normalized = f"{status} {state}".lower()
    if "break" in normalized or "pause" in normalized:
        return AgentStatus.paused
    if "receiving" in normalized or "ring" in normalized:
        return AgentStatus.ringing
    if "queue call" in normalized or "in a queue" in normalized or "busy" in normalized:
        return AgentStatus.in_call
    if "wrap" in normalized:
        return AgentStatus.wrap_up
    if "available" in normalized or "idle" in normalized or "waiting" in normalized:
        return AgentStatus.available
    return AgentStatus.offline
