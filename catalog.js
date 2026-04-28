const PAGE_SIZE = 6;

function reachMetrikaGoal(goal) {
  try {
    if (typeof window !== "undefined" && typeof window.ym === "function") {
      window.ym(108657608, "reachGoal", goal);
    }
  } catch (_error) {
    // no-op in browsers where metrika is unavailable
  }
}

function getCatalogStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return {
    regionGroup: params.get("regionGroup") || "all",
    quickFilter: params.get("quickFilter") || "",
    district: params.get("district") || "",
    metro: params.get("metro") || "",
    budget: params.get("budget") || "",
    rooms: params.get("rooms") || "",
    classType: params.get("classType") || "",
    sort: params.get("sort") || "priority",
    page: Math.max(1, Number.parseInt(params.get("page") || "1", 10) || 1)
  };
}

function writeCatalogStateToUrl(state) {
  const params = new URLSearchParams();
  Object.entries(state).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.set(key, String(value));
    }
  });
  const url = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState({}, "", url);
}

function getBudgetRangeKey(project) {
  const priceRub = Number(project.priceFrom) * 1_000_000;
  if (priceRub <= 10_000_000) return "0-10000000";
  if (priceRub <= 15_000_000) return "10000000-15000000";
  if (priceRub <= 25_000_000) return "15000000-25000000";
  return "25000000-999999999";
}

function buildCatalogCard(project) {
  const classLabelMap = {
    comfort: "Комфорт",
    business: "Бизнес",
    premium: "Премиум"
  };
  const classLabel = classLabelMap[project.classType] || "Комфорт";
  const cardLink = `./project.html?project=${encodeURIComponent(project.id)}`;

  return `
    <article class="project-card project-card-rich catalog-card">
      <div class="project-card-media">
        <img src="${project.heroImage}" alt="${project.title}" loading="lazy" />
        <span class="project-card-badge">${classLabel}</span>
      </div>
      <h3>${project.title}</h3>
      <p class="project-meta">${project.district}</p>
      <p class="project-meta">${project.metro}</p>
      <div class="project-card-chips">
        <span>${classLabel}-класс</span>
        <span>${project.delivery || "Срок уточняется"}</span>
      </div>
      <div class="project-card-footer">
        <p class="project-price">от ${project.priceFrom.toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млн ₽</p>
        <a class="btn btn-small project-card-main-link" href="${cardLink}">Подробнее</a>
      </div>
    </article>
  `;
}

function getRegionGroup(project) {
  const district = String(project?.district || "").toLowerCase();
  const metro = String(project?.metro || "").toLowerCase();
  const address = String(project?.address || "").toLowerCase();
  const source = String(project?.sourceUrl || "").toLowerCase();

  const moHints = [
    "московская область",
    "подмосков",
    "мытищ",
    "химк",
    "красногорск",
    "балаших",
    "одинцов",
    "подольск",
    "люберц",
    "видн",
    "долгопруд",
    "истра",
    "домодедов",
    "королев",
    "реутов",
    "котельник",
    "раменск",
    "щелков",
    "лобн",
    "солнечногор",
    "ногинск",
    "сергиев посад"
  ];
  const hasMoHint = moHints.some(
    (hint) => district.includes(hint) || address.includes(hint)
  );
  if (hasMoHint) return "mo";

  const isMoscow =
    district.includes("москва") ||
    district.includes("цао") ||
    district.includes("сзао") ||
    district.includes("свао") ||
    district.includes("сао") ||
    district.includes("вао") ||
    district.includes("ювао") ||
    district.includes("юао") ||
    district.includes("юзао") ||
    district.includes("зеленоград") ||
    metro.includes("мцк") ||
    source.includes("msk.nmarket.pro");
  if (isMoscow) return "moscow";

  return "other";
}

