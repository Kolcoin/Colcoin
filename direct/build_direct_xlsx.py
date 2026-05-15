#!/usr/bin/env python3
"""Генератор XLSX-файлов для массовой загрузки кампаний в Яндекс.Директ.

Формат соответствует официальному шаблону Яндекс.Директа для импорта через:
direct.yandex.ru → Инструменты → Управление кампаниями с помощью XLS/XLSX → Загрузка

Создаёт по 1 файлу на каждый город (4 группы объявлений × N ключей × M объявлений).
Также экспортирует summary.md для ручного копи-паста.

Использование:
    python3 direct/build_direct_xlsx.py
"""
import json
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).parent.parent
OUT = Path(__file__).parent

SITE = "https://urban-ritual.ru"
PHONE_TEL = "+79852198394"
PHONE_VIS = "+7 (985) 219-83-94"

# UTM-шаблон для всех ссылок
UTM = "utm_source=yandex&utm_medium=cpc&utm_campaign={city}_search&utm_content={group}&utm_term={{keyword}}"

# Базовая структура кампании — 4 группы под Мытищи (по интентам).
# Для других городов адаптируется автоматически (см. CITIES ниже).
GROUP_DEFS = [
    {
        "id": "g1_pokhorony",
        "name": "{CITY} — Похороны под ключ",
        "landing_path": "/city/{slug}/",
        "keywords": [
            "ритуальные услуги {city_low}",
            "ритуальные услуги +в {city_prep_low}",
            "ритуальное агентство {city_low}",
            "ритуальное бюро {city_low}",
            "ритуальная служба {city_low}",
            "организация похорон {city_low}",
            "организация похорон +в {city_prep_low}",
            "похороны {city_low}",
            "похороны +в {city_prep_low}",
            "похороны +под ключ {city_low}",
            "заказать похороны {city_low}",
            "похоронное бюро {city_low}",
            "похоронные услуги {city_low}",
            "ритуальный салон {city_low}",
            "сколько стоят похороны {city_low}",
            "цена похорон {city_low}",
            "стоимость похорон {city_low}",
        ],
        "ads": [
            {
                "h1": "Ритуальные услуги {city_prep} за 30 мин",
                "h2": "Похороны под ключ от 68 500 ₽",
                "text": "Полная организация похорон {city_prep}. Выезд агента бесплатно за {minutes} мин. Фиксированная цена. 24/7.",
                "display": "{slug}/uslugi",
            },
            {
                "h1": "Ритуальная служба {city_prep} 24/7",
                "h2": "Точка-салон у морга",
                "text": "Точка у морга. Полный пакет: гроб, катафалк, бригада, документы, кладбище. От 68 500 ₽.",
                "display": "{slug}",
            },
            {
                "h1": "Похороны {city_prep} от 34 900 ₽",
                "h2": "Эконом · Стандарт · Премиум",
                "text": "3 пакета на любой бюджет. Помощь с пособием. Звонок бесплатно — расскажем по телефону.",
                "display": "{slug}/ceny",
            },
        ],
    },
    {
        "id": "g2_agent",
        "name": "{CITY} — Срочный агент 24/7",
        "landing_path": "/city/{slug}/agent/",
        "keywords": [
            "ритуальный агент {city_low}",
            "вызов ритуального агента {city_low}",
            "вызвать ритуального агента {city_low}",
            "ритуальный агент круглосуточно {city_low}",
            "ритуальные услуги круглосуточно {city_low}",
            "ритуальные услуги ночью {city_low}",
            "ритуальное агентство 24 часа {city_low}",
            "выезд ритуального агента {city_low}",
            "похороны срочно {city_low}",
            "срочно ритуальные услуги {city_low}",
            "что делать если умер близкий {city_low}",
            "что делать после смерти {city_low}",
            "умер дома {city_low} что делать",
            "как организовать похороны {city_low}",
            "вызвать ритуальную службу {city_low}",
        ],
        "ads": [
            {
                "h1": "Срочный ритуальный агент {city_prep}",
                "h2": "Приедем за {minutes} минут 24/7",
                "text": "Бесплатный выезд, без обязательств. Поможем дождаться скорой и полиции.",
                "display": "{slug}/agent",
            },
            {
                "h1": "Умер близкий {city_prep} — что делать?",
                "h2": "Документы, морг, кладбище",
                "text": "Агент приедет за {minutes} мин, объяснит порядок действий, перевозка в морг 24/7.",
                "display": "{slug}/agent",
            },
            {
                "h1": "Вызов ритуального агента {city_prep}",
                "h2": "Бесплатный выезд за {minutes} мин",
                "text": "Агент уже {city_prep} — приезжает не из Москвы. Полное сопровождение под ключ.",
                "display": "{slug}/agent",
            },
        ],
    },
    {
        "id": "g3_kremaciya",
        "name": "{CITY} — Кремация",
        "landing_path": "/city/{slug}/kremaciya/",
        "keywords": [
            "кремация {city_low}",
            "кремация +в {city_prep_low}",
            "заказать кремацию {city_low}",
            "организация кремации {city_low}",
            "стоимость кремации {city_low}",
            "цена кремации {city_low}",
            "кремация +под ключ {city_low}",
            "крематорий {city_low}",
            "крематорий +рядом {city_low}",
            "крематорий носовиха",
            "ритуальное агентство кремация {city_low}",
            "кремация без церемонии {city_low}",
            "сколько стоит кремация {city_low}",
            "урна +с прахом {city_low}",
        ],
        "ads": [
            {
                "h1": "Кремация {city_prep} от 34 900 ₽",
                "h2": "Крематорий Носовиха · Митино",
                "text": "Доставка, гроб для кремации, урна, документы. Под ключ. Звонок 24/7.",
                "display": "{slug}/kremaciya",
            },
            {
                "h1": "Заказать кремацию {city_prep}",
                "h2": "Без скрытых доплат",
                "text": "Полное сопровождение под ключ. Документы, гроб, доставка, урна. С 2014 года.",
                "display": "{slug}/kremaciya",
            },
        ],
    },
    {
        "id": "g4_morg",
        "name": "{CITY} — Морг ГКБ",
        "landing_path": "/city/{slug}/morg/",
        "keywords": [
            "морг {city_low}",
            "{morg_short_low}",
            "морг +в {city_prep_low}",
            "морг +при больнице {city_low}",
            "ритуальные услуги +при морге {city_low}",
            "ритуальное агентство +при морге {city_low}",
            "ритуальный салон +у морга {city_low}",
            "забрать тело +из морга {city_low}",
            "выдача тела +из морга {city_low}",
            "оформление документов морг {city_low}",
        ],
        "ads": [
            {
                "h1": "Салон у морга — {city_low}",
                "h2": "Своя точка в шаговой доступности",
                "text": "Поможем забрать тело, оформить документы, организовать похороны. 24/7.",
                "display": "{slug}/morg",
            },
            {
                "h1": "Выдача тела из морга — {city_low}",
                "h2": "Оформим документы и катафалк",
                "text": "Возьмём на себя выдачу тела, оформление документов, перевозку. Полный пакет.",
                "display": "{slug}/morg",
            },
        ],
    },
]

