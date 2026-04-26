function formatPriceRange(from, to) {
  return `от ${from.toLocaleString("ru-RU", { maximumFractionDigits: 1 })} до ${to.toLocaleString("ru-RU", {
    maximumFractionDigits: 1
  })} млн ₽`;
}

const HOME_EXCLUDED_PROJECT_IDS = new Set([
  "nmarket-89152", // Коттеджный поселок Истра Дом
  "nmarket-91501", // Старый город
  "nmarket-91999", // ПОРТ ЭММ ЗАВИДОВО
  "nmarket-92083" // Космопарк
]);

const HOME_TOP_PINNED_IDS = [
  "nmarket-14867", // Лайм
  "nmarket-61552", // ILOVE
  "nmarket-83554", // Level Академическая
  "nmarket-65154" // FORIVER
];

const HOME_SEGMENT_PINNED_IDS = {
  "first-home": "nmarket-87790",
  invest: "nmarket-88942",
  family: "nmarket-85427",
  premium: "nmarket-76605"
};

function getHomeProjects() {
  if (!Array.isArray(window.REALTY_PROJECTS)) return [];
  return window.REALTY_PROJECTS.filter((item) => !HOME_EXCLUDED_PROJECT_IDS.has(item?.id || item?.slug));
}

function getPinnedTopProjects(source = []) {
  if (!source.length) return [];

  const projectById = new Map(source.map((item) => [item?.id || item?.slug, item]));
  const pinned = HOME_TOP_PINNED_IDS.map((id) => projectById.get(id)).filter(Boolean);

  if (pinned.length >= 4) {
    return pinned.slice(0, 4);
  }

  const pinnedSet = new Set(pinned.map((item) => item?.id || item?.slug));
  const fallback = [...source]
    .filter((item) => !pinnedSet.has(item?.id || item?.slug))
    .sort((a, b) => b.priority - a.priority);

  return [...pinned, ...fallback].slice(0, 4);
}

function reachMetrikaGoal(goal, params = {}) {
  if (typeof window.ym !== "function") return;
  try {
    window.ym(108657608, "reachGoal", goal, params);
  } catch (_error) {
    // no-op: analytics should never break UI interactions
  }
}

if (typeof window !== "undefined") {
  window.trackGoal = (goal, params = {}) => reachMetrikaGoal(goal, params);
}

function getProjectCardLink(item) {
  if (item && item.articleUrl) return item.articleUrl;
  const key = encodeURIComponent(item?.slug || item?.id || "");
  return `./project.html?project=${key}`;
}

function getClassLabel(classType) {
  const labels = {
    comfort: "Комфорт",
    business: "Бизнес",
    premium: "Премиум"
  };
  return labels[classType] || "Комфорт";
}

function buildShowcaseCard(item, options = {}) {
  const cardLink = getProjectCardLink(item);
  const showSource = Boolean(options.showSource) && item.sourceLabel;
  const priceFrom = Number(item.priceFrom).toLocaleString("ru-RU", { maximumFractionDigits: 1 });
  const badge = getClassLabel(item.classType);
  const delivery = item.delivery || "Срок уточняется";

  return `
      <article class="project-card project-card-rich">
        ${
          item.heroImage
            ? `<div class="project-card-media">
                <img class="project-card-image" src="${item.heroImage}" alt="${item.title}" loading="lazy" />
                <span class="project-card-badge">${badge}</span>
              </div>`
            : ""
        }
        <div class="project-card-body">
          <h3>${item.title}</h3>
          <p class="project-meta">${item.district}</p>
          <p class="project-meta">${item.metro}</p>
          <div class="project-card-chips">
            <span>${badge}-класс</span>
            <span>${delivery}</span>
          </div>
          ${showSource ? `<p class="project-source">${item.sourceLabel}</p>` : ""}
          <div class="project-card-footer">
            <p class="project-price">от ${priceFrom} млн ₽</p>
            <a class="btn btn-small project-card-main-link" href="${cardLink}">Карточка ЖК</a>
          </div>
        </div>
      </article>
    `;
}

function renderCards(targetId, items) {
  const root = document.getElementById(targetId);
  if (!root) return;
  root.innerHTML = items
    .map((item) => buildShowcaseCard(item, { showSource: true }))
    .join("");
}

