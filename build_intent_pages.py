#!/usr/bin/env python3
"""Интент-посадочные под Яндекс.Директ: /city/{slug}/{intent}/.
Каждая страница оптимизирована под конкретный рекламный интент:
  - /kremaciya/    — кремация (отдельная группа Директа)
  - /agent/        — срочный вызов агента 24/7
  - /morg/         — гео-запросы по моргу

Шаблон проще, чем у города (нет соседних городов и т.д.), зато
- сфокусирован на 1 услугу
- содержит крупные CTA-блоки сверху и снизу
- имеет собственный JSON-LD Service + FAQPage
- передаёт city + intent в Метрику автоматически (через script.js)
"""
import json
from pathlib import Path

CANONICAL = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"
PHONE_TEL2 = "+74951915128"
PHONE_VIS2 = "+7 (495) 191-51-28"

ROOT = Path(__file__).parent

# Какие города получают интент-страницы (пока — Мытищи; легко расширить)
TARGETS = ["mytishchi"]

INTENTS = {
    "kremaciya": {
        "title": "Кремация {prep} от 34 900 ₽ — Городской Ритуал",
        "h1": "Кремация {prep} — полное сопровождение под ключ",
        "lead": "Организация кремации с доставкой в крематорий Носовиха или Митино. Гроб для кремации, урна, документы, помощь с захоронением праха. Звонок 24/7, агент в&nbsp;вашем городе.",
        "metaDesc": "Кремация {prep} от 34 900 ₽ под ключ. Документы, гроб, урна, доставка в крематорий Носовиха/Митино. Городской Ритуал, агент 24/7.",
        "service": "Кремация",
        "lowPrice": 34900,
        "highPrice": 95000,
        "keywords": ["кремация", "крематорий", "урна", "захоронение праха", "крематорий носовиха", "крематорий митино"],
        "blocks": [
            ("Как устроена кремация {prep}",
             "Прощальная церемония в зале крематория (Носовиха или Митино), кремация в специальной камере (1,5–2,5 часа), подготовка праха в кремуляторе и выдача урны через 3–14 дней. Все этапы под контролем нашего координатора."),
            ("Что входит в пакет под ключ от 34 900 ₽",
             "Выезд агента, оформление медицинского и гербового свидетельства, гроб для кремации, спецтранспорт до крематория, кремация, базовая урна для праха, координатор церемонии, помощь с подзахоронением урны в родственную могилу или нишу колумбария."),
            ("Доставка тела в крематорий",
             "Спецавтомобилем из морга города (например, морг Мытищинской ГКБ) до крематория Носовиха или Митино. Время в пути 40–80 минут. По желанию — остановка у храма для отпевания."),
            ("Что делать с урной после кремации",
             "3 варианта: подзахоронение в родственную могилу на любом кладбище (бесплатно, по закону), захоронение в нишу колумбария (от 30 000 ₽), хранение урны дома или развеяние праха в специально отведённых местах. Поможем оформить любой вариант."),
        ],
        "faq": [
            ("Сколько стоит кремация {prep}?",
             "Социальная кремация — от 34 900 ₽, стандартный пакет «под ключ» — 50 000–70 000 ₽, премиум с залом прощания — от 95 000 ₽. Подробности по телефону за минуту."),
            ("В какой крематорий повезёте?",
             "Чаще всего везём в крематорий Носовиха (Балашиха, МО) — он ближе всего и менее загружен. Альтернатива — Митинский крематорий или Хованский. Выбор согласовываем с вами."),
            ("Когда выдадут урну с прахом?",
             "Стандартный срок — 3–14 дней после кремации. Точную дату назначает крематорий. Мы сами заберём урну и передадим вам."),
            ("Можно ли отпевать перед кремацией?",
             "Да. Отпевание возможно как в храме перед кремацией, так и в часовне при крематории. Помогаем согласовать со священником, организовать прощальную церемонию."),
            ("Какие документы нужны для кремации?",
             "Медицинское свидетельство о смерти, гербовое свидетельство из ЗАГСа, паспорт заявителя, заявление о согласии на кремацию. Если умерший выразил волеизъявление о кремации письменно — приложите его. При отсутствии — нужно согласие супруга и совершеннолетних детей."),
        ],
    },
    "agent": {
        "title": "Срочный вызов ритуального агента {prep} — за 35 минут 24/7",
        "h1": "Ритуальный агент {prep} — выезд за&nbsp;35&nbsp;минут 24/7",
        "lead": "Звоните в любое время — агент приедет за&nbsp;35&nbsp;минут с&nbsp;каталогом, договором и&nbsp;готовыми бланками документов. Поможем дождаться скорой и&nbsp;полиции, организуем перевозку в&nbsp;морг, оформим всё. Без предоплаты и&nbsp;обязательств.",
        "metaDesc": "Срочный вызов ритуального агента {prep} — приедем за 35 минут круглосуточно. Бесплатно, без обязательств. Документы, морг, кладбище — берём на себя.",
        "service": "Выезд ритуального агента",
        "lowPrice": 0,
        "highPrice": 0,
        "keywords": ["ритуальный агент", "вызов ритуального агента", "выезд агента 24/7", "срочно похороны", "что делать если умер близкий"],
        "blocks": [
            ("Когда вызывать ритуального агента",
             "Звоните сразу после того, как факт смерти зафиксирован врачом или полицией. Агент возьмёт на себя организацию перевозки в морг, оформление документов, выбор кладбища или крематория, согласование церемонии."),
            ("Что входит в&nbsp;бесплатный выезд",
             "Приезд в любое место (дом, больница, морг) за&nbsp;35&nbsp;минут, консультация по&nbsp;дальнейшим действиям, помощь с&nbsp;вызовом скорой/полиции если ещё не&nbsp;приехали, оформление перевозки в&nbsp;морг, обсуждение пакета услуг и&nbsp;сметы на&nbsp;месте."),
            ("Что делать до приезда агента",
             "Если человек умер дома: вызовите 103 (скорая) и&nbsp;102 (полиция). Не&nbsp;беспокойтесь о&nbsp;документах — соберём всё после. Подготовьте паспорт умершего, его&nbsp;медкарту и&nbsp;полис ОМС (если есть). Можно начать готовить чай — нашим агентам важно вас успокоить."),
            ("Что НЕ нужно делать",
             "Не&nbsp;подписывайте договор с&nbsp;посторонними агентами, которые приехали без&nbsp;вашего вызова — обычно их&nbsp;вызывают за&nbsp;«комиссию» сотрудники больниц и&nbsp;моргов, услуги дорогие. Дождитесь нашего агента — это бесплатно и&nbsp;без обязательств."),
        ],
        "faq": [
            ("Это правда бесплатно?",
             "Да. Выезд агента, консультация, осмотр документов — бесплатно и без обязательств. Если вы не захотите заключать с нами договор — агент просто уедет, без претензий."),
            ("Сколько времени едет агент {prep}?",
             "В среднем 30–40 минут с момента звонка по любому адресу в городе и ближайших населённых пунктах. Ночью — иногда быстрее (нет пробок)."),
            ("Можно ли вызвать агента ночью?",
             "Да, мы работаем 24/7. Ночные звонки часто самые срочные — в первые часы после смерти нужно вызывать скорую, полицию и параллельно ритуального агента."),
            ("Что взять с собой когда приедет агент?",
             "Ничего готовить не нужно. Если есть под рукой паспорт умершего и его медкарта — это ускорит оформление. Всё остальное агент возьмёт и сделает сам."),
            ("Сколько стоят сами похороны после выезда агента?",
             "Цена согласовывается ОДИН раз и фиксируется в договоре. Социальные похороны — от 34 900 ₽, под ключ — от 68 500 ₽, премиум — от 129 000 ₽. Никаких доплат после."),
        ],
    },
    "morg": {
        "title": "Ритуальный салон у морга {morg} — оформление, выдача тела",
        "h1": "Ритуальные услуги у морга {morg}",
        "lead": "Наш магазин-салон в&nbsp;шаговой доступности от&nbsp;{morg}. Поможем забрать тело, оформить медицинское и гербовое свидетельства о смерти, организовать похороны или кремацию. Звонок 24/7, выезд агента — бесплатно.",
        "metaDesc": "Ритуальные услуги у морга {morg} {prep}. Свой салон рядом, оформление документов, выдача тела, организация похорон под ключ. 24/7.",
        "service": "Ритуальное сопровождение при морге",
        "lowPrice": 34900,
        "highPrice": 250000,
        "keywords": ["морг", "ритуальные услуги при морге", "выдача тела из морга", "оформление документов морг"],
        "blocks": [
            ("Где находится наш салон",
             "В шаговой доступности от&nbsp;{morg} ({morgAddr}). Это позволяет быстро подойти, согласовать выдачу тела с&nbsp;администрацией морга и&nbsp;организовать перевозку без&nbsp;потери времени."),
            ("Как происходит выдача тела из морга",
             "После проведения вскрытия (если оно требуется) и&nbsp;оформления медицинского свидетельства о&nbsp;смерти, тело можно забрать в&nbsp;рабочие часы морга (обычно пн-пт 9:00-15:00). Наш агент согласует точное время, оформит все документы и&nbsp;организует перевозку в&nbsp;зал прощания, на&nbsp;кладбище или в&nbsp;крематорий."),
            ("Что входит в&nbsp;услуги при&nbsp;морге",
             "Бальзамирование (по&nbsp;необходимости), омовение и&nbsp;одевание умершего, макияж, выбор гроба и&nbsp;ритуальных принадлежностей прямо в&nbsp;нашем салоне, оформление документов, помощь с&nbsp;местом на&nbsp;кладбище, организация катафалка."),
            ("Документы, которые мы&nbsp;оформляем",
             "Медицинское свидетельство о&nbsp;смерти (через врача морга или поликлинику), гербовое свидетельство о&nbsp;смерти (в&nbsp;ЗАГСе), справка №11 для&nbsp;пособия на&nbsp;погребение, разрешение на&nbsp;захоронение или кремацию, удостоверение о&nbsp;захоронении."),
        ],
        "faq": [
            ("Сколько времени тело может храниться в морге бесплатно?",
             "Стандартно — до 7 суток. Этого хватает для всех подготовительных действий. Если нужно дольше — возможна доплата за каждый день."),
            ("Можно ли провести прощание прямо при морге?",
             "Да, при многих моргах есть ритуальные залы. Также мы можем организовать прощание в зале при крематории, в храме или у могилы на кладбище."),
            ("Делает ли морг бальзамирование?",
             "Зависит от морга. В большинстве — да, как платная услуга. Цены варьируются от 5 000 до 20 000 ₽. Альтернатива — наш салон проведёт бальзамирование за фиксированную цену."),
            ("Можно ли забрать тело в выходной?",
             "В большинстве моргов — нет, только в рабочие часы (пн-пт). Исключения — при срочной выдаче для перевозки в другой регион или для мусульманских/иудейских похорон (срочно по религии)."),
            ("Нужна ли доверенность чтобы забрать тело?",
             "Если вы — прямой родственник (супруг, родитель, ребёнок), достаточно паспорта и документа о родстве. Для дальних родственников или знакомых — нотариальная доверенность."),
        ],
    },
}