# Минус-слова кампании (общие для всех групп)
MINUS_WORDS = [
    "бесплатно", "халява", "работа", "вакансии", "устроиться", "зарплата", "сотрудник",
    "форум", "обсуждение", "википедия", "вики", "фото", "картинки", "видео", "клипы",
    "песня", "песни", "музыка", "скачать", "торрент", "игра", "игры", "анекдот", "шутки",
    "приколы", "сон", "сонник", "снится", "снятся", "приснилось", "гороскоп",
    "сериал", "фильм", "история", "истории", "курсовая", "реферат", "диссертация",
    "самостоятельно", "самому", "свадебный", "детский", "невесте", "квартира",
    "снять", "купить", "продать", "аренда", "стоматология", "парикмахерская",
    "ресторан", "школа", "детский сад", "погода", "новости", "такси", "доставка",
    "авито", "циан", "юла", "порно", "эротика", "обои", "питомец", "домашний",
    "животных", "собака", "кошка", "заговор", "магия", "обряд", "курсы", "обучение",
]

# Быстрые ссылки на уровне кампании (общие для всей кампании)
def quick_links_for_city(city):
    slug = city["slug"]
    return [
        ("Цены и пакеты", f"{SITE}/city/{slug}/#prices",                "От 34 900 ₽ — 3 пакета"),
        ("Срочный агент", f"{SITE}/city/{slug}/agent/",                  "Выезд за 35 минут 24/7"),
        ("Кремация",      f"{SITE}/city/{slug}/kremaciya/",              "От 34 900 ₽ под ключ"),
        ("Документы",     f"{SITE}/blog/dokumenty-dlya-pohoron/",        "Полный список 2026"),
    ]