function renderDistricts(projects = []) {
  const root = document.getElementById("districts-list");
  const source = projects.length ? projects : getHomeProjects();
  if (!root || !source.length) return;
  const districts = [...new Set(source.map((item) => item.district))]
    .slice(0, 6)
    .map((district) => ({
      name: district.split(",")[0],
      info: `актуальные старты · ${source.filter((p) => p.district === district).length} ЖК`
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

function renderLaunchBlocks(projects = []) {
  const root = document.getElementById("launch-blocks");
  const source = projects.length ? projects : getHomeProjects();
  if (!root || !source.length) return;

  const sorted = [...source].sort((a, b) => b.priority - a.priority);
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

  const usedIds = new Set();
  root.innerHTML = segmentDefs
    .map((segment) => {
      const filteredProjects = sorted.filter(segment.filter);
      const pinnedId = HOME_SEGMENT_PINNED_IDS[segment.id];
      const pinned = pinnedId
        ? filteredProjects.find((item) => (item?.id || item?.slug) === pinnedId)
        : null;

      const picked = [];
      if (pinned) {
        picked.push(pinned);
        usedIds.add(pinned?.id || pinned?.slug);
      }

      for (const item of filteredProjects) {
        const itemId = item?.id || item?.slug;
        if (picked.length >= 3) break;
        if (usedIds.has(itemId)) continue;
        if (picked.some((x) => (x?.id || x?.slug) === itemId)) continue;
        picked.push(item);
        usedIds.add(itemId);
      }

      const cards = picked
        .map((item) => buildShowcaseCard(item, { showSource: false }))
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
          <div class="cards-grid cards-grid-compact cards-grid-symmetric">${cards}</div>
        </section>
      `;
    })
    .join("");
}

function renderGoalCards() {
  const root = document.getElementById("goal-blocks");
  if (!root) return;

  const goals = [
    {
      icon: "🔑",
      title: "Первая квартира",
      text: "Хватит платить за аренду — выбирайте своё. Студии и 1-комнатные форматы с мягким входом в ипотеку.",
      tags: ["Ипотека", "Рассрочка", "Стартовый бюджет"],
      link: "./catalog.html?quickFilter=budget-low"
    },
    {
      icon: "📈",
      title: "Инвестиция",
      text: "Фокус на ликвидных лотах у метро, стратегии аренды и росте стоимости на горизонте 2–4 лет.",
      tags: ["Доходность", "Ликвидность", "Перепродажа"],
      link: "./catalog.html?quickFilter=business-plus"
    },
    {
      icon: "🏡",
      title: "Расширение",
      text: "2–4 комнаты для семейного апгрейда: больше функциональной площади и удобная инфраструктура рядом.",
      tags: ["2-4 комнаты", "Семья", "Trade-in"],
      link: "./catalog.html?rooms=3"
    },
    {
      icon: "💜",
      title: "Для близких",
      text: "Надежные локации с понятной логистикой, безопасной юридической схемой и прозрачной финансовой моделью.",
      tags: ["Безопасно", "Рядом с метро", "Юрпроверка"],
      link: "./districts.html"
    }
  ];

  root.innerHTML = goals
    .map(
      (goal) => `
      <article class="segment-goal-card">
        <p class="segment-goal-icon">${goal.icon}</p>
        <h3>${goal.title}</h3>
        <p>${goal.text}</p>
        <div class="segment-goal-tags">
          ${goal.tags.map((tag) => `<span>${tag}</span>`).join("")}
        </div>
        <a class="segment-goal-link" href="${goal.link}">Подобрать →</a>
      </article>
    `
    )
    .join("");
}

function renderHeroStats(projects = []) {
  const projectsNode = document.getElementById("stat-projects-count");
  const developersNode = document.getElementById("stat-developers-count");
  const source = projects.length ? projects : getHomeProjects();
  if (!source.length) return;

  const projectCount = source.length;
  const developersCount = new Set(source.map((item) => item.developer).filter(Boolean)).size;

  if (projectsNode) {
    projectsNode.textContent = projectCount.toLocaleString("ru-RU");
  }
  if (developersNode) {
    developersNode.textContent = developersCount.toLocaleString("ru-RU");
  }
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
    reachMetrikaGoal("lead_submit", {
      source: "hero_form",
      goal: goal instanceof HTMLSelectElement ? goal.value || "unknown" : "unknown",
      budget: budget instanceof HTMLSelectElement ? budget.value || "unknown" : "unknown"
    });
    alert(`Принято. Цель: ${goalText}. Бюджет: ${budgetText}. Мы свяжемся с вами и подготовим подборку.`);
  });
}

function setupAnalyticsGoals() {
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const link = target.closest("a");
    if (!link) return;

    const href = link.getAttribute("href") || "";
    if (href.startsWith("tel:")) {
      const value = href.replace("tel:", "");
      reachMetrikaGoal("click_phone", { phone: value });
      return;
    }

    if (href.includes("t.me/")) {
      reachMetrikaGoal("click_telegram", { target: href });
      return;
    }

    if (href.includes("catalog.html")) {
      reachMetrikaGoal("go_to_catalog", { source: "home" });
      return;
    }

    if (href === "#lead-form" || href === "./index.html#lead-form") {
      reachMetrikaGoal("open_lead_form", { source: "home" });
    }
  });
}

function setupMobileMenuToggle() {
  const toggle = document.getElementById("mobile-menu-toggle");
  const menu = document.getElementById("primary-menu");
  if (!(toggle instanceof HTMLButtonElement) || !(menu instanceof HTMLElement)) return;

  const closeMenu = () => {
    toggle.setAttribute("aria-expanded", "false");
    menu.classList.remove("menu-open");
  };

  toggle.addEventListener("click", () => {
    const expanded = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", expanded ? "false" : "true");
    menu.classList.toggle("menu-open", !expanded);
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 1024) {
      closeMenu();
    }
  });
}

function initHomePage() {
  if (typeof REALTY_PROJECTS === "undefined") return;
  const homeProjects = getHomeProjects();
  const top = getPinnedTopProjects(homeProjects);
  const premium = [...homeProjects]
    .filter((item) => item.classType === "business" || item.classType === "premium")
    .sort((a, b) => b.priority - a.priority)
    .slice(0, 4);

  renderCards("top-projects", top);
  renderHeroStats(homeProjects);
  renderGoalCards();
  renderLaunchBlocks(homeProjects);
  renderExpandedSegments();
  renderCards("premium-projects", premium);
  renderDistricts(homeProjects);
  setupLeadForm();
  setupMobileMenuToggle();
  setupAnalyticsGoals();
}

initHomePage();
