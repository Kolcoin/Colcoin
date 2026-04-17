function getProjectFromQuery() {
  const params = new URLSearchParams(window.location.search);
  const slug = params.get("project") || params.get("id") || "first-donskoy";
  const match = window.REALTY_PROJECTS.find((project) => project.slug === slug || project.id === slug);
  return match || window.REALTY_PROJECTS[0];
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
  const source = getElementByIds(["project-source", "project-source-link"]);

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
  if (source) source.href = project.sourceUrl;
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
      <article class="project-card">
        <h3>${item.title}</h3>
        <p class="project-meta">${item.district}</p>
        <p class="project-meta">${item.metro}</p>
        <p class="project-price">от ${item.priceFrom} млн ₽</p>
        <a class="project-link" href="./project.html?project=${encodeURIComponent(item.slug)}">Открыть карточку</a>
      </article>
    `
    )
    .join("");
}

function initProjectPage() {
  const project = getProjectFromQuery();
  renderProjectHeader(project);
  renderProjectGallery(project);
  renderLayouts(project);
  renderBuildings(project);
  setupFaqAccordion(project);
  renderSimilar(project);
}

initProjectPage();
