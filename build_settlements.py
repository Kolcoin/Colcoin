#!/usr/bin/env python3
"""Генератор страниц населённых пунктов МО (без точки-салона)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SETTLEMENTS = json.loads((ROOT / "data" / "settlements-mo.json").read_text(encoding="utf-8"))
CITIES = json.loads((ROOT / "data" / "cities-mo.json").read_text(encoding="utf-8"))
CITY_BY_SLUG = {c["slug"]: c for c in CITIES}

OUT_DIR = ROOT / "settlement"

CANONICAL_BASE = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"


def jsonld(s, parent):
    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL_BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Города МО", "item": f"{CANONICAL_BASE}/#cities"},
            {"@type": "ListItem", "position": 3, "name": parent["name"], "item": f"{CANONICAL_BASE}/city/{parent['slug']}/"},
            {"@type": "ListItem", "position": 4, "name": s["name"], "item": f"{CANONICAL_BASE}/settlement/{s['slug']}/"},
        ]
    }
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": f"Ритуальные услуги в {s['name']}",
        "provider": {"@id": f"{CANONICAL_BASE}/#organization"},
        "areaServed": {"@type": "Place", "name": s["name"], "containedInPlace": {"@type": "City", "name": parent["name"]}},
        "description": f"Организация похорон и кремации в {s['name']}. Выезд ритуального агента из {parent['name']} за {s['minutes']} минут.",
        "offers": {"@type": "AggregateOffer", "priceCurrency": "RUB", "lowPrice": "34900", "highPrice": "129000"}
    }
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n</script>'
        for b in (bc, service)
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
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">

  <meta name="geo.region" content="RU-MOS">
  <meta name="geo.placename" content="{name}, {parentName}, Московская область">
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
        <span class="logo__sub">{name} · {parentName} · круглосуточно</span>
      </span>
    </a>
    <nav class="nav">
      <a href="../../#services">Услуги</a>
      <a href="../../#prices">Цены</a>
      <a href="../../#moscow">Москва</a>
      <a href="../../#cities">Города МО</a>
      <a href="../../#cemeteries">Кладбища</a>
      <a href="../../#blog">Справочник</a>
      <a href="../../#faq">Вопросы</a>
    </nav>
    <div class="city-switcher" data-city-switcher>
      <button type="button" class="city-switcher__btn" aria-haspopup="listbox" aria-expanded="false">
        <span class="city-switcher__icon" aria-hidden="true">📍</span>
        <span class="city-switcher__label">{parentName}</span>
        <span class="city-switcher__chev" aria-hidden="true">▾</span>
      </button>
      <div class="city-switcher__pop" role="listbox" hidden>
        <input type="search" class="city-switcher__input" placeholder="Поиск города…">
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

  <nav class="breadcrumbs">
    <div class="container">
      <a href="../../">Главная</a>
      <span aria-hidden="true">›</span>
      <a href="../../#cities">Города МО</a>
      <span aria-hidden="true">›</span>
      <a href="../../city/{parentSlug}/">{parentName}</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{name}</span>
    </div>
  </nav>

  <section class="hero hero--district">
    <div class="container hero__grid">
      <div class="hero__text">
        <div class="hero__eyebrow">{parentName} · {name} · круглосуточно</div>
        <h1>Ритуальные услуги в {name} ({parentName})</h1>
        <p class="hero__lead">
          <b>Работаем по&nbsp;выезду из&nbsp;райцентра «{parentName}». Агент приедет в&nbsp;{name} за&nbsp;{minutes}&nbsp;минут.</b>
          Организация похорон, кремации, отпевания «под&nbsp;ключ». Помощь с&nbsp;документами,
          фиксированные цены, договор и&nbsp;чек.
        </p>
        <div class="hero__cta">
          <a class="btn btn--primary" href="tel:{phone_tel}">Вызвать агента</a>
          <a class="btn btn--ghost" href="../../city/{parentSlug}/">Точка-салон {parentName}</a>
        </div>
        <ul class="hero__badges">
          <li>📍 {name}</li>
          <li>🚗 Выезд из {parentName}</li>
          <li>⏱ {minutes} минут</li>
          <li>24 / 7</li>
        </ul>
      </div>
      <aside class="hero__card">
        <h2 class="hero__card-title">{name} — кратко</h2>
        <ul class="plain">
          <li><b>Округ:</b> {parentDistrict}</li>
          <li><b>Райцентр:</b> {parentName}</li>
          <li><b>Время выезда:</b> {minutes} минут</li>
          <li><b>Морг (район):</b> {parentMorgue}</li>
          <li><b>Кладбища района:</b> {parentCemeteries}</li>
        </ul>
        <a class="btn btn--primary btn--block" href="tel:{phone_tel}">Позвонить</a>
      </aside>
    </div>
  </section>

  <section class="section">
    <div class="container district-text">
      <h2>О {name}</h2>
      <p>{feat}</p>

      <h3>Как мы работаем в {name}</h3>
      <p>
        Наша точка-салон находится в&nbsp;<a href="../../city/{parentSlug}/">{parentName}</a> —
        райцентре округа. Ритуальный агент выезжает в&nbsp;{name} за&nbsp;{minutes}&nbsp;минут. Услуга
        выезда — бесплатная, круглосуточная, без обязательств.
      </p>
      <p>
        В&nbsp;{name} мы&nbsp;организуем похороны и&nbsp;кремацию полного цикла: оформление документов,
        перевозку умершего в&nbsp;ближайший морг ({parentMorgue}), подготовку тела, церемонию
        прощания, отпевание в&nbsp;храме (по&nbsp;желанию), захоронение на&nbsp;кладбищах округа
        и&nbsp;поминальный обед.
      </p>

      <h3>Морг и&nbsp;кладбища для жителей {name}</h3>
      <p>
        Морг для жителей {name} — <b>{parentMorgue}</b>. Захоронение организуем на&nbsp;ближайших
        кладбищах: <b>{parentCemeteries}</b>. Помогаем оформить участок (новый, родственный,
        подзахоронение), согласовать день и&nbsp;час церемонии с&nbsp;администрацией.
      </p>

      <h3>Цены на похороны и кремацию в {name}</h3>
      <p>
        Цены те&nbsp;же, что и&nbsp;для жителей райцентра {parentName}: социальные похороны — от&nbsp;34&nbsp;900&nbsp;₽,
        под ключ — от&nbsp;68&nbsp;500&nbsp;₽, премиум — от&nbsp;129&nbsp;000&nbsp;₽. Никаких надбавок за&nbsp;удалённость:
        выезд агента, катафалк и&nbsp;бригада из&nbsp;{parentName} включены в&nbsp;договор.
      </p>

      <h3>Кремация для жителей {name}</h3>
      <p>
        Кремацию проводим в&nbsp;крематориях Носовиха, Митино или Николо-Архангельский. Сопровождаем
        весь процесс: оформление, гроб для кремации, урна, доставка праха или подзахоронение
        в&nbsp;родственную могилу на&nbsp;ближайшем кладбище.
      </p>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container">
      <header class="section__head">
        <h2>Точка-салон в {parentName}</h2>
        <p>Магазин-салон, где можно посмотреть гробы, венки, ленты и&nbsp;оформить документы. Расположен у&nbsp;{parentMorgueLow}.</p>
      </header>
      <div class="city-map" aria-label="Карта точки-салона в {parentName}">
        <iframe
          title="Городской Ритуал — {parentName}, карта"
          src="https://yandex.ru/map-widget/v1/?ll={parentLng}%2C{parentLat}&z=14&pt={parentLng},{parentLat},pm2rdm"
          allowfullscreen loading="lazy"></iframe>
      </div>
      <p class="map-note">
        Точка-салон расположена в&nbsp;райцентре <b>{parentName}</b>, у&nbsp;{parentMorgueLow}. Это
        ближайшая постоянная точка для жителей {name}. Агент выезжает оттуда за&nbsp;{minutes}&nbsp;минут.
        <br><a href="../../city/{parentSlug}/">Подробнее о&nbsp;нашей точке в&nbsp;{parentName} →</a>
      </p>
    </div>
  </section>

  <section class="section">
    <div class="container faq">
      <header class="section__head">
        <h2>Частые вопросы — {name}</h2>
      </header>
      <details open>
        <summary>У&nbsp;вас есть точка в {name}?</summary>
        <p>Постоянного магазина-салона в&nbsp;{name} у&nbsp;нас нет — мы&nbsp;работаем по&nbsp;выезду из&nbsp;ближайшего райцентра <a href="../../city/{parentSlug}/">{parentName}</a>. Агент приедет к&nbsp;вам за&nbsp;{minutes}&nbsp;минут с&nbsp;каталогом, договором и&nbsp;документами.</p>
      </details>
      <details>
        <summary>Сколько ехать ритуальному агенту в {name}?</summary>
        <p>В&nbsp;среднем {minutes}&nbsp;минут от&nbsp;нашего салона в&nbsp;{parentName}. Услуга выезда бесплатная, без обязательств.</p>
      </details>
      <details>
        <summary>Где морг и кладбища для жителей {name}?</summary>
        <p>Морг — {parentMorgue}. Кладбища: {parentCemeteries}. Подбираем оптимальный вариант, помогаем оформить участок.</p>
      </details>
      <details>
        <summary>Сколько стоят похороны в {name}?</summary>
        <p>Цены те&nbsp;же, что и&nbsp;для жителей {parentName}: от&nbsp;34&nbsp;900&nbsp;₽ (соц), от&nbsp;68&nbsp;500&nbsp;₽ (под ключ), от&nbsp;129&nbsp;000&nbsp;₽ (премиум). Без надбавок за&nbsp;удалённость.</p>
      </details>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container contacts-cta">
      <div>
        <h2>Похороны в {name} — звоните</h2>
        <p>Точка-салон в&nbsp;{parentName}. Выезд агента в&nbsp;{name} — {minutes}&nbsp;минут. Круглосуточно. Бесплатно.</p>
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
      <div class="footer__phones">
        <a href="tel:{phone_tel}">{phone_vis}</a>
        <span class="footer__phone-sep">·</span>
        <a href="tel:+74951915128">+7 (495) 191-51-28</a>
        <span class="footer__phone-sub">круглосуточно</span>
      </div>
    </div>
    <nav class="footer__nav">
      <a href="../../">Главная</a>
      <a href="../../city/{parentSlug}/">{parentName}</a>
      <a href="../../#cities">Все города МО</a>
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
    skipped = 0
    for s in SETTLEMENTS:
        parent = CITY_BY_SLUG.get(s["parent"])
        if not parent:
            print(f"  ! No parent for {s['slug']} (parent={s['parent']}) — skipping")
            skipped += 1
            continue
        slug_dir = OUT_DIR / s["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)

        kw = [
            f"ритуальные услуги {s['name']}",
            f"похороны {s['name']}",
            f"кремация {s['name']}",
            f"ритуальный агент {s['name']}",
            f"выезд ритуального агента {s['name']}",
            f"перевозка умершего {s['name']}",
            f"организация похорон {s['name']}",
            f"похороны {s['name']} {parent['name']}",
            f"кладбища {s['name']}",
            f"отпевание {s['name']}",
        ]

        title = f"Ритуальные услуги в {s['name']} ({parent['name']}) — Городской Ритуал"
        if len(title) > 90:
            title = f"Похороны в {s['name']} ({parent['name']}) — Городской Ритуал"
        desc = (
            f"Организация похорон и кремации в {s['name']} ({parent['name']}, МО). "
            f"Выезд ритуального агента из {parent['name']} за {s['minutes']} минут. ☎ {PHONE_VIS}"
        )
        if len(desc) > 180:
            desc = desc[:177] + "…"

        # Strip "Морг " prefix for genitive form
        parent_morgue_low = parent["morgue"]
        if parent_morgue_low.startswith("Морг "):
            parent_morgue_low = "морга " + parent_morgue_low[5:]
        else:
            parent_morgue_low = parent_morgue_low.lower()

        html = PAGE_TMPL.format(
            canonical=f"{CANONICAL_BASE}/settlement/{s['slug']}/",
            title=title, description=desc, ogtitle=title,
            keywords=", ".join(kw),
            name=s["name"],
            lat=s["lat"], lng=s["lng"],
            minutes=s["minutes"],
            feat=s["feat"],
            parentName=parent["name"],
            parentSlug=parent["slug"],
            parentLat=parent["lat"], parentLng=parent["lng"],
            parentDistrict=parent["district"],
            parentMorgue=parent["morgue"],
            parentMorgueLow=parent_morgue_low,
            parentCemeteries=parent["cemeteries"],
            phone_tel=PHONE_TEL, phone_vis=PHONE_VIS,
            jsonld=jsonld(s, parent),
        )
        (slug_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Generated {len(SETTLEMENTS) - skipped} settlement pages (skipped: {skipped})")


if __name__ == "__main__":
    build()
