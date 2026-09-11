"""Вымышленные данные, подобранные так, чтобы каждое состояние было видно.

**Все имена и названия здесь выдуманы.** Реальный корпус содержит ФИО в
десятках тысяч имён файлов, и ни одно из них в этот репозиторий не попадает —
это условие его существования, а не оформительская мелочь.

Формы и пропорции при этом настоящие, взяты из замеров боевого корпуса:

* на листе бывает от 1 до 72 документов при разбросе объёмов до 30 000 раз;
* оригинальность по программам — 66–98 %, худшие документы уходят в ноль;
* кратность донора у типового текста доходит до нескольких десятков, и
  именно такие фрагменты не должны выглядеть как заимствование.
"""
from __future__ import annotations

from models import (
    BorrowedPassage,
    BorrowingDonor,
    DocumentCard,
    DocumentOriginality,
    LeafOriginality,
    Program,
    TreeFilters,
    TreeRow,
    TreeView,
)

PROGRAMS = [
    Program("ntic", "Центр НТИ"),
    Program("ncmu", "НЦМУ"),
    Program("pish", "ПИШ"),
    # Программа без индекса: показывает плашку «нет индекса», расчёта нет.
    # Это состояние отличается от «не посчитано» и от «заимствований нет».
    Program("demo2030", "Демо-программа", has_report_index=False),
]


def _leaf(number: str, title: str, depth: int) -> TreeRow:
    return TreeRow(number=number, title=title, depth=depth)


def tree_view() -> TreeView:
    rows = [
        TreeRow(
            number="1",
            title="Разработка технологий цифрового моделирования",
            depth=0,
            leader="Иванов И.И.",
            deadline="2025-12-31",
            children=[
                TreeRow(
                    number="1.1",
                    title="Создание расчётного ядра",
                    depth=1,
                    leader="Иванов И.И.",
                    children=[
                        _leaf("1.1.1", "Разработка методики расчёта", 2),
                        _leaf("1.1.2", "Верификация на тестовых задачах", 2),
                        _leaf("1.1.3", "Документирование интерфейсов", 2),
                    ],
                ),
                TreeRow(
                    number="1.2",
                    title="Отраслевые приложения",
                    depth=1,
                    leader="Петрова А.С.",
                    children=[
                        _leaf("1.2.1", "Пилот в машиностроении", 2),
                        _leaf("1.2.2", "Пилот в энергетике", 2),
                    ],
                ),
            ],
        ),
        TreeRow(
            number="2",
            title="Подготовка кадров и образовательные программы",
            depth=0,
            leader="Сидоров П.Н.",
            children=[
                TreeRow(
                    number="2.1",
                    title="Модули повышения квалификации",
                    depth=1,
                    children=[
                        _leaf("2.1.1", "Разработка учебных материалов", 2),
                        _leaf("2.1.2", "Апробация на слушателях", 2),
                    ],
                ),
            ],
        ),
    ]
    return TreeView(rows=rows, filters=TreeFilters(), total_nodes=11)


#: Каждый лист демонстрирует своё состояние.
LEAVES: dict[str, LeafOriginality] = {
    # Хорошо: высокая оригинальность, худший документ тоже высокий.
    "1.1.1": LeafOriginality("1.1.1", 94.2, 88.1, 6, True),
    # Средняя оригинальность при провальном худшем — здесь нужен бейдж тревоги.
    # Взвешенное среднее прячет один плохой документ среди пяти хороших.
    "1.1.2": LeafOriginality("1.1.2", 91.6, 34.8, 5, True),
    # Совсем плохо: почти весь текст найден в других документах.
    "1.1.3": LeafOriginality("1.1.3", 41.3, 12.0, 3, True),
    # Посчитано, заимствований нет. НЕ путать с «не посчитано».
    "1.2.1": LeafOriginality("1.2.1", 100.0, 100.0, 2, True),
    # Не посчитано: по листу нет ни одной строки.
    "1.2.2": LeafOriginality("1.2.2", 0.0, 0.0, 0, False),
    # Один документ на лист — обычный случай, среднее равно худшему.
    "2.1.1": LeafOriginality("2.1.1", 77.4, 77.4, 1, True),
    "2.1.2": LeafOriginality("2.1.2", 68.9, 51.2, 12, True),
}

