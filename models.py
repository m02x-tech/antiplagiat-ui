"""Контракт данных вкладки «Антиплагиат» — копия, а не импорт.

Этот репозиторий содержит **только интерфейс**. Боевое приложение читает те
же поля из PostgreSQL; здесь они приходят из фикстур. Копия нужна, чтобы
репозиторий был самодостаточным и не тянул за собой ни базу, ни корпуса.

**Имена полей менять нельзя.** Шаблоны и маршруты боевого приложения читают
именно их; переименование здесь означает, что правку нельзя будет перенести
обратно. Добавлять поля можно, если интерфейсу нужно что-то ещё — тогда
скажите об этом в описании правок, и поле появится на стороне базы.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LeafOriginality:
    """Три числа на листе дерева.

    Не одно: разброс объёмов документов внутри листа доходит до 30 000 раз,
    и простое арифметическое среднее в такой форме врёт. Поэтому среднее
    взвешено по объёму, и рядом показывается худший документ.
    """

    number: str
    weighted_pct: float
    worst_pct: float
    doc_count: int
    computed: bool  # False — «не посчитано», это НЕ то же самое, что 100 %


@dataclass(frozen=True)
class DocumentOriginality:
    program: str
    relative_path: str
    filename: str
    activity_number: str
    originality_pct: float
    body_words: int
    borrowed_words: int
    body_chars: int
    borrowed_chars: int
    computed_at: str | None = None
    originality_unique_pct: float | None = None
    borrowed_words_unique: int | None = None


@dataclass(frozen=True)
class BorrowingDonor:
    donor_program: str
    donor_relative_path: str
    donor_filename: str
    borrowed_words: int
    passage_count: int
    borrowed_pct: float
    src_year: int | None
    dst_year: int | None
    direction: str  # 'src_older' | 'dst_older' | 'undated'


@dataclass(frozen=True)
class BorrowedPassage:
    """Доказательство: координаты фрагмента, а не его текст.

    Текст в базе не хранится намеренно — иначе появляется ещё одно место,
    где оседают персональные данные. Боевое приложение достаёт фрагмент из
    документа при открытии карточки; здесь он берётся из фикстуры.

    ``donor_count`` — сколько независимых документов дают это же место.
    Замер 2026-09-11: фрагмент, который есть в сорока отчётах, — типовой
    текст, а не заимствование, и подписывать его словом «заимствовано»
    нельзя.
    """

    passage_ord: int
    donor_program: str
    donor_relative_path: str
    donor_filename: str
    chunk_id: int
    page_from: int
    page_to: int
    char_from: int
    char_len: int
    run_words: int
    text: str | None = None
    word_from: int = 0
    donor_count: int = 1


@dataclass(frozen=True)
class DocumentCard:
    program: str
    relative_path: str
    filename: str
    activity_number: str
    variant: str
    sha256: str | None
    body_words: int
    body_chars: int
    borrowed_words: int
    borrowed_chars: int
    originality_pct: float
    char_originality_pct: float
    donors: list[BorrowingDonor]
    passages: list[BorrowedPassage]
    computed_at: str | None = None
    file_exists: bool = False
    local_path: str | None = None
    originality_unique_pct: float | None = None
    borrowed_words_unique: int | None = None
    unique_donor_cutoff: int = 3
    current_k: str = "all"
    base_originality_pct: float | None = None
    base_borrowed_words: int | None = None


@dataclass
class TreeRow:
    """Строка дерева плана. Форма повторяет server/portfolio.py::TreeRow."""

    number: str
    title: str
    depth: int
    deadline: str = ""
    leader: str = ""
    funding: str = ""
    organization: str = ""
    has_reports: bool = True
    italic: bool = False
    has_passport: bool = False
    children: list["TreeRow"] = field(default_factory=list)


@dataclass
class TreeFilters:
    query: str = ""


@dataclass
class TreeView:
    rows: list[TreeRow]
    filters: TreeFilters
    direct_matches: int = 0
    inserted_count: int = 0
    total_nodes: int = 0
    coverage_text: str = ""


@dataclass(frozen=True)
class Program:
    slug: str
    title: str
    has_report_index: bool = True


@dataclass(frozen=True)
class Viewer:
    """Тот, кто смотрит страницу. В боевом приложении — учётная запись."""

    username: str = "Просмотр"
    is_admin: bool = False
    csrf_token: str = "demo"
