const PAGE_SIZE = 6;

function getCatalogStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return {
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
  if (project.priceFrom < 8) return "4-8";
  if (project.priceFrom < 12) return "8-12";
  if (project.priceFrom < 18) return "12-18";
  return "18+";
}

function buildCatalogCard(project) {
  return `
    <article class="project-card catalog-card">
      <img src="${project.heroImage}" alt="${project.title}" loading="lazy" />
      <h3>${project.title}</h3>
      <p class="project-meta">${project.district}</p>
      <p class="project-meta">${project.metro}</p>
      <p class="project-meta">Класс: ${project.classType}</p>
      <p class="project-price">от ${project.priceFrom.toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млн ₽</p>
      <a class="project-link" href="./project.html?project=${encodeURIComponent(project.id)}">Открыть карточку ЖК</a>
    </article>
  `;
}

function applyCatalogFilters(state) {
  return window.REALTY_PROJECTS.filter((project) => {
    if (state.district && project.district !== state.district) return false;
    if (state.metro && project.metro !== state.metro) return false;
    if (state.classType && project.classType !== state.classType) return false;
    if (state.rooms && !project.rooms.includes(state.rooms)) return false;
    if (state.budget && getBudgetRangeKey(project) !== state.budget) return false;
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

function initCatalogPage() {
  if (!Array.isArray(window.REALTY_PROJECTS)) return;
  syncFilterOptions();

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

  document.getElementById("catalog-show-more")?.addEventListener("click", () => {
    state = { ...state, page: state.page + 1 };
    renderCatalog(state);
    writeCatalogStateToUrl(state);
  });
}

initCatalogPage();
