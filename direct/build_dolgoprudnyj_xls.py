#!/usr/bin/env python3
"""Генератор XLS для Долгопрудного по эталонной структуре Яндекса.
Копирует все служебные строки и листы из эталона + подставляет данные под Долгопрудный.
"""
from pathlib import Path
import xlrd
import xlwt

ROOT = Path(__file__).parent
REF_XLS = "/tmp/ref_template.xls"
OUT_XLS = ROOT / "campaign_dolgoprudnyj_v3.xls"

SITE = "https://urban-ritual.ru"
CITY = "Долгопрудный"
CITY_PREP = "в Долгопрудном"
SLUG = "dolgoprudnyj"
MINUTES = 35

GROUPS = [
    {
        "num": 1,
        "name": "Долгопрудный — Ритуальные услуги",
        "landing_path": "/city/dolgoprudnyj/",
        "display": "dolgoprudnyj/uslugi",
        "keywords": [
            "ритуальные услуги долгопрудный",
            "ритуальные услуги +в долгопрудном",
            "ритуальное агентство долгопрудный",
            "ритуальное бюро долгопрудный",
            "ритуальная служба долгопрудный",
            "похоронное бюро долгопрудный",
            "похоронные услуги долгопрудный",
            "ритуальный салон долгопрудный",
            "ритуальные услуги долгопрудный круглосуточно",
            "ритуальные услуги долгопрудный цена",
        ],
        "ads": [
            {
                "h1": "Ритуальные услуги в Долгопрудном 24/7",
                "h2": "Полное сопровождение под ключ",
                "text": "Гроб, катафалк, бригада, документы, кладбище. От 34 900 ₽. Договор и чек.",
            },
        ],
    },
    {
        "num": 2,
        "name": "Долгопрудный — Организация похорон",
        "landing_path": "/city/dolgoprudnyj/",
        "display": "dolgoprudnyj/pohorony",
        "keywords": [
            "организация похорон долгопрудный",
            "организация похорон +в долгопрудном",
            "похороны долгопрудный",
            "похороны +в долгопрудном",
            "похороны +под ключ долгопрудный",
            "заказать похороны долгопрудный",
            "сколько стоят похороны долгопрудный",
            "цена похорон долгопрудный",
            "стоимость похорон долгопрудный",
            "похороны под ключ долгопрудный",
        ],
        "ads": [
            {
                "h1": "Организация похорон в Долгопрудном",
                "h2": "Под ключ от 68 500 ₽",
                "text": "Полная организация: документы, гроб, катафалк, бригада, кладбище. 24/7.",
            },
        ],
    },
    {
        "num": 3,
        "name": "Долгопрудный — Организация кремации",
        "landing_path": "/city/dolgoprudnyj/kremaciya/",
        "display": "dolgoprudnyj/kremaciya",
        "keywords": [
            "кремация долгопрудный",
            "кремация +в долгопрудном",
            "заказать кремацию долгопрудный",
            "организация кремации долгопрудный",
            "стоимость кремации долгопрудный",
            "цена кремации долгопрудный",
            "кремация +под ключ долгопрудный",
            "крематорий долгопрудный",
            "крематорий носовиха",
            "ритуальное агентство кремация долгопрудный",
            "кремация без церемонии долгопрудный",
            "сколько стоит кремация долгопрудный",
        ],
        "ads": [
            {
                "h1": "Организация кремации в Долгопрудном",
                "h2": "От 34 900 ₽ — под ключ",
                "text": "Доставка в крематорий Носовиха или Митино. Гроб, урна, документы. 24/7.",
            },
        ],
    },
    {
        "num": 4,
        "name": "Долгопрудный — Выезд ритуального агента",
        "landing_path": "/city/dolgoprudnyj/agent/",
        "display": "dolgoprudnyj/agent",
        "keywords": [
            "выезд ритуального агента долгопрудный",
            "ритуальный агент долгопрудный",
            "вызов ритуального агента долгопрудный",
            "вызвать ритуального агента долгопрудный",
            "ритуальный агент круглосуточно долгопрудный",
            "ритуальные услуги круглосуточно долгопрудный",
            "ритуальные услуги ночью долгопрудный",
            "ритуальное агентство 24 часа долгопрудный",
            "похороны срочно долгопрудный",
            "срочно ритуальные услуги долгопрудный",
            "что делать если умер близкий долгопрудный",
            "что делать после смерти долгопрудный",
            "умер дома долгопрудный что делать",
            "как организовать похороны долгопрудный",
            "вызвать ритуальную службу долгопрудный",
        ],
        "ads": [
            {
                "h1": "Выезд ритуального агента в Долгопрудном",
                "h2": "Бесплатно за 35 мин 24/7",
                "text": "Поможем дождаться скорой и полиции, оформим документы, перевозка в морг.",
            },
        ],
    },
]

UTM = "?utm_source=yandex&utm_medium=cpc&utm_campaign=dolgoprudnyj_search&utm_content={ad_id}&utm_term={keyword}"

QUICK_LINKS_TITLES = "Цены и пакеты||Срочный агент||Кремация||Документы"
QUICK_LINKS_DESCRIPTIONS = "От 34900 руб - 3 пакета||Выезд за 35 минут||От 34900 руб под ключ||Полный список 2026"
QUICK_LINKS_URLS = (
    f"{SITE}/city/{SLUG}/#prices||{SITE}/city/{SLUG}/agent/||"
    f"{SITE}/city/{SLUG}/kremaciya/||{SITE}/blog/dokumenty-dlya-pohoron/"
)
CLARIFICATIONS = (
    "Работаем с 2014 года||Выезд агента за 35 мин||Договор и кассовый чек||"
    "Цена в договоре||Без предоплаты||Круглосуточно 24/7||Помощь с пособием"
)


def main():
    rb = xlrd.open_workbook(REF_XLS, formatting_info=True)
    wb = xlwt.Workbook(encoding="utf-8")

    for sname in rb.sheet_names():
        rs = rb.sheet_by_name(sname)
        ws = wb.add_sheet(sname, cell_overwrite_ok=True)

        if sname == "Тексты":
            for r in range(11):
                for c in range(rs.ncols):
                    v = rs.cell_value(r, c)
                    if v not in ('', None):
                        ws.write(r, c, v)

            current_row = 11
            for grp in GROUPS:
                for ad in grp["ads"]:
                    for kw in grp["keywords"]:
                        landing = SITE + grp["landing_path"] + UTM
                        ws.write(current_row, 0, "-")
                        ws.write(current_row, 1, "Текстово-графическое")
                        ws.write(current_row, 3, grp["name"])
                        ws.write(current_row, 4, grp["num"])
                        ws.write(current_row, 6, kw)
                        ws.write(current_row, 8, ad["h1"][:56])
                        ws.write(current_row, 9, ad["h2"][:30])
                        ws.write(current_row, 10, ad["text"][:81])
                        ws.write(current_row, 46, landing)
                        ws.write(current_row, 47, grp["display"][:20])
                        ws.write(current_row, 48, CITY)
                        ws.write(current_row, 50, 0.3)
                        ws.write(current_row, 54, QUICK_LINKS_TITLES)
                        ws.write(current_row, 55, QUICK_LINKS_DESCRIPTIONS)
                        ws.write(current_row, 56, QUICK_LINKS_URLS)
                        ws.write(current_row, 63, CLARIFICATIONS)
                        current_row += 1
            print(f"Лист 'Тексты': записано {current_row - 11} строк данных")
        else:
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
    print(f"   Ключевых фраз: {sum(len(g['keywords']) for g in GROUPS)}")


if __name__ == "__main__":
    main()