#: Те же листья без типовых фрагментов (кратность донора >= 3 отсечена).
#: Числа выше, и разрыв между парами — главное, что показывает переключатель.
LEAVES_UNIQUE: dict[str, LeafOriginality] = {
    "1.1.1": LeafOriginality("1.1.1", 98.8, 96.4, 6, True),
    "1.1.2": LeafOriginality("1.1.2", 97.2, 71.0, 5, True),
    "1.1.3": LeafOriginality("1.1.3", 79.5, 44.6, 3, True),
    "1.2.1": LeafOriginality("1.2.1", 100.0, 100.0, 2, True),
    "1.2.2": LeafOriginality("1.2.2", 0.0, 0.0, 0, False),
    "2.1.1": LeafOriginality("2.1.1", 92.0, 92.0, 1, True),
    "2.1.2": LeafOriginality("2.1.2", 88.3, 74.9, 12, True),
}

#: Документы вне дерева: лежат в папке, которой нет в плане. В средние по
#: листьям не входят и показываются отдельным псевдоузлом.
UNATTACHED = LeafOriginality("вне дерева", 72.5, 30.1, 34, True)


def _doc(
    name: str,
    activity: str,
    pct: float,
    body: int,
    unique_pct: float,
) -> DocumentOriginality:
    borrowed = int(body * (100 - pct) / 100)
    return DocumentOriginality(
        program="Центр НТИ",
        relative_path=f"1 Разработка/{activity} Этап/{name}",
        filename=name,
        activity_number=activity,
        originality_pct=pct,
        body_words=body,
        borrowed_words=borrowed,
        body_chars=body * 6,
        borrowed_chars=borrowed * 6,
        computed_at="2026-09-11 09:40",
        originality_unique_pct=unique_pct,
        borrowed_words_unique=int(body * (100 - unique_pct) / 100),
    )


DOCUMENTS: dict[str, list[DocumentOriginality]] = {
    "1.1.1": [
        _doc("Отчёт о НИР, этап 1.pdf", "1.1.1", 96.4, 11_640, 99.1),
        _doc("Отчёт о НИР, этап 2.pdf", "1.1.1", 95.0, 9_820, 98.4),
        _doc("Пояснительная записка.docx", "1.1.1", 92.7, 4_310, 97.9),
        _doc("Акт приёмки этапа.pdf", "1.1.1", 88.1, 620, 96.4),
        _doc("Протокол испытаний.pdf", "1.1.1", 93.3, 2_180, 98.0),
        _doc("Презентация результатов.pdf", "1.1.1", 95.8, 310, 99.0),
    ],
    # Разброс объёмов в 30 000 раз — ровно тот случай, ради которого среднее
    # взвешено: короткий плохой документ не должен утопить лист, но и прятать
    # его нельзя.
    "1.1.2": [
        _doc("Отчёт о верификации.pdf", "1.1.2", 97.1, 31_400, 99.4),
        _doc("Сводная таблица результатов.docx", "1.1.2", 93.8, 1_120, 98.2),
        _doc("Служебная записка.docx", "1.1.2", 34.8, 210, 71.0),
        _doc("Приложение А.pdf", "1.1.2", 90.2, 3_640, 97.1),
        _doc("Приложение Б.pdf", "1.1.2", 89.9, 2_980, 96.8),
    ],
    "1.1.3": [
        _doc("Руководство пользователя.pdf", "1.1.3", 52.0, 8_200, 84.0),
        _doc("Руководство программиста.pdf", "1.1.3", 48.6, 7_100, 81.2),
        _doc("Описание применения.pdf", "1.1.3", 12.0, 3_400, 44.6),
    ],
    "1.2.1": [
        _doc("Отчёт по пилоту.pdf", "1.2.1", 100.0, 6_400, 100.0),
        _doc("Техническое задание.docx", "1.2.1", 100.0, 1_900, 100.0),
    ],
    "2.1.1": [_doc("Учебное пособие.pdf", "2.1.1", 77.4, 14_200, 92.0)],
    "2.1.2": [
        _doc(f"Отчёт группы {i}.pdf", "2.1.2", 60.0 + i * 2.5, 2_000 + i * 400, 80.0 + i * 1.5)
        for i in range(1, 13)
    ],
}


