const BLOG_PAGE_SIZE = 9;
const BLOG_CATEGORY_VISIBLE_LIMIT = 10;
const BLOG_FALLBACK_POSTS = [
  {
    id: "fallback-routes",
    title: "Маршрут покупателя: как выбрать ЖК в Москве и МО без лишнего риска",
    category: "Гайды",
    date: "2026-04-20",
    excerpt: "Собрали пошаговый сценарий: от цели покупки до фиксации безопасных условий сделки.",
    url: "./catalog.html"
  },
  {
    id: "fallback-family-ipoteka",
    title: "Семейная ипотека в 2026: что реально снижает ежемесячный платеж",
    category: "Ипотека",
    date: "2026-04-18",
    excerpt: "Разбираем, как сопоставить ставку, бюджет входа и срок кредита без перегруза по платежу.",
    url: "./mortgage.html"
  },
  {
    id: "fallback-location",
    title: "Районы Москвы и МО: как оценивать локацию до брони квартиры",
    category: "Районы",
    date: "2026-04-16",
    excerpt: "Практичный чеклист по транспортной доступности, окружению и перспективе роста стоимости.",
    url: "./districts.html"
  }
];
const BLOG_CATEGORY_ORDER = [
  "Районы",
  "ЖК",
  "Покупка",
  "Ипотека",
  "Инвестиции",
  "Застройщики",
  "Юридическое",
  "Гайды",
  "Аналитика"
];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function reachMetrikaGoal(goal, params = {}) {
  try {
    if (typeof window.ym === "function") {
      window.ym(108657608, "reachGoal", goal, params);
    }
  } catch (_error) {
    // no-op
  }
}

function getBlogSource() {
  if (Array.isArray(window.REALTY_BLOG_POSTS) && window.REALTY_BLOG_POSTS.length) {
    return window.REALTY_BLOG_POSTS;
  }
  return BLOG_FALLBACK_POSTS;
}

function mapCategory(rawCategory) {
  const value = String(rawCategory || "").trim();
  const lower = value.toLowerCase();
  if (lower.includes("район") || lower.includes("локац") || lower.includes("транспорт")) return "Районы";
  if (lower.includes("жк") || lower.includes("планиров")) return "ЖК";
  if (lower.includes("сделк") || lower.includes("покуп") || lower.includes("бюджет")) return "Покупка";
  if (lower.includes("ипотек")) return "Ипотека";
  if (lower.includes("инвест")) return "Инвестиции";
  if (lower.includes("застрой")) return "Застройщики";
  if (lower.includes("юрид") || lower.includes("дду") || lower.includes("право")) return "Юридическое";
  if (lower.includes("аналит")) return "Аналитика";
  return "Гайды";
}

function formatBlogDate(rawDate) {
  const date = new Date(rawDate);
  if (Number.isNaN(date.getTime())) return String(rawDate || "");
  return date.toLocaleDateString("ru-RU", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  });
}

function normalizePost(post, index) {
  const normalized = {
    id: post?.id || `blog-post-${index + 1}`,
    title: String(post?.title || "").trim() || "Материал о новостройках Москвы и МО",
    excerpt: String(post?.excerpt || "").trim() || "Разбор сценариев покупки, рисков и условий по проектам Москвы и области.",
    category: mapCategory(post?.category),
    date: String(post?.date || ""),
    url: post?.url || "./blog.html"
  };
  normalized.time = Number.isNaN(new Date(normalized.date).getTime()) ? 0 : new Date(normalized.date).getTime();
  return normalized;
}

function getSortedPosts(posts) {
  return [...posts].sort((a, b) => b.time - a.time);
}

function getCategoryCounts(posts) {
  const counts = new Map();
  posts.forEach((post) => {
    counts.set(post.category, (counts.get(post.category) || 0) + 1);
  });
  return counts;
}

function buildCategoryOrder(counts) {
  const ordered = BLOG_CATEGORY_ORDER.filter((category) => counts.has(category));
  const dynamic = [...counts.keys()]
    .filter((category) => !ordered.includes(category))
    .sort((a, b) => a.localeCompare(b, "ru"));
  return ["Все", ...ordered, ...dynamic];
}

function parseStateFromUrl(categories) {
  const params = new URLSearchParams(window.location.search);
  const nextCategory = params.get("category") || "Все";
  return {
    category: categories.includes(nextCategory) ? nextCategory : "Все",
    page: Math.max(1, Number.parseInt(params.get("page") || "1", 10) || 1),
    showAllCategories: params.get("showCategories") === "all"
  };
}

function syncStateToUrl(state) {
  const params = new URLSearchParams();
  if (state.category !== "Все") params.set("category", state.category);
  if (state.page > 1) params.set("page", String(state.page));
  if (state.showAllCategories) params.set("showCategories", "all");
  const query = params.toString();
  const nextUrl = query ? `${window.location.pathname}?${query}` : window.location.pathname;
  window.history.replaceState({}, "", nextUrl);
}

