# Integracao com FusionPBX

## Principios

Este sistema fica separado do FusionPBX.

- Nao altera telas nativas.
- Nao mexe em tabelas criticas sem controle.
- Usa banco proprio para permissoes e estado operacional.
- Le dados do FusionPBX quando necessario.
- Usa FreeSWITCH ESL para eventos em tempo real.

## Banco do FusionPBX

Crie um usuario somente leitura no PostgreSQL do FusionPBX:

```sql
CREATE USER callcenter_panel_read WITH PASSWORD 'strong-password';
GRANT CONNECT ON DATABASE fusionpbx TO callcenter_panel_read;
GRANT USAGE ON SCHEMA public TO callcenter_panel_read;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO callcenter_panel_read;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO callcenter_panel_read;
```

## FreeSWITCH ESL

Troque a senha padrao do Event Socket e restrinja IPs permitidos.

Variaveis:

```env
FREESWITCH_ESL_HOST=fusionpbx-host
FREESWITCH_ESL_PORT=8021
FREESWITCH_ESL_PASSWORD=ClueCon
```

## Multi-tenant

Cada tenant do painel deve mapear para um `domain_uuid` do FusionPBX. Toda consulta operacional precisa filtrar por `tenant_id`.

