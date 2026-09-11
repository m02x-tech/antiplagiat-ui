"""Вымышленные данные остальных вкладок.

**Все имена, организации, номера и суммы здесь выдуманы.** В боевом
приложении паспорта проектов несут руководителей, команды и партнёров —
настоящие персональные данные; в витрине их нет и быть не должно.

Формы и пропорции взяты из боевых: годы 2018–2024, три вида источника
показателя (Договор / Паспорт / Факт), дерево плана с мероприятиями и
результатами, фрагменты поиска с подсветкой.
"""
from __future__ import annotations

from models import TreeFilters, TreeRow, TreeView
from models_tabs import (
    IndicatorRow,
    IndicatorsView,
    PassportItem,
    PassportView,
    ReportFile,
    SearchChunk,
    SearchResult,
    Section,
    WorkNode,
)

# ----------------------------------------------------------- Структура
def tree_view_full() -> TreeView:
    """Дерево плана со всеми колонками: срок, руководитель, финансирование."""
    rows = [
        TreeRow(
            number="1",
            title="Разработка технологий цифрового моделирования",
            depth=0,
            deadline="2025-12-31",
            leader="Иванов И.И.",
            funding="Субсидия",
            organization="Инженерный институт",
            has_reports=True,
            has_passport=True,
            children=[
                TreeRow(
                    number="1.1",
                    title="Создание расчётного ядра",
                    depth=1,
                    deadline="2025-06-30",
                    leader="Иванов И.И.",
                    funding="Субсидия",
                    organization="Инженерный институт",
                    has_passport=True,
                    children=[
                        TreeRow(
                            number="1.1.1",
                            title="Разработка методики расчёта",
                            depth=2,
                            deadline="2024-12-31",
                            leader="Иванов И.И.",
                            funding="Субсидия",
                            organization="Инженерный институт",
                        ),
                        TreeRow(
                            number="1.1.2",
                            title="Верификация на тестовых задачах",
                            depth=2,
                            deadline="2025-06-30",
                            leader="Петрова А.С.",
                            funding="Субсидия",
                            organization="Инженерный институт",
                        ),
                        # Узел без документов: на дереве это отмечено, и
                        # красный цвет строки занят именно этим смыслом.
                        TreeRow(
                            number="1.1.3",
                            title="Документирование интерфейсов",
                            depth=2,
                            deadline="2025-09-30",
                            leader="Петрова А.С.",
                            funding="Внебюджет",
                            organization="Инженерный институт",
                            has_reports=False,
                        ),
                    ],
                ),
                TreeRow(
                    number="1.2",
                    title="Отраслевые приложения",
                    depth=1,
                    deadline="2025-12-31",
                    leader="Сидоров П.Н.",
                    funding="Внебюджет",
                    organization="Центр компетенций",
                    italic=True,
                    children=[
                        TreeRow(
                            number="1.2.1",
                            title="Пилот в машиностроении",
                            depth=2,
                            deadline="2025-03-31",
                            leader="Сидоров П.Н.",
                            funding="Внебюджет",
                            organization="Центр компетенций",
                        ),
                    ],
                ),
            ],
        ),
        TreeRow(
            number="2",
            title="Подготовка кадров и образовательные программы",
            depth=0,
            deadline="2026-12-31",
            leader="Сидоров П.Н.",
            funding="Субсидия",
            organization="Учебный центр",
            children=[
                TreeRow(
                    number="2.1",
                    title="Модули повышения квалификации",
                    depth=1,
                    deadline="2026-06-30",
                    leader="Кузнецова М.В.",
                    funding="Субсидия",
                    organization="Учебный центр",
                    children=[
                        TreeRow(
                            number="2.1.1",
                            title="Разработка учебных материалов",
                            depth=2,
                            deadline="2025-12-31",
                            leader="Кузнецова М.В.",
                            funding="Субсидия",
                            organization="Учебный центр",
                        ),
                    ],
                ),
            ],
        ),
    ]
    return TreeView(
        rows=rows,
        filters=TreeFilters(),
        direct_matches=0,
        inserted_count=0,
        total_nodes=9,
        coverage_text="Документы есть у 6 из 7 листьев (85.7 %)",
    )


# Дерево несёт ещё и справочники для фильтров — они читаются из view.
TREE_LEADERS = ["Иванов И.И.", "Петрова А.С.", "Сидоров П.Н.", "Кузнецова М.В."]
TREE_FUNDING = ["Субсидия", "Внебюджет"]
TREE_ORGS = ["Инженерный институт", "Центр компетенций", "Учебный центр"]
TREE_DATES = ["2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-06-30"]


# ---------------------------------------------------------- Показатели
YEARS = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]

