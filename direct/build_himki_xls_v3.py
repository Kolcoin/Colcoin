#!/usr/bin/env python3
"""Генератор XLS точно по структуре эталона который УЖЕ принят Яндекс.Директом.
Эталон: cursor/urban-ritual-landing-8365/direct_yandex_template_exact/campaign_himki.xls

Делаем НОВУЮ структуру по запросу брата:
1. Химки — Ритуальные услуги (вместо "Похороны под ключ")
2. Химки — Организация похорон (новая группа)
3. Химки — Организация кремации
4. Химки — Выезд ритуального агента
Без морга!

Тексты — новые от брата (см. предыдущий чат).
"""
from pathlib import Path
import xlrd
import xlwt

ROOT = Path(__file__).parent
REF_XLS = "/tmp/ref_template.xls"  # эталонный файл с GitHub
OUT_XLS = ROOT / "campaign_himki_v3.xls"

SITE = "https://urban-ritual.ru"
CITY = "Химки"
CITY_PREP = "в Химках"
SLUG = "himki"
MINUTES = 30

# Конфигурация 4 групп
GROUPS = [
    {
        "num": 1,
        "name": "Химки — Ритуальные услуги",
        "landing_path": "/city/himki/",
        "display": "himki/uslugi",
        "keywords": [
            "ритуальные услуги химки",
            "ритуальные услуги +в химках",
            "ритуальное агентство химки",
            "ритуальное бюро химки",
            "ритуальная служба химки",
            "похоронное бюро химки",
            "похоронные услуги химки",
            "ритуальный салон химки",
            "ритуальные услуги химки круглосуточно",
            "ритуальные услуги химки цена",
        ],
        "ads": [
            {
                "h1": "Ритуальные услуги в Химках 24/7",
                "h2": "Полное сопровождение под ключ",
                "text": "Гроб, катафалк, бригада, документы, кладбище. От 34 900 ₽. Договор и чек.",
            },
        ],
    },
    {
        "num": 2,
        "name": "Химки — Организация похорон",
        "landing_path": "/city/himki/",
        "display": "himki/pohorony",
        "keywords": [
            "организация похорон химки",
            "организация похорон +в химках",
            "похороны химки",
            "похороны +в химках",
            "похороны +под ключ химки",
            "заказать похороны химки",
            "сколько стоят похороны химки",
            "цена похорон химки",
            "стоимость похорон химки",
            "похороны под ключ химки",
        ],
        "ads": [
            {
                "h1": "Организация похорон в Химках",
                "h2": "Под ключ от 68 500 ₽",
                "text": "Полная организация: документы, гроб, катафалк, бригада, кладбище. 24/7.",
            },
        ],
    },
    {
        "num": 3,
        "name": "Химки — Организация кремации",
        "landing_path": "/city/himki/kremaciya/",
        "display": "himki/kremaciya",
        "keywords": [
            "кремация химки",
            "кремация +в химках",
            "заказать кремацию химки",
            "организация кремации химки",
            "стоимость кремации химки",
            "цена кремации химки",
            "кремация +под ключ химки",
            "крематорий химки",
            "крематорий носовиха",
            "ритуальное агентство кремация химки",
            "кремация без церемонии химки",
            "сколько стоит кремация химки",
        ],
        "ads": [
            {
                "h1": "Организация кремации в Химках",
                "h2": "От 34 900 ₽ — под ключ",
                "text": "Доставка в крематорий Носовиха или Митино. Гроб, урна, документы. 24/7.",
            },
        ],
    },
    {
        "num": 4,
        "name": "Химки — Выезд ритуального агента",
        "landing_path": "/city/himki/agent/",
        "display": "himki/agent",
        "keywords": [
            "выезд ритуального агента химки",
            "ритуальный агент химки",
            "вызов ритуального агента химки",
            "вызвать ритуального агента химки",
            "ритуальный агент круглосуточно химки",
            "ритуальные услуги круглосуточно химки",
            "ритуальные услуги ночью химки",
            "ритуальное агентство 24 часа химки",
            "похороны срочно химки",
            "срочно ритуальные услуги химки",
            "что делать если умер близкий химки",
            "что делать после смерти химки",
            "умер дома химки что делать",
            "как организовать похороны химки",
            "вызвать ритуальную службу химки",
        ],
        "ads": [
            {
                "h1": "Выезд ритуального агента в Химках",
                "h2": "Бесплатно за 30 мин 24/7",
                "text": "Поможем дождаться скорой и полиции, оформим документы, перевозка в морг.",
            },
        ],
    },
]