# Уточнения кампании (3-8, Директ покажет 3-4)
CLARIFICATIONS = [
    "Работаем с 2014 года",
    "Выезд агента за 35 минут",
    "Договор и кассовый чек",
    "Фиксированная цена в договоре",
    "Без предоплаты",
    "Круглосуточно 24/7",
    "Помощь с пособием на погребение",
]

# Список целевых городов и их специфика (для подстановки в шаблоны)
CITIES = [
    {
        "slug": "mytishchi", "name": "Мытищи", "name_low": "мытищи",
        "name_prep": "в Мытищах", "name_prep_low": "мытищах",
        "region": "Мытищи (городской округ)",
        "morg_short": "Морг Мытищинской ГКБ", "morg_short_low": "морг мытищинской гкб",
        "minutes": 35,
    },
    {
        "slug": "dolgoprudnyj", "name": "Долгопрудный", "name_low": "долгопрудный",
        "name_prep": "в Долгопрудном", "name_prep_low": "долгопрудном",
        "region": "Долгопрудный",
        "morg_short": "Морг Долгопрудненской ЦГБ", "morg_short_low": "морг долгопрудненской цгб",
        "minutes": 35,
    },
    {
        "slug": "lobnya", "name": "Лобня", "name_low": "лобня",
        "name_prep": "в Лобне", "name_prep_low": "лобне",
        "region": "Лобня",
        "morg_short": "Морг Лобненской ГБ", "morg_short_low": "морг лобненской городской больницы",
        "minutes": 40,
    },
    {
        "slug": "himki", "name": "Химки", "name_low": "химки",
        "name_prep": "в Химках", "name_prep_low": "химках",
        "region": "Химки (городской округ)",
        "morg_short": "Морг ЦКБ Химок", "morg_short_low": "морг цкб химок",
        "minutes": 30,
    },
    {
        "slug": "krasnogorsk", "name": "Красногорск", "name_low": "красногорск",
        "name_prep": "в Красногорске", "name_prep_low": "красногорске",
        "region": "Красногорск (городской округ)",
        "morg_short": "Морг Красногорской ГБ №1", "morg_short_low": "морг красногорской городской больницы",
        "minutes": 35,
    },
]


def fmt(template, city):
    return template.format(
        slug=city["slug"],
        CITY=city["name"], city=city["name"], city_low=city["name_low"],
        city_prep=city["name_prep"], city_prep_low=city["name_prep_low"],
        morg=city["morg_short"], morg_short_low=city["morg_short_low"],
        minutes=city["minutes"],
    )


# ──────────────────── XLSX генерация ────────────────────