INDICATOR_DEFS = [
    {"key": "Демо|Показатели|П1", "title": "П1. Объём выполненных работ", "unit": "млн руб."},
    {"key": "Демо|Показатели|П2", "title": "П2. Количество публикаций", "unit": "шт."},
    {"key": "Демо|Показатели|П3", "title": "П3. Численность исследователей", "unit": "чел."},
]


def indicators_view(selected: str = "Демо|Показатели|П1") -> IndicatorsView:
    """Таблица показателей: план и факт — величины разной природы.

    Источники расходятся в большинстве пар, и это не ошибка данных: договор
    фиксирует обещание, паспорт — план, факт — результат. Интерфейс обязан
    показывать все три, а не «правильное» число.
    """

    def row(text: str, by_year: dict[str, str], **kw) -> IndicatorRow:
        return IndicatorRow(
            text=text,
            values=by_year,
            has_value=bool(by_year),
            raw_values={y: v.replace(" ", "") for y, v in by_year.items()},
            **kw,
        )

    rows = [
        IndicatorRow(
            text="Дирекция программы",
            passive=True,
            children=[
                row("Договор", {"2018": "1 940", "2019": "2 100", "2020": "2 310", "2021": "2 480", "2022": "2 600", "2023": "2 750", "2024": "2 900"}, xlsx_row="12"),
                row("Паспорт", {"2018": "1 940", "2019": "2 100", "2020": "2 310", "2021": "2 480", "2022": "2 600", "2023": "2 750", "2024": "2 900"}, xlsx_row="13"),
                row("Факт", {"2018": "2 021,50", "2019": "2 088", "2020": "2 402", "2021": "2 455", "2022": "2 731", "2023": "2 690", "2024": "—"}, xlsx_row="14", evidence_target="Демо|П1|Факт"),
            ],
        ),
        IndicatorRow(
            text="Иванов И.И.",
            passive=True,
            children=[
                row("Договор", {"2021": "480", "2022": "520", "2023": "560", "2024": "600"}, xlsx_row="21"),
                row("Факт", {"2021": "455", "2022": "610", "2023": "540", "2024": "—"}, xlsx_row="22", evidence_target="Демо|П1|Факт|Иванов"),
            ],
        ),
        IndicatorRow(
            text="Петрова А.С.",
            passive=True,
            children=[
                row("Договор", {"2022": "300", "2023": "340", "2024": "380"}, xlsx_row="31"),
                # Строка без чисел: показывает состояние «значений нет».
                IndicatorRow(text="Факт", values={}, xlsx_row="32"),
            ],
        ),
    ]
    unit = next((d["unit"] for d in INDICATOR_DEFS if d["key"] == selected), "")
    return IndicatorsView(
        years=YEARS,
        indicators=INDICATOR_DEFS,
        selected_key=selected,
        unit=unit,
        rows=rows,
        hide_empty=False,
        has_registry=True,
    )


# --------------------------------------------------------------- Поиск
def search_results(query: str) -> list[SearchResult]:
    if not query:
        return []
    mark = f'<mark>{query}</mark>'
    return [
        SearchResult(
            rank=1,
            file_name="Отчёт о НИР, этап 1.pdf",
            relative_path="1 Разработка/1.1.1 Этап/Отчёт о НИР, этап 1.pdf",
            activity_number="1.1.1",
            relevance_percent=94,
            chunks=[
                SearchChunk(
                    page_label="с. 12–13",
                    snippet_html=(
                        f"Методика расчёта опирается на {mark}, что позволяет "
                        "уменьшить размерность задачи без потери точности в "
                        "зонах концентрации напряжений."
                    ),
                ),
                SearchChunk(
                    page_label="с. 41",
                    snippet_html=(
                        f"Результаты применения {mark} сопоставлены с данными "
                        "натурного эксперимента."
                    ),
                ),
            ],
        ),
        SearchResult(
            rank=2,
            file_name="Пояснительная записка.docx",
            relative_path="1 Разработка/1.1.1 Этап/Пояснительная записка.docx",
            activity_number="1.1.1",
            relevance_percent=71,
            chunks=[
                SearchChunk(
                    page_label="с. 3",
                    snippet_html=f"В разделе описан подход к {mark} и его ограничения.",
                )
            ],
        ),
        SearchResult(
            rank=3,
            file_name="Учебное пособие.pdf",
            relative_path="2 Подготовка кадров/2.1.1 Этап/Учебное пособие.pdf",
            activity_number="2.1.1",
            relevance_percent=48,
            chunks=[
                SearchChunk(
                    page_label="с. 88",
                    snippet_html=f"Глава посвящена {mark} в инженерной практике.",
                )
            ],
        ),
    ]