def render_jsonld(city: dict, intent: str, cfg: dict) -> str:
    url = f"{CANONICAL}/city/{city['slug']}/{intent}/"
    service_jsonld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": cfg["service"] + " " + city["namePrep"],
        "provider": {"@id": f"{CANONICAL}/#organization"},
        "areaServed": {"@type": "City", "name": city["name"]},
        "description": cfg["metaDesc"].format(prep=city["namePrep"], morg=city.get("morgue", ""), nameGen=city["nameGen"]),
        "url": url,
    }
    if cfg["lowPrice"] and cfg["highPrice"]:
        service_jsonld["offers"] = {
            "@type": "AggregateOffer",
            "priceCurrency": "RUB",
            "lowPrice": str(cfg["lowPrice"]),
            "highPrice": str(cfg["highPrice"]),
        }
    faq_jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question",
             "name": q.format(prep=city["namePrep"]),
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in cfg["faq"]
        ]
    }
    bc_jsonld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL}/"},
            {"@type": "ListItem", "position": 2, "name": "Города МО", "item": f"{CANONICAL}/#cities"},
            {"@type": "ListItem", "position": 3, "name": city["name"], "item": f"{CANONICAL}/city/{city['slug']}/"},
            {"@type": "ListItem", "position": 4, "name": cfg["service"], "item": url},
        ]
    }
    return "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(b, ensure_ascii=False, indent=2)}\n</script>'
        for b in (service_jsonld, faq_jsonld, bc_jsonld)
    )


