function formatPriceRange(from, to) {
  return `от ${from.toLocaleString("ru-RU", { maximumFractionDigits: 1 })} до ${to.toLocaleString("ru-RU", {
    maximumFractionDigits: 1
  })} млн ₽`;
}

function renderCards(targetId, items) {
  const root = document.getElementById(targetId);
  if (!root) return;
  root.innerHTML = items
    .map(
      (item) => `
      <article class="project-card">
        <h3>${item.title}</h3>
        <p class="project-meta">${item.district}</p>
        <p class="project-meta">${item.metro}</p>
        ${item.sourceLabel ? `<p class="project-source">${item.sourceLabel}</p>` : ""}
        <p class="project-price">${formatPriceRange(item.priceFrom, item.priceTo)}</p>
        <a class="project-link" href="./project.html?project=${item.slug}" target="_blank" rel="noopener noreferrer">
          Открыть карточку ЖК
        </a>
      </article>
    `
    )
    .join("");
}

function renderDistricts() {
  const root = document.getElementById("districts-list");
  if (!root || typeof REALTY_PROJECTS === "undefined") return;
  const districts = [...new Set(REALTY_PROJECTS.map((item) => item.district))]
    .slice(0, 6)
    .map((district) => ({
      name: district.split(",")[0],
      info: `актуальные старты · ${REALTY_PROJECTS.filter((p) => p.district === district).length} ЖК`
    }));

  root.innerHTML = districts
    .map(
      (district) => `
      <article class="district-card">
        <h3>${district.name}</h3>
        <p>${district.info}</p>
      </article>
    `
    )
    .join("");
}

function renderLaunchBlocks() {
  const root = document.getElementById("launch-blocks");
  if (!root || typeof REALTY_PROJECTS === "undefined") return;

  const sorted = [...REALTY_PROJECTS].sort((a, b) => b.priority - a.priority);
  const segmentDefs = [
    {
      id: "first-home",
      icon: "🏠",
      title: "Первая квартира",
      description: "Проекты с доступным входом и удобным транспортом.",
      tags: ["До 12 млн ₽", "Льготная ипотека", "Комфорт-класс"],
      buttonText: "Смотреть сценарий",
      buttonClass: "btn-warm",
      filter: (p) => p.priceFrom <= 12
    },
    {
      id: "invest",
      icon: "📈",
      title: "Инвестиция",
      description: "Лоты для аренды и стратегии роста капитала.",
      tags: ["Ликвидность", "Бизнес-класс", "Транспорт"],
      buttonText: "Открыть подборку",
      buttonClass: "btn-cool",
      filter: (p) => p.classType === "business" || p.classType === "premium"
    },
    {
      id: "family",
      icon: "👨‍👩‍👧‍👦",
      title: "Семейный формат",
      description: "Планировки с 2+ комнатами и инфраструктурой для семьи.",
      tags: ["2-4 комнаты", "Школы и сады", "Дворы"],
      buttonText: "Выбрать ЖК",
      buttonClass: "btn-berry",
      filter: (p) => p.rooms.includes("3") || p.rooms.includes("4+")
    },
    {
      id: "premium",
      icon: "✨",
      title: "Премиум",
      description: "Статусные проекты с высокими стандартами и локацией.",
      tags: ["Премиум", "Архитектура", "Приватность"],
      buttonText: "Премиум-каталог",
      buttonClass: "btn-invest",
      filter: (p) => p.classType === "premium"
    }
  ];

  root.innerHTML = segmentDefs
    .map((segment) => {
      const cards = sorted
        .filter(segment.filter)
        .slice(0, 2)
        .map(
          (item) => `
            <article class="project-card">
              <h3>${item.title}</h3>
              <p class="project-meta">${item.district}</p>
              <p class="project-meta">${item.metro}</p>
              <p class="project-price">${formatPriceRange(item.priceFrom, item.priceTo)}</p>
              <a class="project-link" href="./project.html?project=${item.slug}">Открыть карточку</a>
            </article>
          `
        )
        .join("");

      return `
        <section class="launch-block" id="launch-${segment.id}">
          <div class="launch-block-head">
            <p class="launch-icon">${segment.icon}</p>
            <h3>${segment.title}</h3>
            <p>${segment.description}</p>
            <div class="segment-tags">
              ${segment.tags.map((tag) => `<span>${tag}</span>`).join("")}
            </div>
            <a class="btn ${segment.buttonClass}" href="./catalog.html">${segment.buttonText}</a>
          </div>
          <div class="cards-grid cards-grid-compact">${cards}</div>
        </section>
      `;
    })
    .join("");
}

