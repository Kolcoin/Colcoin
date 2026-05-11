const DISTRICT_PLACEHOLDER_IMAGE =
  "https://static.tildacdn.com/tild6339-3531-4536-b739-626330353335/headliner-moskva-jk-.jpg";

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function getDistrictProjects(districtId) {
  const map = window.DISTRICT_PROJECT_ASSIGNMENTS;
  if (!map || !Array.isArray(map[districtId])) return [];
  return map[districtId];
}

function buildProjectCards(projects) {
  if (!projects.length) {
    return `
      <p class="project-meta">
        Для этого района карточки временно обновляются. Откройте
        <a class="project-link" href="./catalog.html">каталог ЖК</a>
        для актуального списка.
      </p>
    `;
  }

  return `
    <div class="district-project-grid">
      ${projects
        .map(
          (project) => `
            <article class="blog-card district-project-card">
              <img
                class="district-project-image"
                src="${escapeHtml(project.image || DISTRICT_PLACEHOLDER_IMAGE)}"
                alt="${escapeHtml(project.title)}"
                loading="lazy"
              />
              <h3>${escapeHtml(project.title)}</h3>
              <p class="project-meta">${escapeHtml(project.metro || "Метро уточняется")}</p>
              <p class="project-price">${escapeHtml(project.priceText || "Цена уточняется")}</p>
              <a class="project-link" href="${escapeHtml(project.url || "./catalog.html")}">Открыть ЖК</a>
            </article>
          `
        )
        .join("")}
    </div>
  `;
}

function buildDistrictCard(district, index) {
  const projects = getDistrictProjects(district.id);
  const count = projects.length || district.complexes || 0;

  return `
    <details class="district-accordion" ${index === 0 ? "open" : ""}>
      <summary class="district-accordion-summary">
        <div>
          <h3>${escapeHtml(district.name)}</h3>
          <p class="project-meta">Метро: ${escapeHtml(district.metro)}</p>
          <div class="districts-page-meta">
            <span>${escapeHtml(district.region)}</span>
            <span>${count} ЖК</span>
          </div>
        </div>
        <span class="district-toggle-label">Показать ЖК</span>
      </summary>
      <div class="district-accordion-content">
        <p class="project-meta">
          Подборка по району ${escapeHtml(district.name)}: без дублей между округами и городами.
        </p>
        ${buildProjectCards(projects)}
      </div>
    </details>
  `;
}

function renderDistrictList(targetId, districts) {
  const root = document.getElementById(targetId);
  if (!root) return;
  root.innerHTML = districts.map((district, idx) => buildDistrictCard(district, idx)).join("");
}

function initDistrictsPage() {
  if (!Array.isArray(window.REALTY_DISTRICTS)) return;
  const moscow = window.REALTY_DISTRICTS.filter((district) => district.region === "Москва");
  const mo = window.REALTY_DISTRICTS.filter((district) => district.region === "Московская область");
  renderDistrictList("districts-moscow", moscow);
  renderDistrictList("districts-mo", mo);
}

initDistrictsPage();
