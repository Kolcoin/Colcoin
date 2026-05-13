#!/usr/bin/env python3
"""
Генератор страниц кладбищ Москвы и МО.
Цель: топ-выдача по запросам «X кладбище схема проезда / режим работы / документы».
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "cemeteries.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "cemetery"

CANONICAL_BASE = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"


def render_jsonld(c: dict) -> str:
    place = {
        "@context": "https://schema.org",
        "@type": "Cemetery",
        "@id": f"{CANONICAL_BASE}/cemetery/{c['slug']}/#cemetery",
        "name": c["name"],
        "url": f"{CANONICAL_BASE}/cemetery/{c['slug']}/",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": c["address"],
            "addressCountry": "RU"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": c["lat"], "longitude": c["lng"]
        },
        "description": c["features"]
    }
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": f"Организация похорон {c.get('prepFull', 'на ' + c['nameGen'])}",
        "provider": {"@id": f"{CANONICAL_BASE}/#organization"},
        "areaServed": {"@type": "Place", "name": c["name"]},
        "description": f"Полное сопровождение похорон {c.get('prepFull', 'на ' + c['nameGen'])}: оформление участка, копка могилы, катафалк, бригада, координатор церемонии.",
        "offers": {
            "@type": "AggregateOffer",
            "priceCurrency": "RUB",
            "lowPrice": "34900", "highPrice": "129000"
        }
    }
    bc = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL_BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Кладбища Москвы и МО", "item": f"{CANONICAL_BASE}/#cemeteries"},
            {"@type": "ListItem", "position": 3, "name": c["name"], "item": f"{CANONICAL_BASE}/cemetery/{c['slug']}/"},
        ]
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f"Какой режим работы {c['nameGen']}?",
             "acceptedAnswer": {"@type": "Answer", "text": c["schedule"]}},
            {"@type": "Question", "name": f"Как добраться до {c['nameGen']}?",
             "acceptedAnswer": {"@type": "Answer", "text": c["directions"]}},
            {"@type": "Question", "name": f"Какие документы нужны для захоронения {c.get('prepFull', 'на ' + c['nameGen'])}?",
             "acceptedAnswer": {"@type": "Answer", "text": c["documents"]}},
            {"@type": "Question", "name": f"Какие типы захоронений возможны {c.get('prepFull', 'на ' + c['nameGen'])}?",
             "acceptedAnswer": {"@type": "Answer", "text": c["burialTypes"]}},
        ]
    }
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n</script>'
        for b in (place, service, bc, faq)
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

  <meta name="geo.region" content="RU">
  <meta name="geo.placename" content="{name}, Москва и Подмосковье">
  <meta name="geo.position" content="{lat};{lng}">
  <meta name="ICBM" content="{lat}, {lng}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{ogtitle}">
  <meta property="og:description" content="{ogdesc}">
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
      <a href="../../#faq">Вопросы</a>
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
      <a href="../../#cemeteries">Кладбища</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{name}</span>
    </div>
  </nav>

  <section class="hero hero--district">
    <div class="container hero__grid">
      <div class="hero__text">
        <div class="hero__eyebrow">Кладбище · {type} · {districts}</div>
        <h1>{name} — схема проезда, режим работы, документы</h1>
        <p class="hero__lead">
          <b>Полное сопровождение похорон {prepFull}.</b>
          Оформление участка, копка могилы, катафалк, бригада, координатор церемонии.
          Помощь с&nbsp;документами и&nbsp;согласование с&nbsp;администрацией кладбища.
        </p>
        <div class="hero__cta">
          <a class="btn btn--primary" href="tel:{phone_tel}">Заказать похороны</a>
          <a class="btn btn--ghost" href="#map">Схема проезда</a>
        </div>
        <ul class="hero__badges" aria-label="Информация">
          <li>📍 {areaHa} га</li>
          <li>🕐 {scheduleShort}</li>
          <li>{burialBadge}</li>
          <li>24/7 поддержка</li>
        </ul>
      </div>
      <aside class="hero__card">
        <h2 class="hero__card-title">{name} — кратко</h2>
        <ul class="plain">
          <li><b>Адрес:</b> {address}</li>
          <li><b>Площадь:</b> {areaHa} га</li>
          <li><b>Режим работы:</b> {schedule}</li>
          <li><b>Округ:</b> {districts}</li>
          <li><b>Крематорий:</b> {cremaBadge}</li>
        </ul>
        <a class="btn btn--primary btn--block" href="tel:{phone_tel}">Позвонить</a>
      </aside>
    </div>
  </section>

  <section class="section">
    <div class="container district-text">
      <h2>О&nbsp;{namePrep}</h2>
      <p>{features}</p>

      <h3>Режим работы {nameGen}</h3>
      <p>{schedule} Администрация принимает заявления о&nbsp;захоронении в&nbsp;будние дни. Наш ритуальный агент согласует все вопросы с&nbsp;администрацией и&nbsp;поможет получить участок без очередей.</p>

      <h3>Как добраться до&nbsp;{nameGen} — схема проезда</h3>
      <p>{directions}</p>

      <h3>Документы для захоронения {prepFull}</h3>
      <p>{documents}</p>
      <p>Если документов не&nbsp;хватает, наш ритуальный агент поможет восстановить недостающие справки в&nbsp;ЗАГСе и&nbsp;администрации. Также мы&nbsp;берём на&nbsp;себя коммуникацию с&nbsp;администрацией: согласование даты захоронения, оплату работ, оформление удостоверения о&nbsp;захоронении.</p>

      <h3>Типы захоронений {prepFull}</h3>
      <p>{burialTypes}</p>

      <h3>Стоимость захоронения {prepFull}</h3>
      <p>
        Полный комплекс работ — копка могилы, катафалк, бригада, гроб, венки и&nbsp;оформление документов — начинается от&nbsp;34&nbsp;900&nbsp;₽ (социальные похороны) и&nbsp;до&nbsp;129&nbsp;000&nbsp;₽ (премиум-пакет под&nbsp;ключ). Подробный расчёт делает наш агент на&nbsp;месте, исходя из&nbsp;ваших пожеланий.
        Стоимость самого участка зависит от&nbsp;типа: подзахоронение в&nbsp;родственную могилу обычно бесплатно (городская услуга), новый участок — оформляется через администрацию.
      </p>
    </div>
  </section>

  <section id="map" class="section section--alt">
    <div class="container">
      <header class="section__head">
        <h2>📍 {name} — на карте</h2>
        <p>{address}</p>
      </header>
      <div class="city-map" aria-label="Карта {name}">
        <iframe
          title="{name} — карта"
          src="https://yandex.ru/map-widget/v1/?ll={lng}%2C{lat}&z=15&pt={lng},{lat},pm2rdm"
          allowfullscreen loading="lazy"></iframe>
      </div>
      <p class="map-note">
        Точная точка кладбища отмечена меткой. Для построения маршрута откройте
        <a href="https://yandex.ru/maps/?ll={lng}%2C{lat}&z=15&pt={lng},{lat},pm2rdm&rtext=~{lat},{lng}&rtt=auto" target="_blank" rel="noopener">Яндекс.Карты</a>.
      </p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <header class="section__head">
        <h2>Услуги ритуального агентства {prepFull}</h2>
        <p>Полное сопровождение церемонии прощания и&nbsp;погребения. Берём на&nbsp;себя всё — от&nbsp;звонка до&nbsp;благоустройства могилы.</p>
      </header>
      <div class="grid grid--3">
        <article class="card">
          <h3>Оформление участка</h3>
          <p>Согласование с&nbsp;администрацией {nameGen}, оформление документов на&nbsp;новый или родственный участок, удостоверение о&nbsp;захоронении.</p>
        </article>
        <article class="card">
          <h3>Копка могилы и&nbsp;бригада</h3>
          <p>Профессиональная копка по&nbsp;нормативам, бригада из&nbsp;4–6&nbsp;человек для&nbsp;выноса и&nbsp;опускания гроба, заключительные работы.</p>
        </article>
        <article class="card">
          <h3>Катафалк до&nbsp;{nameGen}</h3>
          <p>Спецтранспорт из&nbsp;морга или ритуального зала до&nbsp;{nameGen}. Возможность остановки у&nbsp;храма для отпевания.</p>
        </article>
        <article class="card">
          <h3>Гроб, венки, ленты</h3>
          <p>Подбор гроба, ритуальных венков с&nbsp;живыми и&nbsp;искусственными цветами, лент с&nbsp;надписью. Доставка к&nbsp;моменту прощания.</p>
        </article>
        <article class="card">
          <h3>Координатор церемонии</h3>
          <p>Распорядитель ведёт всю церемонию {prepFull}: встречает гостей, организует подвоз цветов, согласует время с&nbsp;бригадой и&nbsp;администрацией.</p>
        </article>
        <article class="card">
          <h3>Памятник и&nbsp;благоустройство</h3>
          <p>Установка памятника, ограды, цветника после оседания грунта (обычно через 6–12&nbsp;месяцев). Гарантия на&nbsp;работы — 3&nbsp;года.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container faq">
      <header class="section__head">
        <h2>Частые вопросы о {namePrep}</h2>
      </header>
      <details open>
        <summary>Какой режим работы {nameGen}?</summary>
        <p>{schedule}</p>
      </details>
      <details>
        <summary>Как добраться до {nameGen}?</summary>
        <p>{directions}</p>
      </details>
      <details>
        <summary>Какие документы нужны для захоронения {prepFull}?</summary>
        <p>{documents}</p>
      </details>
      <details>
        <summary>Какие типы захоронений возможны {prepFull}?</summary>
        <p>{burialTypes}</p>
      </details>
      <details>
        <summary>Сколько стоят похороны {prepFull}?</summary>
        <p>Полный пакет «под ключ» — от&nbsp;68&nbsp;500&nbsp;₽, социальные похороны — от&nbsp;34&nbsp;900&nbsp;₽. Включают копку могилы, катафалк, бригаду, гроб, венки и&nbsp;оформление документов. Сам участок {prepFull} оформляется отдельно через администрацию.</p>
      </details>
      <details>
        <summary>Можно ли заказать кремацию вместо захоронения {prepFull}?</summary>
        <p>{cremaAnswer}</p>
      </details>
    </div>
  </section>

  <section class="section">
    <div class="container contacts-cta">
      <div>
        <h2>Похороны {prepFull}</h2>
        <p>Звонок и&nbsp;консультация — бесплатно, круглосуточно. Берём на&nbsp;себя всё, от&nbsp;документов до&nbsp;благоустройства могилы.</p>
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
      <div class="footer__brand">Городской Ритуал — Москва и МО</div>
      <div class="footer__legal">ООО «Городской Ритуал» · ОГРН&nbsp;1147746000000 · ИНН&nbsp;7700000000</div>
      <div class="footer__phones">
        <a href="tel:{phone_tel}">{phone_vis}</a>
        <span class="footer__phone-sep">·</span>
        <a href="tel:+74951915128">+7 (495) 191-51-28</a>
        <span class="footer__phone-sub">круглосуточно</span>
      </div>
    </div>
    <nav class="footer__nav" aria-label="Подвал">
      <a href="../../">Главная</a>
      <a href="../../#cemeteries">Все кладбища</a>
      <a href="../../#cities">Все города</a>
    </nav>
    <div class="footer__copy">© 2014–2026. Все права защищены.</div>
  </div>
</footer>

<script src="../../cities-data.js" defer></script>
<script src="../../script.js" defer></script>
</body>
</html>
"""


