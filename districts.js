const DISTRICT_PLACEHOLDER_IMAGE =
  "https://static.tildacdn.com/tild6339-3531-4536-b739-626330353335/headliner-moskva-jk-.jpg";

function formatProjectPrice(project) {
  if (typeof project.priceText === "string" && project.priceText.trim()) return project.priceText;
  if (typeof project.priceFrom === "number") {
    return `от ${project.priceFrom.toLocaleString("ru-RU", { maximumFractionDigits: 1 })} млн ₽`;
  }
  return "Цена уточняется";
}

function inferProjectRegion(project) {
  const district = String(project.district || "").toLowerCase();
  if (district.includes("москва")) return "Москва";
  return "Московская область";
}

function getProjectPool() {
  const base = Array.isArray(window.REALTY_PROJECTS)
    ? window.REALTY_PROJECTS.map((project) => ({
        id: project.slug || project.id,
        title: project.title,
        metro: project.metro || "уточняется",
        priceText: formatProjectPrice(project),
        image: project.heroImage || DISTRICT_PLACEHOLDER_IMAGE,
        url: `./project.html?project=${encodeURIComponent(project.slug || project.id)}`,
        region: inferProjectRegion(project)
      }))
    : [];

  const extra = [
    {
      id: "nmarket-85433",
      title: "ЖК 1-й Донской",
      metro: "Калинина",
      priceText: "от 8.2 млн ₽",
      image: "https://img1.nmarket.pro/photo/pid/b192664e-bdcf-4286-88c0-7719ecd976d2/?type=jpg&v=1&wpsid=13",
      url: "./starts/nmarket-85433.html",
      region: "Московская область"
    },
    {
      id: "nmarket-86396",
      title: "ЖК Сабурово Клаб",
      metro: "Пятницкое шоссе",
      priceText: "от 19.9 млн ₽",
      image: "https://img1.nmarket.pro/photo/pid/d236cecc-938e-4ae5-8658-80ce8356ce84/?type=jpg&v=1&wpsid=13",
      url: "./starts/nmarket-86396.html",
      region: "Московская область"
    },
    {
      id: "nmarket-86403",
      title: "ЖК ЭВО",
      metro: "Новокосино",
      priceText: "Цена уточняется",
      image: "https://img5.nmarket.pro/photo/pid/e5cd5b5a-8671-4360-afa5-ee0f58ca9a54/?type=jpg&v=1&wpsid=13",
      url: "./starts/nmarket-86403.html",
      region: "Московская область"
    }
  ];

  const byId = new Map();
  [...base, ...extra].forEach((project) => byId.set(project.id, project));
  return [...byId.values()];
}

function buildProjectCards(projects) {
  if (!projects.length) {
    return `
      <p class="project-meta">
        В этом районе подборка обновляется. Откройте
        <a class="project-link" href="./catalog.html">каталог ЖК</a>
        для актуальных предложений.
      </p>
    `;
  }

  return `
    <div class="district-project-grid">
      ${projects
        .map(
          (project) => `
            <article class="blog-card district-project-card">
              <img class="district-project-image" src="${project.image}" alt="${project.title}" loading="lazy" />
              <h3>${project.title}</h3>
              <p class="project-meta">${project.metro}</p>
              <p class="project-price">${project.priceText}</p>
              <a class="project-link" href="${project.url}">Открыть ЖК</a>
            </article>
          `
        )
        .join("")}
    </div>
  `;
}

function pickDistrictProjects(district, index, pool) {
  const regionPool = pool.filter((project) => project.region === district.region);
  if (!regionPool.length) return [];
  const limit = Math.min(3, regionPool.length);
  const start = index % regionPool.length;
  const result = [];
  for (let i = 0; i < limit; i += 1) {
    result.push(regionPool[(start + i) % regionPool.length]);
  }
  return result;
}

function buildDistrictCard(item, index, pool) {
  const projects = pickDistrictProjects(item, index, pool);
  return `
    <details class="district-accordion" ${index === 0 ? "open" : ""}>
      <summary class="district-accordion-summary">
        <div>
          <h3>${item.name}</h3>
          <p class="project-meta">Метро: ${item.metro}</p>
          <div class="districts-page-meta">
            <span>${item.region}</span>
            <span>${item.complexes} ЖК</span>
          </div>
        </div>
        <span class="district-toggle-label">Показать ЖК</span>
      </summary>
      <div class="district-accordion-content">
        <p class="project-meta">
          Подборка по району ${item.name}: открывайте карточки ЖК с ценами, фото и подробным описанием.
        </p>
        ${buildProjectCards(projects)}
      </div>
    </details>
  `;
}

function renderDistrictList(targetId, list, pool) {
  const root = document.getElementById(targetId);
  if (!root) return;
  root.innerHTML = list.map((item, idx) => buildDistrictCard(item, idx, pool)).join("");
}

function initDistrictsPage() {
  if (!Array.isArray(window.REALTY_DISTRICTS)) return;
  const pool = getProjectPool();
  const moscow = window.REALTY_DISTRICTS.filter((item) => item.region === "Москва");
  const mo = window.REALTY_DISTRICTS.filter((item) => item.region === "Московская область");
  renderDistrictList("districts-moscow", moscow, pool);
  renderDistrictList("districts-mo", mo, pool);
}

initDistrictsPage();
