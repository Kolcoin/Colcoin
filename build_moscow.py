#!/usr/bin/env python3
"""Генератор страниц районов и АО Москвы."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "moscow.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "moscow"

CANONICAL_BASE = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"


def jsonld(name, name_gen, slug, lat, lng, parent_breadcrumb=None, is_ao=False):
    org = {
        "@context": "https://schema.org",
        "@type": "FuneralHome",
        "@id": f"{CANONICAL_BASE}/moscow/{slug}/#org",
        "name": f"Городской Ритуал — {name}",
        "parentOrganization": {"@id": f"{CANONICAL_BASE}/#organization"},
        "url": f"{CANONICAL_BASE}/moscow/{slug}/",
        "telephone": PHONE_TEL,
        "priceRange": "₽₽",
        "areaServed": {"@type": "Place", "name": f"{name}, Москва"},
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Москва",
            "addressRegion": "Москва",
            "addressCountry": "RU"
        },
        "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "opens": "00:00", "closes": "23:59"
        }
    }
    bc_items = [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL_BASE}/"},
        {"@type": "ListItem", "position": 2, "name": "Москва", "item": f"{CANONICAL_BASE}/#moscow"},
    ]
    if parent_breadcrumb:
        bc_items.append({"@type": "ListItem", "position": 3, "name": parent_breadcrumb["name"], "item": parent_breadcrumb["url"]})
        bc_items.append({"@type": "ListItem", "position": 4, "name": name, "item": f"{CANONICAL_BASE}/moscow/{slug}/"})
    else:
        bc_items.append({"@type": "ListItem", "position": 3, "name": name, "item": f"{CANONICAL_BASE}/moscow/{slug}/"})

    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": bc_items
    }
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n</script>'
        for b in (org, bc)
    )


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

  <meta name="geo.region" content="RU-MOW">
  <meta name="geo.placename" content="{name}, Москва">
  <meta name="geo.position" content="{lat};{lng}">
  <meta name="ICBM" content="{lat}, {lng}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{ogtitle}">
  <meta property="og:locale" content="ru_RU">

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

<header class="topbar">
  <div class="container topbar__row">
    <a href="../../" class="logo">
      <span class="logo__mark" aria-hidden="true">ГР</span>
      <span class="logo__text">
        <span class="logo__name">Городской Ритуал</span>
        <span class="logo__sub">{name} · круглосуточно</span>
      </span>
    </a>
    <nav class="nav">
      <a href="../../#services">Услуги</a>
      <a href="../../#prices">Цены</a>
      <a href="../../#moscow">Москва</a>
      <a href="../../#cities">Города МО</a>
      <a href="../../#cemeteries">Кладбища</a>
      <a href="../../#faq">Вопросы</a>
    </nav>
    <div class="city-switcher" data-city-switcher>
      <button type="button" class="city-switcher__btn" aria-haspopup="listbox" aria-expanded="false">
        <span class="city-switcher__icon" aria-hidden="true">📍</span>
        <span class="city-switcher__label">{name}</span>
        <span class="city-switcher__chev" aria-hidden="true">▾</span>
      </button>
      <div class="city-switcher__pop" role="listbox" hidden>
        <input type="search" class="city-switcher__input" placeholder="Поиск города…">
        <ul class="city-switcher__list"></ul>
      </div>
    </div>
    <a class="phone-link" href="tel:{phone_tel}">
      <span class="phone-link__dot" aria-hidden="true"></span>
      <span class="phone-link__num">{phone_vis}</span>
      <span class="phone-link__sub">круглосуточно, бесплатно</span>
    </a>
  </div>
</header>

<main id="main">

  <nav class="breadcrumbs">
    <div class="container">
      <a href="../../">Главная</a>
      <span aria-hidden="true">›</span>
      <a href="../../#moscow">Москва</a>
      {parentBreadcrumb}
      <span aria-hidden="true">›</span>
      <span aria-current="page">{name}</span>
    </div>
  </nav>

  <section class="hero hero--district">
    <div class="container hero__grid">
      <div class="hero__text">
        <div class="hero__eyebrow">{eyebrow}</div>
        <h1>{h1}</h1>
        <p class="hero__lead">
          {lead}
        </p>
        <div class="hero__cta">
          <a class="btn btn--primary" href="tel:{phone_tel}">Вызвать агента</a>
          <a class="btn btn--ghost" href="#services">Все услуги</a>
        </div>
        <ul class="hero__badges">
          <li>📍 Москва, {name}</li>
          <li>Выезд за&nbsp;{minutes}&nbsp;минут</li>
          <li>Договор и&nbsp;чек</li>
          <li>24 / 7</li>
        </ul>
      </div>
      <aside class="hero__card">
        <h2 class="hero__card-title">{name} — для нас приоритет</h2>
        <ul class="plain">
          <li>Выезд агента — <b>{minutes} минут</b></li>
          <li>Морг: {nearMorgue}</li>
          <li>Кладбища: {nearCemetery}</li>
          <li>Кремация: Хованский, Митинский, Николо-Архангельский</li>
          <li>Документы — берём на&nbsp;себя</li>
        </ul>
        <a class="btn btn--primary btn--block" href="tel:{phone_tel}">Позвонить</a>
      </aside>
    </div>
  </section>

  <section id="services" class="section">
    <div class="container district-text">
      <h2>Ритуальные услуги {namePrep}</h2>
      <p>{specific}</p>
      <p>Наш ритуальный агент приедет к&nbsp;вам в&nbsp;квартиру, частный дом или больницу
        {namePrep} за&nbsp;{minutes}&nbsp;минут после звонка. Услуга выезда бесплатная, без обязательств.
        Согласуем смету, оформим документы и&nbsp;организуем перевозку умершего в&nbsp;{nearMorgue}.</p>

      <h3>Кладбища рядом с {namePrep}</h3>
      <p>Ближайшие действующие кладбища: <b>{nearCemetery}</b>. Помогаем оформить участок, согласовать день и&nbsp;час захоронения с&nbsp;администрацией, провести копку могилы и&nbsp;церемонию прощания.</p>

      <h3>Кремация для жителей {nameGen}</h3>
      <p>Кремация в&nbsp;Москве осуществляется в&nbsp;Хованском, Митинском, Николо-Архангельском или Донском крематории. Сопровождаем процесс полностью: гроб для кремации, оформление документов, доставка урны с&nbsp;прахом.</p>

      <h3>Отпевание и&nbsp;прощание {namePrep}</h3>
      <p>Помогаем согласовать отпевание в&nbsp;ближайших к&nbsp;{namePrep} храмах, организуем гражданскую панихиду в&nbsp;зале прощания, музыкальное и&nbsp;цветочное оформление церемонии.</p>

      <h3>Перевозка умершего {namePrep}</h3>
      <p>Спецавтомобиль 24/7 для перевозки тела из&nbsp;квартиры или больницы в&nbsp;морг, из&nbsp;морга — в&nbsp;ритуальный зал, храм или на&nbsp;кладбище. Также организуем перевозку по&nbsp;РФ и&nbsp;за&nbsp;рубеж.</p>

      <h3>Документы о&nbsp;смерти — берём на&nbsp;себя</h3>
      <p>Гербовое свидетельство о&nbsp;смерти в&nbsp;ЗАГСе, справка для соцпособия, оформление участка на&nbsp;кладбище, разрешение на&nbsp;перевозку. Берём на&nbsp;себя — вы&nbsp;никуда не&nbsp;едете.</p>
    </div>
  </section>

  {areasGrid}

  <section class="section section--alt">
    <div class="container">
      <header class="section__head">
        <h2>Цены {namePrep}</h2>
        <p>Все цены фиксируются в&nbsp;договоре. Доплат «на&nbsp;месте» не&nbsp;возникает.</p>
      </header>
      <div class="grid grid--3 plans">
        <article class="plan">
          <header class="plan__head"><h3>Эконом</h3><p class="plan__price">от <b>34&nbsp;900&nbsp;₽</b></p><p class="plan__sub">социальные похороны</p></header>
          <ul class="plan__list"><li>Выезд агента, документы</li><li>Гроб обитый, ритуальный набор</li><li>Катафалк {namePrep}</li><li>Бригада из&nbsp;4&nbsp;человек</li><li>Венок и&nbsp;лента</li></ul>
          <a class="btn btn--ghost btn--block" href="tel:{phone_tel}">Уточнить состав</a>
        </article>
        <article class="plan plan--featured">
          <div class="plan__badge">Выбирают чаще</div>
          <header class="plan__head"><h3>Стандарт</h3><p class="plan__price">от <b>68&nbsp;500&nbsp;₽</b></p><p class="plan__sub">похороны под ключ</p></header>
          <ul class="plan__list"><li>Всё из&nbsp;«Эконом»</li><li>Гроб лакированный</li><li>Подготовка тела в&nbsp;морге</li><li>2&nbsp;венка, корзина цветов</li><li>Координатор церемонии</li><li>Помощь с&nbsp;соц. пособием</li></ul>
          <a class="btn btn--primary btn--block" href="tel:{phone_tel}">Заказать пакет</a>
        </article>
        <article class="plan">
          <header class="plan__head"><h3>Премиум</h3><p class="plan__price">от <b>129&nbsp;000&nbsp;₽</b></p><p class="plan__sub">полное сопровождение</p></header>
          <ul class="plan__list"><li>Всё из&nbsp;«Стандарт»</li><li>Премиум-гроб</li><li>Зал прощания и&nbsp;отпевание</li><li>Цветочное оформление</li><li>Поминальный обед</li><li>Персональный распорядитель</li></ul>
          <a class="btn btn--ghost btn--block" href="tel:{phone_tel}">Обсудить детали</a>
        </article>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container faq">
      <header class="section__head">
        <h2>Частые вопросы — {name}</h2>
      </header>
      <details open>
        <summary>Сколько ехать ритуальному агенту {namePrep}?</summary>
        <p>В&nbsp;среднем {minutes}&nbsp;минут с&nbsp;момента звонка. Работаем по&nbsp;всей Москве круглосуточно, бесплатный выезд.</p>
      </details>
      <details>
        <summary>На каких кладбищах хоронят жителей {nameGen}?</summary>
        <p>Ближайшие действующие кладбища: {nearCemetery}. Также можно выбрать любое кладбище Москвы или МО — поможем оформить участок.</p>
      </details>
      <details>
        <summary>В каком морге работаем по {namePrep}?</summary>
        <p>Основной — {nearMorgue}. Также сотрудничаем с&nbsp;Бюро СМЭ ДЗМ, моргами крупных ГКБ Москвы.</p>
      </details>
      <details>
        <summary>Можно ли сделать кремацию вместо захоронения?</summary>
        <p>Да. В&nbsp;Москве работают 4 крематория: Хованский, Митинский, Николо-Архангельский, Донской. Полное сопровождение и&nbsp;доставка праха.</p>
      </details>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container contacts-cta">
      <div>
        <h2>Связаться с&nbsp;нами — {name}</h2>
        <p>Круглосуточно. Звонок и&nbsp;выезд агента — бесплатно, без обязательств.</p>
      </div>
      <a class="btn btn--primary btn--xl" href="tel:{phone_tel}">{phone_vis}</a>
    </div>
  </section>

</main>

<a class="fab" href="tel:{phone_tel}">
  <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.4 21 3 13.6 3 4.5c0-.6.4-1 1-1H7.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .7-.2 1L6.6 10.8Z"/></svg>
  <span>Позвонить</span>
</a>

<footer class="footer">
  <div class="container footer__row">
    <div>
      <div class="footer__brand">Городской Ритуал — Москва и&nbsp;МО</div>
      <div class="footer__legal">ООО «Городской Ритуал» · ОГРН&nbsp;1147746000000 · ИНН&nbsp;7700000000</div>
    </div>
    <nav class="footer__nav">
      <a href="../../">Главная</a>
      <a href="../../#cities">Все города</a>
      <a href="../../#cemeteries">Кладбища</a>
    </nav>
    <div class="footer__copy">© 2014–2026. Все права защищены.</div>
  </div>
</footer>

<script src="../../cities-data.js" defer></script>
<script src="../../script.js" defer></script>
</body>
</html>
"""


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # AO pages
    for ao in DATA["districts"]:
        slug_dir = OUT_DIR / ao["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)

        areas_in_ao = [a for a in DATA["areas"] if a["ao"] == ao["slug"]]
        areas_html = ""
        if areas_in_ao:
            items = "\n".join(
                f'<li><a href="../{a["slug"]}/" class="cgrid__inner"><span class="cgrid__name">{a["name"]}</span><span class="cgrid__min">район</span></a></li>'
                for a in areas_in_ao
            )
            areas_html = f"""
  <section class="section">
    <div class="container">
      <header class="section__head">
        <h2>Районы {ao['name']} — выезжаем в каждый</h2>
        <p>{len(areas_in_ao)} района округа. Кликните на свой район — подробная информация о выезде и услугах.</p>
      </header>
      <ul class="cities-grid">{items}</ul>
    </div>
  </section>"""

        kw = [
            f"ритуальные услуги {ao['name']}",
            f"похороны {ao['name']} Москва",
            f"кремация {ao['name']}",
            f"ритуальный агент {ao['name']}",
            f"выезд ритуального агента {ao['name']}",
            f"организация похорон {ao['name']}",
            f"ритуальное агентство {ao['name']}",
            f"перевозка умершего {ao['name']}",
            f"кладбища {ao['name']}",
            f"отпевание {ao['name']}",
            f"гражданская панихида {ao['name']}",
        ]

        title = f"Ритуальные услуги в {ao['name']} (Москва) 24/7 — Городской Ритуал"
        desc = f"Организация похорон, кремации, отпевания в {ao['name']} Москвы. Выезд агента бесплатно за {ao['minutes']} минут. Морги, кладбища округа. ☎ {PHONE_VIS}"

        html = PAGE_TMPL.format(
            canonical=f"{CANONICAL_BASE}/moscow/{ao['slug']}/",
            title=title, description=desc, ogtitle=title,
            keywords=", ".join(kw),
            name=ao['name'],
            namePrep=f"в {ao['name']}",
            nameGen=ao['name'],
            eyebrow=f"Ритуальное агентство · {ao['fullName']} · круглосуточно",
            h1=f"Ритуальные услуги в {ao['name']} Москвы — {ao['fullName']}",
            lead=f"<b>Выезд ритуального агента в {ao['name']} за {ao['minutes']} минут — бесплатно, круглосуточно.</b> Полная организация похорон, кремации, отпевания и поминального обеда. Работаем по всем районам округа.",
            specific=ao['specific'],
            lat=ao['lat'], lng=ao['lng'],
            minutes=ao['minutes'],
            nearMorgue="ближайшая ГКБ",
            nearCemetery=ao['specific'].split('Ближайш')[1] if 'Ближайш' in ao['specific'] else 'все кладбища Москвы',
            areasGrid=areas_html,
            parentBreadcrumb='',
            phone_tel=PHONE_TEL, phone_vis=PHONE_VIS,
            jsonld=jsonld(ao['name'], ao['name'], ao['slug'], ao['lat'], ao['lng'], is_ao=True),
        )
        (slug_dir / "index.html").write_text(html, encoding="utf-8")

    # Area pages
    for a in DATA["areas"]:
        slug_dir = OUT_DIR / a["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)

        ao = next(x for x in DATA["districts"] if x["slug"] == a["ao"])

        kw = [
            f"ритуальные услуги {a['name']}",
            f"похороны {a['name']}",
            f"кремация {a['name']}",
            f"ритуальный агент {a['name']}",
            f"выезд ритуального агента {a['name']}",
            f"организация похорон {a['name']}",
            f"перевозка умершего {a['name']}",
            f"ритуальное агентство {a['name']}",
            f"морг {a['name']}",
            f"кладбища {a['name']}",
            f"отпевание {a['name']}",
            f"гражданская панихида {a['name']}",
        ]

        title = f"Ритуальные услуги в районе {a['name']} (Москва) — Городской Ритуал"
        desc = f"Похороны и кремация в районе {a['name']} ({ao['name']}, Москва). Выезд ритуального агента бесплатно за {ao['minutes']} минут. Помощь с документами. ☎ {PHONE_VIS}"

        html = PAGE_TMPL.format(
            canonical=f"{CANONICAL_BASE}/moscow/{a['slug']}/",
            title=title, description=desc, ogtitle=title,
            keywords=", ".join(kw),
            name=a['name'],
            namePrep=f"в районе {a['name']}",
            nameGen=f"района {a['name']}",
            eyebrow=f"Район {a['name']} · {ao['name']} · круглосуточно",
            h1=f"Ритуальные услуги в районе {a['name']} (Москва)",
            lead=f"<b>Выезд ритуального агента в район {a['name']} за {ao['minutes']} минут — бесплатно, круглосуточно.</b> Работаем по всему району. Организация похорон, кремации, отпевания «под ключ».",
            specific=f"Район {a['name']} входит в {ao['fullName']} ({ao['name']}). Ближайший морг — {a['nearMorgue']}. Ближайшие кладбища — {a['nearCemetery']}. Наш ритуальный агент сопровождает похороны и кремацию для жителей всех улиц и микрорайонов района {a['name']}.",
            lat=a['lat'], lng=a['lng'],
            minutes=ao['minutes'],
            nearMorgue=a['nearMorgue'],
            nearCemetery=a['nearCemetery'],
            areasGrid='',
            parentBreadcrumb=f'<span aria-hidden="true">›</span><a href="../{ao["slug"]}/">{ao["name"]}</a>',
            phone_tel=PHONE_TEL, phone_vis=PHONE_VIS,
            jsonld=jsonld(a['name'], a['name'], a['slug'], a['lat'], a['lng'],
                          parent_breadcrumb={"name": ao['name'], "url": f"{CANONICAL_BASE}/moscow/{ao['slug']}/"}),
        )
        (slug_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Generated {len(DATA['districts'])} AO + {len(DATA['areas'])} area pages = {len(DATA['districts']) + len(DATA['areas'])} total")


if __name__ == "__main__":
    build()
