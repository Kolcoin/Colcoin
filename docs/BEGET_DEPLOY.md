# Размещение SEO Automation Service на Beget

Инструкция рассчитана на VPS/VDS Beget с Ubuntu/Debian и доступом по SSH. Для обычного shared-хостинга Python-сервис с постоянным процессом обычно не подходит: нужен VPS или Beget Cloud.

## 1. Подключиться к серверу

```bash
ssh root@SERVER_IP
```

## 2. Установить базовые пакеты

```bash
apt update
apt install -y git python3 python3-venv nginx
```

## 3. Скачать проект

```bash
cd /opt
git clone https://github.com/Kolcoin/Colcoin.git seo-automation-service
cd seo-automation-service
git checkout cursor/seo-automation-service-c1de
```

## 4. Создать окружение и директорию данных

```bash
python3 -m venv .venv
mkdir -p /var/lib/seo-automation-service
```

Сервис использует только стандартную библиотеку Python, поэтому `pip install` не нужен.

## 5. Создать systemd-сервис

```bash
cat >/etc/systemd/system/seo-automation-service.service <<'EOF'
[Unit]
Description=SEO Automation Service
After=network.target

[Service]
WorkingDirectory=/opt/seo-automation-service
ExecStart=/opt/seo-automation-service/.venv/bin/python -m seo_service serve --host 127.0.0.1 --port 8080 --data-file /var/lib/seo-automation-service/projects.json --max-pages 25
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

Запустить сервис:

```bash
systemctl daemon-reload
systemctl enable --now seo-automation-service
systemctl status seo-automation-service
```

## 6. Настроить Nginx

Замените `seo.example.ru` на ваш домен или поддомен.

```bash
cat >/etc/nginx/sites-available/seo-automation-service <<'EOF'
server {
    listen 80;
    server_name seo.example.ru;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -s /etc/nginx/sites-available/seo-automation-service /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## 7. Подключить домен

В панели Beget добавьте A-запись:

- имя: `seo` или нужный поддомен;
- значение: IP вашего VPS;
- TTL: по умолчанию.

После обновления DNS сайт будет доступен по `http://seo.example.ru`.

## 8. Проверить работу

```bash
curl http://127.0.0.1:8080/api/projects
```

Откройте домен в браузере, добавьте свой сайт и ключевые запросы, затем нажмите `Запустить аудит`.

## 9. Обновление сервиса

```bash
cd /opt/seo-automation-service
git pull origin cursor/seo-automation-service-c1de
systemctl restart seo-automation-service
```