UTM = (
    "?utm_source=yandex&utm_medium=cpc&utm_campaign=himki_search"
    "&utm_content={ad_id}&utm_term={keyword}"
)

QUICK_LINKS_TITLES = "Цены и пакеты||Срочный агент||Кремация||Документы"
QUICK_LINKS_DESCRIPTIONS = (
    "От 34900 руб - 3 пакета||Выезд за 30 минут||От 34900 руб под ключ||Полный список 2026"
)
QUICK_LINKS_URLS = (
    f"{SITE}/city/{SLUG}/#prices"
    "||"
    f"{SITE}/city/{SLUG}/agent/"
    "||"
    f"{SITE}/city/{SLUG}/kremaciya/"
    "||"
    f"{SITE}/blog/dokumenty-dlya-pohoron/"
)

CLARIFICATIONS = (
    "Работаем с 2014 года||Выезд агента за 30 мин||Договор и кассовый чек||"
    "Цена в договоре||Без предоплаты||Круглосуточно 24/7||Помощь с пособием"
)


def main():
    # Читаем эталон
    rb = xlrd.open_workbook(REF_XLS, formatting_info=True)

    # Создаём новый файл xlwt
    wb = xlwt.Workbook(encoding="utf-8")

    # Копируем каждый лист
    for sheet_idx, sname in enumerate(rb.sheet_names()):
        rs = rb.sheet_by_name(sname)
        ws = wb.add_sheet(sname, cell_overwrite_ok=True)

        if sname == "Тексты":
            # Копируем строки 1-11 (служебные + заголовки)
            for r in range(11):
                for c in range(rs.ncols):
                    v = rs.cell_value(r, c)
                    if v not in ('', None):
                        ws.write(r, c, v)

            # Теперь записываем НАШИ данные начиная с 12-й строки (idx 11)
            current_row = 11
            for grp in GROUPS:
                for ad in grp["ads"]:
                    # Каждое объявление повторяется для каждой фразы (как в эталоне)
                    for kw in grp["keywords"]:
                        landing = SITE + grp["landing_path"] + UTM
                        # 66 колонок, заполняем только нужные
                        ws.write(current_row, 0, "-")  # Доп. объявление группы
                        ws.write(current_row, 1, "Текстово-графическое")
                        ws.write(current_row, 3, grp["name"])  # Название группы
                        ws.write(current_row, 4, grp["num"])    # Номер группы
                        ws.write(current_row, 6, kw)            # Фраза
                        ws.write(current_row, 8, ad["h1"][:56]) # Заголовок 1
                        ws.write(current_row, 9, ad["h2"][:30]) # Заголовок 2
                        ws.write(current_row, 10, ad["text"][:81]) # Текст
                        ws.write(current_row, 46, landing)      # Ссылка
                        ws.write(current_row, 47, grp["display"][:20]) # Отображаемая
                        ws.write(current_row, 48, CITY)         # Регион
                        ws.write(current_row, 50, 0.3)          # Ставка (как в эталоне)
                        ws.write(current_row, 54, QUICK_LINKS_TITLES)
                        ws.write(current_row, 55, QUICK_LINKS_DESCRIPTIONS)
                        ws.write(current_row, 56, QUICK_LINKS_URLS)
                        ws.write(current_row, 63, CLARIFICATIONS)
                        current_row += 1

            print(f"Лист 'Тексты': записано {current_row - 11} строк данных")

        else:
            # Листы "Регионы" и "Словарь значений полей" копируем 1:1
            for r in range(rs.nrows):
                for c in range(rs.ncols):
                    v = rs.cell_value(r, c)
                    if v not in ('', None):
                        try:
                            ws.write(r, c, v)
                        except Exception:
                            pass
            print(f"Лист '{sname}': скопировано {rs.nrows} строк")

    wb.save(str(OUT_XLS))
    print(f"\n✅ Сохранено: {OUT_XLS}")
    print(f"   Размер: {OUT_XLS.stat().st_size} bytes")
    print(f"   Групп: {len(GROUPS)}")
    print(f"   Ключевых фраз всего: {sum(len(g['keywords']) for g in GROUPS)}")


if __name__ == "__main__":
    main()