function applyCatalogFilters(state) {
  return window.REALTY_PROJECTS.filter((project) => {
    if (state.regionGroup && state.regionGroup !== "all") {
      if (getRegionGroup(project) !== state.regionGroup) return false;
    }
    if (state.district && project.district !== state.district) return false;
    if (state.metro && project.metro !== state.metro) return false;
    if (state.classType && project.classType !== state.classType) return false;
    if (state.rooms && !project.rooms.includes(state.rooms)) return false;
    if (state.budget && getBudgetRangeKey(project) !== state.budget) return false;
    if (state.quickFilter === "budget-low" && Number(project.priceFrom) > 10) return false;
    if (
      state.quickFilter === "ready" &&
      !/сдан|сда[нт]/i.test(String(project.delivery || ""))
    ) {
      return false;
    }
    if (
      state.quickFilter === "metro" &&
      (/уточня/i.test(String(project.metro || "")) || !String(project.metro || "").trim())
    ) {
      return false;
    }
    if (
      state.quickFilter === "business-plus" &&
      !["business", "premium"].includes(String(project.classType || ""))
    ) {
      return false;
    }
    return true;
  });
}

function sortCatalogProjects(projects, sortMode) {
  const copy = [...projects];
  if (sortMode === "price-asc") {
    return copy.sort((a, b) => a.priceFrom - b.priceFrom);
  }
  if (sortMode === "price-desc") {
    return copy.sort((a, b) => b.priceFrom - a.priceFrom);
  }
  if (sortMode === "title-asc") {
    return copy.sort((a, b) => a.title.localeCompare(b.title, "ru"));
  }
  return copy.sort((a, b) => b.priority - a.priority);
}

function renderCatalog(state) {
  const filtered = applyCatalogFilters(state);
  const sorted = sortCatalogProjects(filtered, state.sort);
  const visibleCount = Math.min(sorted.length, state.page * PAGE_SIZE);
  const visible = sorted.slice(0, visibleCount);

  const resultsRoot = document.getElementById("catalog-results");
  if (resultsRoot) {
    resultsRoot.innerHTML = visible.map(buildCatalogCard).join("");
  }

  const summary = document.getElementById("catalog-summary");
  if (summary) {
    summary.textContent = `Показано ${visible.length} из ${sorted.length} объектов`;
  }

  const showMoreBtn = document.getElementById("catalog-show-more");
  if (showMoreBtn) {
    showMoreBtn.hidden = visible.length >= sorted.length;
  }

  document.querySelectorAll("[data-region-group]").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-region-group") === state.regionGroup);
  });
  document.querySelectorAll("[data-quick-filter]").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-quick-filter") === state.quickFilter);
  });

  const regionSummary = document.getElementById("catalog-region-summary");
  if (regionSummary) {
    const labels = {
      all: "Все регионы",
      moscow: "Москва",
      mo: "Московская область",
      other: "Остальные регионы"
    };
    regionSummary.textContent = `Сегмент: ${labels[state.regionGroup] || labels.all}`;
  }
  const quickSummary = document.getElementById("catalog-quick-summary");
  if (quickSummary) {
    const quickLabels = {
      "": "Без дополнительного фильтра",
      "budget-low": "до 10 млн ₽",
      ready: "Сданные ЖК",
      metro: "Есть метро",
      "business-plus": "Бизнес и премиум"
    };
    quickSummary.textContent = `Быстрый фильтр: ${quickLabels[state.quickFilter] || quickLabels[""]}`;
  }
}

function getRegionCounts() {
  const counts = { all: 0, moscow: 0, mo: 0, other: 0 };
  window.REALTY_PROJECTS.forEach((project) => {
    counts.all += 1;
    const group = getRegionGroup(project);
    counts[group] += 1;
  });
  return counts;
}

function renderRegionSegmentCounts() {
  const counts = getRegionCounts();
  document.querySelectorAll("[data-region-group]").forEach((btn) => {
    const key = btn.getAttribute("data-region-group") || "all";
    const label = btn.getAttribute("data-label") || btn.textContent.trim();
    btn.textContent = `${label} (${counts[key] || 0})`;
  });
}

