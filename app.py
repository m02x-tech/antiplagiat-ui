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

# indicators.html зовёт indicator_label(indicator) — в боевом приложении это
# portfolio.indicator_label, склеивающий заголовок с единицей измерения.
templates.env.globals["indicator_label"] = lambda indicator: (
    f"{indicator['title']}, {indicator['unit']}" if indicator.get("unit") else indicator["title"]
)


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


# ======================================================================
# Остальные вкладки. Те же шаблоны боевого приложения, те же имена
# параметров; данные — из fixtures_tabs.py, все вымышленные.
# ======================================================================
import fixtures_tabs as ft  # noqa: E402


def _tab_context(request: Request, slug: str | None, tab: str) -> dict:
    entry = _program(slug)
    return {
        "request": request,
        "programs": fixtures.PROGRAMS,
        "program": entry,
        "section": "programs",
        "active_section": "programs",
        "active_tab": tab,
        "me": VIEWER,
        "message": "",
        "error": "",
    }


@app.get("/{slug}/tree", response_class=HTMLResponse)
def tree(request: Request, slug: str, q: str = ""):
    context = _tab_context(request, slug, "tree")
    view = ft.tree_view_full()
    view.filters.query = q
    # Справочники фильтров живут на view — так же, как в боевом приложении.
    view.leaders = ft.TREE_LEADERS
    view.funding_sources = ft.TREE_FUNDING
    view.organizations = ft.TREE_ORGS
    view.dates = ft.TREE_DATES
    context["view"] = view
    return templates.TemplateResponse(request, "tree.html", context)


@app.get("/{slug}/indicators", response_class=HTMLResponse)
def indicators(request: Request, slug: str, key: str = "Демо|Показатели|П1"):
    context = _tab_context(request, slug, "indicators")
    context["view"] = ft.indicators_view(key)
    return templates.TemplateResponse(request, "indicators.html", context)


@app.get("/{slug}/indicators/edit", response_class=HTMLResponse)
def indicators_edit(request: Request, slug: str, key: str = "Демо|Показатели|П1"):
    context = _tab_context(request, slug, "indicators")
    context["view"] = ft.indicators_view(key)
    context["version"] = "demo"
    return templates.TemplateResponse(request, "indicators_edit.html", context)


@app.get("/{slug}/search", response_class=HTMLResponse)
def search(request: Request, slug: str, q: str = ""):
    context = _tab_context(request, slug, "search")
    context["query"] = q
    context["results"] = ft.search_results(q)
    context["query_id"] = "demo-query"
    context["rated"] = {}
    return templates.TemplateResponse(request, "search.html", context)


@app.get("/{slug}/edit", response_class=HTMLResponse)
def program_edit(request: Request, slug: str):
    context = _tab_context(request, slug, "program")
    context["card"] = "# Демо-программа развития\n\nТекст карточки в markdown."
    context["cards_path"] = "data/programs/demo.md"
    context["version"] = "demo"
    return templates.TemplateResponse(request, "program_edit.html", context)


@app.get("/{slug}/reports/{number}", response_class=HTMLResponse)
def reports(request: Request, slug: str, number: str):
    context = _tab_context(request, slug, "tree")
    context.update(
        number=number,
        title=f"Мероприятие {number}",
        files=[
            {"name": f.name, "previewable": f.suffix == ".pdf", "size_text": f.size_text, "modified": f.modified}
            for f in ft.REPORT_FILES
        ],
        allowed_extensions=".pdf, .docx, .pptx",
        max_upload_mb=50,
    )
    return templates.TemplateResponse(request, "reports.html", context)


@app.get("/{slug}/reports/{number}/preview", response_class=HTMLResponse)
def report_preview(request: Request, slug: str, number: str, filename: str = "Отчёт о НИР, этап 1.pdf"):
    context = _tab_context(request, slug, "tree")
    context.update(
        number=number,
        title=f"Мероприятие {number}",
        filename=filename,
        preview_url="/static/demo.pdf",
        download_url="/static/demo.pdf",
    )
    return templates.TemplateResponse(request, "report_preview.html", context)


@app.get("/{slug}/tree/{number}/meta", response_class=HTMLResponse)
def node_meta(request: Request, slug: str, number: str):
    context = _tab_context(request, slug, "tree")
    context.update(
        number=number,
        title="Разработка методики расчёта",
        meta={
            "deadline": "2024-12-31",
            "leaders_exact": "Иванов И.И.",
            "funding": "Субсидия",
            "organization": "Инженерный институт",
        },
        version="demo",
    )
    return templates.TemplateResponse(request, "node_meta.html", context)


@app.get("/{slug}/passport/{number}", response_class=HTMLResponse)
def passport(request: Request, slug: str, number: str):
    context = _tab_context(request, slug, "tree")
    context["view"] = ft.passport_view(number)
    return templates.TemplateResponse(request, "passport.html", context)


@app.get("/{slug}/evidence", response_class=HTMLResponse)
def evidence(request: Request, slug: str, label: str = "П1 · Факт · 2023"):
    context = _tab_context(request, slug, "indicators")
    context.update(label=label, columns=ft.EVIDENCE_COLUMNS, records=ft.EVIDENCE_RECORDS)
    return templates.TemplateResponse(request, "evidence.html", context)


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    context = _tab_context(request, None, "admin")
    # Админка видна только администратору; в демо смотрящий им и назначен,
    # иначе страницу нельзя было бы верстать.
    context["me"] = Viewer(username="Администратор", is_admin=True, csrf_token="demo")
    context.update(
        entries=ft.JOURNAL,
        journal_path="logs/audit.jsonl",
        run=ft.INDEX_RUN,
        log_tail=ft.LOG_TAIL,
        indexable=[p for p in fixtures.PROGRAMS if p.has_report_index],
    )
    return templates.TemplateResponse(request, "admin.html", context)


@app.get("/login", response_class=HTMLResponse)
def login(request: Request, error: str = "", next: str = "/"):
    return templates.TemplateResponse(
        request, "login.html", {"request": request, "error": error, "next": next}
    )


@app.get("/demo/error", response_class=HTMLResponse)
def demo_error(request: Request):
    return templates.TemplateResponse(
        request,
        "error.html",
        {"request": request, "status_code": 403, "detail": "Недостаточно прав", "back": "/"},
    )


@app.get("/sitcentre", response_class=HTMLResponse)
def sitcentre(request: Request):
    context = _tab_context(request, None, "")
    context["section"] = "sitcentre"
    context["available"] = False  # витрины в демо нет — видна заглушка
    return templates.TemplateResponse(request, "sitcentre.html", context)


# ----------------------------------------------------------------------
# Карточка программы объявлена ПОСЛЕДНЕЙ намеренно. `/{slug}` съедает любой
# односегментный путь, и, стоя выше, она перехватывала /admin, /login и
# /sitcentre — все три отдавали карточку программы. В боевом server/app.py
# на этот счёт стоит отдельное предупреждение: разделы регистрируются до
# программных маршрутов. Здесь порядок обратный, и результат тот же.
# ----------------------------------------------------------------------
@app.get("/{slug}/program", response_class=HTMLResponse)
def program_card(request: Request, slug: str):
    context = _tab_context(request, slug, "program")
    context["digest_html"] = (
        "<h2>Демо-программа развития</h2>"
        "<p>Карточка программы собирается из markdown-файла. Здесь — "
        "вымышленный текст: цели, задачи и ожидаемые результаты.</p>"
        "<ul><li>Цель: показать вёрстку карточки.</li>"
        "<li>Задача: не нести ни одного настоящего имени.</li></ul>"
    )
    return templates.TemplateResponse(request, "program.html", context)
