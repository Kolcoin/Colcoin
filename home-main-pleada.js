(() => {
  "use strict";

  if (window.__PLEADA_HOME_MAIN_SCRIPT__) return;
  window.__PLEADA_HOME_MAIN_SCRIPT__ = true;

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

  const HOME_SEGMENT_PINNED = {
    "first-home": "nmarket-87790",
    invest: "nmarket-88942",
    family: "nmarket-85427",
    premium: "nmarket-77467"
  };

  function esc(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function normalizeId(item) {
    return item?.id || item?.slug || "";
  }

  function getClassLabel(classType) {
    const labels = {
      comfort: "Комфорт",
      business: "Бизнес",
      premium: "Премиум"
    };
    return labels[classType] || "Комфорт";
  }

  function getHomeProjects() {
    if (!Array.isArray(window.REALTY_PROJECTS)) return [];
    return window.REALTY_PROJECTS.filter((item) => !HOME_EXCLUDED_PROJECT_IDS.has(normalizeId(item)));
  }

  function getPinnedTopProjects(source) {
    const byId = new Map(source.map((item) => [normalizeId(item), item]));
    const pinned = HOME_TOP_PINNED_IDS.map((id) => byId.get(id)).filter(Boolean);
    const pinnedIds = new Set(pinned.map(normalizeId));
    const fallback = source
      .filter((item) => !pinnedIds.has(normalizeId(item)))
      .sort((a, b) => (b.priority || 0) - (a.priority || 0));
    return [...pinned, ...fallback].slice(0, 4);
  }

  function getProjectCardLink(item) {
    if (item?.articleUrl) return item.articleUrl;
    return `./project.html?project=${encodeURIComponent(normalizeId(item))}`;
  }

  function buildCard(item, options = {}) {
    const cardLink = getProjectCardLink(item);
    const showSource = options.showSource ?? true;

    const classLabel = getClassLabel(item.classType);
    const delivery = item.delivery || "Срок уточняется";
    const priceFrom = Number(item.priceFrom || 0).toLocaleString("ru-RU", { maximumFractionDigits: 1 });

    return `
      <article class="project-card project-card-rich">
        ${
          item.heroImage
            ? `<div class="project-card-media">
                 <img class="project-card-image" src="${esc(item.heroImage)}" alt="${esc(item.title)}" loading="lazy" />
                 <span class="project-card-badge">${esc(classLabel)}</span>
               </div>`
            : ""
        }
        <div class="project-card-body">
          <h3>${esc(item.title)}</h3>
          <p class="project-meta">${esc(item.district || "Локация уточняется")}</p>
          <p class="project-meta">${esc(item.metro || "Метро уточняется")}</p>
          <div class="project-card-chips">
            <span>${esc(classLabel)}-класс</span>
            <span>${esc(delivery)}</span>
          </div>
          ${
            showSource && item.sourceLabel
              ? `<p class="project-source">${esc(item.sourceLabel)}</p>`
              : ""
          }
          <div class="project-card-footer">
            <p class="project-price">от ${esc(priceFrom)} млн ₽</p>
            <a class="btn btn-small project-card-main-link" href="${esc(cardLink)}">Карточка ЖК</a>
          </div>
        </div>
      </article>
    `;
  }

  function renderCards(targetId, items, options) {
    const root = document.getElementById(targetId);
    if (!root) return;
    root.innerHTML = items.map((item) => buildCard(item, options)).join("");
  }

  function renderHeroStats(projects) {
    const projectsNode = document.getElementById("stat-projects-count");
    const developersNode = document.getElementById("stat-developers-count");
    const projectCount = projects.length;
    const developersCount = new Set(projects.map((item) => item.developer).filter(Boolean)).size;

    if (projectsNode) projectsNode.textContent = projectCount.toLocaleString("ru-RU");
    if (developersNode) developersNode.textContent = developersCount.toLocaleString("ru-RU");
  }

  function renderDistricts(projects) {
    const root = document.getElementById("districts-list");
    if (!root) return;
    const districts = [...new Set(projects.map((item) => item.district))]
      .slice(0, 6)
      .map((district) => ({
        name: (district || "Локация").split(",")[0],
        info: `актуальные старты · ${projects.filter((p) => p.district === district).length} ЖК`
      }));

    root.innerHTML = districts
      .map(
        (district) => `
          <article class="district-card">
            <h3>${esc(district.name)}</h3>
            <p>${esc(district.info)}</p>
          </article>
        `
      )
      .join("");
  }

  function renderLaunchBlocks(projects) {
    const root = document.getElementById("launch-blocks");
    if (!root) return;

    const sorted = [...projects].sort((a, b) => (b.priority || 0) - (a.priority || 0));
    const segmentDefs = [
      {
        id: "first-home",
        icon: "🏠",
        title: "Первая квартира",
        description: "Проекты с доступным входом и удобным транспортом.",
        tags: ["До 12 млн ₽", "Льготная ипотека", "Комфорт-класс"],
        buttonText: "Смотреть сценарий",
        buttonClass: "btn-warm",
        filter: (p) => Number(p.priceFrom || 0) <= 12
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
        filter: (p) => (Array.isArray(p.rooms) ? p.rooms.includes("3") || p.rooms.includes("4+") : false)
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
        const filtered = sorted.filter(segment.filter);
        const pinnedId = HOME_SEGMENT_PINNED[segment.id];
        const pinnedItem = pinnedId ? filtered.find((item) => normalizeId(item) === pinnedId) : null;
        const cards = (pinnedItem ? [pinnedItem] : filtered.slice(0, 1))
          .map((item) => buildCard(item, { showSource: false }))
          .join("");
        return `
          <section class="launch-block" id="launch-${segment.id}">
            <div class="launch-block-head">
              <p class="launch-icon">${segment.icon}</p>
              <h3>${esc(segment.title)}</h3>
              <p>${esc(segment.description)}</p>
              <div class="segment-tags">
                ${segment.tags.map((tag) => `<span>${esc(tag)}</span>`).join("")}
              </div>
              <a class="btn ${segment.buttonClass}" href="./catalog.html">${esc(segment.buttonText)}</a>
            </div>
            <div class="cards-grid cards-grid-compact">${cards}</div>
          </section>
        `;
      })
      .join("");
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

    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
  }

  function initPleadaHomeMain() {
    const projects = getHomeProjects();
    if (!projects.length) return;

    const top = getPinnedTopProjects(projects);
    const premium = [...projects]
      .filter((item) => item.classType === "business" || item.classType === "premium")
      .sort((a, b) => (b.priority || 0) - (a.priority || 0))
      .slice(0, 4);

    renderCards("top-projects", top, { showSource: true });
    renderCards("premium-projects", premium, { showSource: true });
    renderHeroStats(projects);
    renderDistricts(projects);
    renderLaunchBlocks(projects);
    setupMobileMenuToggle();
  }

  window.initPleadaHomeMain = initPleadaHomeMain;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPleadaHomeMain);
  } else {
    initPleadaHomeMain();
  }
})();
