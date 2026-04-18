function buildDistrictCard(item) {
  return `
    <article class="project-card districts-page-card">
      <h3>${item.name}</h3>
      <p class="project-meta">Метро: ${item.metro}</p>
      <div class="districts-page-meta">
        <span>${item.region}</span>
        <span>${item.complexes} ЖК</span>
      </div>
    </article>
  `;
}

function renderDistrictList(targetId, list) {
  const root = document.getElementById(targetId);
  if (!root) return;
  root.innerHTML = list.map(buildDistrictCard).join("");
}

function setupDistrictGoals() {
  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const telLink = target.closest('a[href^="tel:"]');
    if (telLink) {
      window.trackGoal?.("click_phone");
      return;
    }
    const telegramLink = target.closest('a[href*="t.me/"]');
    if (telegramLink) {
      window.trackGoal?.("click_telegram");
    }
  });
}

function initDistrictsPage() {
  if (!Array.isArray(window.REALTY_DISTRICTS)) return;
  const moscow = window.REALTY_DISTRICTS.filter((item) => item.region === "Москва");
  const mo = window.REALTY_DISTRICTS.filter((item) => item.region === "Московская область");
  renderDistrictList("districts-moscow", moscow);
  renderDistrictList("districts-mo", mo);
  setupDistrictGoals();
}

initDistrictsPage();
