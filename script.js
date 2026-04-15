const topProjects = [
  { title: "Квартал Мит", district: "СЗАО, Москва", metro: "Пятницкое шоссе", price: "от 10.6 млн ₽", sourceLabel: "старт февраль 2026" },
  { title: "Зелёный парк", district: "ЗелАО, Москва", metro: "Зеленоград", price: "от 7.7 млн ₽", sourceLabel: "вывод корпусов март 2026" },
  { title: "Нарвин", district: "САО, Москва", metro: "Водный стадион", price: "от 12.26 млн ₽", sourceLabel: "вывод корпусов март 2026" },
  { title: "Татум", district: "ЮЗАО, Москва", metro: "Калужская / Воронцовская", price: "от 20.33 млн ₽", sourceLabel: "старт продаж март 2026" }
];

const launchProjects = [
  {
    title: "Аникеевский",
    district: "Красногорск, МО",
    metro: "Николо-Урюпино",
    price: "от 4.6 млн ₽",
    sourceLabel: "Novostroy-M · март 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_mart_2026"
  },
  {
    title: "Никольский квартал Отрада",
    district: "Красногорск, МО",
    metro: "мкр. Опалиха",
    price: "от 5.1 млн ₽",
    sourceLabel: "Novostroy-M · февраль 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_fevral_2026"
  },
  {
    title: "Сити-квартал Отрада",
    district: "Красногорск, МО",
    metro: "Чернево-2",
    price: "от 6.5 млн ₽",
    sourceLabel: "Novostroy-M · март 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_mart_2026"
  },
  {
    title: "Лесная Отрада",
    district: "Аристово, МО",
    metro: "Пятницкое шоссе",
    price: "от 6.44 млн ₽",
    sourceLabel: "Novostroy-M · февраль 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_fevral_2026"
  },
  {
    title: "Сердце Лыткарино",
    district: "Лыткарино, МО",
    metro: "Томилинский лесопарк",
    price: "от 6 млн ₽",
    sourceLabel: "Novostroy-M · март 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_mart_2026"
  },
  {
    title: "Прибрежный Парк",
    district: "Домодедово, МО",
    metro: "с. Ям",
    price: "от 5.8 млн ₽",
    sourceLabel: "Novostroy-M · март 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_mart_2026"
  },
  {
    title: "Восточное Бутово",
    district: "Ленинский, МО",
    metro: "Бутовский лесопарк",
    price: "от 7.1 млн ₽",
    sourceLabel: "Novostroy-M · март 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_mart_2026"
  },
  {
    title: "Белая Дача Парк",
    district: "Котельники, МО",
    metro: "Томилинский лесопарк",
    price: "от 9.37 млн ₽",
    sourceLabel: "Novostroy-M · март 2026",
    sourceUrl: "https://www.novostroy-m.ru/analitika/starty_prodaj_mart_2026"
  }
];

const premiumProjects = [
  { title: "АУРУС Резиденции", district: "ЦАО, Москва", metro: "Москва-Сити", price: "от 38.88 млн ₽", sourceLabel: "старт февраль 2026" },
  { title: "Оне", district: "Пресненский р-н", metro: "Москва-Сити", price: "от 74.4 млн ₽", sourceLabel: "новый пул март 2026" },
  { title: "Резиденция Омега", district: "Гагаринский р-н", metro: "ул. Фотиевой", price: "от 123 млн ₽", sourceLabel: "старт март 2026" },
  { title: "Мастерс", district: "Хорошевский р-н", metro: "Аэропорт", price: "цена по запросу", sourceLabel: "старт март 2026" }
];

const segments = [
  {
    id: "first",
    chip: "🔑 Первая квартира",
    title: "Первая квартира в Москве и ближнем Подмосковье",
    description: "Студии и 1-комнатные форматы от 4.6 млн ₽ в новых стартах продаж.",
    tags: ["Ипотека от 0.1%", "Рассрочка 0%", "Субсидии"],
    projects: [
      { title: "Аникеевский", district: "Красногорск, МО", metro: "4–6 этажей", price: "от 4.6 млн ₽" },
      { title: "Никольский квартал Отрада", district: "Опалиха, МО", metro: "студии 21.2 м²", price: "от 5.1 млн ₽" },
      { title: "Лесная Отрада", district: "Аристово, МО", metro: "без отделки", price: "от 6.44 млн ₽" }
    ]
  },
  {
    id: "invest",
    chip: "📈 Инвестиция",
    title: "Инвестиционные старты рядом с Москвой",
    description: "Выбираем новые корпуса и старты продаж с потенциалом роста цены входа.",
    tags: ["Доход 8-12%", "Рост стоимости", "Аренда"],
    projects: [
      { title: "Квартал Мит", district: "Митино, Москва", metro: "Пятницкое шоссе", price: "от 10.6 млн ₽" },
      { title: "Нарвин", district: "Головинский р-н", metro: "Водный стадион", price: "от 12.26 млн ₽" },
      { title: "Зелёный парк", district: "Зеленоград", metro: "готовые кварталы", price: "от 7.7 млн ₽" }
    ]
  },
  {
    id: "upgrade",
    chip: "🏡 Расширение",
    title: "Семья растёт — расширяемся в новых очередях",
    description: "2–4 комнаты в новых корпусах Москвы и Новой Москвы, включая trade-in.",
    tags: ["Trade-in", "Зачёт квартиры", "Без переплат"],
    projects: [
      { title: "Преображенская площадь (2 очередь)", district: "ВАО, Москва", metro: "Преображенская площадь", price: "от 15.3 млн ₽" },
      { title: "Северный порт (2 очередь)", district: "САО, Москва", metro: "Беломорская", price: "от 15.4 млн ₽" },
      { title: "Литературный Квартал", district: "Внуково, НАО", metro: "Рассказовка / Пыхтино", price: "от 10.3 млн ₽" }
    ]
  },
  {
    id: "family",
    chip: "💜 Для близких",
    title: "Надёжная квартира для родителей и детей",
    description: "Подбираем спокойные районы и комплексы с готовой инфраструктурой.",
    tags: ["Безопасные районы", "Оформление", "Рядом с вузами"],
    projects: [
      { title: "Баланс", district: "Рязанский р-н, Москва", metro: "Окская", price: "от 14 млн ₽" },
      { title: "Бунинская набережная", district: "Коммунарка, НАО", metro: "НАО", price: "от 9.3 млн ₽" },
      { title: "Первый Московский", district: "Филимонковский р-н", metro: "Филатов Луг", price: "от 12.79 млн ₽" }
    ]
  }
];

const districts = [
  { name: "СЗАО", info: "Митино и Северо-Запад · от 10.6 млн ₽" },
  { name: "САО", info: "Головинский и Левобережный · от 12.26 млн ₽" },
  { name: "ВАО", info: "Преображенское и Сокольники · от 15.3 млн ₽" },
  { name: "ЮЗАО", info: "Обручевский район · от 20.33 млн ₽" },
  { name: "НАО", info: "Новая Москва · от 9.3 млн ₽" },
  { name: "ЦАО", info: "Пресненский район · от 38.88 млн ₽" },
  { name: "Красногорск, МО", info: "несколько стартов · от 4.6 млн ₽" },
  { name: "Домодедово, МО", info: "новые очереди · от 5.8 млн ₽" }
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