# Колонки шаблона Яндекс.Директа для импорта новой кампании.
# Это упрощённая версия — основные поля для текстово-графических объявлений.
# Полная инструкция: https://yandex.ru/support/direct/efficiency/xls-import.html
XLSX_COLUMNS = [
    "ID кампании",        # пусто для новой кампании
    "Название кампании",
    "ID группы",          # пусто для новой группы
    "Название группы",
    "Номер группы",
    "Регионы",
    "Минус-фразы группы",
    "Метки",
    "Дополнительные релевантные фразы",
    "Ключевая фраза",     # одна строка = одна фраза
    "ID фразы",
    "Цена в Поиске",
    "Цена в Сетях",
    "ID объявления",
    "Заголовок 1",
    "Заголовок 2",
    "Текст объявления",
    "Длинный заголовок",
    "Изображение",
    "Видео",
    "Ссылка",
    "Отображаемая ссылка",
    "Уточнения",
    "Быстрые ссылки (заголовок 1)",
    "Быстрые ссылки (адрес 1)",
    "Быстрые ссылки (описание 1)",
    "Быстрые ссылки (заголовок 2)",
    "Быстрые ссылки (адрес 2)",
    "Быстрые ссылки (описание 2)",
    "Быстрые ссылки (заголовок 3)",
    "Быстрые ссылки (адрес 3)",
    "Быстрые ссылки (описание 3)",
    "Быстрые ссылки (заголовок 4)",
    "Быстрые ссылки (адрес 4)",
    "Быстрые ссылки (описание 4)",
    "Минус-фразы кампании",
    "Параметры URL",
]


def header_style(ws, row=1):
    """Стилизация заголовка."""
    fill = PatternFill(start_color="6E2A2A", end_color="6E2A2A", fill_type="solid")
    font = Font(color="FFFFFF", bold=True, size=11)
    align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border = Border(
        left=Side(style="thin", color="999999"),
        right=Side(style="thin", color="999999"),
        bottom=Side(style="thin", color="999999"),
    )
    for cell in ws[row]:
        cell.fill = fill
        cell.font = font
        cell.alignment = align
        cell.border = border
    ws.row_dimensions[row].height = 32


def autosize_columns(ws, max_width=60):
    """Подбор ширины колонок."""
    for col_cells in ws.columns:
        col_letter = get_column_letter(col_cells[0].column)
        max_len = 0
        for cell in col_cells:
            if cell.value is None:
                continue
            l = max(len(s) for s in str(cell.value).split("\n"))
            if l > max_len:
                max_len = l
        ws.column_dimensions[col_letter].width = min(max(max_len + 2, 10), max_width)


