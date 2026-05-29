# Deploy em Debian 12

## 1. Preparar servidor

```bash
apt update
apt upgrade -y
apt install -y ca-certificates curl gnupg ufw fail2ban git
```

## 2. Instalar Docker

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## 3. Firewall do painel

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow from FUSIONPBX_PRIVATE_IP to any port 8000 proto tcp
ufw enable
```

Nao exponha PostgreSQL, Redis nem FreeSWITCH ESL publicamente.

## 4. Subir aplicacao

```bash
cd /opt
git clone YOUR_REPOSITORY_URL callcenter-control
cd callcenter-control
cp .env.example .env
nano .env
docker compose up -d --build
```

## 5. Primeiro acesso

- Painel: `http://SERVER_IP:8080`
- API: `http://SERVER_IP:8000/docs`

Usuario inicial:

- `admin@example.com`
- `ChangeMe123!`

Altere `APP_SECRET_KEY`, senhas do banco e senha inicial antes de producao.

## 6. Producao com HTTPS

Coloque Nginx ou Caddy na frente do painel e da API:

- `painel.seudominio.com` -> container `web:80`
- `api-painel.seudominio.com` -> container `api:8000`

Depois ajuste:

```env
APP_PUBLIC_URL=https://painel.seudominio.com
```

