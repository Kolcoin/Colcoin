const topProjects = [
  { title: "ЖК Про.Молодость", district: "Невский р-н", metro: "Улица Дыбенко, 10 мин", price: "от 5.7 млн ₽" },
  { title: "ЖК Легенда Васильевского", district: "Василеостровский р-н", metro: "Горный институт, 20 мин", price: "от 13.4 млн ₽" },
  { title: "ЖК Цивилизация на Неве", district: "Невский р-н", metro: "Улица Дыбенко, 10 мин", price: "от 7.5 млн ₽" },
  { title: "ЖК Лисино", district: "Курортный р-н", metro: "Беговая, 15 мин", price: "от 10 млн ₽" }
];

const premiumProjects = [
  { title: "ЖК Прагма City", district: "Выборгский р-н", metro: "Парнас, 10 мин", price: "от 7.7 млн ₽" },
  { title: "ЖК МОСКО", district: "Московский р-н", metro: "Московские ворота, 10 мин", price: "от 8.1 млн ₽" },
  { title: "ЖК Морская миля", district: "Красносельский р-н", metro: "Юго-Западная, 10 мин", price: "от 8 млн ₽" },
  { title: "ЖК Образцовый квартал", district: "Пушкинский р-н", metro: "Купчино, 15 мин", price: "от 6.1 млн ₽" }
];

const segments = [
  {
    id: "first",
    chip: "🔑 Первая квартира",
    title: "Хватит платить за аренду — платите за своё",
    description: "Студии и 1-комнатные от 3 млн ₽. Ипотека от 0.1%, рассрочка без переплат.",
    tags: ["Ипотека от 0.1%", "Рассрочка 0%", "Субсидии"],
    projects: [
      { title: "ЖК LIBERTY DOM", district: "Тосненский р-н", metro: "Проспект Ветеранов, 40 мин", price: "от 2.7 млн ₽" },
      { title: "ЖК Аннино Сити", district: "Ломоносовский р-н", metro: "Проспект Ветеранов, 25 мин", price: "от 2.7 млн ₽" },
      { title: "ЖК Квартал Лаголово", district: "Ломоносовский р-н", metro: "Проспект Ветеранов, 20 мин", price: "от 3 млн ₽" }
    ]
  },
  {
    id: "invest",
    chip: "📈 Инвестиция",
    title: "Недвижимость доходнее вкладов — от 8% годовых",
    description: "Студии у метро от 4 млн ₽. Аналитика окупаемости и помощь с арендой.",
    tags: ["Доход 8-12%", "Рост стоимости", "Аренда"],
    projects: [
      { title: "ЖК Авенир Индастриал", district: "Кировский р-н", metro: "Кировский завод, 5 мин", price: "от 5.1 млн ₽" },
      { title: "ЖК Большой Казачий 10А", district: "Адмиралтейский р-н", metro: "Пушкинская, 5 мин", price: "от 4.5 млн ₽" },
      { title: "ЖК Апарт-отель Заневский", district: "Красногвардейский р-н", metro: "Ладожская, 5 мин", price: "от 5.6 млн ₽" }
    ]
  },
  {
    id: "upgrade",
    chip: "🏡 Расширение",
    title: "Семья растёт — пора в квартиру побольше",
    description: "2-4 комнаты с отделкой от 6 млн ₽. Trade-in: зачтём старую квартиру.",
    tags: ["Trade-in", "Зачёт квартиры", "Без переплат"],
    projects: [
      { title: "ЖК Образцовый квартал", district: "Пушкинский р-н", metro: "Купчино, 15 мин", price: "от 6.1 млн ₽" },
      { title: "ЖК Морская миля", district: "Красносельский р-н", metro: "Юго-Западная, 10 мин", price: "от 8 млн ₽" },
      { title: "ЖК Легенда Васильевского", district: "Василеостровский р-н", metro: "Горный институт, 20 мин", price: "от 13.4 млн ₽" }
    ]
  },
  {
    id: "family",
    chip: "💜 Для близких",
    title: "Надёжная квартира — лучший подарок",
    description: "Безопасные районы рядом с вузами. Помощь с оформлением и сопровождением.",
    tags: ["Безопасные районы", "Оформление", "Рядом с вузами"],
    projects: [
      { title: "ЖК Цветной город", district: "Красногвардейский р-н", metro: "Гражданский проспект, 15 мин", price: "от 4.2 млн ₽" },
      { title: "ЖК Ручьи 2", district: "Красногвардейский р-н", metro: "Академическая, 10 мин", price: "от 4.7 млн ₽" },
      { title: "ЖК Образцовый квартал", district: "Пушкинский р-н", metro: "Купчино, 15 мин", price: "от 6.1 млн ₽" }
    ]
  }
];

const districts = [
  { name: "Выборгский р-н", info: "28 ЖК · от 3.1 млн ₽" },
  { name: "Приморский р-н", info: "23 ЖК · от 4.9 млн ₽" },
  { name: "Пушкинский р-н", info: "21 ЖК · от 3.6 млн ₽" },
  { name: "Василеостровский р-н", info: "20 ЖК · от 7.7 млн ₽" },
  { name: "Московский р-н", info: "20 ЖК · от 5.5 млн ₽" },
  { name: "Петроградский р-н", info: "18 ЖК · от 6.5 млн ₽" },
  { name: "Невский р-н", info: "18 ЖК · от 4.7 млн ₽" },
  { name: "Красногвардейский р-н", info: "14 ЖК · от 4 млн ₽" }
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
        <p class="project-price">${item.price}</p>
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
renderCards("premium-projects", premiumProjects);
renderSegments();
renderDistricts();
setupLeadForm();
