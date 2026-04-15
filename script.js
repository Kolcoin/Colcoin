const topProjects = [
  {
    title: "ЖК Изумрудные холмы",
    district: "Красногорск, МО",
    metro: "22 км от центра Москвы",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · etalon-msk",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "ЖК Летний сад",
    district: "Москва",
    metro: "район Селигерская / 800-летия Москвы",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · etalon-msk",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "ЖК Нормандия",
    district: "Лосиноостровский район, Москва",
    metro: "Медведково (пешком)",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · etalon-msk",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "ЖК Headliner",
    district: "ЦАО, Москва",
    metro: "Москва-Сити",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · headliner",
    sourceUrl: "https://promo.nmarket.pro/headliner"
  }
];

const launchProjects = [
  {
    title: "Изумрудные холмы",
    district: "Красногорск, МО",
    metro: "комплексная квартальная застройка",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: Нмаркет.ПРО",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "Летний сад",
    district: "Москва",
    metro: "вблизи Селигерской",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: Нмаркет.ПРО",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "Нормандия",
    district: "Москва",
    metro: "Лосиноостровский район",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: Нмаркет.ПРО",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "Headliner",
    district: "ЦАО, Москва",
    metro: "Москва-Сити",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: Нмаркет.ПРО",
    sourceUrl: "https://promo.nmarket.pro/headliner"
  }
];

