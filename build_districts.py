#!/usr/bin/env python3
"""
Генератор страниц микрорайонов для urban-ritual.ru.

Читает data/districts.json и для каждого района создаёт
rayon/<slug>/index.html с уникальным SEO-оптимизированным контентом.

Запуск:
    python3 build_districts.py
"""
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "districts.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "rayon"

CANONICAL_BASE = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"


def render_chips(current_slug: str) -> str:
    """Чипы соседних районов — внутренняя перелинковка."""
    parts = []
    for d in DATA:
        if d["slug"] == current_slug:
            continue
        parts.append(
            f'<li><a href="../{d["slug"]}/">{d["nameShort"]}</a></li>'
        )
    return "\n        ".join(parts)


def render_jsonld(d: dict) -> str:
    """Три JSON-LD блока: LocalBusiness, Service, BreadcrumbList."""
    org = {
        "@context": "https://schema.org",
        "@type": "FuneralHome",
        "@id": f"{CANONICAL_BASE}/rayon/{d['slug']}/#org",
        "name": f"Городской Ритуал — {d['nameShort']}",
        "parentOrganization": {"@id": f"{CANONICAL_BASE}/#organization"},
        "url": f"{CANONICAL_BASE}/rayon/{d['slug']}/",
        "telephone": PHONE_TEL.replace("+", "+"),
        "image": f"{CANONICAL_BASE}/assets/products/wreath_elite_30.jpg",
        "priceRange": "₽₽",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Химки",
            "addressRegion": "Московская область",
            "addressCountry": "RU",
            "streetAddress": d.get("streets", "").split(",")[0].strip(),
        },
        "geo": {"@type": "GeoCoordinates", "latitude": d["lat"], "longitude": d["lng"]},
        "areaServed": {"@type": "Place", "name": d["name"], "address": {"@type": "PostalAddress", "addressLocality": "Химки", "addressCountry": "RU"}},
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "opens": "00:00", "closes": "23:59"
        }
    }
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": f"Ритуальные услуги {d['namePrep']}",
        "provider": {"@id": f"{CANONICAL_BASE}/#organization"},
        "areaServed": {"@type": "Place", "name": d["name"]},
        "description": f"Организация похорон и кремации {d['namePrep']} (Химки). Выезд ритуального агента бесплатно за {d['minutes']} минут, круглосуточно. Помощь с документами, перевозка умершего, гробы, венки, памятники.",
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "RUB",
            "lowPrice": "34900",
            "highPrice": "129000",
            "offerCount": "3"
        }
    }
    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL_BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Зона выезда", "item": f"{CANONICAL_BASE}/#agent"},
            {"@type": "ListItem", "position": 3, "name": d["name"], "item": f"{CANONICAL_BASE}/rayon/{d['slug']}/"},
        ]
    }
    blocks = [json.dumps(org, ensure_ascii=False, indent=2),
              json.dumps(service, ensure_ascii=False, indent=2),
              json.dumps(bc, ensure_ascii=False, indent=2)]
    return "\n".join(
        f'<script type="application/ld+json">\n{b}\n</script>' for b in blocks
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

  <meta name="geo.region" content="RU-MOS">
  <meta name="geo.placename" content="{name}, Химки">
  <meta name="geo.position" content="{lat};{lng}">
  <meta name="ICBM" content="{lat}, {lng}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{ogtitle}">
  <meta property="og:description" content="{ogdesc}">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:image" content="{base}/assets/products/wreath_elite_30.jpg">

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
        <span class="logo__sub">Химки · круглосуточно</span>
      </span>
    </a>
    <nav class="nav" aria-label="Основная навигация">
      <a href="../../#services">Услуги</a>
      <a href="../../#prices">Цены</a>
      <a href="../../#moscow">Москва</a>
      <a href="../../#cities">Города МО</a>
      <a href="../../#cemeteries">Кладбища</a>
      <a href="../../#faq">Вопросы</a>
    </nav>
    <a class="phone-link" href="tel:{phone_tel}">
      <span class="phone-link__dot" aria-hidden="true"></span>
      <span class="phone-link__num">{phone_vis}</span>
      <span class="phone-link__sub">круглосуточно, бесплатно</span>
    </a>
  </div>
</header>

<main id="main">

  <nav class="breadcrumbs" aria-label="Хлебные крошки">
    <div class="container">
      <a href="../../">Главная</a>
      <span aria-hidden="true">›</span>
      <a href="../../#agent">Зона выезда</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{name}</span>
    </div>
  </nav>

  <section class="hero hero--district">
    <div class="container hero__grid">
      <div class="hero__text">
        <div class="hero__eyebrow">Ритуальное агентство · {nameShort} · круглосуточно</div>
        <h1>Ритуальные услуги {namePrep} (Химки)</h1>
        <p class="hero__lead">
          <b>Выезд ритуального агента {namePrep} за&nbsp;{minutes}&nbsp;минут — бесплатно, круглосуточно.</b>
          Полная организация похорон и&nbsp;кремации, помощь с&nbsp;документами,
          фиксированная стоимость, договор.
        </p>
        <div class="hero__cta">
          <a class="btn btn--primary" href="tel:{phone_tel}">Вызвать агента {namePrep}</a>
          <a class="btn btn--ghost" href="../../#prices">Цены и пакеты</a>
        </div>
        <ul class="hero__badges" aria-label="Гарантии">
          <li>Выезд за&nbsp;{minutes}&nbsp;минут</li>
          <li>Договор и&nbsp;чек</li>
          <li>Без предоплаты</li>
          <li>24 / 7</li>
        </ul>
      </div>
      <aside class="hero__card">
        <h2 class="hero__card-title">Что входит — {nameShort}</h2>
        <ul class="plain">
          <li>Выезд агента и&nbsp;консультация — бесплатно</li>
          <li>Оформление гербового свидетельства о&nbsp;смерти</li>
          <li>Перевозка умершего из&nbsp;{nameGen} в&nbsp;морг</li>
          <li>Гроб, венок, лента с&nbsp;надписью</li>
          <li>Катафалк и&nbsp;бригада на&nbsp;кладбище</li>
          <li>Координатор церемонии</li>
        </ul>
        <a class="btn btn--primary btn--block" href="tel:{phone_tel}">Позвонить</a>
      </aside>
    </div>
  </section>

  <section class="section">
    <div class="container district-text">
      <h2>Выезд ритуального агента {namePrep} — {minutes}&nbsp;минут</h2>
      <p>{intro}</p>
      <p>{specific}</p>

      <h3>Адресная зона работы {namePrep}</h3>
      <p>Работаем по всем улицам микрорайона: {streets}. Ориентиры: {landmarks}.</p>

      <h3>Кладбища и&nbsp;морги рядом с&nbsp;{nameShort}</h3>
      <p>Ближайшие кладбища: {cemeteries}. Сотрудничаем с {morgue} — все маршруты перевозки умершего из&nbsp;{nameGen} отработаны и&nbsp;занимают минимальное время.</p>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container">
      <header class="section__head">
        <h2>Что мы делаем {namePrep}</h2>
        <p>Полный спектр ритуальных услуг — от&nbsp;звонка до&nbsp;благоустройства могилы.</p>
      </header>

      <div class="grid grid--3">
        <article class="card">
          <h3>Организация похорон {namePrep}</h3>
          <p>Сопровождение «под ключ»: документы, гроб, катафалк, бригада, церемония на&nbsp;кладбище. Цены от&nbsp;34&nbsp;900&nbsp;₽, итог&nbsp;— в&nbsp;договоре.</p>
        </article>
        <article class="card">
          <h3>Кремация {namePrep}</h3>
          <p>Сопровождение в&nbsp;крематориях Носовиха и&nbsp;Митино. Гроб, урна, документы, доставка праха. От&nbsp;34&nbsp;900&nbsp;₽.</p>
        </article>
        <article class="card">
          <h3>Перевозка умершего из&nbsp;{nameGen}</h3>
          <p>Спецавтомобиль 24/7, грузчики, оформление справок. Перевозка в&nbsp;морг или из&nbsp;морга на&nbsp;кладбище — по&nbsp;Химкам и&nbsp;Москве.</p>
        </article>
        <article class="card">
          <h3>Подготовка тела</h3>
          <p>Омовение, бальзамирование, одевание, макияж. Сотрудничаем с моргом Химкинской ЦКБ и частными моргами.</p>
        </article>
        <article class="card">
          <h3>Гробы, венки, ленты</h3>
          <p>Деревянные и комбинированные гробы (Эколь, Косичка), ритуальные венки, ленты с&nbsp;надписью. Доставка в&nbsp;{name} в&nbsp;день обращения.</p>
        </article>
        <article class="card">
          <h3>Памятники и&nbsp;благоустройство</h3>
          <p>Гранит, мрамор, гравировка, ограда, цветник. Установка на&nbsp;кладбищах ближайших к&nbsp;{nameShort}. Гарантия 3&nbsp;года.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container faq">
      <header class="section__head">
        <h2>Частые вопросы {namePrep}</h2>
      </header>
      <details open>
        <summary>Сколько ехать ритуальному агенту {namePrep}?</summary>
        <p>В&nbsp;среднем {minutes}&nbsp;минут с&nbsp;момента звонка. В&nbsp;ночное время — быстрее за&nbsp;счёт отсутствия пробок. Услуга выезда бесплатная и&nbsp;без обязательств.</p>
      </details>
      <details>
        <summary>Сколько стоит организация похорон {namePrep}?</summary>
        <p>Социальные похороны — от&nbsp;34&nbsp;900&nbsp;₽, под ключ — от&nbsp;68&nbsp;500&nbsp;₽, премиум — от&nbsp;129&nbsp;000&nbsp;₽. Точная стоимость рассчитывается на&nbsp;месте с&nbsp;учётом кладбища, гроба и&nbsp;поминального обеда. Всё фиксируется в&nbsp;договоре.</p>
      </details>
      <details>
        <summary>Где провести похороны жителю {nameShort}?</summary>
        <p>{cemeteries}. Подберём оптимальный вариант по&nbsp;стоимости и&nbsp;близости, поможем оформить участок (новый, родственный или подзахоронение).</p>
      </details>
      <details>
        <summary>Можно ли организовать кремацию вместо захоронения?</summary>
        <p>Да. Кремация {namePrep} — реальная альтернатива классическим похоронам, в&nbsp;среднем дешевле. Сопровождаем в&nbsp;крематориях Носовиха и&nbsp;Митино, доставляем урну с&nbsp;прахом родственникам.</p>
      </details>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container">
      <h2 class="zones__title">Другие микрорайоны Химок, где мы&nbsp;работаем</h2>
      <ul class="chips chips--linked">
        {chips}
      </ul>
      <p class="zones__note">Выезд агента и&nbsp;организация похорон возможна в&nbsp;любом районе Химкинского городского округа. Если вашего адреса нет в&nbsp;списке — просто позвоните, мы&nbsp;приедем.</p>
    </div>
  </section>

  <section class="section">
    <div class="container contacts-cta">
      <div>
        <h2>Свяжитесь с&nbsp;нами — {nameShort}</h2>
        <p>Круглосуточно. Звонок и&nbsp;выезд&nbsp;— бесплатно. Без обязательств.</p>
      </div>
      <a class="btn btn--primary btn--xl" href="tel:{phone_tel}">{phone_vis}</a>
    </div>
  </section>

</main>

<a class="fab" href="tel:{phone_tel}" aria-label="Позвонить">
  <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
    <path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.4 21 3 13.6 3 4.5c0-.6.4-1 1-1H7.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .7-.2 1L6.6 10.8Z"/>
  </svg>
  <span>Позвонить</span>
</a>

<footer class="footer">
  <div class="container footer__row">
    <div>
      <div class="footer__brand">Городской Ритуал — Химки</div>
      <div class="footer__legal">ООО «Городской Ритуал» · ОГРН&nbsp;1147746000000 · ИНН&nbsp;7700000000</div>
    </div>
    <nav class="footer__nav" aria-label="Подвал">
      <a href="../../">Главная</a>
      <a href="../../#services">Услуги</a>
      <a href="../../#prices">Цены</a>
      <a href="../../#faq">Вопросы</a>
    </nav>
    <div class="footer__copy">© 2014–2026. Все права защищены.</div>
  </div>
</footer>

</body>
</html>
"""


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for d in DATA:
        slug_dir = OUT_DIR / d["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)

        # 6-9 ключей для каждого района
        keywords = [
            f"ритуальные услуги {d['nameShort']}",
            f"похороны {d['nameShort']}",
            f"кремация {d['nameShort']}",
            f"ритуальный агент {d['nameShort']}",
            f"выезд ритуального агента {d['nameShort']}",
            f"перевозка умершего {d['nameShort']}",
            f"организация похорон {d['nameShort']} Химки",
            f"ритуальное агентство {d['nameShort']}",
            f"похороны Химки {d['nameShort']}",
        ]

        title = f"Ритуальные услуги {d['namePrep']} (Химки) 24/7 — выезд агента за {d['minutes']} мин"
        # Подрезать до ~75 символов
        if len(title) > 95:
            title = title[:92] + "…"

        description = (
            f"Организация похорон и кремации {d['namePrep']} (г. Химки). "
            f"Выезд ритуального агента бесплатно за {d['minutes']} минут, круглосуточно. "
            f"Помощь с документами, перевозка умершего, гробы, венки. ☎ {PHONE_VIS}"
        )

        html = PAGE_TMPL.format(
            base=CANONICAL_BASE,
            canonical=f"{CANONICAL_BASE}/rayon/{d['slug']}/",
            title=title,
            description=description,
            ogtitle=f"Ритуальные услуги {d['namePrep']} (Химки) — Городской Ритуал",
            ogdesc=f"Выезд ритуального агента {d['namePrep']} за {d['minutes']} минут, бесплатно, 24/7. Похороны и кремация под ключ.",
            keywords=", ".join(keywords),
            name=d["name"],
            nameShort=d["nameShort"],
            namePrep=d["namePrep"],
            nameGen=d["nameGen"],
            minutes=d["minutes"],
            lat=d["lat"],
            lng=d["lng"],
            streets=d["streets"],
            landmarks=d["landmarks"],
            cemeteries=d["cemeteries"],
            morgue=d["morgue"],
            intro=d["intro"],
            specific=d["specific"],
            phone_tel=PHONE_TEL,
            phone_vis=PHONE_VIS,
            jsonld=render_jsonld(d),
            chips=render_chips(d["slug"]),
        )
        out = slug_dir / "index.html"
        out.write_text(html, encoding="utf-8")
        print(f"  ✓ rayon/{d['slug']}/index.html  ({len(html):>6} bytes, {d['minutes']} мин, ключей: {len(keywords)})")

    print(f"\nGenerated {len(DATA)} district pages in {OUT_DIR}")


if __name__ == "__main__":
    build()
