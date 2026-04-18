const fs = require("fs");
const path = require("path");

const dataCode = fs.readFileSync(path.join(__dirname, "data.js"), "utf8");
let projects;
eval(dataCode.replace("const projects", "projects"));

function formatPrice(n) {
  if (!n) return "по запросу";
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace(".0", "") + " млн ₽";
  return n.toLocaleString("ru-RU") + " ₽";
}

function classColor(cls) {
  const map = { "эконом": "#16a34a", "комфорт": "#2563eb", "бизнес": "#7c3aed", "элит": "#dc2626" };
  return map[cls] || "#6b7280";
}

function articleForProject(p) {
  const prefix = p.isApartments ? "Апартаменты" : "ЖК";
  const fullName = `${prefix} «${p.title}»`;
  const priceRange = p.priceMin ? `от ${formatPrice(p.priceMin)} до ${formatPrice(p.priceMax)}` : "по запросу";
  const pricePerSqm = p.pricePerSqmMin ? `${formatPrice(p.pricePerSqmMin)} – ${formatPrice(p.pricePerSqmMax)}` : "уточняется";

  const scenarios = [];
  if (p.class === "эконом" || p.class === "комфорт") {
    scenarios.push({ icon: "🔑", title: "Первая квартира", text: `${fullName} подходит для покупателей первого жилья: доступный вход от ${formatPrice(p.priceMin)}, понятные условия ипотеки и готовая инфраструктура в локации ${p.location}.` });
  }
  scenarios.push({ icon: "📈", title: "Инвестиция", text: `Инвестиционный потенциал проекта определяется классом «${p.class}», стоимостью квадратного метра (${pricePerSqm}) и перспективой роста цены до сдачи в ${p.delivery}.` });
  if (p.apartments >= 30) {
    scenarios.push({ icon: "🏡", title: "Расширение", text: `Большой выбор планировок (${p.apartments} ${p.isApartments ? "апартаментов" : "квартир"} в продаже) позволяет подобрать оптимальный вариант для семьи с детьми.` });
  }

  const nearby = projects.filter(o => o.id !== p.id && o.location === p.location).slice(0, 3);
  const nearbyHtml = nearby.length > 0
    ? nearby.map(o => `<article class="project-card"><h3>${o.isApartments ? "" : "ЖК "}«${o.title}»</h3><p class="project-meta">${o.location}</p><p class="project-price">от ${formatPrice(o.priceMin)}</p><a class="project-link" href="/novostrojki/${o.slug}.html">Подробнее</a></article>`).join("")
    : "";

  return `<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${fullName} — от ${formatPrice(p.priceMin)}, ${p.location} | Савушкин Эстейт</title>
    <meta name="description" content="${fullName} в ${p.location}: цены ${priceRange}, ${p.apartments} ${p.isApartments ? "апартаментов" : "квартир"}, класс ${p.class}, сдача ${p.delivery}. Подбор и сопровождение сделки — Савушкин Эстейт." />
    <meta name="keywords" content="${p.title}, ${p.title} цены, ${p.title} планировки, новостройки ${p.location}, ${p.class} класс Москва, Савушкин Эстейт" />
    <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large" />
    <meta property="og:type" content="article" />
    <meta property="og:locale" content="ru_RU" />
    <meta property="og:site_name" content="Савушкин Эстейт" />
    <meta property="og:title" content="${fullName} — ${p.location} | Савушкин Эстейт" />
    <meta property="og:description" content="Подробный разбор ${fullName}: цены, сценарии покупки, локация и план действий." />
    <meta property="og:url" content="http://localhost:4173/novostrojki/${p.slug}.html" />
    <link rel="canonical" href="http://localhost:4173/novostrojki/${p.slug}.html" />
    <link rel="stylesheet" href="../styles.css" />
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@graph": [
          {
            "@type": "BreadcrumbList",
            "itemListElement": [
              {"@type":"ListItem","position":1,"name":"Главная","item":"http://localhost:4173/"},
              {"@type":"ListItem","position":2,"name":"Новостройки","item":"http://localhost:4173/novostrojki/"},
              {"@type":"ListItem","position":3,"name":"${p.title}","item":"http://localhost:4173/novostrojki/${p.slug}.html"}
            ]
          },
          {
            "@type": "Article",
            "headline": "${fullName}: обзор, цены и сценарии покупки",
            "inLanguage": "ru-RU",
            "datePublished": "2026-04-16",
            "dateModified": "2026-04-16",
            "author": {"@type":"Organization","name":"Савушкин Эстейт"},
            "publisher": {"@type":"Organization","name":"Савушкин Эстейт"},
            "mainEntityOfPage": "http://localhost:4173/novostrojki/${p.slug}.html",
            "description": "Обзор ${fullName}: цены, класс жилья, расположение, сценарии покупки и контакты брокера.",
            "keywords": ["${p.title}","новостройки Москвы","${p.class} класс","${p.location}"]
          },
          {
            "@type": "FAQPage",
            "mainEntity": [
              {"@type":"Question","name":"Сколько стоит квартира в ${fullName}?","acceptedAnswer":{"@type":"Answer","text":"Цены в ${fullName} — ${priceRange}. Стоимость квадратного метра: ${pricePerSqm}."}},
              {"@type":"Question","name":"Когда сдаётся ${fullName}?","acceptedAnswer":{"@type":"Answer","text":"Срок сдачи ${fullName} — ${p.delivery}."}},
              {"@type":"Question","name":"Какой класс жилья у ${fullName}?","acceptedAnswer":{"@type":"Answer","text":"${fullName} — проект класса «${p.class}», конструкция: ${p.construction}, этажность: ${p.floors}."}}
            ]
          }
        ]
      }
    </script>
  </head>
  <body>
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="../index.html"><span class="brand-dot"></span> Савушкин Эстейт</a>
        <nav class="menu">
          <a href="../index.html">Главная</a>
          <a href="../novostrojki/">Каталог</a>
          <a href="../index.html#contact">Контакты</a>
        </nav>
        <a class="btn btn-small btn-outline" href="../index.html#lead-form">Заявка</a>
      </div>
    </header>

    <main class="section article-page">
      <div class="container article-container">
        <nav class="breadcrumb-nav" aria-label="Хлебные крошки">
          <a href="../index.html">Главная</a> <span>›</span>
          <a href="../novostrojki/">Новостройки</a> <span>›</span>
          <span>${p.title}</span>
        </nav>

        <header class="article-hero">
          <h1>${fullName} — обзор, цены и сценарии покупки</h1>
          <p class="hero-text">
            Экспертный материал от «Савушкин Эстейт» по проекту ${p.title}: ключевые параметры,
            целевые сценарии покупки, анализ локации и практический план действий покупателя.
          </p>
          <nav class="article-anchor-nav" aria-label="Разделы">
            <a href="#summary">О проекте</a>
            <a href="#params">Параметры</a>
            <a href="#scenarios">Кому подходит</a>
            <a href="#risks">Риски</a>
            <a href="#plan">План действий</a>
            <a href="#faq">FAQ</a>
            <a href="#source">Источник</a>
          </nav>
        </header>

        <section class="article-section" id="summary">
          <h2>О проекте ${p.title}</h2>
          <p>
            ${fullName} — жилой проект класса «${p.class}» в локации ${p.location}.
            ${p.metro !== "—" ? `Ближайшая станция метро — ${p.metro} (${p.metroTime}).` : "Проект расположен за пределами метрополитена."}
            Конструктив — ${p.construction}, этажность ${p.floors} этажей.
            ${p.finish === "с отделкой" ? "Квартиры сдаются с чистовой отделкой." : "Квартиры предлагаются без отделки — возможность реализовать собственный дизайн-проект."}
            Срок сдачи — ${p.delivery}.
          </p>
          <div class="article-kpi-grid">
            <article class="article-kpi-card">
              <h3>Цена</h3>
              <p>${priceRange}</p>
            </article>
            <article class="article-kpi-card">
              <h3>Цена за м²</h3>
              <p>${pricePerSqm}</p>
            </article>
            <article class="article-kpi-card">
              <h3>В продаже</h3>
              <p>${p.apartments} ${p.isApartments ? "апартаментов" : "квартир"}</p>
            </article>
          </div>
        </section>

        <section class="article-section section-muted" id="params">
          <h2>Ключевые параметры</h2>
          <div class="article-two-col">
            <div>
              <h3>Характеристики</h3>
              <ul>
                <li><strong>Класс:</strong> ${p.class}</li>
                <li><strong>Отделка:</strong> ${p.finish}</li>
                <li><strong>Этажность:</strong> ${p.floors}</li>
                <li><strong>Конструкция:</strong> ${p.construction}</li>
              </ul>
            </div>
            <div>
              <h3>Расположение</h3>
              <ul>
                <li><strong>Локация:</strong> ${p.location}</li>
                <li><strong>Метро:</strong> ${p.metro !== "—" ? `${p.metro}, ${p.metroTime}` : "нет данных"}</li>
                <li><strong>Сдача:</strong> ${p.delivery}</li>
                <li><strong>Квартир:</strong> ${p.apartments}</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="article-section" id="scenarios">
          <h2>Кому подходит ${p.title}</h2>
          ${scenarios.map(s => `
          <div style="margin-bottom:16px">
            <h3>${s.icon} ${s.title}</h3>
            <p>${s.text}</p>
          </div>`).join("")}
        </section>

        <section class="article-section section-muted" id="risks">
          <h2>На что обратить внимание</h2>
          <div class="article-two-col">
            <div>
              <h3>Проверяем обязательно</h3>
              <ul>
                <li>Сроки строительства и реальную стадию готовности корпусов.</li>
                <li>Условия договора: ДДУ, эскроу-счёт, график платежей.</li>
                <li>Качество планировок — инсоляцию, вид и функциональность.</li>
                <li>Транспортную доступность ${p.metro !== "—" ? `(метро ${p.metro})` : ""} и перспективу развития района.</li>
              </ul>
            </div>
            <div>
              <h3>Частые ошибки</h3>
              <ul>
                <li>Оценка только входной цены без полной стоимости владения.</li>
                <li>Отсутствие сравнения с альтернативами в локации ${p.location}.</li>
                <li>Переоценка темпа роста цены без учёта рыночных рисков.</li>
                <li>Игнорирование расходов на отделку${p.finish === "без отделки" ? " (в данном проекте квартиры без отделки)" : ""}.</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="article-section" id="plan">
          <h2>План действий: 5 шагов к покупке</h2>
          <ol class="article-plan-list">
            <li><strong>Определите цель:</strong> для жизни, аренды или перепродажи — от этого зависит выбор лота.</li>
            <li><strong>Зафиксируйте бюджет:</strong> первоначальный взнос, ежемесячный платёж и резерв на допрасходы.</li>
            <li><strong>Отберите 3–5 лотов:</strong> сравните по планировке, виду из окна, этажу и срокам.</li>
            <li><strong>Проверьте документы:</strong> структуру ДДУ, эскроу-счёт и условия рассрочки/ипотеки.</li>
            <li><strong>Выходите на сделку:</strong> бронирование, подписание и контроль ключевых дат.</li>
          </ol>
        </section>

        <section class="article-section section-muted" id="faq">
          <h2>FAQ по ${fullName}</h2>
          <div class="faq-grid">
            <article class="faq-item">
              <h3>Сколько стоит квартира?</h3>
              <p>Цены в ${fullName}: ${priceRange}. Стоимость за м²: ${pricePerSqm}.</p>
            </article>
            <article class="faq-item">
              <h3>Когда сдаётся проект?</h3>
              <p>Срок сдачи ${fullName} — ${p.delivery}. Конструкция: ${p.construction}.</p>
            </article>
            <article class="faq-item">
              <h3>Можно ли получить подборку альтернатив?</h3>
              <p>Да, «Савушкин Эстейт» подберёт аналогичные проекты класса «${p.class}» в ${p.location} и окрестностях.</p>
            </article>
          </div>
        </section>

        <section class="article-section" id="source">
          <h2>Контакты и источник</h2>
          <p>
            Команда «Савушкин Эстейт» поможет оценить ${fullName}, сравнить с альтернативами и провести сделку под ключ.
          </p>
          <p class="article-contact-line">
            Телефон: <a class="section-link" href="tel:+79857614885">+7 985 761-48-85</a>,
            Telegram: <a class="section-link" href="https://t.me/AlexSavushkin" target="_blank" rel="noopener noreferrer">@AlexSavushkin</a>
          </p>
          <p>Источник данных: <a class="section-link" href="${p.sourceUrl}" target="_blank" rel="noopener noreferrer">MskGuru.ru</a></p>
        </section>

        ${nearbyHtml ? `
        <section class="article-section section-muted">
          <h2>Похожие проекты в ${p.location}</h2>
          <div class="cards-grid cards-grid-compact">${nearbyHtml}</div>
        </section>` : ""}
      </div>
    </main>

    <footer class="site-footer">
      <div class="container footer-row">
        <p>© 2026 Савушкин Эстейт</p>
        <p>Москва · Ежедневно 10:00–21:00</p>
      </div>
    </footer>
  </body>
</html>`;
}

const outDir = path.join(__dirname, "novostrojki");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

let count = 0;
for (const p of projects) {
  const html = articleForProject(p);
  fs.writeFileSync(path.join(outDir, `${p.slug}.html`), html, "utf8");
  count++;
}

console.log(`Generated ${count} article pages in /novostrojki/`);
