# FreeSWITCH ESL para status de agentes

Este guia habilita o Event Socket do FreeSWITCH para o painel consultar status dos agentes.

## 1. No servidor FusionPBX

Edite o Event Socket:

```bash
nano /etc/freeswitch/autoload_configs/event_socket.conf.xml
```

Use uma senha forte e limite o IP permitido. Exemplo:

```xml
<configuration name="event_socket.conf" description="Socket Client">
  <settings>
    <param name="nat-map" value="false"/>
    <param name="listen-ip" value="0.0.0.0"/>
    <param name="listen-port" value="8021"/>
    <param name="password" value="SENHA_ESL_FORTE_AQUI"/>
    <param name="apply-inbound-acl" value="painel_acl"/>
  </settings>
</configuration>
```

## 2. Criar ACL para o IP do painel

Edite:

```bash
nano /etc/freeswitch/autoload_configs/acl.conf.xml
```

Adicione uma lista semelhante dentro de `<network-lists>`:

```xml
<list name="painel_acl" default="deny">
  <node type="allow" cidr="IP_DO_SERVIDOR_PAINEL/32"/>
</list>
```

## 3. Liberar firewall do FusionPBX

Se o FusionPBX usa iptables direto, libere somente o IP do painel:

```bash
iptables -I INPUT -p tcp -s IP_DO_SERVIDOR_PAINEL --dport 8021 -j ACCEPT
netfilter-persistent save
```

## 4. Recarregar FreeSWITCH

```bash
fs_cli -x "reloadacl"
fs_cli -x "reload mod_event_socket"
```

Se necessario:

```bash
systemctl restart freeswitch
```

## 5. Configurar o painel

No servidor do painel:

```bash
cd /opt/callcenter-control
nano .env
```

Configure:

```env
FREESWITCH_ESL_HOST=95.216.185.239
FREESWITCH_ESL_PORT=8021
FREESWITCH_ESL_PASSWORD=SENHA_ESL_FORTE_AQUI
```

Depois:

```bash
docker compose up -d
```

## 6. Teste

No painel, clique no botao **Status** no topo.

Ou pelo terminal:

```bash
docker compose exec api python -c "from app.services.freeswitch_esl import FreeSwitchEslClient; print(FreeSwitchEslClient().list_callcenter_agents())"
```

