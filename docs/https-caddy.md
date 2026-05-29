# HTTPS com painel.alcatele.com.br

Este guia publica o painel em `https://painel.alcatele.com.br` usando Caddy no Debian 12.

## 1. DNS

No provedor DNS do dominio `alcatele.com.br`, crie:

```text
Tipo: A
Nome: painel
Valor: IP_PUBLICO_DO_SERVIDOR
TTL: 300
```

Aguarde propagar. Teste:

```bash
dig +short painel.alcatele.com.br
```

O resultado deve ser o IP publico do servidor.

## 2. Instalar Caddy

```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy
```

## 3. Configurar Caddy

Edite:

```bash
nano /etc/caddy/Caddyfile
```

Conteudo:

```caddyfile
painel.alcatele.com.br {
  encode zstd gzip
  reverse_proxy 127.0.0.1:8080
}
```

Valide e reinicie:

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
systemctl status caddy
```

## 4. Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

Nao exponha `8000`, `8080`, PostgreSQL nem Redis publicamente.

## 5. Atualizar APP_PUBLIC_URL

No projeto:

```bash
cd /opt/callcenter-control
nano .env
```

Use:

```env
APP_PUBLIC_URL=https://painel.alcatele.com.br
```

Depois:

```bash
docker compose up -d --build
```

## 6. Acesso

Abra:

```text
https://painel.alcatele.com.br
```

