function normalizeProjectKey(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/ё/g, "е")
    .replace(/[^a-zа-я0-9]+/gi, " ")
    .trim();
}

function trackGoal(goal, params = {}) {
  try {
    if (typeof window !== "undefined" && typeof window.trackGoal === "function") {
      window.trackGoal(goal, params);
      return;
    }
    if (typeof window !== "undefined" && typeof window.ym === "function") {
      window.ym(108657608, "reachGoal", goal, params);
    }
  } catch (_error) {
    // analytics failures should not affect UX
  }
}

function getClassLabel(classType) {
  const labels = {
    comfort: "Комфорт",
    business: "Бизнес",
    premium: "Премиум"
  };
  return labels[classType] || "Комфорт";
}

function getProjectFromQuery() {
  if (!Array.isArray(window.REALTY_PROJECTS) || window.REALTY_PROJECTS.length === 0) return null;

  const params = new URLSearchParams(window.location.search);
  const rawKey = (params.get("project") || params.get("id") || params.get("name") || "").trim();
  if (!rawKey) return window.REALTY_PROJECTS[0];

  const key = rawKey.toLowerCase();
  const normalizedKey = normalizeProjectKey(rawKey);

  const exactMatch = window.REALTY_PROJECTS.find((project) => {
    const slug = String(project.slug || "").toLowerCase();
    const id = String(project.id || "").toLowerCase();
    return slug === key || id === key;
  });
  if (exactMatch) return exactMatch;

  if (/^\d+$/.test(rawKey)) {
    const numericMatch = window.REALTY_PROJECTS.find((project) => {
      const slug = String(project.slug || "").toLowerCase();
      const id = String(project.id || "").toLowerCase();
      return slug.endsWith(`-${rawKey}`) || id.endsWith(`-${rawKey}`);
    });
    if (numericMatch) return numericMatch;
  }

  const titleMatch = window.REALTY_PROJECTS.find(
    (project) => normalizeProjectKey(project.title) === normalizedKey
  );
  if (titleMatch) return titleMatch;

  return window.REALTY_PROJECTS[0];
}

function getElementByIds(ids) {
  for (const id of ids) {
    const node = document.getElementById(id);
    if (node) return node;
  }
  return null;
}

function renderProjectHeader(project) {
  const title = document.getElementById("project-title");
  const subtitle = document.getElementById("project-subtitle");
  const chips = getElementByIds(["project-tags", "project-chips"]);

  if (title) title.textContent = project.title;
  if (subtitle) {
    subtitle.textContent = `${project.district} · ${project.metro} · ${project.classType}`;
  }
  if (chips) {
    chips.innerHTML = [
      `Класс: ${project.classType}`,
      `Срок: ${project.delivery}`,
      `Застройщик: ${project.developer}`,
      `Диапазон: ${project.priceFrom}–${project.priceTo} млн ₽`
    ]
      .map((chip) => `<span>${chip}</span>`)
      .join("");
  }
}

function renderProjectGallery(project) {
  const root = document.getElementById("project-gallery");
  if (!root) return;
  root.innerHTML = project.gallery
    .map(
      (image, idx) => `
      <figure class="article-gallery-item">
        <img src="${image}" alt="${project.title} — изображение ${idx + 1}" loading="lazy" />
        <figcaption>${project.title}: визуал ${idx + 1}</figcaption>
      </figure>
    `
    )
    .join("");
}

function renderLayouts(project) {
  const body = getElementByIds(["project-layouts", "layouts-tbody"]);
  if (!body) return;
  body.innerHTML = project.layouts
    .map(
      (layout) => `
      <tr>
        <td>${layout.type}</td>
        <td>${layout.area}</td>
        <td>${layout.price}</td>
        <td>${layout.finish}</td>
      </tr>
    `
    )
    .join("");
}

function renderBuildings(project) {
  const root = getElementByIds(["project-buildings", "buildings-list"]);
  if (!root) return;
  root.innerHTML = project.buildings
    .map(
      (building) => `
      <article class="project-card">
        <h3>${building.name}</h3>
        <p class="project-meta">Срок сдачи: ${building.handover}</p>
        <p class="project-meta">${building.status}</p>
      </article>
    `
    )
    .join("");
}

function setupFaqAccordion(project) {
  const root = document.getElementById("project-faq");
  if (!root) return;
  root.innerHTML = project.faq
    .map(
      (item, idx) => `
      <article class="faq-item">
        <button class="faq-accordion-btn" type="button" aria-expanded="false" data-faq="${idx}">
          ${item.q}
        </button>
        <div class="faq-accordion-panel" hidden>
          <p>${item.a}</p>
        </div>
      </article>
    `
    )
    .join("");

  root.querySelectorAll(".faq-accordion-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", expanded ? "false" : "true");
      const panel = button.nextElementSibling;
      if (panel) panel.hidden = expanded;
    });
  });
}

function renderSimilar(project) {
  const root = getElementByIds(["project-similar", "similar-projects"]);
  if (!root) return;
  const similar = window.REALTY_PROJECTS.filter((item) => item.id !== project.id).slice(0, 3);
  root.innerHTML = similar
    .map(
      (item) => `
      <article class="project-card project-card-rich">
        ${
          item.heroImage
            ? `<div class="project-card-media">
                <img class="project-card-image" src="${item.heroImage}" alt="${item.title}" loading="lazy" />
                <span class="project-card-badge">${getClassLabel(item.classType)}</span>
              </div>`
            : ""
        }
        <h3>${item.title}</h3>
        <p class="project-meta">${item.district}</p>
        <p class="project-meta">${item.metro}</p>
        <div class="project-card-chips">
          <span>${getClassLabel(item.classType)}-класс</span>
          <span>${item.delivery || "Срок уточняется"}</span>
        </div>
        <div class="project-card-footer">
          <p class="project-price">от ${Number(item.priceFrom).toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млн ₽</p>
          <a class="btn btn-small project-card-main-link" href="./project.html?project=${encodeURIComponent(item.slug)}">Карточка ЖК</a>
        </div>
      </article>
    `
    )
    .join("");
}

function initProjectPage() {
  const project = getProjectFromQuery();
  trackGoal("view_project_card", { project: project?.id || "" });
  renderProjectHeader(project);
  renderProjectGallery(project);
  renderLayouts(project);
  renderBuildings(project);
  setupFaqAccordion(project);
  renderSimilar(project);

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const telLink = target.closest('a[href^="tel:"]');
    if (telLink) {
      trackGoal("click_phone", { section: "project" });
      return;
    }

    const telegramLink = target.closest('a[href*="t.me/"]');
    if (telegramLink) {
      trackGoal("click_telegram", { section: "project" });
      return;
    }

    const toCatalogLink = target.closest('a[href*="catalog.html"]');
    if (toCatalogLink) {
      trackGoal("go_to_catalog", { section: "project" });
    }
  });
}

initProjectPage();
