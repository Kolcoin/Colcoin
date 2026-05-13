#!/usr/bin/env python3
"""Генератор страниц справочника (/blog/{slug}/) для urban-ritual.ru."""
import json, re, html
from pathlib import Path

CANONICAL_BASE = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"
ROOT = Path(__file__).parent
OUT = ROOT / "blog"

# Категории → иконки (HTML emoji)
CATEGORY_ICONS = {
    "Срочная помощь": "🚨",
    "Документы и пособия": "📋",
    "Кремация": "⚱️",
    "Религиозные традиции": "✝️",
    "Кладбища": "🌳",
    "Памятники": "🪦",
    "Услуги": "🕊️",
}


def slugify_anchor(text: str) -> str:
    """Преобразовать заголовок h2 в slug для anchor."""
    s = re.sub(r'<[^>]+>', '', text).strip().lower()
    s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
    s = re.sub(r'[\s_]+', '-', s, flags=re.UNICODE)
    return s.strip('-')


def render_jsonld(a: dict) -> str:
    url = f"{CANONICAL_BASE}/blog/{a['slug']}/"
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["h1"],
        "description": a["description"],
        "datePublished": a["publishedDate"],
        "dateModified": a["modifiedDate"],
        "author": {"@type": "Organization", "@id": f"{CANONICAL_BASE}/#organization", "name": 'ООО «Городской Ритуал»'},
        "publisher": {"@type": "Organization", "@id": f"{CANONICAL_BASE}/#organization",
                      "name": 'ООО «Городской Ритуал»',
                      "logo": {"@type": "ImageObject", "url": f"{CANONICAL_BASE}/assets/logo.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "url": url,
        "image": f"{CANONICAL_BASE}/assets/og-default.jpg",
        "inLanguage": "ru-RU",
        "articleSection": a["category"],
        "keywords": ", ".join(a["keywords"]),
        "wordCount": sum(len(s["content"].split()) for s in a["sections"])
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', q["a"])}}
            for q in a["faq"]
        ]
    }
    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL_BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Справочник", "item": f"{CANONICAL_BASE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": a["h1"], "item": url},
        ]
    }
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n</script>'
        for b in (article, faq, bc)
    )


def render_toc(a: dict) -> str:
    items = []
    for s in a["sections"]:
        anchor = slugify_anchor(s["h2"])
        items.append(f'    <li><a href="#{anchor}">{s["h2"]}</a></li>')
    items.append('    <li><a href="#faq">Частые вопросы</a></li>')
    return "\n".join(items)


