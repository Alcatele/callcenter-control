# Hetzner sizing para 100 agentes e 30 supervisores

## Distribuicao recomendada

Use **Debian 12 Bookworm**.

Motivos:

- FusionPBX e FreeSWITCH costumam ser mais previsiveis em Debian.
- Boa compatibilidade com PostgreSQL, Docker, Nginx e Fail2ban.
- Menos mudancas agressivas de pacotes que Ubuntu.

## Arquitetura recomendada

Para producao multi-tenant, separe:

1. **PBX/Media**
   - FusionPBX + FreeSWITCH
   - SIP/RTP
   - Gravacoes
   - CDR nativo

2. **Painel**
   - Este sistema
   - API, frontend, banco proprio e Redis
   - Acesso controlado ao FusionPBX

## Capacidade recomendada

### Painel separado

- 4 vCPU dedicadas
- 16 GB RAM
- 160 GB NVMe
- Debian 12

Na Hetzner Cloud, prefira Dedicated vCPU, linha CCX, em vez de shared vCPU.

### PBX/Media

Para 100 agentes, 30 supervisores, multi-tenant e gravacoes:

- 16 cores fortes ou vCPU dedicadas
- 64 GB RAM
- 2 x NVMe em RAID 1
- 1 Gbit/s
- Backup externo para gravacoes

Configuracao confortavel:

- Ryzen 9 ou EPYC
- 128 GB RAM
- 2 x NVMe Datacenter

## Observacao de latencia

Se os agentes e clientes estiverem no Brasil, a Hetzner na Europa pode gerar latencia perceptivel em SIP/RTP. O painel pode ficar na Hetzner sem problema, mas voz deve ser testada com chamadas reais antes da migracao.

## Gravacoes

Planeje armazenamento desde o inicio. Em call center, gravacoes podem crescer centenas de GB por mes. Use retencao, compressao e backup externo.

