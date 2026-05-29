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