# ------------------------------------------------------------- Паспорт
def passport_view(number: str = "1.1") -> PassportView:
    return PassportView(
        number=number,
        title=f"Создание расчётного ядра (проект {number})",
        title_is_placeholder=False,
        meta_text="Срок: 2025-06-30 · Руководитель: Иванов И.И. · Финансирование: субсидия",
        source="демо-данные",
        sections=[
            Section(
                title="Общие сведения",
                items=[
                    PassportItem(kind="kv", field="Руководитель проекта", value="Иванов И.И."),
                    PassportItem(kind="kv", field="Направления", value="Цифровое моделирование, прочность"),
                    PassportItem(kind="kv", field="Индустриальный партнёр", value="ООО «Демо-Партнёр»"),
                    PassportItem(kind="kv", field="Потребитель результата", value="ООО «Демо-Потребитель»"),
                ],
            ),
            Section(
                title="Команда",
                items=[
                    PassportItem(
                        kind="table",
                        headers=["ФИО", "Роль", "Занятость"],
                        rows=[
                            ["Иванов И.И.", "Руководитель", "0,5 ставки"],
                            ["Петрова А.С.", "Ведущий инженер", "1,0 ставки"],
                            ["Сидоров П.Н.", "Инженер", "0,5 ставки"],
                        ],
                        row_bold=[True, False, False],
                    )
                ],
            ),
            Section(
                title="План работ",
                items=[
                    PassportItem(
                        kind="work_tree",
                        work_nodes=[
                            WorkNode(
                                key="1.1.1",
                                title="Разработка методики расчёта",
                                value="выполнено",
                                bold=True,
                                children=[
                                    WorkNode("1.1.1.1", "Обзор подходов", "выполнено"),
                                    WorkNode("1.1.1.2", "Выбор схемы дискретизации", "выполнено"),
                                ],
                            ),
                            WorkNode(
                                key="1.1.2",
                                title="Верификация на тестовых задачах",
                                value="в работе",
                                bold=True,
                                children=[WorkNode("1.1.2.1", "Подготовка тестов", "в работе")],
                            ),
                        ],
                    )
                ],
            ),
            Section(
                title="Показатели проекта",
                items=[
                    PassportItem(kind="subtitle", field="Плановые значения"),
                    PassportItem(
                        kind="table",
                        headers=["Показатель", "2024", "2025"],
                        rows=[["Публикации, шт.", "4", "6"], ["Объём работ, млн руб.", "12,0", "14,5"]],
                        row_bold=[False, False],
                    ),
                ],
            ),
        ],
    )


# -------------------------------------------------------------- Отчёты
REPORT_FILES = [
    ReportFile("Отчёт о НИР, этап 1.pdf", "2,4 МБ", "2024-12-20"),
    ReportFile("Отчёт о НИР, этап 2.pdf", "1,9 МБ", "2025-06-25"),
    ReportFile("Пояснительная записка.docx", "310 КБ", "2025-06-26", ".docx"),
    ReportFile("Протокол испытаний.pdf", "780 КБ", "2025-05-14"),
]


# ------------------------------------------- Реестр подтверждающих данных
EVIDENCE_COLUMNS = ["Год", "Источник", "Значение", "Документ"]
EVIDENCE_RECORDS = [
    {"Год": "2023", "Источник": "Смета", "Значение": "2 690", "Документ": "Свод за 2023 год.xlsx"},
    {"Год": "2022", "Источник": "Смета", "Значение": "2 731", "Документ": "Свод за 2022 год.xlsx"},
    {"Год": "2021", "Источник": "Смета", "Значение": "2 455", "Документ": "Свод за 2021 год.xlsx"},
]


# --------------------------------------------------------- Администрирование
JOURNAL = [
    {"ts": "2026-09-11 09:41", "user": "Администратор", "action": "originality.recompute", "target": "все программы", "ok": True, "reason": "", "program": "", "slug": "", "title": ""},
    {"ts": "2026-09-10 18:02", "user": "Администратор", "action": "indicator.edit", "target": "Демо|П1|Факт|2023", "ok": True, "reason": "", "program": "Демо", "slug": "demo", "title": "Демо-программа"},
    {"ts": "2026-09-10 17:55", "user": "Просмотр", "action": "report.delete", "target": "Черновик.docx", "ok": False, "reason": "недостаточно прав", "program": "", "slug": "", "title": ""},
]

INDEX_RUN = {
    "running": False,
    "program": "Демо-программа",
    "pid": 0,
    "started_at": "2026-09-11 08:10",
    "finished_at": "2026-09-11 08:38",
    "returncode": 0,
    "log_path": "logs/reindex-20260911-0810.log",
}

LOG_TAIL = """[102/102] elapsed: 00:28:37 | rate: 17.0 s/item
IndexSummary(discovered=102, indexed=102, unchanged=0, removed=0, failed=0)
indexed in Демо-программа: 102"""
