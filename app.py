"""Демо-приложение вкладки «Антиплагиат»: те же шаблоны, вымышленные данные.

Запуск:

    pip install -r requirements.txt
    uvicorn app:app --reload

Затем http://127.0.0.1:8000/antiplagiat

Ни базы, ни корпусов, ни авторизации — всё, что нужно, лежит в
``fixtures.py``. Маршруты и имена параметров повторяют боевые, чтобы правка
шаблона переносилась обратно копированием файла, без перевода.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import fixtures
from models import Viewer

ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

app = FastAPI(title="Антиплагиат — интерфейс")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

VIEWER = Viewer()
UNIQUE_CUTOFFS = {"unique", "no_typical", "without_typical", "3"}

# base.html вызывает identity(request) как глобальную функцию шаблона: в
# боевом приложении она достаёт учётную запись из подписанной куки. Здесь
# смотрящий всегда один и тот же, авторизации в демо нет.
templates.env.globals["identity"] = lambda request: VIEWER


def _program(slug: str | None):
    for entry in fixtures.PROGRAMS:
        if entry.slug == slug or entry.title == slug:
            return entry
    return fixtures.PROGRAMS[0]


def _base_context(request: Request, program, variant: str, cutoff: str) -> dict:
    return {
        "request": request,
        "programs": fixtures.PROGRAMS,
        "program": program,
        "section": "antiplagiat",
        "active_section": "antiplagiat",
        "active_tab": "",
        "me": VIEWER,
        "variant": variant,
        "cutoff": cutoff,
        "message": "",
        "error": "",
        "query": "",
    }


@app.get("/", response_class=HTMLResponse)
@app.get("/antiplagiat", response_class=HTMLResponse)
def antiplagiat(
    request: Request,
    program: str | None = None,
    variant: str = "default",
    cutoff: str = "all",
):
    entry = _program(program)
    context = _base_context(request, entry, variant, cutoff)

    if not entry.has_report_index:
        # Плашка «нет индекса». Это третье состояние, и его нельзя путать с
        # «не посчитано»: там расчёт возможен, но не запускался, а здесь
        # искать не в чем.
        context.update(no_index=True, view=None, originality_by_leaf={}, unattached_stats=None)
        return templates.TemplateResponse(request, "antiplagiat.html", context)

    by_leaf = fixtures.LEAVES_UNIQUE if cutoff in UNIQUE_CUTOFFS else fixtures.LEAVES
    context.update(
        no_index=False,
        view=fixtures.tree_view(),
        originality_by_leaf=by_leaf,
        unattached_stats=fixtures.UNATTACHED,
        unattached_keys=[],
    )
    return templates.TemplateResponse(request, "antiplagiat.html", context)


@app.get("/{slug}/antiplagiat", response_class=HTMLResponse)
def antiplagiat_scoped(
    request: Request, slug: str, variant: str = "default", cutoff: str = "all"
):
    return antiplagiat(request, program=slug, variant=variant, cutoff=cutoff)


@app.get("/antiplagiat/{slug}/leaf/{number}", response_class=HTMLResponse)
def leaf(
    request: Request,
    slug: str,
    number: str,
    variant: str = "default",
    cutoff: str = "all",
    partial: bool = False,
):
    entry = _program(slug)
    context = _base_context(request, entry, variant, cutoff)
    context.update(
        number=number,
        title=f"Мероприятие {number}",
        documents=fixtures.DOCUMENTS.get(number, []),
        partial=bool(partial) or request.headers.get("X-Requested-With") == "XMLHttpRequest",
    )
    return templates.TemplateResponse(request, "antiplagiat_leaf.html", context)


@app.get("/antiplagiat/{slug}/document", response_class=HTMLResponse)
def document(
    request: Request,
    slug: str,
    path: str = "1 Разработка/1.1.1 Этап/Отчёт о НИР, этап 1.pdf",
    variant: str = "default",
    cutoff: str = "all",
    k: str = "all",
):
    entry = _program(slug)
    active_k = "3" if (k == "all" and cutoff in UNIQUE_CUTOFFS) else k
    context = _base_context(request, entry, variant, cutoff)
    context.update(
        card=fixtures.document_card(path, variant, active_k),
        current_k=active_k,
    )
    return templates.TemplateResponse(request, "antiplagiat_document.html", context)
