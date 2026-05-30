from dataclasses import dataclass
import socket

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

    def api(self, command: str) -> str:
        if not self.enabled():
            raise RuntimeError("FreeSWITCH ESL is not configured")

        with socket.create_connection(
            (settings.freeswitch_esl_host, settings.freeswitch_esl_port),
            timeout=10,
        ) as connection:
            connection.settimeout(10)
            self._read_frame(connection)
            self._send(connection, f"auth {settings.freeswitch_esl_password}")
            auth_response = self._read_frame(connection)
            if "+OK accepted" not in auth_response:
                raise RuntimeError("FreeSWITCH ESL authentication failed")

            self._send(connection, f"api {command}")
            return self._read_frame(connection)

    def list_callcenter_agents(self) -> list[dict[str, str]]:
        response = self.api("callcenter_config agent list")
        body = response.split("\n\n", maxsplit=1)[-1]
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines:
            return []

        headers = [part.strip() for part in lines[0].split("|")]
        agents: list[dict[str, str]] = []

        for line in lines[1:]:
            values = [part.strip() for part in line.split("|")]
            if len(values) != len(headers):
                continue
            agents.append(dict(zip(headers, values)))

        return agents

    async def run_forever(self) -> None:
        if not self.enabled():
            return
        raise NotImplementedError("Realtime ESL subscriptions will be implemented after polling sync.")

    def _send(self, connection: socket.socket, command: str) -> None:
        connection.sendall(f"{command}\n\n".encode())

    def _read_frame(self, connection: socket.socket) -> str:
        chunks: list[bytes] = []
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            payload = b"".join(chunks)
            if b"\n\n" not in payload:
                continue

            headers, _, body_start = payload.partition(b"\n\n")
            content_length = self._content_length(headers.decode(errors="replace"))
            if content_length is None:
                return payload.decode(errors="replace")

            while len(body_start) < content_length:
                next_chunk = connection.recv(4096)
                if not next_chunk:
                    break
                body_start += next_chunk
            return (headers + b"\n\n" + body_start).decode(errors="replace")

        return b"".join(chunks).decode(errors="replace")

    def _content_length(self, headers: str) -> int | None:
        for line in headers.splitlines():
            if line.lower().startswith("content-length:"):
                return int(line.split(":", maxsplit=1)[1].strip())
        return None
