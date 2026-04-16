const topProjects = [
  {
    title: "ЖК Urban Riverside",
    district: "СЗАО, Москва",
    metro: "10 минут до метро",
    price: "от 9.1 млн ₽",
    sourceLabel: "Авторская витрина",
    sourceUrl: "./starts/zhk-enigmiya.html"
  },
  {
    title: "ЖК 1-й Донской",
    district: "7 км от МКАД · М-4 Дон",
    metro: "станция Калинина 15–17 мин пешком",
    price: "по запросу",
    sourceLabel: "Авторская витрина",
    sourceUrl: "./starts/zhk-enigmiya.html"
  },
  {
    title: "ЖК Park Side",
    district: "Московская область",
    metro: "рядом МЦД",
    price: "от 7.8 млн ₽",
    sourceLabel: "Авторская витрина",
    sourceUrl: "./starts/zhk-enigmiya.html"
  }
];

const launchBlocks = [
  {
    id: "first-home",
    icon: "🔑",
    title: "Старт для жизни: первая квартира без хаоса выбора",
    description:
      "Собрали варианты для первой покупки: удобные районы, понятный бюджет входа и прогнозируемые условия сделки.",
    tags: ["Первичная покупка", "Ипотека", "Готовая инфраструктура"],
    buttonText: "Подобрать проекты для первой покупки",
    buttonClass: "btn-warm",
    projects: [
      {
        title: "ЖК 1-й Донской",
        district: "Москва",
        metro: "подбор по параметрам",
        price: "по запросу",
        sourceUrl: "./starts/zhk-enigmiya.html"
      },
      {
        title: "ЖК 1-й Донской (семейный формат)",
        district: "Московская область",
        metro: "рядом транспорт",
        price: "по запросу",
        sourceUrl: "./starts/zhk-enigmiya.html"
      }
    ]
  },
  {
    id: "invest",
    icon: "📈",
    title: "Инвестиционный сценарий: новостройки с потенциалом",
    description:
      "Выделили проекты, которые чаще выбирают под арендную стратегию и долгосрочный рост стоимости.",
    tags: ["Инвестиция", "Ликвидность", "ЦАО"],
    buttonText: "Открыть инвестиционные проекты",
    buttonClass: "btn-cool",
    projects: [
      {
        title: "ЖК 1-й Донской (инвест-формат)",
        district: "Москва",
        metro: "транспортная доступность",
        price: "по запросу",
        sourceUrl: "./starts/zhk-enigmiya.html"
      },
      {
        title: "ЖК 1-й Донской (доходный сценарий)",
        district: "Москва и МО",
        metro: "быстрый выезд",
        price: "по запросу",
        sourceUrl: "./starts/zhk-enigmiya.html"
      }
    ]
  },
  {
    id: "family-upgrade",
    icon: "🏡",
    title: "Семейный апгрейд: больше пространства и инфраструктуры",
    description:
      "Подходящие варианты для семьи: комфортная среда, нужный метраж и инфраструктура рядом с домом.",
    tags: ["Семья", "Расширение", "Комфортная среда"],
    buttonText: "Перейти к семейным вариантам",
    buttonClass: "btn-berry",
    projects: [
      {
        title: "ЖК 1-й Донской (семья)",
        district: "Москва",
        metro: "школы и сервисы",
        price: "по запросу",
        sourceUrl: "./starts/zhk-enigmiya.html"
      },
      {
        title: "ЖК 1-й Донской (расширение)",
        district: "Московская область",
        metro: "спокойная локация",
        price: "по запросу",
        sourceUrl: "./starts/zhk-enigmiya.html"
      }
    ]
  }
];

const premiumProjects = [
  {
    title: "ЖК 1-й Донской",
    district: "Москва и область",
    metro: "подбор по цели",
    price: "по запросу",
    sourceLabel: "Новая статья",
    sourceUrl: "./starts/zhk-enigmiya.html"
  }
];

const districts = [
  { name: "Москва", info: "актуальные старты · по запросу" },
  { name: "Московская область", info: "актуальные старты · по запросу" },
  { name: "Новая Москва", info: "актуальные старты · по запросу" },
  { name: "Ближнее Подмосковье", info: "актуальные старты · по запросу" }
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

function renderLaunchBlocks() {
  const root = document.getElementById("launch-blocks");
  if (!root) return;

  root.innerHTML = launchBlocks
    .map((block) => {
      const cards = block.projects
        .map(
          (item) => `
            <article class="project-card">
              <h3>${item.title}</h3>
              <p class="project-meta">${item.district}</p>
              <p class="project-meta">${item.metro}</p>
              <p class="project-price">${item.price}</p>
              <a class="project-link" href="${item.sourceUrl}">Открыть страницу старта</a>
            </article>
          `
        )
        .join("");

      return `
        <section class="launch-block" id="launch-${block.id}">
          <div class="launch-block-head">
            <p class="launch-icon">${block.icon}</p>
            <h3>${block.title}</h3>
            <p>${block.description}</p>
            <div class="segment-tags">
              ${block.tags.map((tag) => `<span>${tag}</span>`).join("")}
            </div>
            <a class="btn ${block.buttonClass}" href="#contact">${block.buttonText}</a>
          </div>
          <div class="cards-grid cards-grid-compact">${cards}</div>
        </section>
      `;
    })
    .join("");
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
renderLaunchBlocks();
renderCards("premium-projects", premiumProjects);
renderDistricts();
setupLeadForm();
