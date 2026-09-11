"""Контракт данных остальных вкладок — те же копии, что и в `models.py`.

Имена полей повторяют боевые (`server/portfolio.py`, `server/passport.py`) и
менять их нельзя: по ним правка переносится обратно.
"""
from __future__ import annotations

# `field` импортируется как `dc_field`: у PassportItem есть
# собственный атрибут `field`, и внутри тела класса он затеняет
# dataclasses.field. Так же сделано в боевом server/passport.py.
from dataclasses import dataclass
from dataclasses import field as dc_field


# ----------------------------------------------------------- показатели
@dataclass
class IndicatorRow:
    text: str
    values: dict[str, str] = dc_field(default_factory=dict)
    passive: bool = False
    has_value: bool = False
    evidence_target: str = ""
    children: list["IndicatorRow"] = dc_field(default_factory=list)
    xlsx_row: str = ""
    raw_values: dict[str, str] = dc_field(default_factory=dict)


@dataclass
class IndicatorsView:
    years: list[str]
    indicators: list[dict]
    selected_key: str
    unit: str
    rows: list[IndicatorRow]
    hide_empty: bool = False
    has_registry: bool = True


# ------------------------------------------------------------- паспорт
@dataclass
class WorkNode:
    key: str
    title: str
    value: str
    bold: bool = False
    children: list["WorkNode"] = dc_field(default_factory=list)


@dataclass
class PassportItem:
    kind: str  # "kv" | "subtitle" | "table" | "work_tree" | "group"
    field: str = ""
    value: str = ""
    title: str = ""
    headers: list[str] = dc_field(default_factory=list)
    rows: list[list[str]] = dc_field(default_factory=list)
    row_bold: list[bool] = dc_field(default_factory=list)
    work_nodes: list[WorkNode] = dc_field(default_factory=list)
    children: list["PassportItem"] = dc_field(default_factory=list)


@dataclass
class Section:
    title: str
    items: list[PassportItem] = dc_field(default_factory=list)


@dataclass
class PassportView:
    number: str
    title: str
    title_is_placeholder: bool
    meta_text: str
    sections: list[Section]
    source: str


# --------------------------------------------------------------- поиск
@dataclass
class SearchChunk:
    page_label: str
    snippet_html: str


@dataclass
class SearchResult:
    rank: int
    file_name: str
    relative_path: str
    activity_number: str
    relevance_percent: int
    chunks: list[SearchChunk] = dc_field(default_factory=list)


# ------------------------------------------------------------- отчёты
@dataclass
class ReportFile:
    name: str
    size_text: str = ""
    modified: str = ""
    suffix: str = ".pdf"