function syncFilterOptions() {
  const districts = [...new Set(window.REALTY_PROJECTS.map((p) => p.district))].sort((a, b) => a.localeCompare(b, "ru"));
  const metros = [...new Set(window.REALTY_PROJECTS.map((p) => p.metro))].sort((a, b) => a.localeCompare(b, "ru"));

  const districtSelect = document.getElementById("filter-district");
  const metroSelect = document.getElementById("filter-metro");

  if (districtSelect) {
    districts.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      districtSelect.append(option);
    });
  }

  if (metroSelect) {
    metros.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      metroSelect.append(option);
    });
  }
}

function fillFormFromState(state) {
  const mapping = {
    "filter-district": state.district,
    "filter-metro": state.metro,
    "filter-budget": state.budget,
    "filter-rooms": state.rooms,
    "filter-class": state.classType,
    "filter-sort": state.sort
  };
  Object.entries(mapping).forEach(([id, value]) => {
    const field = document.getElementById(id);
    if (field) field.value = value;
  });
}

function readFormToState(baseState) {
  return {
    ...baseState,
    district: document.getElementById("filter-district")?.value || "",
    metro: document.getElementById("filter-metro")?.value || "",
    budget: document.getElementById("filter-budget")?.value || "",
    rooms: document.getElementById("filter-rooms")?.value || "",
    classType: document.getElementById("filter-class")?.value || "",
    sort: document.getElementById("filter-sort")?.value || "priority",
    page: 1
  };
}

function setupRegionSegments(onChange) {
  const root = document.getElementById("catalog-region-segment");
  if (!root) return;
  root.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const btn = target.closest("button[data-region-group]");
    if (!btn) return;
    const value = btn.getAttribute("data-region-group") || "all";
    onChange(value);
  });
}

function setupQuickFilters(onApply) {
  const root = document.getElementById("catalog-quick-filters");
  if (!root) return;
  root.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const btn = target.closest("button[data-quick-filter]");
    if (!btn) return;
    onApply(btn.getAttribute("data-quick-filter") || "");
  });
}

function setupCatalogGoalTracking() {
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const telLink = target.closest('a[href^="tel:"]');
    if (telLink) {
      reachMetrikaGoal("click_phone");
      return;
    }

    const telegramLink = target.closest('a[href*="t.me/"]');
    if (telegramLink) {
      reachMetrikaGoal("click_telegram");
      return;
    }

    const toCatalogLink = target.closest('a[href*="catalog.html"]');
    if (toCatalogLink) {
      reachMetrikaGoal("go_to_catalog");
      return;
    }
  });
}

function initCatalogPage() {
  if (!Array.isArray(window.REALTY_PROJECTS)) return;
  syncFilterOptions();
  renderRegionSegmentCounts();

  let state = getCatalogStateFromUrl();
  fillFormFromState(state);
  renderCatalog(state);
  writeCatalogStateToUrl(state);

  const form = document.getElementById("catalog-filters-form");
  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      state = readFormToState(state);
      renderCatalog(state);
      writeCatalogStateToUrl(state);
    });
  }

  document.getElementById("catalog-reset")?.addEventListener("click", () => {
    state = {
      regionGroup: "all",
      quickFilter: "",
      district: "",
      metro: "",
      budget: "",
      rooms: "",
      classType: "",
      sort: "priority",
      page: 1
    };
    fillFormFromState(state);
    renderCatalog(state);
    writeCatalogStateToUrl(state);
  });

  setupRegionSegments((regionGroup) => {
    state = { ...state, regionGroup, page: 1 };
    renderCatalog(state);
    writeCatalogStateToUrl(state);
  });

  setupQuickFilters((filter) => {
    state = { ...state, quickFilter: filter, page: 1 };
    fillFormFromState(state);
    renderCatalog(state);
    writeCatalogStateToUrl(state);
  });

  document.getElementById("catalog-show-more")?.addEventListener("click", () => {
    state = { ...state, page: state.page + 1 };
    renderCatalog(state);
    writeCatalogStateToUrl(state);
  });

  setupCatalogGoalTracking();
}

initCatalogPage();