function renderExpandedSegments() {
  const root = document.getElementById("expanded-segment-blocks");
  if (!root || typeof REALTY_PROJECTS === "undefined") return;

  const segmentDetails = [
    {
      id: "goal-first-home",
      title: "Сценарий «Первая квартира»",
      text: "Фокус на минимальном входе, удобной логистике и предсказуемой финансовой модели.",
      bullets: [
        "Подбор в рамках комфортного ежемесячного платежа",
        "Проверка юридической структуры сделки",
        "Сравнение 3-5 лотов в одном бюджете"
      ]
    },
    {
      id: "goal-invest",
      title: "Сценарий «Инвестиция»",
      text: "Подбираем лоты с потенциалом арендного потока и роста цены на этапах строительства.",
      bullets: [
        "Анализ ликвидности на горизонте 2-4 лет",
        "Оценка срока выхода и сценариев продажи",
        "Фильтрация по транспортным кластерам"
      ]
    },
    {
      id: "goal-family",
      title: "Сценарий «Семейный апгрейд»",
      text: "Ключевой акцент на функциональных планировках и ежедневной инфраструктуре.",
      bullets: [
        "Планировки с несколькими сценариями зонирования",
        "Близость образовательной и спортивной инфраструктуры",
        "Пешеходные и транспортные маршруты для семьи"
      ]
    },
    {
      id: "goal-premium",
      title: "Сценарий «Премиум»",
      text: "Подбор проектов с повышенным уровнем сервиса, приватности и архитектурной ценности.",
      bullets: [
        "Сравнение качества входных групп и лобби",
        "Оценка видовых характеристик",
        "Приоритет по локации и статусу окружения"
      ]
    }
  ];

  root.innerHTML = segmentDetails
    .map(
      (segment) => `
      <section class="launch-block" id="${segment.id}">
        <div class="launch-block-head">
          <h3>${segment.title}</h3>
          <p>${segment.text}</p>
        </div>
        <ul class="article-checklist">
          ${segment.bullets.map((bullet) => `<li>${bullet}</li>`).join("")}
        </ul>
      </section>
    `
    )
    .join("");
}

function setupLeadForm() {
  const form = document.getElementById("hero-lead-form");
  if (!form) return;

  const goal = document.getElementById("goal");
  const budget = document.getElementById("budget");
  const button = form.querySelector("button");

  if (!(button instanceof HTMLButtonElement)) return;
  button.addEventListener("click", () => {
    const goalText = goal instanceof HTMLSelectElement ? goal.options[goal.selectedIndex].text : "цель не выбрана";
    const budgetText =
      budget instanceof HTMLSelectElement ? budget.options[budget.selectedIndex].text : "бюджет не выбран";
    alert(`Принято. Цель: ${goalText}. Бюджет: ${budgetText}. Мы свяжемся с вами и подготовим подборку.`);
  });
}

function initHomePage() {
  if (typeof REALTY_PROJECTS === "undefined") return;
  const top = [...REALTY_PROJECTS].sort((a, b) => b.priority - a.priority).slice(0, 4);
  const premium = [...REALTY_PROJECTS]
    .filter((item) => item.classType === "business" || item.classType === "premium")
    .sort((a, b) => b.priority - a.priority)
    .slice(0, 4);

  renderCards("top-projects", top);
  renderLaunchBlocks();
  renderExpandedSegments();
  renderCards("premium-projects", premium);
  renderDistricts();
  setupLeadForm();
}

initHomePage();