def build_xlsx_for_city(city):
    """Генерирует XLSX для одного города."""
    wb = Workbook()
    ws = wb.active
    ws.title = f"Кампания {city['name']}"

    # Шапка
    ws.append(XLSX_COLUMNS)
    header_style(ws, row=1)

    campaign_name = f"{city['name']} — Поиск"
    utm = UTM.format(city=city["slug"], group="{group_id}")  # group_id заменим позже
    quick_links = quick_links_for_city(city)

    # Для каждой группы и каждой комбинации (фраза × объявление)
    for grp in GROUP_DEFS:
        group_name = grp["name"].format(CITY=city["name"], city=city["name"])
        landing = SITE + grp["landing_path"].format(slug=city["slug"])
        group_utm = UTM.format(city=city["slug"], group=grp["id"])

        keywords = [fmt(kw, city) for kw in grp["keywords"]]
        # Сортируем для удобства
        keywords = list(dict.fromkeys(keywords))  # dedupe сохраняя порядок

        # Объявления группы
        for ad_idx, ad in enumerate(grp["ads"]):
            for kw_idx, kw in enumerate(keywords):
                row = ["" for _ in XLSX_COLUMNS]

                # Кампанию указываем только на первой строке группы
                is_first_in_campaign = (grp == GROUP_DEFS[0] and ad_idx == 0 and kw_idx == 0)

                row[XLSX_COLUMNS.index("Название кампании")] = campaign_name if is_first_in_campaign else ""
                row[XLSX_COLUMNS.index("Название группы")] = group_name if (ad_idx == 0 and kw_idx == 0) else ""
                row[XLSX_COLUMNS.index("Номер группы")] = grp["id"]
                row[XLSX_COLUMNS.index("Регионы")] = city["region"] if (ad_idx == 0 and kw_idx == 0) else ""
                row[XLSX_COLUMNS.index("Ключевая фраза")] = kw if ad_idx == 0 else ""  # фразы только в первом объявлении группы
                row[XLSX_COLUMNS.index("Заголовок 1")] = fmt(ad["h1"], city)
                row[XLSX_COLUMNS.index("Заголовок 2")] = fmt(ad["h2"], city)
                row[XLSX_COLUMNS.index("Текст объявления")] = fmt(ad["text"], city)
                row[XLSX_COLUMNS.index("Ссылка")] = landing
                row[XLSX_COLUMNS.index("Отображаемая ссылка")] = fmt(ad["display"], city)[:20]
                row[XLSX_COLUMNS.index("Уточнения")] = "\n".join(CLARIFICATIONS) if (ad_idx == 0 and kw_idx == 0) else ""

                # Быстрые ссылки — только в первой строке кампании
                if is_first_in_campaign:
                    for i, (qtitle, qurl, qdesc) in enumerate(quick_links, start=1):
                        row[XLSX_COLUMNS.index(f"Быстрые ссылки (заголовок {i})")] = qtitle
                        row[XLSX_COLUMNS.index(f"Быстрые ссылки (адрес {i})")] = qurl
                        row[XLSX_COLUMNS.index(f"Быстрые ссылки (описание {i})")] = qdesc
                    row[XLSX_COLUMNS.index("Минус-фразы кампании")] = "\n".join("-" + m for m in MINUS_WORDS)
                    row[XLSX_COLUMNS.index("Параметры URL")] = (
                        "utm_source=yandex&utm_medium=cpc&utm_campaign={slug}_search"
                        "&utm_content={{ad_id}}&utm_term={{keyword}}"
                    ).format(slug=city["slug"])

                ws.append(row)

        # Между группами оставляем пустую строку для читаемости
        ws.append(["" for _ in XLSX_COLUMNS])

    autosize_columns(ws, max_width=50)

    # Лист 2: справочная информация
    ws2 = wb.create_sheet("Справка")
    ws2.append(["Параметр", "Значение"])
    header_style(ws2)
    info = [
        ("Город", city["name"]),
        ("Slug", city["slug"]),
        ("Регион Директа", city["region"]),
        ("Главная посадочная", f"{SITE}/city/{city['slug']}/"),
        ("Интент: Срочный агент", f"{SITE}/city/{city['slug']}/agent/"),
        ("Интент: Кремация", f"{SITE}/city/{city['slug']}/kremaciya/"),
        ("Интент: Морг", f"{SITE}/city/{city['slug']}/morg/"),
        ("", ""),
        ("Рекомендации:", ""),
        ("Стратегия", "Максимум конверсий, оплата за клики"),
        ("Бюджет", "6 500 ₽/неделю (тест), 28 000 ₽/мес (стабильно)"),
        ("Максимальная ставка", "110 ₽ (для конкурентных запросов)"),
        ("Цель в Метрике", f"phone_click_{city['slug']} или Конверсия (любая) — {city['name']}"),
        ("Стоимость цели", "500 ₽ (целевая CPA)"),
        ("Корректировки", "Мобильные +20%, возраст 35-64 +20%, ночь 23-06 +15%"),
        ("«Директ помогает»", "ОТКЛЮЧИТЬ — автоматические рекомендации портят таргетинг"),
    ]
    for k, v in info:
        ws2.append([k, v])
    autosize_columns(ws2)

    return wb


