# SEO Automation Service

Автоматизированный сервис для безопасного продвижения сайта через технический SEO-аудит, контроль ключевых запросов и генерацию плана работ. Сервис не накручивает поведенческие факторы, не имитирует пользователей и не обходит правила поисковых систем.

## Что делает сервис

- создает проекты с сайтом и списком ключевых запросов;
- обходит страницы сайта с учетом `robots.txt`;
- проверяет title, description, H1/H2, canonical, изображения без alt, внутренние ссылки и объем текста;
- считает вхождения ключевых запросов на страницах;
- формирует SEO-оценку, список проблем и практический план улучшений;
- хранит последний отчет в локальном JSON-файле;
- предоставляет веб-интерфейс, HTTP API и CLI.

## Почему это безопаснее накрутки

Сервисы, которые обещают быстрый рост через “роботов как людей”, обычно пытаются имитировать визиты, клики и поведенческие сигналы. Это рискованно: поисковые системы могут распознавать такие схемы и понижать сайт. Этот проект автоматизирует белые SEO-процессы: аудит, мониторинг, улучшение страниц и регулярный контроль качества.

## Быстрый запуск

```bash
python3 -m seo_service serve --host 0.0.0.0 --port 8080
```

Откройте `http://127.0.0.1:8080`, добавьте сайт и ключевые запросы, затем нажмите “Запустить аудит”.

По умолчанию данные сохраняются в `data/projects.json`. Путь можно изменить:

```bash
python3 -m seo_service serve --data-file /path/to/projects.json
```

Для production можно задавать настройки через переменные окружения:

```bash
SEO_SERVICE_HOST=0.0.0.0 SEO_SERVICE_PORT=8080 SEO_SERVICE_DATA=/var/lib/seo-automation-service/projects.json python3 -m seo_service serve
```

## API

Создать проект:

```bash
curl -X POST http://127.0.0.1:8080/api/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"Demo","site_url":"https://example.com","keywords":["seo","услуги"]}'
```

Запустить аудит:

```bash
curl -X POST http://127.0.0.1:8080/api/projects/<project_id>/audit
```

Получить проекты:

```bash
curl http://127.0.0.1:8080/api/projects
```

Проверить, что сервис жив:

```bash
curl http://127.0.0.1:8080/health
```

## CLI-аудит одной страницы

```bash
python3 -m seo_service audit https://example.com --keyword seo --keyword "поисковое продвижение"
```

## Тесты

```bash
python3 -m unittest discover -s tests -v
python3 scripts/smoke_test.py http://127.0.0.1:8080
```

## Размещение на Beget

Пошаговая инструкция для VPS/VDS Beget находится в `docs/BEGET_DEPLOY.md`.
Быстрая установка одной командой:

```bash
curl -fsSL https://raw.githubusercontent.com/Kolcoin/Colcoin/cursor/seo-automation-service-c1de/scripts/install_beget.sh | bash
```
