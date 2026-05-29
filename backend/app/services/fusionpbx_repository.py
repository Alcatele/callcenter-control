from sqlalchemy import create_engine, text

from app.core.config import settings


class FusionPbxRepository:
    def __init__(self) -> None:
        self._engine = create_engine(settings.fusionpbx_db_url) if settings.fusionpbx_db_url else None

    def enabled(self) -> bool:
        return self._engine is not None

    def list_domains(self) -> list[dict[str, str]]:
        if not self._engine:
            return []
        query = text(
            """
            select domain_uuid, domain_name
            from v_domains
            where domain_enabled = 'true'
            order by domain_name
            """
        )
        with self._engine.connect() as conn:
            return [
                {
                    "domain_uuid": str(row._mapping["domain_uuid"]),
                    "domain_name": str(row._mapping["domain_name"]),
                }
                for row in conn.execute(query)
            ]

    def list_queues(self) -> list[dict[str, str | None]]:
        if not self._engine:
            return []
        query = text(
            """
            select
                call_center_queue_uuid,
                domain_uuid,
                queue_name,
                queue_extension
            from v_call_center_queues
            order by queue_name
            """
        )
        with self._engine.connect() as conn:
            return [
                {
                    "call_center_queue_uuid": str(row._mapping["call_center_queue_uuid"]),
                    "domain_uuid": str(row._mapping["domain_uuid"]),
                    "queue_name": str(row._mapping["queue_name"]),
                    "queue_extension": (
                        str(row._mapping["queue_extension"])
                        if row._mapping["queue_extension"] is not None
                        else None
                    ),
                    "queue_enabled": "true",
                }
                for row in conn.execute(query)
            ]

    def list_agents(self) -> list[dict[str, str | None]]:
        if not self._engine:
            return []
        query = text(
            """
            select
                call_center_agent_uuid,
                domain_uuid,
                agent_name,
                agent_id,
                agent_contact,
                agent_status
            from v_call_center_agents
            order by agent_name
            """
        )
        with self._engine.connect() as conn:
            return [
                {
                    "call_center_agent_uuid": str(row._mapping["call_center_agent_uuid"]),
                    "domain_uuid": str(row._mapping["domain_uuid"]),
                    "agent_name": str(row._mapping["agent_name"]),
                    "agent_id": (
                        str(row._mapping["agent_id"])
                        if row._mapping["agent_id"] is not None
                        else None
                    ),
                    "agent_contact": (
                        str(row._mapping["agent_contact"])
                        if row._mapping["agent_contact"] is not None
                        else None
                    ),
                    "agent_status": (
                        str(row._mapping["agent_status"])
                        if row._mapping["agent_status"] is not None
                        else None
                    ),
                }
                for row in conn.execute(query)
            ]
