const topProjects = [
  {
    title: "ЖК Изумрудные холмы",
    district: "Красногорск, МО",
    metro: "22 км от центра Москвы",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/izumrudnye-kholmy.html"
  },
  {
    title: "ЖК Летний сад",
    district: "Москва",
    metro: "район Селигерская / 800-летия Москвы",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/letniy-sad.html"
  },
  {
    title: "ЖК Нормандия",
    district: "Лосиноостровский район, Москва",
    metro: "Медведково (пешком)",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/normandiya.html"
  },
  {
    title: "ЖК Headliner",
    district: "ЦАО, Москва",
    metro: "Москва-Сити",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/headliner.html"
  }
];

const launchProjects = [
  {
    title: "Изумрудные холмы",
    district: "Красногорск, МО",
    metro: "комплексная квартальная застройка",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: отдельная SEO-страница",
    sourceUrl: "./starts/izumrudnye-kholmy.html"
  },
  {
    title: "Летний сад",
    district: "Москва",
    metro: "вблизи Селигерской",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: отдельная SEO-страница",
    sourceUrl: "./starts/letniy-sad.html"
  },
  {
    title: "Нормандия",
    district: "Москва",
    metro: "Лосиноостровский район",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: отдельная SEO-страница",
    sourceUrl: "./starts/normandiya.html"
  },
  {
    title: "Headliner",
    district: "ЦАО, Москва",
    metro: "Москва-Сити",
    price: "старт в витрине Нмаркет.ПРО",
    sourceLabel: "Источник: отдельная SEO-страница",
    sourceUrl: "./starts/headliner.html"
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
        title: "Изумрудные холмы",
        district: "Красногорск, МО",
        metro: "22 км от центра Москвы",
        price: "цены по запросу",
        sourceUrl: "./starts/izumrudnye-kholmy.html"
      },
      {
        title: "Летний сад",
        district: "Москва",
        metro: "Селигерская / 800-летия Москвы",
        price: "цены по запросу",
        sourceUrl: "./starts/letniy-sad.html"
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
        title: "Headliner",
        district: "ЦАО, Москва",
        metro: "Москва-Сити",
        price: "цены по запросу",
        sourceUrl: "./starts/headliner.html"
      },
      {
        title: "Нормандия",
        district: "Лосиноостровский район, Москва",
        metro: "Медведково (пешком)",
        price: "цены по запросу",
        sourceUrl: "./starts/normandiya.html"
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
        title: "Летний сад",
        district: "Москва",
        metro: "развитый район",
        price: "цены по запросу",
        sourceUrl: "./starts/letniy-sad.html"
      },
      {
        title: "Изумрудные холмы",
        district: "Красногорск, МО",
        metro: "квартальная застройка",
        price: "цены по запросу",
        sourceUrl: "./starts/izumrudnye-kholmy.html"
      }
    ]
  }
];

const premiumProjects = [
  {
    title: "Headliner",
    district: "ЦАО, Москва",
    metro: "вид на Москву-реку и Москва-Сити",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/headliner.html"
  },
  {
    title: "Нормандия",
    district: "Лосиноостровский район",
    metro: "Медведково",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/normandiya.html"
  },
  {
    title: "Летний сад",
    district: "Москва",
    metro: "Селигерская",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/letniy-sad.html"
  },
  {
    title: "Изумрудные холмы",
    district: "Красногорск",
    metro: "МО",
    price: "цены по запросу",
    sourceLabel: "Нмаркет.ПРО · отдельная SEO-страница",
    sourceUrl: "./starts/izumrudnye-kholmy.html"
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
renderCards("launch-projects", launchProjects);
renderLaunchBlocks();
renderCards("premium-projects", premiumProjects);
renderDistricts();
setupLeadForm();
