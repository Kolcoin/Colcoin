const BLOG_PAGE_SIZE = 6;

function reachMetrikaGoal(goal) {
  try {
    if (typeof window !== "undefined" && typeof window.ym === "function") {
      window.ym(108657608, "reachGoal", goal);
    }
  } catch (_error) {
    // no-op for analytics safety
  }
}

function getBlogState() {
  const params = new URLSearchParams(window.location.search);
  return {
    category: params.get("category") || "",
    page: Math.max(1, Number.parseInt(params.get("page") || "1", 10) || 1)
  };
}

function writeBlogState(state) {
  const params = new URLSearchParams();
  if (state.category) params.set("category", state.category);
  if (state.page > 1) params.set("page", String(state.page));
  const query = params.toString();
  const nextUrl = query ? `${window.location.pathname}?${query}` : window.location.pathname;
  window.history.replaceState({}, "", nextUrl);
}

function formatBlogDate(isoDate) {
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) return isoDate;
  return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function sortedPostsByDate(posts) {
  return [...posts].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

function renderCategoryFilters(currentCategory) {
  const root = document.getElementById("blog-category-filters");
  if (!root) return;
  const categories = [...new Set(window.REALTY_BLOG_POSTS.map((post) => post.category))];
  const all = [{ key: "", label: "Все" }, ...categories.map((c) => ({ key: c, label: c }))];
  root.innerHTML = all
    .map(
      (item) => `
      <button class="segment-chip ${item.key === currentCategory ? "active" : ""}" type="button" data-blog-category="${item.key}">
        ${item.label}
      </button>
    `
    )
    .join("");
}

function filterPosts(category) {
  if (!category) return sortedPostsByDate(window.REALTY_BLOG_POSTS);
  return sortedPostsByDate(window.REALTY_BLOG_POSTS.filter((post) => post.category === category));
}

function renderPosts(posts, page) {
  const root = document.getElementById("blog-results");
  if (!root) return;
  const visible = posts.slice(0, page * BLOG_PAGE_SIZE);
  root.innerHTML = visible
    .map(
      (post) => `
      <article class="blog-card">
        <span class="blog-category">${post.category}</span>
        <h3>${post.title}</h3>
        <p class="project-meta">${formatBlogDate(post.date)}</p>
        <p>${post.excerpt}</p>
        <a class="project-link" href="${post.url}">Читать статью</a>
      </article>
    `
    )
    .join("");
}

function updateBlogSummary(posts, page) {
  const summary = document.getElementById("blog-summary");
  if (!summary) return;
  const visible = Math.min(posts.length, page * BLOG_PAGE_SIZE);
  summary.textContent = `Показано ${visible} из ${posts.length} материалов`;
}

function updateBlogPager(posts, page) {
  const more = document.getElementById("blog-show-more");
  if (!more) return;
  more.hidden = page * BLOG_PAGE_SIZE >= posts.length;
}

function initBlogPage() {
  if (!Array.isArray(window.REALTY_BLOG_POSTS)) return;

  let state = getBlogState();

  const render = () => {
    const filtered = filterPosts(state.category);
    renderCategoryFilters(state.category);
    renderPosts(filtered, state.page);
    updateBlogSummary(filtered, state.page);
    updateBlogPager(filtered, state.page);
    writeBlogState(state);

    document.querySelectorAll("[data-blog-category]").forEach((button) => {
      button.addEventListener("click", () => {
        state = { category: button.dataset.blogCategory || "", page: 1 };
        render();
      });
    });
  };

  document.getElementById("blog-show-more")?.addEventListener("click", () => {
    state = { ...state, page: state.page + 1 };
    render();
  });

  document.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;

    const articleLink = target.closest('.blog-card a.project-link');
    if (articleLink) {
      reachMetrikaGoal("open_article");
      return;
    }

    const telLink = target.closest('a[href^="tel:"]');
    if (telLink) {
      reachMetrikaGoal("click_phone");
      return;
    }

    const telegramLink = target.closest('a[href*="t.me/"]');
    if (telegramLink) {
      reachMetrikaGoal("click_telegram");
    }
  });

  render();
}

initBlogPage();