def document_card(relative_path: str, variant: str, current_k: str) -> DocumentCard | None:
    """Карточка одного документа. Здесь она одна на все пути — это демо."""
    filename = relative_path.rsplit("/", 1)[-1]
    donors = [
        BorrowingDonor(
            donor_program="Центр НТИ",
            donor_relative_path="1 Разработка/1.1.3 Этап/Руководство программиста.pdf",
            donor_filename="Руководство программиста.pdf",
            borrowed_words=1_940,
            passage_count=12,
            borrowed_pct=23.7,
            src_year=2024,
            dst_year=2022,
            direction="dst_older",
        ),
        BorrowingDonor(
            donor_program="НЦМУ",
            donor_relative_path="101 Исследования/101.4 Этап/Отчёт о НИР.pdf",
            donor_filename="Отчёт о НИР.pdf",
            borrowed_words=860,
            passage_count=5,
            borrowed_pct=10.5,
            src_year=2024,
            dst_year=2024,
            # Годы равны — стрелка «донор → реципиент» не показывается:
            # иначе отчёт 2024 года «списывает» у отчёта 2024 года.
            direction="undated",
        ),
        BorrowingDonor(
            donor_program="ПИШ",
            donor_relative_path="1.1 Программа/1.1.2022 Этап/Типовой раздел.pdf",
            donor_filename="Типовой раздел.pdf",
            borrowed_words=640,
            passage_count=4,
            borrowed_pct=7.8,
            src_year=None,
            dst_year=None,
            direction="undated",
        ),
    ]
    passages = [
        # Уникальное совпадение: один донор. Вот это — настоящий перенос.
        BorrowedPassage(
            passage_ord=1,
            donor_program="Центр НТИ",
            donor_relative_path="1 Разработка/1.1.3 Этап/Руководство программиста.pdf",
            donor_filename="Руководство программиста.pdf",
            chunk_id=101,
            page_from=12,
            page_to=13,
            char_from=430,
            char_len=1_180,
            run_words=214,
            word_from=1_530,
            donor_count=1,
            text=(
                "Методика расчёта строится на разбиении расчётной области "
                "тетраэдральной сеткой с локальным сгущением в зонах "
                "концентрации напряжений, при этом шаг сетки выбирается по "
                "результатам предварительного анализа сходимости."
            ),
        ),
        # Два донора: пограничный случай, при K = 3 ещё считается.
        BorrowedPassage(
            passage_ord=2,
            donor_program="НЦМУ",
            donor_relative_path="101 Исследования/101.4 Этап/Отчёт о НИР.pdf",
            donor_filename="Отчёт о НИР.pdf",
            chunk_id=102,
            page_from=18,
            page_to=18,
            char_from=120,
            char_len=410,
            run_words=64,
            word_from=3_210,
            donor_count=2,
            text=(
                "Верификация проводилась сопоставлением расчётных значений с "
                "данными натурного эксперимента, расхождение не превысило "
                "пяти процентов по всем контрольным точкам."
            ),
        ),
        # Типовой текст: сорок отчётов. Подписывать это «заимствованием»
        # нельзя — им один раз воспользуются и перестанут верить интерфейсу.
        BorrowedPassage(
            passage_ord=3,
            donor_program="ПИШ",
            donor_relative_path="1.1 Программа/1.1.2022 Этап/Типовой раздел.pdf",
            donor_filename="Типовой раздел.pdf",
            chunk_id=103,
            page_from=2,
            page_to=2,
            char_from=0,
            char_len=520,
            run_words=88,
            word_from=180,
            donor_count=40,
            text=(
                "Настоящий отчёт составлен в соответствии с требованиями "
                "ГОСТ 7.32 и содержит сведения о выполнении работ по этапу, "
                "результаты которых подлежат приёмке в установленном порядке."
            ),
        ),
        BorrowedPassage(
            passage_ord=4,
            donor_program="ПИШ",
            donor_relative_path="1.1 Программа/1.1.2022 Этап/Типовой раздел.pdf",
            donor_filename="Типовой раздел.pdf",
            chunk_id=104,
            page_from=3,
            page_to=3,
            char_from=90,
            char_len=300,
            run_words=52,
            word_from=640,
            donor_count=17,
            text=(
                "Работы выполнены в полном объёме в сроки, предусмотренные "
                "календарным планом, отклонений от технического задания не "
                "выявлено."
            ),
        ),
    ]
    body_words = 8_180
    borrowed = sum(p.run_words for p in passages)
    unique_borrowed = sum(p.run_words for p in passages if p.donor_count < 3)
    return DocumentCard(
        program="Центр НТИ",
        relative_path=relative_path,
        filename=filename,
        activity_number="1.1.1",
        variant=variant,
        sha256="0" * 64,
        body_words=body_words,
        body_chars=body_words * 6,
        borrowed_words=borrowed,
        borrowed_chars=borrowed * 6,
        originality_pct=round(100 * (1 - borrowed / body_words), 1),
        char_originality_pct=round(100 * (1 - borrowed / body_words), 1),
        donors=donors,
        passages=passages,
        computed_at="2026-09-11 09:40",
        file_exists=False,
        originality_unique_pct=round(100 * (1 - unique_borrowed / body_words), 1),
        borrowed_words_unique=unique_borrowed,
        unique_donor_cutoff=3,
        current_k=current_k,
        base_originality_pct=round(100 * (1 - borrowed / body_words), 1),
        base_borrowed_words=borrowed,
    )
