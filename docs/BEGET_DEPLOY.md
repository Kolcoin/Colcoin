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
cp deploy/seo-automation-service.env.example /etc/seo-automation-service.env
```

Сервис использует только стандартную библиотеку Python, поэтому `pip install` не нужен. В файле `/etc/seo-automation-service.env` можно поменять порт, путь к данным и лимит страниц.

## 5. Установить systemd-сервис

```bash
cp deploy/seo-automation-service.service /etc/systemd/system/seo-automation-service.service
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
cp deploy/nginx.conf.example /etc/nginx/sites-available/seo-automation-service
nano /etc/nginx/sites-available/seo-automation-service
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
python3 scripts/smoke_test.py http://127.0.0.1:8080
```

Откройте домен в браузере, добавьте свой сайт и ключевые запросы, затем нажмите `Запустить аудит`.

## 9. Обновление сервиса

```bash
cd /opt/seo-automation-service
git pull origin cursor/seo-automation-service-c1de
systemctl restart seo-automation-service
```