TMPL = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#F7F5F2">

  <title>{title}</title>
  <meta name="description" content="{metaDesc}">
  <meta name="keywords" content="{keywords}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{canonical}">

  <meta name="geo.region" content="RU-MOS">
  <meta name="geo.placename" content="{cityName}, Московская область">
  <meta name="geo.position" content="{lat};{lng}">
  <meta name="ICBM" content="{lat}, {lng}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{metaDesc}">
  <meta property="og:locale" content="ru_RU">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=PT+Serif:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../../styles.css">

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

  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
</head>
<body>

<a class="skip" href="#main">Перейти к содержимому</a>

<header class="topbar">
  <div class="container topbar__row">
    <a href="../../../" class="logo" aria-label="Городской Ритуал — на главную">
      <span class="logo__mark" aria-hidden="true">ГР</span>
      <span class="logo__text">
        <span class="logo__name">Городской Ритуал</span>
        <span class="logo__sub">Москва и&nbsp;МО · круглосуточно</span>
      </span>
    </a>
    <nav class="nav" aria-label="Основная навигация">
      <a href="../../../#services">Услуги</a>
      <a href="../../../#prices">Цены</a>
      <a href="../../../#moscow">Москва</a>
      <a href="../../../#cities">Города МО</a>
      <a href="../../../#cemeteries">Кладбища</a>
      <a href="../../../#blog">Справочник</a>
      <a href="../../../#faq">Вопросы</a>
    </nav>
    <div class="phone-block">
      <a class="phone-link" href="tel:{phoneTel}">
        <span class="phone-link__dot" aria-hidden="true"></span>
        <span class="phone-link__num">{phoneVis}</span>
        <span class="phone-link__sub">круглосуточно · мобильный</span>
      </a>
      <a class="phone-link phone-link--second" href="tel:{phoneTel2}">
        <span class="phone-link__num">{phoneVis2}</span>
        <span class="phone-link__sub">офис · городской</span>
      </a>
    </div>
  </div>