const premiumProjects = [
  {
    title: "Headliner",
    district: "ЦАО, Москва",
    metro: "вид на Москву-реку и Москва-Сити",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · headliner",
    sourceUrl: "https://promo.nmarket.pro/headliner"
  },
  {
    title: "Нормандия",
    district: "Лосиноостровский район",
    metro: "Медведково",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · etalon-msk",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "Летний сад",
    district: "Москва",
    metro: "Селигерская",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · etalon-msk",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  },
  {
    title: "Изумрудные холмы",
    district: "Красногорск",
    metro: "МО",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · etalon-msk",
    sourceUrl: "https://promo.nmarket.pro/etalon-msk"
  }
];

const segments = [
  {
    id: "first",
    chip: "🔑 Первая квартира",
    title: "Старты для первой покупки",
    description: "Выбор из московских и подмосковных проектов по Нмаркет.ПРО.",
    tags: ["Подбор по цели", "Официальные страницы", "Актуальные витрины"],
    projects: [
      { title: "Изумрудные холмы", district: "Красногорск, МО", metro: "квартальный формат", price: "Нмаркет.ПРО" },
      { title: "Летний сад", district: "Москва", metro: "развитый район", price: "Нмаркет.ПРО" },
      { title: "Нормандия", district: "Москва", metro: "зелёная локация", price: "Нмаркет.ПРО" }
    ]
  },
  {
    id: "invest",
    chip: "📈 Инвестиция",
    title: "Проекты с инвестиционным интересом",
    description: "Центральные и масштабные объекты из публичных страниц Нмаркет.ПРО.",
    tags: ["Москва", "ЦАО", "Крупные проекты"],
    projects: [
      { title: "Headliner", district: "ЦАО", metro: "небоскрёбы", price: "Нмаркет.ПРО" },
      { title: "Летний сад", district: "Москва", metro: "метро рядом", price: "Нмаркет.ПРО" },
      { title: "Нормандия", district: "Москва", metro: "устойчивый спрос", price: "Нмаркет.ПРО" }
    ]
  },
  {
    id: "upgrade",
    chip: "🏡 Расширение",
    title: "Расширение жилплощади",
    description: "Семейные форматы в проектах с готовой инфраструктурой.",
    tags: ["Семья", "Инфраструктура", "Надёжный застройщик"],
    projects: [
      { title: "Изумрудные холмы", district: "Красногорск", metro: "микрорайон", price: "Нмаркет.ПРО" },
      { title: "Летний сад", district: "Москва", metro: "территория комфорта", price: "Нмаркет.ПРО" },
      { title: "Headliner", district: "ЦАО", metro: "многофункциональный комплекс", price: "Нмаркет.ПРО" }
    ]
  },
  {
    id: "family",
    chip: "💜 Для близких",
    title: "Покупка для родителей и детей",
    description: "Подбираем проекты с удобной транспортной доступностью и окружением.",
    tags: ["Транспорт", "Школы и сады", "Городская среда"],
    projects: [
      { title: "Нормандия", district: "Москва", metro: "рядом парки", price: "Нмаркет.ПРО" },
      { title: "Летний сад", district: "Москва", metro: "собственная инфраструктура", price: "Нмаркет.ПРО" },
      { title: "Изумрудные холмы", district: "МО", metro: "комплексный проект", price: "Нмаркет.ПРО" }
    ]
  }
];

const districts = [
  { name: "ЦАО", info: "Headliner · Нмаркет.ПРО" },
  { name: "СВАО", info: "Нормандия · Нмаркет.ПРО" },
  { name: "САО", info: "Летний сад · Нмаркет.ПРО" },
  { name: "Красногорск, МО", info: "Изумрудные холмы · Нмаркет.ПРО" }
];

function renderCards(targetId, items) {
  const root = document.getElementById(targetId);
  if (!root) return;
  root.innerHTML = items
    .map(
      (item) => `
      <article class="project-card">
        <h3>${item.title}</h3>
        <p class="project-meta">${item.district}</p>
        <p class="project-meta">${item.metro}</p>
        ${item.sourceLabel ? `<p class="project-source">${item.sourceLabel}</p>` : ""}
        <p class="project-price">${item.price}</p>
        ${
          item.sourceUrl
            ? `<a class="project-link" href="${item.sourceUrl}" target="_blank" rel="noopener noreferrer">Проверить источник</a>`
            : ""
        }
      </article>
    `
    )
    .join("");
}

function renderDistricts() {
  const root = document.getElementById("districts-list");
  if (!root) return;
  root.innerHTML = districts
    .map(
      (district) => `
      <article class="district-card">
        <h3>${district.name}</h3>
        <p>${district.info}</p>
      </article>
    `
    )
    .join("");
}

function renderSegments() {
  const controls = document.getElementById("segment-controls");
  const title = document.getElementById("segment-title");
  const description = document.getElementById("segment-description");
  const tags = document.getElementById("segment-tags");
  const cardsRoot = document.getElementById("segment-projects");

  if (!controls || !title || !description || !tags || !cardsRoot) return;

  let activeId = segments[0].id;

  const draw = () => {
    controls.innerHTML = segments
      .map(
        (segment) => `
        <button class="segment-chip ${segment.id === activeId ? "active" : ""}" data-segment-id="${segment.id}" type="button">
          ${segment.chip}
        </button>
      `
      )
      .join("");

    const activeSegment = segments.find((segment) => segment.id === activeId) || segments[0];
    title.textContent = activeSegment.title;
    description.textContent = activeSegment.description;
    tags.innerHTML = activeSegment.tags.map((tag) => `<span>${tag}</span>`).join("");

    cardsRoot.innerHTML = activeSegment.projects
      .map(
        (item) => `
        <article class="project-card">
          <h3>${item.title}</h3>
          <p class="project-meta">${item.district}</p>
          <p class="project-meta">${item.metro}</p>
          ${item.sourceLabel ? `<p class="project-source">${item.sourceLabel}</p>` : ""}
          <p class="project-price">${item.price}</p>
        </article>
      `
      )
      .join("");
  };

  controls.addEventListener("click", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLElement)) return;
    const nextId = target.dataset.segmentId;
    if (!nextId || nextId === activeId) return;
    activeId = nextId;
    draw();
  });

  draw();
}

function setupLeadForm() {
  const form = document.querySelector(".lead-form");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    event.preventDefault();
  });

  const button = form.querySelector("button");
  if (button) {
    button.addEventListener("click", () => {
      const nameInput = document.getElementById("name");
      const name = nameInput instanceof HTMLInputElement ? nameInput.value.trim() : "";
      alert(
        name
          ? `${name}, спасибо! Мы подготовим подборку и свяжемся с вами в ближайшее время.`
          : "Спасибо! Мы подготовим подборку и свяжемся с вами в ближайшее время."
      );
    });
  }
}

renderCards("top-projects", topProjects);
renderCards("launch-projects", launchProjects);
renderCards("premium-projects", premiumProjects);
renderSegments();
renderDistricts();
setupLeadForm();