def render_sections(a: dict) -> str:
    parts = []
    for s in a["sections"]:
        anchor = slugify_anchor(s["h2"])
        # Content paragraphs (separated by \n\n)
        paragraphs = []
        for chunk in s["content"].split("\n\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            chunk = chunk.replace("\n", "<br>")
            paragraphs.append(f"      <p>{chunk}</p>")
        parts.append(
            f'    <section class="article-section" id="{anchor}">\n'
            f'      <h2>{s["h2"]}</h2>\n'
            + "\n".join(paragraphs) + "\n"
            f'    </section>'
        )
    return "\n\n".join(parts)


def render_faq(a: dict) -> str:
    items = []
    for q in a["faq"]:
        items.append(
            f'    <details class="article-faq__item">\n'
            f'      <summary>{q["q"]}</summary>\n'
            f'      <p>{q["a"]}</p>\n'
            f'    </details>'
        )
    return "\n".join(items)


def render_related(a: dict, all_articles: list) -> str:
    # Pick up to 3 related: same category first, then any others
    same_cat = [x for x in all_articles if x["category"] == a["category"] and x["slug"] != a["slug"]]
    other = [x for x in all_articles if x["category"] != a["category"] and x["slug"] != a["slug"]]
    related = (same_cat + other)[:3]
    cards = []
    for r in related:
        icon = CATEGORY_ICONS.get(r["category"], "📄")
        cards.append(
            f'      <a class="article-related__card" href="../{r["slug"]}/">\n'
            f'        <span class="article-related__icon" aria-hidden="true">{icon}</span>\n'
            f'        <span class="article-related__cat">{r["category"]}</span>\n'
            f'        <span class="article-related__title">{r["h1"]}</span>\n'
            f'        <span class="article-related__read">Читать ›</span>\n'
            f'      </a>'
        )
    return "\n".join(cards)


PAGE_TMPL = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#F7F5F2">

  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="keywords" content="{keywords}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{canonical}">

  <meta name="geo.region" content="RU">
  <meta name="geo.placename" content="Москва и Подмосковье">

  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{ogtitle}">
  <meta property="og:description" content="{ogdesc}">
  <meta property="og:locale" content="ru_RU">
  <meta property="article:published_time" content="{publishedDate}">
  <meta property="article:modified_time" content="{modifiedDate}">
  <meta property="article:section" content="{category}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../styles.css">

  {jsonld}

  <!-- Yandex.Metrika counter -->
  <script type="text/javascript">
      (function(m,e,t,r,i,k,a){{
          m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
          m[i].l=1*new Date();
          for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
          k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
      }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=109160037', 'ym');

      ym(109160037, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
  </script>
  <noscript><div><img src="https://mc.yandex.ru/watch/109160037" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
  <!-- /Yandex.Metrika counter -->

</head>
<body>

<a class="skip" href="#main">Перейти к содержимому</a>

<header class="topbar">
  <div class="container topbar__row">
    <a href="../../" class="logo" aria-label="Городской Ритуал — на главную">
      <span class="logo__mark" aria-hidden="true">ГР</span>
      <span class="logo__text">
        <span class="logo__name">Городской Ритуал</span>
        <span class="logo__sub">Москва и&nbsp;МО · круглосуточно</span>
      </span>
    </a>
    <nav class="nav" aria-label="Основная навигация">
      <a href="../../#services">Услуги</a>
      <a href="../../#prices">Цены</a>
      <a href="../../#moscow">Москва</a>
      <a href="../../#cities">Города МО</a>
      <a href="../../#cemeteries">Кладбища</a>
      <a href="../../#blog">Справочник</a>
    </nav>
    <div class="city-switcher" data-city-switcher>
      <button type="button" class="city-switcher__btn" aria-haspopup="listbox" aria-expanded="false">
        <span class="city-switcher__icon" aria-hidden="true">📍</span>
        <span class="city-switcher__label">Москва</span>
        <span class="city-switcher__chev" aria-hidden="true">▾</span>
      </button>
      <div class="city-switcher__pop" role="listbox" hidden>
        <input type="search" class="city-switcher__input" placeholder="Поиск города…" aria-label="Поиск города">
        <ul class="city-switcher__list"></ul>
      </div>
    </div>
    <div class="phone-block">
      <a class="phone-link" href="tel:{phone_tel}">
        <span class="phone-link__dot" aria-hidden="true"></span>
        <span class="phone-link__num">{phone_vis}</span>
        <span class="phone-link__sub">круглосуточно · мобильный</span>
      </a>
      <a class="phone-link phone-link--second" href="tel:+74951915128">
        <span class="phone-link__num">+7 (495) 191-51-28</span>
        <span class="phone-link__sub">офис · городской</span>
      </a>
    </div>
  </div>
</header>

<main id="main">

  <nav class="breadcrumbs" aria-label="Хлебные крошки">
    <div class="container">
      <a href="../../">Главная</a>
      <span aria-hidden="true">›</span>
      <a href="../../#blog">Справочник</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{h1}</span>
    </div>
  </nav>

  <article class="article">
    <header class="article__header">
      <div class="container">
        <div class="article__meta">
          <span class="article__category">{categoryIcon} {category}</span>
          <span class="article__sep" aria-hidden="true">·</span>
          <time datetime="{publishedDate}">{publishedDateRu}</time>
          <span class="article__sep" aria-hidden="true">·</span>
          <span class="article__read">⏱ {readTimeMin}&nbsp;мин чтения</span>
        </div>
        <h1>{h1}</h1>
        <p class="article__lead">{lead}</p>
        <div class="article__hero-cta">
          <a class="btn btn--primary" href="tel:{phone_tel}">📞 Срочно: {phone_vis}</a>
          <a class="btn btn--ghost" href="#main-content">Читать справочник ↓</a>
        </div>
      </div>
    </header>

    <div class="article__body container" id="main-content">
      <aside class="article__toc" aria-label="Оглавление">
        <div class="article__toc-title">📑 Содержание</div>
        <ol class="article__toc-list">
{toc}
        </ol>
      </aside>

      <div class="article__content">
{sections}

        <section class="article-section article-faq" id="faq">
          <h2>Частые вопросы</h2>
{faq}
        </section>

        <section class="article-cta">
          <div class="article-cta__inner">
            <h2>Нужна помощь прямо сейчас?</h2>
            <p>Дежурный ритуальный агент «Городской Ритуал» — на связи 24/7. Бесплатная консультация, выезд по&nbsp;Москве и&nbsp;МО в&nbsp;течение 30&nbsp;минут.</p>
            <div class="article-cta__buttons">
              <a class="btn btn--primary btn--lg" href="tel:{phone_tel}">📞 {phone_vis}</a>
              <a class="btn btn--ghost btn--lg" href="tel:+74951915128">+7 (495) 191-51-28</a>
            </div>
            <p class="article-cta__note">⏱ Звонок и&nbsp;консультация — бесплатно. Помогаем независимо от&nbsp;того, заказываете ли&nbsp;вы у&nbsp;нас услуги.</p>
          </div>
        </section>
      </div>
    </div>

    <section class="article-related">
      <div class="container">
        <h2>Читайте также</h2>
        <div class="article-related__grid">
{related}
        </div>
      </div>
    </section>
  </article>

</main>

<footer class="footer">
  <div class="container footer__grid">
    <div>
      <div class="footer__brand">Городской Ритуал — Москва и&nbsp;МО</div>
      <p class="footer__small">ООО «Городской Ритуал» · ОГРН 1147746000000 · ИНН 7700000000</p>
      <p class="footer__small">{phone_vis} · +7&nbsp;(495)&nbsp;191-51-28 · круглосуточно</p>
      <p class="footer__small">Куркинское шоссе, 9, Химки, Москва</p>
    </div>
    <div>
      <div class="footer__title">Справочник</div>
      <a href="../chto-delat-esli-umer-blizkiy/">Что делать при&nbsp;смерти близкого</a>
      <a href="../posobie-na-pogrebenie-2026/">Пособие на&nbsp;погребение 2026</a>
      <a href="../dokumenty-dlya-pohoron/">Документы для&nbsp;похорон</a>
      <a href="../../#blog">Все статьи</a>
    </div>
    <div>
      <div class="footer__title">Услуги</div>
      <a href="../../#services">Полный перечень услуг</a>
      <a href="../../#prices">Цены и&nbsp;пакеты</a>
      <a href="../../#cemeteries">Кладбища Москвы</a>
      <a href="../../#moscow">Москва · округа</a>
      <a href="../../#cities">Города МО</a>
    </div>
    <div>
      <div class="footer__title">Связь</div>
      <a href="tel:{phone_tel}">{phone_vis}</a>
      <a href="tel:+74951915128">+7&nbsp;(495)&nbsp;191-51-28</a>
      <a href="https://t.me/ritual_khimki" rel="nofollow noopener" target="_blank">Telegram</a>
      <a href="mailto:info@urban-ritual.ru">info@urban-ritual.ru</a>
    </div>
  </div>
  <div class="container footer__bottom">
    © 2026 ООО «Городской Ритуал». Все права защищены.
  </div>
</footer>

<a class="callback-fab" href="#callback-modal" aria-label="Заказать обратный звонок">
  <span class="callback-fab__icon" aria-hidden="true">📞</span>
  <span class="callback-fab__text">Обратный звонок</span>
</a>

<script src="../../script.js" defer></script>
</body>
</html>
"""


def format_date_ru(date_str: str) -> str:
    months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    y, m, d = date_str.split('-')
    return f"{int(d)} {months[int(m)-1]} {y}"


def build():
    OUT.mkdir(exist_ok=True)
    articles = json.load(open(ROOT / "data" / "blog.json", encoding="utf-8"))

    for a in articles:
        slug_dir = OUT / a["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)

        title = f"{a['title']} | Городской Ритуал"
        if len(title) > 100:
            title = a["title"]

        canonical = f"{CANONICAL_BASE}/blog/{a['slug']}/"

        page = PAGE_TMPL.format(
            title=title,
            description=a["description"],
            keywords=", ".join(a["keywords"]),
            canonical=canonical,
            ogtitle=a["h1"],
            ogdesc=a["description"],
            publishedDate=a["publishedDate"],
            publishedDateRu=format_date_ru(a["publishedDate"]),
            modifiedDate=a["modifiedDate"],
            category=a["category"],
            categoryIcon=CATEGORY_ICONS.get(a["category"], "📄"),
            readTimeMin=a["readTimeMin"],
            h1=a["h1"],
            lead=a["lead"],
            toc=render_toc(a),
            sections=render_sections(a),
            faq=render_faq(a),
            related=render_related(a, articles),
            phone_tel=PHONE_TEL,
            phone_vis=PHONE_VIS,
            jsonld=render_jsonld(a),
        )
        (slug_dir / "index.html").write_text(page, encoding="utf-8")

    # ─── Build index page /blog/ ───
    build_index(articles)
    print(f"Generated {len(articles)} blog articles + /blog/ index")


INDEX_TMPL = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#F7F5F2">
  <title>Справочник по похоронам — Москва и МО | Городской Ритуал</title>
  <meta name="description" content="Справочник «Городского Ритуала»: пошаговые инструкции, документы, пособия, традиции, кладбища, памятники. Всё, что нужно знать при организации похорон в Москве и Подмосковье.">
  <meta name="keywords" content="справочник похорон, инструкция при смерти, пособие на погребение, документы для похорон, кремация, отпевание, похороны Москва">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="https://urban-ritual.ru/blog/">

  <meta property="og:type" content="website">
  <meta property="og:url" content="https://urban-ritual.ru/blog/">
  <meta property="og:title" content="Справочник по похоронам — Москва и МО">
  <meta property="og:description" content="Пошаговые инструкции, документы, пособия, традиции, цены 2026 года.">
  <meta property="og:locale" content="ru_RU">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css">

  <script type="application/ld+json">
  {jsonld}
  </script>

  <!-- Yandex.Metrika counter -->
  <script type="text/javascript">
      (function(m,e,t,r,i,k,a){{
          m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
          m[i].l=1*new Date();
          for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
          k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
      }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=109160037', 'ym');

      ym(109160037, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
  </script>
  <noscript><div><img src="https://mc.yandex.ru/watch/109160037" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
  <!-- /Yandex.Metrika counter -->

</head>
<body>

<header class="topbar">
  <div class="container topbar__row">
    <a href="../" class="logo">
      <span class="logo__mark" aria-hidden="true">ГР</span>
      <span class="logo__text">
        <span class="logo__name">Городской Ритуал</span>
        <span class="logo__sub">Москва и&nbsp;МО · круглосуточно</span>
      </span>
    </a>
    <nav class="nav">
      <a href="../#services">Услуги</a>
      <a href="../#prices">Цены</a>
      <a href="../#moscow">Москва</a>
      <a href="../#cities">Города МО</a>
      <a href="../#cemeteries">Кладбища</a>
      <a href="./" class="is-active">Справочник</a>
    </nav>
    <div class="phone-block">
      <a class="phone-link" href="tel:{phone_tel}">
        <span class="phone-link__dot" aria-hidden="true"></span>
        <span class="phone-link__num">{phone_vis}</span>
        <span class="phone-link__sub">круглосуточно · мобильный</span>
      </a>
      <a class="phone-link phone-link--second" href="tel:+74951915128">
        <span class="phone-link__num">+7 (495) 191-51-28</span>
        <span class="phone-link__sub">офис · городской</span>
      </a>
    </div>
  </div>
</header>

<main>

  <nav class="breadcrumbs" aria-label="Хлебные крошки">
    <div class="container">
      <a href="../">Главная</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">Справочник</span>
    </div>
  </nav>

  <section class="blog-hero">
    <div class="container">
      <h1>Справочник по&nbsp;похоронам — Москва и&nbsp;МО</h1>
      <p class="blog-hero__lead">Пошаговые инструкции, документы, пособия 2026&nbsp;года, религиозные традиции, кладбища, памятники. Всё, что нужно знать при организации похорон в&nbsp;Москве и&nbsp;Подмосковье — собрано в&nbsp;одном месте.</p>
      <div class="blog-hero__stats">
        <div><b>{total}</b><span>статей</span></div>
        <div><b>7</b><span>разделов</span></div>
        <div><b>24/7</b><span>агент на&nbsp;связи</span></div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
{categories}
    </div>
  </section>

  <section class="article-cta">
    <div class="container">
      <div class="article-cta__inner">
        <h2>Не&nbsp;нашли ответа?</h2>
        <p>Позвоните дежурному ритуальному агенту — проконсультируем по&nbsp;любому вопросу, поможем разобраться в&nbsp;документах и&nbsp;ситуации.</p>
        <div class="article-cta__buttons">
          <a class="btn btn--primary btn--lg" href="tel:{phone_tel}">📞 {phone_vis}</a>
          <a class="btn btn--ghost btn--lg" href="tel:+74951915128">+7 (495) 191-51-28</a>
        </div>
      </div>
    </div>
  </section>

</main>

<footer class="footer">
  <div class="container footer__grid">
    <div>
      <div class="footer__brand">Городской Ритуал — Москва и&nbsp;МО</div>
      <p class="footer__small">ООО «Городской Ритуал» · ОГРН 1147746000000 · ИНН 7700000000</p>
      <p class="footer__small">{phone_vis} · +7&nbsp;(495)&nbsp;191-51-28 · круглосуточно</p>
    </div>
    <div>
      <div class="footer__title">Связь</div>
      <a href="tel:{phone_tel}">{phone_vis}</a>
      <a href="tel:+74951915128">+7&nbsp;(495)&nbsp;191-51-28</a>
      <a href="https://t.me/ritual_khimki" rel="nofollow noopener" target="_blank">Telegram</a>
      <a href="mailto:info@urban-ritual.ru">info@urban-ritual.ru</a>
    </div>
  </div>
  <div class="container footer__bottom">© 2026 ООО «Городской Ритуал». Все права защищены.</div>
</footer>

<a class="callback-fab" href="#callback-modal" aria-label="Заказать обратный звонок">
  <span class="callback-fab__icon" aria-hidden="true">📞</span>
  <span class="callback-fab__text">Обратный звонок</span>
</a>

<script src="../script.js" defer></script>
</body>
</html>
"""


def build_index(articles: list) -> None:
    # Group by category preserving first-seen order
    by_cat = {}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)

    chunks = []
    for cat, items in by_cat.items():
        icon = CATEGORY_ICONS.get(cat, "📄")
        cards = []
        for a in items:
            cards.append(
                f'        <a class="blog-card" href="{a["slug"]}/">\n'
                f'          <div class="blog-card__icon" aria-hidden="true">{icon}</div>\n'
                f'          <div class="blog-card__body">\n'
                f'            <h3>{a["h1"]}</h3>\n'
                f'            <p>{a["description"]}</p>\n'
                f'            <span class="blog-card__meta">⏱ {a["readTimeMin"]}&nbsp;мин · Читать ›</span>\n'
                f'          </div>\n'
                f'        </a>'
            )
        chunks.append(
            f'      <div class="blog-category">\n'
            f'        <h2 class="blog-category__title"><span aria-hidden="true">{icon}</span> {cat}</h2>\n'
            f'        <div class="blog-grid">\n'
            + "\n".join(cards) + "\n"
            f'        </div>\n'
            f'      </div>'
        )

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Справочник по похоронам — Москва и МО",
        "description": "Пошаговые инструкции, документы, пособия, традиции, кладбища.",
        "url": f"{CANONICAL_BASE}/blog/",
        "publisher": {"@type": "Organization", "@id": f"{CANONICAL_BASE}/#organization",
                      "name": "ООО «Городской Ритуал»"},
        "hasPart": [
            {"@type": "Article", "headline": a["h1"], "url": f"{CANONICAL_BASE}/blog/{a['slug']}/",
             "description": a["description"], "datePublished": a["publishedDate"]}
            for a in articles
        ]
    }, ensure_ascii=False, indent=2)

    page = INDEX_TMPL.format(
        categories="\n".join(chunks),
        total=len(articles),
        phone_tel=PHONE_TEL,
        phone_vis=PHONE_VIS,
        jsonld=jsonld,
    )
    (OUT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    build()
