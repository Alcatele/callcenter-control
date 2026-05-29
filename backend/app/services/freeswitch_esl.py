from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class FreeSwitchEvent:
    event_name: str
    tenant_domain: str | None
    channel_uuid: str | None
    payload: dict[str, str]


class FreeSwitchEslClient:
    def enabled(self) -> bool:
        return bool(settings.freeswitch_esl_host and settings.freeswitch_esl_password)

    async def run_forever(self) -> None:
        if not self.enabled():
            return
        raise NotImplementedError("Install an ESL client and implement event subscriptions here.")

