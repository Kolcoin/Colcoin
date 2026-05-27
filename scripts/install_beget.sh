#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${SEO_SERVICE_REPO_URL:-https://github.com/Kolcoin/Colcoin.git}"
BRANCH="${SEO_SERVICE_BRANCH:-cursor/seo-automation-service-c1de}"
APP_DIR="${SEO_SERVICE_APP_DIR:-/opt/seo-automation-service}"
SERVER_NAME="${SEO_SERVICE_SERVER_NAME:-217.12.40.193}"

export DEBIAN_FRONTEND=noninteractive

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this installer as root." >&2
  exit 1
fi

apt update
apt install -y git python3 python3-venv nginx curl

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch origin "$BRANCH"
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" reset --hard "origin/$BRANCH"
else
  rm -rf "$APP_DIR"
  git clone -b "$BRANCH" --single-branch "$REPO_URL" "$APP_DIR"
fi

python3 -m venv "$APP_DIR/.venv"
mkdir -p /var/lib/seo-automation-service

cat >/etc/seo-automation-service.env <<'EOF'
SEO_SERVICE_HOST=127.0.0.1
SEO_SERVICE_PORT=8080
SEO_SERVICE_DATA=/var/lib/seo-automation-service/projects.json
SEO_SERVICE_MAX_PAGES=25
EOF

cp "$APP_DIR/deploy/seo-automation-service.service" /etc/systemd/system/seo-automation-service.service
systemctl daemon-reload
systemctl enable seo-automation-service
systemctl restart seo-automation-service

cat >/etc/nginx/sites-available/seo-automation-service <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name $SERVER_NAME _;

    location /health {
        proxy_pass http://127.0.0.1:8080/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/seo-automation-service /etc/nginx/sites-enabled/seo-automation-service
nginx -t
systemctl enable nginx
systemctl restart nginx

curl -fsS http://127.0.0.1:8080/health
printf '\nDone. Open http://%s\n' "$SERVER_NAME"
