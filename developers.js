function sortDevelopers(items, mode) {
  const data = [...items];
  if (mode === "count-desc") {
    return data.sort((a, b) => b.displays - a.displays || a.name.localeCompare(b.name, "ru"));
  }
  if (mode === "count-asc") {
    return data.sort((a, b) => a.displays - b.displays || a.name.localeCompare(b.name, "ru"));
  }
  return data.sort((a, b) => a.name.localeCompare(b.name, "ru"));
}

function developerCard(dev) {
  const classLabel = Array.isArray(dev.classes) ? dev.classes.join(", ") : "";
  return `
    <article class="project-card developer-card">
      <h3>${dev.name}</h3>
      <p class="project-meta">Регион: ${dev.region}</p>
      <p class="project-meta">Классы: ${classLabel}</p>
      <p class="project-price">${dev.displays} ЖК-дисплеев</p>
    </article>
  `;
}

function renderDevelopers(mode) {
  const root = document.getElementById("developers-grid");
  const summary = document.getElementById("developers-summary");
  if (!root) return;
  const source = Array.isArray(window.REALTY_DEVELOPERS) ? window.REALTY_DEVELOPERS : [];
  const sorted = sortDevelopers(source, mode);
  root.innerHTML = sorted.map(developerCard).join("");
  if (summary) {
    summary.textContent = `Показано ${sorted.length} застройщиков`;
  }
}

function initDevelopersPage() {
  const sortSelect = document.getElementById("developers-sort");
  let mode = sortSelect?.value || "name-asc";
  renderDevelopers(mode);

  sortSelect?.addEventListener("change", () => {
    mode = sortSelect.value;
    renderDevelopers(mode);
  });
}

initDevelopersPage();
