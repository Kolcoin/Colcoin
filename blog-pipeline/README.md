# Blog Pipeline (topics -> HTML -> blog index -> sitemap)

Готовый конвейер для массового пополнения блога:

1. Таблица тем (CSV)  
2. Генерация HTML-страниц в `/seo/`  
3. Автодобавление записей в `window.REALTY_BLOG_POSTS` в `realty-data.js`  
4. Автодобавление URL в `sitemap.xml`

---

## Быстрый старт

### 1) Подготовь CSV

Скопируй `topics.example.csv` в новый файл, например:

`blog-pipeline/topics-2026-04-28.csv`

Колонки (достаточно минимального набора):

- `enabled` — `1/0` (обрабатывать строку или нет)
- `slug` — часть URL, только латиница/цифры/дефисы
- `title` — заголовок статьи (H1 + title)
- `category` — категория для карточки блога (`Районы`, `ЖК`, `Покупка`, `Ипотека`, `Инвестиции`, `Застройщики`, `Юридическое`, `Гайды`, `Аналитика`)
- `excerpt` — короткое описание для карточки

Поддерживаемые дополнительные поля:

- `date` — дата `YYYY-MM-DD` (если пусто, ставится текущая)
- `keywords` или `focus_keyword` — ключи для meta keywords
- `target_dir` — папка публикации (`seo` по умолчанию)
- `priority` — приоритет sitemap (`0.76` по умолчанию)
- `changefreq` — частота обновления sitemap (`weekly` по умолчанию)

### 2) Запусти конвейер

```bash
python3 blog-pipeline/run_pipeline.py --csv blog-pipeline/topics-2026-04-28.csv
```

или с алиасами:

```bash
python3 blog-pipeline/run_pipeline.py --topics blog-pipeline/topics-2026-04-28.csv --base-url https://xn--h1aagfvid9b.xn--p1ai
```

По умолчанию обновляются:

- `seo/` (создаются/обновляются HTML)
- `realty-data.js`
- `sitemap.xml`

---

## Режим проверки (без записи)

```bash
python3 blog-pipeline/run_pipeline.py --topics blog-pipeline/topics-2026-04-28.csv --base-url https://xn--h1aagfvid9b.xn--p1ai --dry-run
```

---

## Что делает скрипт

### 1. Генерация SEO-страниц

Для каждой строки CSV создаёт файл:

`/seo/{slug}.html`

Содержит:
- SEO meta (title/description/keywords/canonical/og/twitter)
- JSON-LD (`WebPage` + `BreadcrumbList`)
- H1 + контентные блоки + FAQ + CTA
- внутренние ссылки на `catalog/districts/developers/mortgage/blog`

### 2. Обновление `window.REALTY_BLOG_POSTS`

В `realty-data.js`:
- добавляет новые записи
- обновляет существующие по `id = slug`
- сортирует по дате (новые сверху)

### 3. Обновление `sitemap.xml`

- добавляет URL вида `https://xn--h1aagfvid9b.xn--p1ai/seo/{slug}.html`
- если URL уже есть — не дублирует
- ставит `lastmod` из CSV даты

---

## После запуска

1. Проверь diff:

```bash
git diff -- seo realty-data.js sitemap.xml
```

2. Залей изменённые файлы на Beget:
- новые/обновлённые `seo/*.html`
- `realty-data.js`
- `sitemap.xml`

3. Проверка live:
- `https://xn--h1aagfvid9b.xn--p1ai/blog.html?v={timestamp}`
- `https://xn--h1aagfvid9b.xn--p1ai/sitemap.xml?v={timestamp}`

---

## Ограничения

- `slug` должен быть уникальным.
- Формат даты строго `YYYY-MM-DD`.
- Скрипт не удаляет старые статьи и старые URL из sitemap (только добавляет/обновляет).