def build_summary_md(city):
    """Markdown-сводка для ручного копи-паста."""
    lines = [
        f"# Кампания Яндекс.Директ — {city['name']}",
        "",
        f"**Город:** {city['name']} (`{city['slug']}`)",
        f"**Регион Директа:** {city['region']}",
        f"**Главная посадочная:** `{SITE}/city/{city['slug']}/`",
        "",
        "## Настройки кампании",
        "",
        "| Поле | Значение |",
        "|---|---|",
        f"| Название | `{city['name']} — Поиск` |",
        "| Стратегия | Максимум конверсий, оплата за клики |",
        "| Бюджет недельный | 6 500 ₽ (тест) |",
        "| Максимальная ставка | 110 ₽ |",
        f"| Регион показа | {city['region']} |",
        "| Места показа | Только «Продвижение в поисковой выдаче» |",
        f"| Цель | `Конверсия (любая) — {city['name']}` (стоимость 500 ₽) |",
        f"| Параметры URL | `utm_source=yandex&utm_medium=cpc&utm_campaign={city['slug']}_search&utm_content={{ad_id}}&utm_term={{keyword}}` |",
        "| «Директ помогает» | ❌ ВЫКЛ |",
        "",
        "## Быстрые ссылки на уровне кампании",
        "",
        "| Заголовок | URL | Описание |",
        "|---|---|---|",
    ]
    for qtitle, qurl, qdesc in quick_links_for_city(city):
        lines.append(f"| {qtitle} | `{qurl}` | {qdesc} |")
    lines.extend([
        "",
        "## Уточнения (Директ покажет 3-4)",
        "",
    ])
    for c in CLARIFICATIONS:
        lines.append(f"- {c}")

    lines.extend([
        "",
        "## Минус-фразы кампании",
        "",
        "```",
    ])
    for m in MINUS_WORDS:
        lines.append("-" + m)
    lines.extend([
        "```",
        "",
        "## Группы объявлений",
        "",
    ])

    for grp in GROUP_DEFS:
        group_name = grp["name"].format(CITY=city["name"], city=city["name"])
        landing = SITE + grp["landing_path"].format(slug=city["slug"])
        lines.append(f"### {group_name}")
        lines.append("")
        lines.append(f"**Посадочная:** `{landing}`")
        lines.append("")
        lines.append("**Ключевые фразы:**")
        lines.append("```")
        for kw in grp["keywords"]:
            lines.append(fmt(kw, city))
        lines.append("```")
        lines.append("")
        lines.append("**Объявления (A/B/C — Директ ротирует, оставит лучшее):**")
        lines.append("")
        for i, ad in enumerate(grp["ads"], 1):
            letter = chr(64 + i)  # A, B, C
            lines.append(f"**Объявление {letter}**")
            lines.append("")
            lines.append(f"- **Заголовок 1:** `{fmt(ad['h1'], city)}`")
            lines.append(f"- **Заголовок 2:** `{fmt(ad['h2'], city)}`")
            lines.append(f"- **Текст:** {fmt(ad['text'], city)}")
            lines.append(f"- **Отображаемая ссылка:** `{fmt(ad['display'], city)}`")
            lines.append("")
        lines.append("")

    lines.extend([
        "## После загрузки в Директ",
        "",
        "1. Проверить, что все 4 группы созданы и в каждой — нужное число ключей и объявлений",
        "2. Отправить кампанию на модерацию",
        "3. После модерации (1-3 дня) — пополнить баланс минимум на 7 000 ₽",
        "4. Подождать 5-7 дней — Директ обучается",
        "5. Через неделю — оптимизация по поисковым запросам и корректировкам ставок",
    ])

    return "\n".join(lines)


# ──────────────────── Main ────────────────────

def main():
    OUT.mkdir(exist_ok=True)
    print(f"Генерация для {len(CITIES)} городов:")

    for city in CITIES:
        # XLSX
        wb = build_xlsx_for_city(city)
        xlsx_path = OUT / f"campaign_{city['slug']}.xlsx"
        wb.save(xlsx_path)

        # Markdown summary
        md_path = OUT / f"campaign_{city['slug']}_summary.md"
        md_path.write_text(build_summary_md(city), encoding="utf-8")

        # Стат по объёму
        groups = len(GROUP_DEFS)
        keywords = sum(len(g["keywords"]) for g in GROUP_DEFS)
        ads = sum(len(g["ads"]) for g in GROUP_DEFS)
        print(f"  ✅ {city['name']:15} → {xlsx_path.name:30} ({groups} групп, {keywords} ключей, {ads} объявлений)")
        print(f"     {md_path.name}")


if __name__ == "__main__":
    main()