</header>

<main id="main">

  <nav class="breadcrumbs" aria-label="Хлебные крошки">
    <div class="container">
      <a href="../../../">Главная</a>
      <span aria-hidden="true">›</span>
      <a href="../../../#cities">Города МО</a>
      <span aria-hidden="true">›</span>
      <a href="../">{cityName}</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{serviceName}</span>
    </div>
  </nav>

  <section class="hero hero--intent">
    <div class="container hero__grid">
      <div class="hero__text">
        <div class="hero__eyebrow">{cityName} · {serviceName} · круглосуточно</div>
        <h1>{h1}</h1>
        <p class="hero__lead">{lead}</p>
        <div class="hero__cta">
          <a class="btn btn--primary btn--lg" href="tel:{phoneTel}">📞 {phoneVis}</a>
          <a class="btn btn--ghost btn--lg" href="tel:{phoneTel2}">{phoneVis2}</a>
        </div>
        <ul class="hero__badges" aria-label="Преимущества">
          <li>⏱ Выезд за&nbsp;{minutes}&nbsp;мин</li>
          <li>🆓 Бесплатно</li>
          <li>📝 Договор и&nbsp;чек</li>
          <li>🕐 24/7</li>
        </ul>
      </div>
      <aside class="hero__card">
        <h2 class="hero__card-title">Заявка — мы&nbsp;перезвоним</h2>
        <p class="hero__card-sub">Через 1–2&nbsp;минуты, круглосуточно. Звонок бесплатный.</p>
        <form class="callback" onsubmit="return submitCallback(event)" novalidate>
          <label><input type="text" name="name" required placeholder="Ваше имя" autocomplete="name"></label>
          <label><input type="tel" name="phone" required placeholder="+7 ___ ___-__-__" autocomplete="tel"></label>
          <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
          <input type="hidden" name="_subject" value="Заявка с {cityName} — {serviceName}">
          <input type="hidden" name="Источник" value="{cityName} / {serviceName} (интент-посадочная)">
          <button type="submit" class="btn btn--primary btn--block">Перезвоните мне</button>
          <p class="callback__ok" hidden>Спасибо! Перезвоним в&nbsp;течение 5&nbsp;минут.</p>
          <p class="callback__err" hidden>Не&nbsp;удалось отправить. Позвоните <a href="tel:{phoneTel}">{phoneVis}</a></p>
        </form>
      </aside>
    </div>
  </section>

  <section class="section">
    <div class="container district-text">
{blocks}
    </div>
  </section>

  <section class="section section--alt">
    <div class="container">
      <header class="section__head">
        <h2>Частые вопросы — {serviceName} {cityNamePrep}</h2>
      </header>
{faq}
    </div>
  </section>

  <section class="article-cta">
    <div class="container">
      <div class="article-cta__inner">
        <h2>Звонок и&nbsp;консультация — бесплатно</h2>
        <p>Мы&nbsp;работаем круглосуточно. Расскажем, что делать, поможем с&nbsp;документами и&nbsp;организуем всё&nbsp;«под&nbsp;ключ».</p>
        <div class="article-cta__buttons">
          <a class="btn btn--primary btn--lg" href="tel:{phoneTel}">📞 {phoneVis}</a>
          <a class="btn btn--ghost btn--lg" href="tel:{phoneTel2}">{phoneVis2}</a>
        </div>
        <p class="article-cta__note">⏱ Выезд агента {prepGen}&nbsp;{cityNameGen} — за&nbsp;{minutes}&nbsp;минут.</p>
      </div>
    </div>
  </section>

