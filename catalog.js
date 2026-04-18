function formatPrice(n) {
  if (!n) return "по запросу";
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace(".0", "") + " млн ₽";
  return n.toLocaleString("ru-RU") + " ₽";
}

function classColor(cls) {
  const map = { "эконом": "#16a34a", "комфорт": "#2563eb", "бизнес": "#7c3aed", "элит": "#dc2626" };
  return map[cls] || "#6b7280";
}

function projectCard(p) {
  const priceText = p.priceMin ? `от ${formatPrice(p.priceMin)}` : "по запросу";
  const metroLine = p.metro !== "—" ? `<p class="project-meta">🚇 ${p.metro}, ${p.metroTime}</p>` : "";
  return `
    <a href="/novostrojki/${p.slug}.html" class="project-card project-card-link">
      <div class="card-img-placeholder" style="background: linear-gradient(135deg, ${classColor(p.class)}22, ${classColor(p.class)}44)">
        <span class="card-badge" style="background:${classColor(p.class)}">${p.class}</span>
        ${p.isApartments ? '<span class="card-badge card-badge-right">апартаменты</span>' : ''}
      </div>
      <div class="card-body">
        <h3>${p.isApartments ? '' : 'ЖК '}«${p.title}»</h3>
        <p class="project-meta">${p.location}</p>
        ${metroLine}
        <p class="project-meta">${p.floors} эт. · ${p.construction} · сдача ${p.delivery}</p>
        <p class="project-price">${priceText}</p>
        <p class="project-meta">${p.apartments} ${p.isApartments ? 'апарт.' : 'кв.'}</p>
      </div>
    </a>`;
}

let currentFilter = "all";
let currentSort = "popular";
let searchQuery = "";
let visibleCount = 24;

function getFiltered() {
  let list = [...projects];
  if (currentFilter !== "all") list = list.filter(p => p.class === currentFilter);
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    list = list.filter(p => p.title.toLowerCase().includes(q) || p.location.toLowerCase().includes(q) || p.metro.toLowerCase().includes(q));
  }
  if (currentSort === "price-asc") list.sort((a, b) => (a.priceMin || Infinity) - (b.priceMin || Infinity));
  else if (currentSort === "price-desc") list.sort((a, b) => (b.priceMin || 0) - (a.priceMin || 0));
  else if (currentSort === "apartments") list.sort((a, b) => b.apartments - a.apartments);
  return list;
}

function render() {
  const filtered = getFiltered();
  const grid = document.getElementById("catalog-grid");
  const shown = filtered.slice(0, visibleCount);
  grid.innerHTML = shown.map(projectCard).join("");
  document.getElementById("results-count").textContent = `Найдено: ${filtered.length} ЖК`;
  const wrap = document.getElementById("load-more-wrap");
  wrap.style.display = visibleCount < filtered.length ? "" : "none";
}

document.querySelectorAll("#class-filter .pill").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#class-filter .pill").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.value;
    visibleCount = 24;
    render();
  });
});

document.querySelectorAll("#sort-filter .pill").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#sort-filter .pill").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentSort = btn.dataset.value;
    render();
  });
});

let debounceTimer;
document.getElementById("search-input").addEventListener("input", (e) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    searchQuery = e.target.value.trim();
    visibleCount = 24;
    render();
  }, 300);
});

document.getElementById("load-more-btn").addEventListener("click", () => {
  visibleCount += 24;
  render();
});

render();