function filterPosts(posts, category) {
  if (category === "Все") return posts;
  return posts.filter((post) => post.category === category);
}

function renderHeroCount(totalCount) {
  const root = document.getElementById("blog-total-label");
  if (!root) return;
  root.textContent = `${totalCount} материалов о новостройках Москвы и МО`;
}

function renderCategoryChips(categories, counts, state) {
  const root = document.getElementById("blog-category-chips");
  if (!root) return;
  const totalCount = [...counts.values()].reduce((sum, value) => sum + value, 0);
  const visible = state.showAllCategories ? categories : categories.slice(0, BLOG_CATEGORY_VISIBLE_LIMIT);
  root.innerHTML = visible
    .map((category) => {
      const count = category === "Все" ? totalCount : counts.get(category) || 0;
      const active = state.category === category;
      return `
        <button class="blog-chip${active ? " is-active" : ""}" type="button" data-blog-category="${escapeHtml(category)}" aria-pressed="${active ? "true" : "false"}">
          <span>${escapeHtml(category)}</span>
          <span class="blog-chip-count">${count}</span>
        </button>
      `;
    })
    .join("");

  const toggle = document.getElementById("blog-toggle-categories");
  if (!toggle) return;
  const hasOverflow = categories.length > BLOG_CATEGORY_VISIBLE_LIMIT;
  toggle.hidden = !hasOverflow;
  if (hasOverflow) {
    toggle.textContent = state.showAllCategories ? "Свернуть" : "Показать ещё";
    toggle.setAttribute("aria-expanded", state.showAllCategories ? "true" : "false");
  }
}

function renderPosts(posts, state) {
  const root = document.getElementById("blog-grid");
  if (!root) return;
  const visible = posts.slice(0, state.page * BLOG_PAGE_SIZE);
  if (!visible.length) {
    root.innerHTML = `
      <article class="blog-empty-state">
        По выбранному фильтру пока нет материалов. Выберите другую категорию или вернитесь к разделу «Все».
      </article>
    `;
    return;
  }
  root.innerHTML = visible
    .map(
      (post) => `
        <article class="blog-card-v2">
          <div class="blog-card-top">
            <span class="blog-card-category">${escapeHtml(post.category)}</span>
            <time class="blog-card-date" datetime="${escapeHtml(post.date)}">${escapeHtml(formatBlogDate(post.date))}</time>
          </div>
          <h3>${escapeHtml(post.title)}</h3>
          <p class="blog-card-excerpt">${escapeHtml(post.excerpt)}</p>
          <a class="blog-card-link" href="${escapeHtml(post.url)}">Читать материал</a>
        </article>
      `
    )
    .join("");
}

function renderSummary(posts, state) {
  const root = document.getElementById("blog-summary");
  if (!root) return;
  const visible = Math.min(posts.length, state.page * BLOG_PAGE_SIZE);
  root.textContent = `Показано ${visible} из ${posts.length} материалов`;
}

function renderShowMore(posts, state) {
  const button = document.getElementById("blog-show-more");
  if (!button) return;
  const hasMore = posts.length > state.page * BLOG_PAGE_SIZE;
  button.hidden = !hasMore;
  button.disabled = !hasMore;
}

function initBlogPage() {
  const rawPosts = getBlogSource();
  const posts = getSortedPosts(rawPosts.map(normalizePost));
  const counts = getCategoryCounts(posts);
  const categories = buildCategoryOrder(counts);
  let state = parseStateFromUrl(categories);
  renderHeroCount(posts.length);

  const render = () => {
    const filtered = filterPosts(posts, state.category);
    const maxPage = Math.max(1, Math.ceil(filtered.length / BLOG_PAGE_SIZE));
    if (state.page > maxPage) {
      state = { ...state, page: maxPage };
    }
    renderCategoryChips(categories, counts, state);
    renderPosts(filtered, state);
    renderSummary(filtered, state);
    renderShowMore(filtered, state);
    syncStateToUrl(state);
  };

  document.getElementById("blog-category-chips")?.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const button = target.closest("[data-blog-category]");
    if (!(button instanceof HTMLButtonElement)) return;
    const nextCategory = button.dataset.blogCategory || "Все";
    if (state.category === nextCategory) return;
    state = { ...state, category: nextCategory, page: 1 };
    reachMetrikaGoal("blog_filter_change", { category: nextCategory });
    render();
  });

  document.getElementById("blog-toggle-categories")?.addEventListener("click", () => {
    state = { ...state, showAllCategories: !state.showAllCategories };
    render();
  });

  document.getElementById("blog-show-more")?.addEventListener("click", () => {
    state = { ...state, page: state.page + 1 };
    reachMetrikaGoal("blog_show_more", { page: state.page });
    render();
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.closest(".blog-card-link")) {
      reachMetrikaGoal("blog_open_article");
    }
  });

  render();
}

initBlogPage();