</main>

<footer class="footer">
  <div class="container footer__grid">
    <div>
      <div class="footer__brand">Городской Ритуал — Москва и&nbsp;МО</div>
      <p class="footer__small">ООО «Городской Ритуал» · ОГРН 1147746000000 · ИНН 7700000000</p>
      <p class="footer__small">{phoneVis} · {phoneVis2} · круглосуточно</p>
      <p class="footer__small">Куркинское шоссе, 9, Химки</p>
    </div>
    <div>
      <div class="footer__title">{cityName} — другие услуги</div>
      <a href="../">Главная страница {cityNameGen}</a>
      <a href="../../mytishchi/kremaciya/">Кремация {cityNamePrep}</a>
      <a href="../../mytishchi/agent/">Срочный вызов агента</a>
      <a href="../../mytishchi/morg/">Услуги у&nbsp;морга</a>
    </div>
    <div>
      <div class="footer__title">Справочник</div>
      <a href="../../../blog/chto-delat-esli-umer-blizkiy/">Что делать при&nbsp;смерти близкого</a>
      <a href="../../../blog/posobie-na-pogrebenie-2026/">Пособие на&nbsp;погребение 2026</a>
      <a href="../../../blog/kremaciya-v-moskve/">Кремация — гайд</a>
      <a href="../../../blog/">Все статьи</a>
    </div>
    <div>
      <div class="footer__title">Связь</div>
      <a href="tel:{phoneTel}">{phoneVis}</a>
      <a href="tel:{phoneTel2}">{phoneVis2}</a>
      <a href="https://t.me/ritual_khimki" rel="nofollow noopener" target="_blank">Telegram</a>
      <a href="https://wa.me/79852198394" rel="nofollow noopener" target="_blank">WhatsApp</a>
      <a href="mailto:direkt.ritual@yandex.ru">direkt.ritual@yandex.ru</a>
    </div>
  </div>
  <div class="container footer__bottom">© 2026 ООО «Городской Ритуал». Все права защищены.</div>
