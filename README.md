# Call Center Control

Sistema separado para monitoramento e configuracao de agentes, supervisores e filas em ambientes FusionPBX/FreeSWITCH multi-tenant.

## Stack

- Backend: FastAPI
- Frontend: React + Vite
- Banco: PostgreSQL
- Cache/eventos: Redis
- Realtime: WebSocket
- Integracao: FreeSWITCH ESL + leitura controlada do PostgreSQL do FusionPBX

## Modulos incluidos

- Autenticacao com JWT
- Tenants/domains
- Usuarios por perfil: admin, supervisor, agent
- Cadastro de agentes
- Cadastro de filas
- Vinculo agente/fila
- Dashboard de supervisao
- Endpoint WebSocket para eventos em tempo real
- Esqueleto de integracao FreeSWITCH ESL
- Docker Compose para desenvolvimento/producao simples

## Como iniciar

```bash
cp .env.example .env
docker compose up -d --build
```

Acesse:

- Frontend: `http://SERVER_IP:8080`
- API: `http://SERVER_IP:8000/docs`

Usuario inicial:

- Email: `admin@example.com`
- Senha: `ChangeMe123!`

Altere essa senha antes de usar em producao.

## Servidor recomendado

Use Debian 12. Para 100 agentes e 30 supervisores multi-tenant, recomendo separar:

- Servidor 1: FusionPBX/FreeSWITCH, SIP/RTP e gravacoes.
- Servidor 2: este painel, API, banco proprio e Redis.

Detalhes em `docs/hetzner-sizing.md`.

## Proximo passo no servidor

Siga `docs/deploy-debian12.md` para preparar o Debian 12, instalar Docker e subir o painel.
