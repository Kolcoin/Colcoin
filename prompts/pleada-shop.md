# Промт: Агрегатор новостроек PLEADA.shop

> Полноценный промт для воссоздания сайта-агрегатора квартир в новостройках по типу [pleada.shop](https://pleada.shop/?utm_source=denblog). Охватывает главную страницу, каталог ЖК, карточку ЖК, страницу районов, страницу застройщиков, страницу ипотеки, блог и общую архитектуру.

---

## Промт

```
Создай мультистраничный сайт-агрегатор квартир в новостройках Санкт-Петербурга.

Бренд: PLEADA — экспертное бюро недвижимости.
Слоган: «Подберём квартиру в новостройке СПб под вашу цель».
Город: Санкт-Петербург и Ленинградская область.

=== ТЕХНОЛОГИИ ===

HTML5 + CSS3 + vanilla JavaScript ES6+. Без фреймворков, без сборки, без npm.
Внешние ресурсы: Google Fonts (Inter: 400, 500, 600, 700, 800).
Файловая структура:
  /index.html                        — главная
  /novostrojki/index.html             — каталог ЖК
  /novostrojki/[slug]/index.html      — карточка ЖК (шаблон)
  /districts/index.html               — районы
  /zastrojshchiki/index.html          — застройщики
  /mortgage/index.html                — ипотека
  /blog/index.html                    — блог
  /styles.css                         — общие стили
  /script.js                          — общая логика
  /data.js                            — все данные (ЖК, районы, застройщики)
  /sitemap.xml
  /robots.txt

=== ЦВЕТОВАЯ СХЕМА ===

:root {
  --bg: #f7f8fb;                    /* светло-серый фон страницы */
  --surface: #ffffff;               /* белый фон карточек */
  --surface-muted: #f2f4fa;         /* фон muted-секций */
  --text: #1c2333;                  /* основной текст */
  --text-muted: #5f6980;            /* вторичный текст */
  --primary: #c8102e;               /* красный — главный accent (CTA, бейджи, цены) */
  --primary-hover: #a50d24;         /* красный hover */
  --primary-light: #fef2f2;         /* светло-красный фон */
  --secondary: #7c3aed;            /* фиолетовый — вторичный accent (акции, MAX) */
  --secondary-hover: #6d28d9;
  --segment-first: #fff1f2;         /* розовый — «Первая квартира» */
  --segment-invest: #eff6ff;        /* голубой — «Инвестиция» */
  --segment-upgrade: #f0fdf4;       /* мятный — «Расширение» */
  --segment-family: #faf5ff;        /* лавандовый — «Для близких» */
  --dark: #111827;                  /* тёмный фон футера */
  --dark-surface: #1f2937;
  --border: #e5e7eb;
  --radius: 16px;
  --radius-sm: 12px;
  --radius-pill: 999px;
  --shadow-card: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-hover: 0 10px 25px rgba(0,0,0,0.08);
  --container: 1200px;
}

=== ТИПОГРАФИКА ===

Шрифт: Inter через Google Fonts.
H1: clamp(2rem, 4vw, 2.75rem), font-weight: 800, line-height: 1.15.
H2: clamp(1.5rem, 3vw, 2rem), font-weight: 700.
H3: 1.1rem, font-weight: 600.
Body: 1rem/1.6, weight 400, цвет var(--text).
Мелкий текст (meta, badges): 0.85–0.9rem, weight 500–600.

=== КОМПОНЕНТЫ (общие для всех страниц) ===

1. HEADER (sticky, backdrop-filter: blur(10px)):
   - Лого «PLEADA» (текст, font-weight: 800, letter-spacing: 0.02em) + красная точка (8px circle var(--primary))
   - Навигация: Новостройки, Районы, Застройщики, Ипотека, Блог
   - Счётчик: «1180 ЖК · 57 189 квартир» (серый мелкий текст)
   - Кнопка «Подобрать квартиру» (var(--primary), белый текст, radius-sm)
   - Мобильный бургер (появляется ≤1024px, slide-in меню)

2. FOOTER (background: var(--dark)):
   - Лого PLEADA + описание компании (мелкий серый текст)
   - 3 колонки ссылок: КАТАЛОГ (По районам, По метро, Премиальные, Все ЖК), ПОКУПАТЕЛЯМ (Ипотека, Trade-in, Материнский капитал, Блог), КОНТАКТЫ (Телефон, Email, Адрес)
   - Иконки соцсетей: Telegram, MAX, YouTube
   - Контактная строка: телефон (кликабельный tel:), email, адрес
   - Копирайт + «Все цены актуальны на [месяц год]»
   - Юридический disclaimer мелким шрифтом

3. CTA-БАННЕР (повторяется внизу каждой страницы):
   - Фон var(--secondary), белый текст
   - Заголовок + форма (имя + телефон) или ссылка на MAX
   - «Акции, старты продаж и скидки до 1 млн — в мессенджере MAX»

4. КАРТОЧКА ЖК (project-card, переиспользуется везде):
   - Изображение сверху (aspect-ratio: 16/10, object-fit: cover, border-radius сверху)
   - Бейдж класса жилья (позиция: absolute top-left): «бизнес» / «комфорт» / «эконом» / «премиум» — pill, мелкий текст, полупрозрачный фон
   - Название ЖК (H3, font-weight: 600)
   - Район + кол-во квартир (мелкий серый текст, 2 строки)
   - Застройщик (мелкий текст)
   - Метро: название + время (иконка 🚇 или цветная точка линии)
   - Цена: «от X млн ₽» — красный бейдж или красный текст, font-weight: 700
   - Вся карточка — ссылка <a>. Hover: translateY(-2px) + shadow-hover
   - Без кнопок внутри карточки

5. ФОРМА ЗАЯВКИ (lead-form):
   - Заголовок: «Получить подборку квартир»
   - Подзаголовок: «Бесплатно за 2 часа от экспертов PLEADA»
   - Поле 1: «Что вы ищете?» — 4 кнопки-выбора (🔑 Первая квартира, 📈 Инвестиция, 🏡 Расширение, 💜 Для близких). Визуально — pills, активная подсвечена var(--primary)
   - Поле 2: «Бюджет» — 5 pills (до 5 млн, 5–8 млн, 8–12 млн, 12–20 млн, от 20 млн)
   - Кнопка: «Получить подборку за 2 часа» (var(--primary), full-width, крупная, min-height: 52px)
   - Подпись: «Бесплатно и без обязательств»
   - JS: при клике alert с персонализацией. Сохранение выбора в переменные

=== СТРАНИЦА 1: ГЛАВНАЯ (index.html) ===

Структура секций:

1. HERO:
   - Левая колонка (60%):
     * Мелкая надпись сверху: «1180 новостроек · 57 189 квартир»
     * H1: «Подберём квартиру в новостройке СПб под вашу цель»
     * Подзаголовок (var(--text-muted)): «Первая квартира, инвестиция или расширение — находим лучшие варианты бесплатно. Скидки до 1 млн ₽ от застройщиков.»
     * 4 KPI-карточки (grid 4 колонки): 0₽ комиссия / 2 часа подборка / 188 застройщиков / 4.8 ★ рейтинг. Каждая — border, radius-sm, padding 14px
   - Правая колонка (40%): ФОРМА ЗАЯВКИ (компонент #5)
   - Grid: grid-template-columns: 1fr minmax(340px, 420px), gap: 32px. На мобильном — 1 колонка

2. ТОП НОВОСТРОЕК:
   - Заголовок H2 + ссылка «Все 1180 ЖК →» (var(--primary), стрелка)
   - Grid 4 колонки карточек ЖК (компонент #4)
   - Данные из JS-массива topProjects[]

3. КАКАЯ У ВАС ЦЕЛЬ (segment-cards):
   - Заголовок H2 + подзаголовок
   - Grid 4 колонки (2 на планшете, 1 на мобильном)
   - 4 карточки-сегмента, каждая:
     * Фон: свой пастельный цвет (--segment-first / invest / upgrade / family)
     * Эмодзи: 🔑 / 📈 / 🏡 / 💜
     * Заголовок (bold): «Первая квартира» / «Инвестиция» / «Расширение» / «Для близких»
     * Описание-подзаголовок (italic или normal, muted)
     * Выгода крупным текстом: «Студии от 3 млн ₽. Ипотека от 0.1%» и т.д.
     * 3 pill-тега (мелкие, фон чуть темнее пастельного)
     * Ссылка «Подобрать →» (var(--primary))
   - Вся карточка кликабельна

4. РАЗВЁРНУТЫЕ СЕГМЕНТЫ (4 секции, по одной на каждую цель):
   Каждая секция:
   - Фон: пастельный цвет сегмента
   - Эмодзи + H2 с сильным заголовком (не «Первая квартира», а «Хватит платить за аренду — платите за своё»)
   - Описание + 3 pill-тега
   - Sidebar-карточка: «Акции и скидки в MAX» — фиолетовый фон, кнопка «Подписаться на MAX →»
   - Grid 3 карточки ЖК, подходящих под этот сегмент
   - Ссылка «Смотреть все варианты →»

   Конкретные секции:
   a) 🔑 Первая квартира:
      H2: «Хватит платить за аренду — платите за своё»
      Текст: «Студии и 1-комнатные от 3 млн ₽. Ипотека от 0.1%, рассрочка без переплат.»
      Теги: Ипотека от 0.1% / Рассрочка 0% / Субсидии
   b) 📈 Инвестиция:
      H2: «Недвижимость доходнее вкладов — от 8% годовых»
      Текст: «Студии у метро от 4 млн. Аналитика окупаемости, помощь с арендой.»
      Теги: Доход 8-12% / Рост стоимости / Аренда
   c) 🏡 Расширение:
      H2: «Семья растёт — пора в квартиру побольше»
      Текст: «2-4 комнаты с отделкой от 6 млн. Trade-in: зачтём старую квартиру.»
      Теги: Trade-in / Зачёт квартиры / Без переплат
   d) 💜 Для близких:
      H2: «Надёжная квартира — лучший подарок»
      Текст: «Безопасные районы рядом с вузами. Помощь с оформлением дарения.»
      Теги: Безопасные районы / Оформление / Рядом с вузами

5. КАК ЭТО РАБОТАЕТ (4 шага):
   - Заголовок H2 + подзаголовок «4 шага от заявки до ключей»
   - Grid 4 колонки. Каждый шаг:
     * Номер: «01» / «02» / «03» / «04» — крупный, var(--primary), font-weight: 700
     * H3: Расскажите о цели / Получите подборку / Посмотрите объекты / Оформите сделку
     * Описание (muted)

6. ПРЕМИАЛЬНЫЕ НОВОСТРОЙКИ:
   - H2 + «Все 1180 ЖК →»
   - Grid 6 карточек (3 колонки × 2 ряда) — бизнес/премиум ЖК
   - Данные из JS-массива premiumProjects[]

7. РАЙОНЫ:
   - H2: «Районы Санкт-Петербурга»
   - Подзаголовок: «Квартиры в новостройках по районам»
   - Grid 4 колонки. Каждая карточка района:
     * Название района (H3)
     * «N ЖК · от X млн ₽» (мелкий текст)
     * Вся карточка — ссылка на /novostrojki/?district=slug
   - 8 районов на главной

8. ПОЧЕМУ ВЫБИРАЮТ PLEADA:
   - H2: «Почему 2 300+ клиентов выбрали PLEADA»
   - Подзаголовок: «8 лет помогаем покупать квартиры — от подбора до ключей»
   - Grid 4 карточки преимуществ:
     * 💰 0₽ комиссия — «Наши услуги оплачивает застройщик»
     * 🏷️ Скидки до 1 млн — «Эксклюзивные условия от застройщиков»
     * 📅 Рассрочка от 5% — «Без процентов от застройщика»
     * 🔄 Trade-in обмен — «Зачёт старой квартиры»
   - Под ними — 3 KPI крупными цифрами (красный цвет):
     * 8 лет — на рынке СПб
     * 2 300+ — довольных клиентов
     * 4.8 ★ — средний рейтинг

9. ФИНАЛЬНЫЙ CTA:
   - Форма заявки (упрощённая: имя + телефон)
   - Блок «Акции в MAX» с фиолетовой кнопкой

10. SEO-ТЕКСТ (внизу, перед футером):
    - H2: «Купить квартиру в новостройке Санкт-Петербурга 2026»
    - 2–3 абзаца: описание PLEADA, статистика (1180 ЖК, 57 189 квартир, 188 застройщиков), разбивка клиентов по целям (45% первая квартира, 30% инвестиции, 15% trade-in, 10% для близких), условия работы
    - Мелкий шрифт, var(--text-muted)

=== СТРАНИЦА 2: КАТАЛОГ ЖК (/novostrojki/index.html) ===

1. Breadcrumbs: Главная → Новостройки
2. H1: «Новостройки СПб 2026»
3. Счётчик: «Найдено: N ЖК»
4. Фильтры (горизонтальная панель):
   - Район (select)
   - Метро (select)
   - Бюджет (select: до 5 млн, 5–8, 8–12, 12–20, от 20)
   - Комнаты (pills: Студия, 1, 2, 3, 4+)
   - Класс (pills: эконом, комфорт, бизнес, премиум)
   - Кнопка «Сбросить»
5. Сортировка: «По рейтингу / Цена ↑ / Цена ↓ / По кол-ву квартир / По названию» — pills
6. Grid карточек ЖК (3 колонки). Рендер из JS-массива с фильтрацией
7. Кнопка «Показать ещё» (подгрузка следующих 12)
8. Блоки ссылок: «Новостройки по районам», «Новостройки по метро»
9. CTA-баннер

JS:
- Фильтрация массива ЖК по всем параметрам (AND-логика)
- Сортировка: sort() по цене, рейтингу, названию, кол-ву квартир
- «Показать ещё»: slice() с offset, инкремент по 12
- URL-параметры: ?district=xxx&segment=xxx&budget=xxx — парсинг при загрузке
- Debounced фильтрация (300ms)
- Состояние «Ничего не найдено» с текстом «Попробуйте изменить фильтры»

=== СТРАНИЦА 3: КАРТОЧКА ЖК (/novostrojki/[slug]/index.html) ===

Шаблонная страница, заполняемая данными одного ЖК:

1. Breadcrumbs: Главная → Новостройки → [Название ЖК]
2. Галерея: 1 большое фото + 4 маленьких (grid). Все — gradient-заглушки. Бейдж «N фото». Бейдж класса: «бизнес» / «комфорт»
3. Шапка:
   - H1: название ЖК
   - Застройщик (ссылка), район (ссылка), класс, цена за м²
   - Теги: «Ипотека», «Рассрочка» (если доступно)
   - Адрес + ближайшее метро с временем
4. ЦЕНЫ И ПЛАНИРОВКИ — таблица:
   | Тип | Площадь | Цена от | Квартир |
   Типы: Студия, 1-комн., 2-комн., 3-комн., 4-комн.
   Итого: «Всего в продаже: N»
5. ПЛАНИРОВКИ КВАРТИР:
   - Grid карточек планировок (тип, от X млн, от Y м², N вариантов)
   - Ссылка «Все N квартир →»
6. О ЖИЛОМ КОМПЛЕКСЕ — текстовый блок (2–3 абзаца)
7. КОРПУСА И СРОКИ СДАЧИ — таблица:
   | Корпус | Очередь | Срок сдачи | Тип |
8. Блок «Акции на квартиры в [ЖК]» — фиолетовая карточка MAX
9. FAQ (аккордеон):
   - Сколько стоит квартира в [ЖК]?
   - Когда сдаётся [ЖК]?
   - Какой застройщик строит [ЖК]?
   - Как добраться до [ЖК]?
   - Можно ли купить в ипотеку?
   - Какая цена за м²?
10. ПОЛЕЗНЫЕ ССЫЛКИ: Все ЖК в районе, ЖК у метро, Все ЖК от застройщика, Ипотека, Блог
11. ПОХОЖИЕ ЖК: Grid 4 карточки (тот же район)
12. ЖК у метро [станция]: Grid 4 карточки

SEO:
- <title>: «[Название ЖК] — от X млн ₽, [Район] | PLEADA»
- JSON-LD: Residence + FAQPage + BreadcrumbList + AggregateOffer

=== СТРАНИЦА 4: РАЙОНЫ (/districts/index.html) ===

1. H1: «Районы для покупки новостройки»
2. Подзаголовок: «27 районов · 57 189 квартир в продаже»
3. Секция «Санкт-Петербург (18 районов)»:
   - Grid 3 колонки, карточка района:
     * Название (H3)
     * «N ЖК · X кв.» + «от Y млн ₽»
     * Список ближайших станций метро (до 3 + «+N»)
     * Ссылка
4. Секция «Ленинградская область (9 районов)»: аналогичный grid
5. CTA-баннер: «Не знаете какой район выбрать?»

=== СТРАНИЦА 5: ЗАСТРОЙЩИКИ (/zastrojshchiki/index.html) ===

1. H1: «Застройщики Санкт-Петербурга»
2. Подзаголовок: «188 компаний»
3. Сортировка: pills (По кол-ву ЖК, По кол-ву квартир, По алфавиту)
4. Grid карточек застройщиков:
   - Лого-заглушка (инициалы на цветном круге)
   - Название
   - «N ЖК · X квартир»
5. CTA-баннер

=== СТРАНИЦА 6: ИПОТЕКА (/mortgage/index.html) ===

1. H1: «Ипотека на новостройки в СПб»
2. Подзаголовок + навигация-pills: Ипотечный калькулятор / Программы / ЖК с ипотекой
3. КАКАЯ ИПОТЕКА ВАМ ПОДХОДИТ — 4 карточки (grid 4 col, с эмодзи):
   - 🔑 Семейная ипотека (от 6%, от 15%, до 12 млн)
   - 📈 Стандартная (от 15%, быстрое одобрение)
   - 🏡 Trade-in + ипотека (зачёт квартиры)
   - ⭐ Военная ипотека (НИС, 0% взнос)
4. СРАВНЕНИЕ ПРОГРАММ — таблица:
   | Программа | Ставка | Взнос | Макс. сумма | Для кого |
   7 строк: Семейная, IT, Стандартная, Военная, Рассрочка, Trade-in, Маткапитал
5. Ипотечный калькулятор (JS):
   - Input: стоимость квартиры (range slider + число)
   - Input: первоначальный взнос (range slider + число + %)
   - Input: срок (range slider: 1–30 лет)
   - Input: ставка (число, default 6%)
   - Output: ежемесячный платёж, переплата, общая сумма
   - Формула: аннуитетный платёж
6. ЖК С ИПОТЕКОЙ: Grid 6 карточек (378 ЖК)
7. ЖК С РАССРОЧКОЙ 0%: Grid 6 карточек (271 ЖК)
8. FAQ (аккордеон): 6 вопросов про ипотеку
9. CTA-баннер

=== СТРАНИЦА 7: БЛОГ (/blog/index.html) ===

1. H1: «Блог PLEADA» + «2000 статей о недвижимости»
2. Фильтры-категории (pills): Все, ЖК, Районы, Покупка, Ипотека, Инвестиции, Юридическое, Застройщики, Гайды, Полезное
3. Grid карточек статей (2 колонки):
   - Заголовок (H3)
   - Категория-бейдж
   - Дата + время чтения
   - Excerpt (2–3 строки, line-clamp: 3)
4. «Показать ещё» (пагинация)

=== JAVASCRIPT (script.js + data.js) ===

data.js — единый файл данных:
- const projects = [...] — массив 20+ ЖК: { id, slug, title, district, districtSlug, metro, metroTime, developer, developerSlug, class, priceFrom, pricePerM2, totalApartments, rooms: {studio, one, two, three}, deliveryDate, hasIpoteka, hasRassrochka, imageUrl, tags, segment[] }
- const districts = [...] — 27 районов: { name, slug, region, projectCount, apartmentCount, priceFrom, metros[] }
- const developers = [...] — 20+ застройщиков: { name, slug, projectCount, apartmentCount }
- const blogPosts = [...] — 12+ статей: { title, slug, category, date, readTime, excerpt }

script.js — логика:
- renderProjectCards(containerId, projectsArray) — универсальный рендер карточек ЖК
- renderDistrictCards(containerId, districtsArray)
- renderDeveloperCards(containerId, developersArray)
- filterProjects(filters) — фильтрация по district, budget, rooms, class, segment
- sortProjects(array, sortBy) — сортировка
- setupLeadForm() — обработка формы (pills selection + alert)
- setupFAQ() — аккордеон (click toggle класс .open, max-height transition)
- setupMobileMenu() — бургер меню (toggle класс .menu-open на body)
- setupSortingPills() — переключение активной сортировки
- setupCategoryFilter() — фильтрация блога/каталога по категории
- animateCounters() — IntersectionObserver + requestAnimationFrame для счётчиков
- parseURLParams() — чтение ?district=&segment=&budget= при загрузке
- mortgageCalculator() — формула: P * [r(1+r)^n] / [(1+r)^n - 1]
- loadMore(offset, limit) — подгрузка карточек
- smoothScroll() — плавный скролл для якорей
- highlightActiveNav() — подсветка текущей страницы в навигации по URL
- setupSegmentPills() — выбор цели/бюджета в форме (toggle active класс)

=== CSS (styles.css) ===

Ключевые паттерны:

/* Контейнер */
.container { width: min(var(--container), calc(100% - 32px)); margin: 0 auto; }

/* Карточка ЖК */
.project-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.project-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-hover); }
.project-card img { width: 100%; aspect-ratio: 16/10; object-fit: cover; }
.project-card .price { color: var(--primary); font-weight: 700; }

/* Сегмент-карточки */
.segment-card { border-radius: var(--radius); padding: 24px; }
.segment-card--first { background: var(--segment-first); }
.segment-card--invest { background: var(--segment-invest); }
.segment-card--upgrade { background: var(--segment-upgrade); }
.segment-card--family { background: var(--segment-family); }

/* Pill-теги */
.pill {
  display: inline-flex; padding: 6px 12px;
  border-radius: var(--radius-pill);
  font-size: 0.85rem; font-weight: 600;
  background: rgba(0,0,0,0.06);
}
.pill.active { background: var(--primary); color: #fff; }

/* Таблицы */
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }
th { font-weight: 600; background: var(--surface-muted); }

/* Аккордеон FAQ */
.faq-item { border: 1px solid var(--border); border-radius: var(--radius-sm); }
.faq-item h3 { cursor: pointer; padding: 16px; margin: 0; }
.faq-item h3::after { content: '+'; float: right; transition: transform 0.2s; }
.faq-item.open h3::after { transform: rotate(45deg); }
.faq-item .faq-answer { max-height: 0; overflow: hidden; transition: max-height 0.3s ease; padding: 0 16px; }
.faq-item.open .faq-answer { max-height: 500px; padding: 0 16px 16px; }

/* Секции */
.section { padding: 64px 0; }
.section-muted { background: var(--surface-muted); }

/* Кнопки */
.btn { display: inline-flex; align-items: center; justify-content: center; border: 0; border-radius: var(--radius-sm); padding: 14px 24px; font-weight: 600; font-size: 1rem; cursor: pointer; transition: all 0.2s; }
.btn-primary { background: var(--primary); color: #fff; }
.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
.btn-secondary { background: var(--secondary); color: #fff; }
.btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text); }

/* Грид адаптивный */
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }

@media (max-width: 1024px) {
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
  .nav-menu { display: none; }
  .burger { display: flex; }
}

@media (max-width: 640px) {
  .grid-4, .grid-3, .grid-2 { grid-template-columns: 1fr; }
  .hero-grid { grid-template-columns: 1fr; }
  .section { padding: 40px 0; }
}

=== SEO (для каждой страницы) ===

Каждая страница содержит:
- Уникальный <title> с ключевым запросом + «| PLEADA»
- <meta description> до 160 символов
- <meta keywords>
- <meta robots content="index,follow">
- Open Graph: og:type, og:locale (ru_RU), og:site_name (PLEADA), og:title, og:description, og:url, og:image
- Twitter Card: summary_large_image
- Canonical URL
- Hreflang: ru-RU + x-default
- JSON-LD @graph (разный для каждой страницы):
  * Главная: WebSite + Organization + LocalBusiness + FAQPage + ItemList + BreadcrumbList
  * Каталог: ItemList + BreadcrumbList
  * Карточка ЖК: Residence + AggregateOffer + FAQPage + BreadcrumbList
  * Районы: ItemList + BreadcrumbList
  * Ипотека: FinancialProduct + FAQPage + BreadcrumbList
  * Блог: Blog + BreadcrumbList
- Семантические теги: <main>, <article>, <section>, <nav>, <header>, <footer>

=== ДОПОЛНИТЕЛЬНЫЕ ФАЙЛЫ ===

robots.txt:
  User-agent: *
  Allow: /
  Sitemap: https://pleada.shop/sitemap.xml

sitemap.xml: все страницы с <lastmod>, <changefreq>, <priority>

=== ВАЖНЫЕ ДЕТАЛИ ДИЗАЙНА ===

1. Цены всегда красные (var(--primary)), жирные
2. Карточки ЖК — изображения сверху, текст снизу (vertical layout)
3. Pill-теги: маленькие, скруглённые, мелкий шрифт
4. Формы — минимум полей, крупные кнопки
5. «Акции в MAX» — всегда фиолетовый фон (var(--secondary))
6. Хлебные крошки — на каждой внутренней странице
7. Номера шагов (01–04) крупные, красные
8. Sticky header с blur — не перекрывает контент (padding-top на body)
9. Мобильное меню — slide-in слева, overlay с backdrop
10. Ссылки «Все ЖК →» — красные, со стрелкой →
11. Footer — 4 колонки, тёмный фон, мелкий текст

Весь контент — на русском языке. Все данные заполнены реалистично (не lorem ipsum).
```

---

## Как пользоваться этим промтом

### Генерация целиком
Скопируй весь промт и отправь в AI-ассистент (Cursor, Claude, ChatGPT). Для больших моделей промт сгенерирует все страницы за 1–3 итерации.

### Генерация по частям
Разбей на подзапросы:
1. «Сгенерируй styles.css и data.js по спецификации выше»
2. «Сгенерируй index.html (главную) по спецификации выше»
3. «Сгенерируй script.js по спецификации выше»
4. «Сгенерируй /novostrojki/index.html (каталог) по спецификации выше»
5. И так далее для каждой страницы

### Адаптация под свой город / нишу
Замени:
- **Город**: «Санкт-Петербург» → свой город
- **Данные**: массивы ЖК, районов, застройщиков — на свои
- **Цвета**: var(--primary) red → свой accent
- **Бренд**: PLEADA → своё название
- **Контакты**: телефон, Telegram, адрес