</footer>

<script src="../../../script.js" defer></script>
</body>
</html>
"""


def render_blocks(blocks, city):
    parts = []
    for h2, p in blocks:
        h2f = h2.format(prep=city["namePrep"], morg=city.get("morgue", ""), nameGen=city["nameGen"])
        pf = p.format(prep=city["namePrep"], morg=city.get("morgue", ""), morgAddr=city.get("morgueAddress", ""), nameGen=city["nameGen"])
        parts.append(f"      <h2>{h2f}</h2>\n      <p>{pf}</p>")
    return "\n\n".join(parts)


def render_faq(faq, city):
    parts = []
    for q, a in faq:
        qf = q.format(prep=city["namePrep"])
        parts.append(
            f'      <details class="article-faq__item">\n'
            f'        <summary>{qf}</summary>\n'
            f'        <p>{a}</p>\n'
            f'      </details>'
        )
    return "\n".join(parts)


def build():
    cities = json.load(open(ROOT / "data" / "cities-mo.json", encoding="utf-8"))
    cities_by_slug = {c["slug"]: c for c in cities}

    generated = 0
    for slug in TARGETS:
        city = cities_by_slug.get(slug)
        if not city:
            print(f"  skip {slug}: not found")
            continue
        for intent, cfg in INTENTS.items():
            out_dir = ROOT / "city" / slug / intent
            out_dir.mkdir(parents=True, exist_ok=True)

            page = TMPL.format(
                title=cfg["title"].format(prep=city["namePrep"], morg=city.get("morgue", ""), nameGen=city["nameGen"]),
                metaDesc=cfg["metaDesc"].format(prep=city["namePrep"], morg=city.get("morgue", ""), nameGen=city["nameGen"]),
                keywords=", ".join([f"{kw} {city['namePrep']}" for kw in cfg["keywords"]]
                                   + [f"{kw} {city['name'].lower()}" for kw in cfg["keywords"]]),
                canonical=f"{CANONICAL}/city/{slug}/{intent}/",
                cityName=city["name"],
                cityNameGen=city["nameGen"],
                cityNamePrep=city["namePrep"],
                serviceName=cfg["service"],
                lat=city["lat"],
                lng=city["lng"],
                h1=cfg["h1"].format(prep=city["namePrep"], morg=city.get("morgue", "")),
                lead=cfg["lead"].format(prep=city["namePrep"], morg=city.get("morgue", "")),
                blocks=render_blocks(cfg["blocks"], city),
                faq=render_faq(cfg["faq"], city),
                minutes=city.get("minutes", 60),
                prepGen=("в " if not city["namePrep"].startswith("в") else "в"),
                phoneTel=PHONE_TEL,
                phoneVis=PHONE_VIS,
                phoneTel2=PHONE_TEL2,
                phoneVis2=PHONE_VIS2,
                jsonld=render_jsonld(city, intent, cfg),
            )
            (out_dir / "index.html").write_text(page, encoding="utf-8")
            generated += 1
    print(f"Generated {generated} intent landing pages")


if __name__ == "__main__":
    build()