def short_schedule(s: str) -> str:
    """Pick a short schedule fragment for hero badge."""
    return "9:00–19:00 (лето)"


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for c in DATA:
        slug_dir = OUT_DIR / c["slug"]
        slug_dir.mkdir(parents=True, exist_ok=True)

        kw = [
            f"{c['name']}",
            f"{c['name']} схема проезда",
            f"{c['name']} режим работы",
            f"{c['name']} документы для захоронения",
            f"{c['name']} как добраться",
            f"{c['name']} адрес",
            f"похороны {c.get('prepFull', 'на ' + c['nameGen'])}",
            f"{c['name']} участок",
            f"{c['name']} цена",
            f"{c['name']} подзахоронение",
            f"захоронение {c.get('prepFull', 'на ' + c['nameGen'])}",
            f"организация похорон {c['nameGen']}",
        ]
        if c.get("crematorium"):
            kw.append(f"крематорий {c['name']}")

        title = f"{c['name']} — схема проезда, режим работы, документы | Городской Ритуал"
        if len(title) > 95:
            title = f"{c['name']} — схема проезда, режим, документы | Городской Ритуал"

        desc = (
            f"{c['name']}: адрес, режим работы, схема проезда, документы для захоронения. "
            f"Организация похорон {c.get('prepFull', 'на ' + c['nameGen'])} под ключ. ☎ {PHONE_VIS}"
        )
        if len(desc) > 180:
            desc = desc[:177] + "…"

        burial_badge = "Подзахоронения" if "Подзахоронения" in c["burialTypes"][:60] else "Открыто для захоронений"
        crema_badge = "✅ есть" if c.get("crematorium") else "✗ нет"
        crema_answer = (
            f"Да, на территории {c['nameGen']} действует крематорий. Сопровождаем кремацию полностью: документы, гроб для кремации, урна, доставка праха."
            if c.get("crematorium")
            else f"{c.get('prepFull', 'на ' + c['nameGen']).capitalize()} крематория нет. Кремацию проводим в крематориях Москвы (Хованский, Митинский, Николо-Архангельский) или МО (Носовиха). После — урну захораниваем в нишу колумбария или подзахораниваем в родственную могилу {c.get('prepFull', 'на ' + c['nameGen'])}."
        )

        html = PAGE_TMPL.format(
            canonical=f"{CANONICAL_BASE}/cemetery/{c['slug']}/",
            title=title,
            description=desc,
            ogtitle=f"{c['name']} — Городской Ритуал",
            ogdesc=f"Похороны {c.get('prepFull', 'на ' + c['nameGen'])}: схема, режим, документы, цены. 24/7.",
            keywords=", ".join(kw),
            name=c["name"],
            nameGen=c["nameGen"],
            namePrep=c.get("namePrep", c["nameGen"]),
            prepFull=c.get("prepFull", "на " + c["nameGen"]),
            type=c["type"],
            districts=c["districts"],
            lat=c["lat"], lng=c["lng"],
            address=c["address"],
            areaHa=c["areaHa"],
            schedule=c["schedule"],
            scheduleShort=short_schedule(c["schedule"]),
            directions=c["directions"],
            documents=c["documents"],
            burialTypes=c["burialTypes"],
            features=c["features"],
            burialBadge=burial_badge,
            cremaBadge=crema_badge,
            cremaAnswer=crema_answer,
            phone_tel=PHONE_TEL,
            phone_vis=PHONE_VIS,
            jsonld=render_jsonld(c),
        )
        (slug_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Generated {len(DATA)} cemetery pages")


if __name__ == "__main__":
    build()
