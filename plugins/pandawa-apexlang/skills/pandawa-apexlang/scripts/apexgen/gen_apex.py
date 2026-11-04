"""Generate an APEXlang (APEX 26.2) application from an app spec.

Every construct here was validated with SQLcl `apex validate` on the MBMS MVP
(see references/apexlang-gotchas.md for the rules this file relies on).
"""
import gen_sql
from apx import A, Comp, G, ML, O, render
from spec import kebab

MONEY = "999G999G999G999G990"
QTY = "999G999G999G990D99"
EDIT_ICON = '<span aria-label="Edit"><span class="fa fa-edit" aria-hidden="true" title="Edit"></span></span>'
EDITABLE = "('DRAFT','REJECTED')"
CORE = "Halaman inti template (core module), bukan dari entities."


class Ctx:
    def __init__(self, app):
        self.app = app
        self.files = {}
        self.e2e_pages = []

    def put(self, rel, content):
        self.files[rel] = content

    def page(self, num, alias, comp, e2e_title=None):
        n = 0
        for m in comp.members:
            if isinstance(m, Comp) and m.kind == "process":
                n += 1
                m.members.append(("advanced", G(("executionMappingIdentifier", "9%05d%03d" % (num, n)))))
        self.put("pages/p%05d-%s.apx" % (num, alias), render(comp))
        if e2e_title:
            self.e2e_pages.append({"alias": alias, "no": num, "title": e2e_title})


# ----------------------------------------------------------------------------- helpers
def auth(name):
    return ("security", G(("authorizationScheme", "@" + kebab(name))))


def region_comments(intent, role, guidance=None):
    """Metadata AI per region (konvensi Oracle APEX UX Pattern Catalog)."""
    lines = ["Intent: " + intent, "Pattern role: " + role]
    if guidance:
        lines.append("AI guidance: " + guidance)
    return ("comments", G(("comments", ML("", "\n".join(lines)))))


def page_comments(purpose, when_use, guidance, source, reqs=None):
    """Metadata AI per halaman: Purpose / When to Use / AI Guidance / Source / Requirements (bukan help user)."""
    parts = ["## Purpose", purpose, "## When to Use", when_use, "## AI Guidance", guidance,
             "## Source", source + " Ubah app.yaml lalu jalankan scripts/generate.sh; jangan edit file ini."]
    if reqs:
        key = lambda r: [int(x) if x.isdigit() else x for x in r[4:].split(".")]  # noqa: E731
        parts += ["## Requirements", ", ".join(sorted(set(reqs), key=key)) + " (lihat docs/02-frs.md dan docs/traceability.md)."]
    text = "\n\n".join(parts)
    return ("comments", G(("comments", ML("", text))))


def cond_expr(expr):
    return ("serverSideCondition", G(("type", "expression"), ("plsqlExpression", expr)))


def breadcrumb_region():
    return Comp("region", "breadcrumb",
                ("name", "Breadcrumb"),
                ("type", "breadcrumb"),
                ("source", G(("breadcrumb", "@breadcrumb"))),
                ("layout", G(("sequence", 10), ("slot", "breadcrumbBar"))),
                ("appearance", G(("template", "@/title-bar"),
                                 ("templateOptions", A(["#DEFAULT#", "t-BreadcrumbRegion--useBreadcrumbTitle"])))),
                ("componentAppearance", G(("breadcrumbTemplate", "@/breadcrumb"), ("templateOptions", "#DEFAULT#"))))


def refresh_on_dialog_close(region_id):
    return Comp("dynamicAction", "on-dialog-closed-refresh-report",
                ("name", "ON_DIALOG_CLOSED_REFRESH_REPORT"),
                ("execution", G(("sequence", 10))),
                ("when", G(("event", "apexafterclosedialog"), ("selectionType", "region"), ("region", "@" + region_id))),
                Comp("action", "native-refresh",
                     ("action", "refresh"),
                     ("affectedElements", G(("selectionType", "region"), ("region", "@" + region_id))),
                     ("execution", G(("sequence", 10), ("fireOnInit", False)))))


def val_expr(ident_, name, seq, expr, msg, item_name, requests=None):
    return Comp("validation", ident_,
                ("name", name),
                ("execution", G(("sequence", seq))),
                ("validation", G(("type", "expression"), ("plsqlExpression", expr))),
                ("error", G(("errorMessage", msg), ("displayLocation", "inlineWithFieldAndInNotification"),
                            ("associatedItem", "@" + item_name) if item_name else None)),
                ("serverSideCondition", G(("type", "requestIsContainedInValue"), ("value", requests))) if requests else None)


def ir_column(name, heading, kind, seq, alias_):
    m = [("type", "hidden" if kind == "hidden" else "plainText")]
    head, lay = [("heading", heading)], [("sequence", seq)]
    if kind in ("money", "qty", "number", "int", "pct"):
        head.append(("alignment", "end"))
        lay.append(("columnAlignment", "end"))
    m += [("heading", G(*head)), ("layout", G(*lay))]
    if kind == "money":
        m.append(("appearance", G(("formatMask", MONEY))))
    elif kind == "qty":
        m.append(("appearance", G(("formatMask", QTY))))
    dtype = "date" if kind == "date" else "number" if kind in ("money", "qty", "number", "int", "pct", "hidden") else "varchar2"
    m += [("source", G(("dataType", dtype))), ("advanced", G(("endUserAlias", alias_)))]
    return Comp("column", name, *m)


def _alias(i):
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def ir_page(ctx, num, name, alias_, group, region_id, sql, cols, auth_name, form_page=None, pk=None,
            create=True, create_auth=None, sort_col=None, sort_desc=False, help_text=None, meta=None, region_meta=None):
    col_comps, shown = [], []
    for i, (c, h, k) in enumerate(cols):
        col_comps.append(ir_column(c, h, k, i + 1, _alias(i)))
        if k != "hidden":
            shown.append(c)
    rm = [("name", name), ("type", "interactiveReport"),
          ("source", G(("location", "localDatabase"), ("type", "sqlQuery"), ("sqlQuery", ML("sql", sql)))),
          ("layout", G(("sequence", 20), ("slot", "body"))),
          ("appearance", G(("template", "@/interactive-report"), ("templateOptions", "#DEFAULT#"))),
          region_comments(*region_meta) if region_meta else None]
    if form_page:
        rm.append(("link", G(("linkColumn", "customTarget"),
                             ("target", O(("page", form_page), ("items", O(("P%d_%s" % (form_page, pk), "\\#%s#\\" % pk))),
                                          ("clearCache", form_page))),
                             ("linkIcon", EDIT_ICON))))
    rm += [("pagination", G(("type", "rowRangesXToY"))), ("messages", G(("whenNoDataFound", "Tidak ada data."))),
           ("actionsMenu", G(("subscription", False)))] + col_comps
    sr = [("visibility", "primaryDefault"), ("view", G(("rowsPerPage", 50)))]
    sr += [Comp("displayColumn", c, ("sequence", i + 1)) for i, c in enumerate(shown)]
    if sort_col:
        sr.append(Comp("sort", None, ("column", sort_col), ("sort", G(("sequence", 1), ("direction", "desc") if sort_desc else None))))
    rm.append(Comp("savedReport", str(num * 1000 + 1), *sr))
    comps = [breadcrumb_region(), Comp("region", region_id, *rm)]
    if form_page and create:
        btn = [("buttonName", "CREATE"), ("label", "Create"),
               ("layout", G(("sequence", 10), ("region", "@" + region_id), ("slot", "rightOfInteractiveReportSearchBar"))),
               ("appearance", G(("buttonTemplate", "@/text"), ("hot", True), ("templateOptions", "#DEFAULT#"))),
               ("behavior", G(("action", "redirectThisApp"), ("target", O(("page", form_page), ("clearCache", form_page))),
                              ("warnOnUnsavedChanges", "doNotCheck")))]
        if create_auth:
            btn.append(auth(create_auth))
        comps.append(Comp("button", "create", *btn))
    if form_page:
        comps.append(refresh_on_dialog_close(region_id))
    return Comp("page", str(num), ("name", name), ("alias", alias_.upper()), ("title", name),
                ("pageGroup", "@" + group),
                ("appearance", G(("pageTemplate", "@/standard"), ("templateOptions", "#DEFAULT#"))),
                auth(auth_name),
                ("help", G(("helpText", help_text))) if help_text else None,
                page_comments(*meta) if meta else None,
                *comps)


def dialog_appearance(style="modal"):
    """modal: dialog tengah (dokumen/form panjang). drawer: panel kanan untuk form pendek (UX Pattern Catalog p420)."""
    if style == "drawer":
        return [("appearance", G(("pageMode", "modalDialog"), ("dialogTemplate", "@/drawer"),
                                 ("templateOptions", A(["#DEFAULT#", "js-dialog-class-t-Drawer--pullOutEnd"])))),
                ("dialog", G(("chained", False)))]
    return [("appearance", G(("pageMode", "modalDialog"), ("dialogTemplate", "@/modal-dialog"), ("templateOptions", "#DEFAULT#"))),
            ("dialog", G(("chained", False), ("resizable", True)))]


def buttons_region():
    return Comp("region", "buttons", ("name", "Buttons"), ("type", "staticContent"),
                ("layout", G(("sequence", 20), ("slot", "dialogFooter"))),
                ("appearance", G(("template", "@/buttons-container"), ("templateOptions", "#DEFAULT#"))),
                ("settings", G(("outputAs", "text"))))


def dialog_button(ident_, name, label, seq, slot, hot=False, db_action=None, cond=None, danger=False,
                  confirm=None, validations=True):
    m = [("buttonName", name), ("label", label), ("layout", G(("sequence", seq), ("region", "@buttons"), ("slot", slot)))]
    if danger:
        m.append(("appearance", G(("buttonTemplate", "@/text"), ("templateOptions", A(["#DEFAULT#", "t-Button--danger", "t-Button--simple"])))))
    else:
        m.append(("appearance", G(("buttonTemplate", "@/text"), ("hot", True) if hot else None, ("templateOptions", "#DEFAULT#"))))
    beh = []
    if ident_ == "cancel":
        beh.append(("action", "definedByDynamicAction"))
    else:
        if not validations:
            beh.append(("executeValidations", False))
        beh.append(("warnOnUnsavedChanges", "doNotCheck"))
        if db_action:
            beh.append(("databaseAction", db_action))
        if confirm:
            beh.append(("requiresConfirmation", True))
    m.append(("behavior", G(*beh)))
    if confirm:
        m.append(("confirmation", G(("message", confirm), ("style", "danger" if danger else "information"))))
    if cond:
        m.append(cond_expr(cond))
    return Comp("button", ident_, *m)


def cancel_da():
    return Comp("dynamicAction", "on-click-cancel-close-dialog", ("name", "ON_CLICK_CANCEL_CLOSE_DIALOG"),
                ("execution", G(("sequence", 10))),
                ("when", G(("event", "click"), ("selectionType", "button"), ("button", "@cancel"))),
                Comp("action", "native-dialog-cancel", ("action", "cancelDialog"),
                     ("execution", G(("sequence", 10), ("fireOnInit", False)))))


def page_item(num, col, label, kind, region_id, seq, dtype="varchar2", req=False, maxlen=None, lov=None,
              lov_sql=None, cascade=None, default_static=None, default_sql=None, readonly_expr=None,
              query_only=False, form=True, pk=False, help_=None, min_=None, max_=None, null_text="- Pilih -", wide=False,
              subtype=None, text_case=None):
    t = {"text": "textField", "number": "numberField", "date": "datePicker", "textarea": "textarea",
         "select": "selectList", "display": "displayOnly", "hidden": "hidden"}[kind]
    m = [("type", t)]
    if kind != "hidden":
        m.append(("label", G(("label", label), ("alignment", "right"))))
    if kind == "number":
        m.append(("settings", G(("numberAlignment", "end"), ("virtualKeyboard", "decimal"),
                                ("minValue", min_) if min_ is not None else None, ("maxValue", max_) if max_ is not None else None)))
    if kind == "display":
        m.append(("settings", G(("sendOnPageSubmit", False))))
    if kind == "text" and (subtype or text_case):
        m.append(("settings", G(("subtype", subtype) if subtype else None, ("textCase", text_case) if text_case else None)))
    if kind == "select":
        lg = [("type", "sharedComponent"), ("lov", "@" + lov)] if lov else [("type", "sqlQuery"), ("sqlQuery", lov_sql)]
        lg += [("displayExtraValues", True), ("displayNullValue", True), ("nullDisplayValue", null_text)]
        m.append(("lov", G(*lg)))
        if cascade:
            m.append(("cascadingLov", G(("parentItems", "P%d_%s" % (num, cascade)), ("parentRequired", False))))
    lay = [("sequence", seq), ("region", "@" + region_id), ("slot", "regionBody")]
    if kind != "hidden":
        lay.append(("alignment", "left"))
    m.append(("layout", G(*lay)))
    if kind != "hidden":
        ap = [("template", "@/required-floating" if req else "@/optional-floating"), ("templateOptions", "#DEFAULT#")]
        if kind == "select":
            ap.append(("height", 1))
        elif kind == "textarea":
            ap += [("width", 60), ("height", 3)]
        elif kind in ("text", "number", "date"):
            ap.append(("width", 60 if wide else 32))
        m.append(("appearance", G(*ap)))
    val = ([("valueRequired", True)] if req else []) + ([("maxLength", maxlen)] if maxlen else [])
    if val:
        m.append(("validation", G(*val)))
    if form:
        src = [("formRegion", "@" + region_id), ("column", col), ("dataType", dtype)]
        if pk:
            src.append(("primaryKey", True))
        if query_only:
            src.append(("queryOnly", True))
        m.append(("source", G(*src)))
    if default_sql:
        m.append(("default", G(("type", "sqlQuerySingleValue"), ("sqlQuerySingleValue", default_sql))))
    elif default_static is not None:
        m.append(("default", G(("type", "static"), ("staticValue", str(default_static)))))
    if readonly_expr:
        m.append(("readOnly", G(("type", "expression"), ("plsqlExpression", readonly_expr))))
    if pk:
        m.append(("security", G(("sessionStateProtection", "checksumRequiredSessionLevel"))))
    if help_:
        m.append(("help", G(("inlineHelpText", help_))))
    return Comp("pageItem", "P%d_%s" % (num, col), *m)


# ----------------------------------------------------------------------------- entity pages
def ir_kind(c):
    return {"money": "money", "qty": "qty", "number": "number", "int": "int", "pct": "pct", "date": "date"}.get(c.type, "text")


def entity_list_page(ctx, e):
    app = ctx.app
    view_cols = gen_sql.entity_view_columns(app, e)
    cols = [(e.pk, "ID", "hidden")]
    if e.document:
        cols.append((e.document.number, "No. " + e.document.name, "text"))
    for c in e.columns:
        if not c.list:
            continue
        if c.type == "ref":
            cols.append((c.name + "_DSP", c.label, "text"))
        elif c.type in ("textarea",):
            cols.append((c.name, c.label, "text"))
        else:
            cols.append((c.name, c.label, ir_kind(c)))
    if e.document:
        cols.append(("STATUS", "Status", "text"))
    cols += [("UPDATED_BY", "Diubah Oleh", "text"), ("UPDATED_ON", "Diubah", "date")]
    names = {a for _, a in view_cols}
    sel = ", ".join(c.lower() for c, _, _ in cols if c in names)
    sql = "select %s\n  from %s_v" % (sel, e.table)
    sort = e.document.number if e.document else next((c.name for c in e.columns if c.type in ("code", "text")), e.pk)
    kind = "dokumen ber-approval %s" % e.document.name if e.document else ("baris detail dari %s" % app.entity(e.parent["entity"]).label
                                                                           if e.parent else "master data")
    purpose = e.purpose or "Daftar %s (%s)." % (e.label_plural, kind)
    meta = (purpose,
            "Mencari, memfilter, dan membuka %s. Create/Edit membuka form %s di halaman %d (%s)." % (e.label_plural, e.form_style, e.form_page, e.form_alias),
            "Pola list: Interactive Report dari view %s_v (MVC: region membaca view, bukan tabel). Kolom ref tampil sebagai <KOLOM>_DSP. "
            "Hak akses list %s, create/edit %s." % (e.table, e.view_auth, e.auth),
            "Generated dari app.yaml entities.%s." % e.name, app.entity_reqs(e))
    region_meta = ("Menampilkan %s yang bisa dicari dan difilter." % e.label_plural, "Browse list (Interactive Report).",
                   "Tambah kolom lewat columns di app.yaml (list: true/false), bukan dengan mengubah query ini.")
    if e.list_type != "ir":
        return faceted_page(ctx, e, cols, sort, meta)
    ctx.page(e.list_page, e.list_alias,
             ir_page(ctx, e.list_page, e.label_plural, e.list_alias, e.group, kebab(e.name), sql, cols, e.view_auth,
                     form_page=e.form_page, pk=e.pk, create="add" in e.operations, create_auth=e.auth,
                     sort_col=sort, sort_desc=bool(e.document), help_text=e.help, meta=meta, region_meta=region_meta),
             e2e_title=e.label_plural)


def title_column(e):
    """Kolom judul baris: nomor dokumen, atau kolom text/code pertama."""
    if e.document:
        return e.document.number
    return next((c.name for c in e.columns if c.type in ("code", "text") and not c.virtual), e.pk)


def facet_comps(app, e, num):
    out = [Comp("facet", "P%d_SEARCH" % num, ("type", "search"), ("label", G(("label", "Cari"))),
                ("layout", G(("sequence", 10))))]
    seq = 20

    def checkbox_facet(col, label, lov):
        lg = G(("type", "sharedComponent"), ("lov", "@" + lov)) if lov else G(("type", "distinctValues"))
        return Comp("facet", "P%d_%s" % (num, col), ("type", "checkboxGroup"), ("label", G(("label", label))),
                    ("lov", lg), ("layout", G(("sequence", seq))),
                    ("listEntries", G(("maxDisplayedEntries", 7), ("allowToExclude", False))),
                    ("source", G(("databaseColumn", col))))
    if e.document:
        out.append(checkbox_facet("STATUS", "Status", None))
        seq += 10
    for c in e.columns:
        if not c.facet or c.virtual:
            continue
        if c.type == "enum":
            out.append(checkbox_facet(c.name, c.label, "%s-%s" % (kebab(e.name), kebab(c.name))))
        elif c.type == "yn":
            out.append(checkbox_facet(c.name, c.label, "yes-no"))
        elif c.type == "ref":
            # _DSP + distinct values: LOV entitas bisa terfilter (active_yn, lov_where) sehingga hitungan facet tidak lengkap
            out.append(checkbox_facet(c.name + "_DSP", c.label, None))
        else:
            out.append(checkbox_facet(c.name, c.label, None))
        seq += 10
    return out


def faceted_page(ctx, e, cols, sort, meta):
    """Faceted search: facet di kolom kiri, hasil cards/classic report (UX Pattern Catalog p210/p220)."""
    app, num = ctx.app, e.list_page
    rid = "results"
    view_names = {a for _, a in gen_sql.entity_view_columns(app, e)}
    facet_cols = []
    for c in e.columns:
        if c.facet and not c.virtual:
            facet_cols.append(c.name + "_DSP" if c.type == "ref" else c.name)
    if e.document:
        facet_cols.append("STATUS")
    names = [c for c, _, _ in cols] + [f for f in facet_cols if f not in [c for c, _, _ in cols]]
    sel = "\n      ,".join(n.lower() for n in names if n in view_names)
    sql = "select %s\n  from %s_v" % (sel, e.table)
    order_by = ("orderBy", G(("type", "staticValue"), ("orderByClause", sort + (" DESC" if e.document else ""))))
    target = O(("page", e.form_page), ("items", O(("P%d_%s" % (e.form_page, e.pk), "&%s." % e.pk))), ("clearCache", e.form_page))
    title = title_column(e)
    shown = [(c, h, k) for c, h, k in cols if k != "hidden" and c not in ("UPDATED_BY",)]
    if e.list_type == "faceted-cards":
        sub = next((c for c, _, _ in shown if c != title and c not in ("STATUS", "UPDATED_ON")), None)
        body = next((c for c, _, _ in shown if c not in (title, sub, "STATUS", "UPDATED_ON")), None)
        results = Comp("region", rid, ("name", "Hasil " + e.label_plural), ("type", "cards"),
                       ("source", G(("location", "localDatabase"), ("type", "sqlQuery"), ("sqlQuery", ML("sql", sql)))),
                       order_by,
                       ("layout", G(("sequence", 20), ("slot", "body"))),
                       ("appearance", G(("template", "@/cards-container"),
                                        ("templateOptions", A(["#DEFAULT#", "t-CardsRegion--hideHeader js-addHiddenHeadingRoleDesc",
                                                               "t-CardsRegion--styleC"])))),
                       region_comments("Hasil pencarian %s yang sudah difilter facet." % e.label_plural, "Faceted search results (Cards).",
                                       "Klik judul kartu untuk membuka form. Kolom kartu diambil dari columns di app.yaml."),
                       ("messages", G(("whenNoDataFound", "Tidak ada data."))),
                       ("title", G(("column", title))),
                       ("subtitle", G(("column", sub))) if sub else None,
                       ("body", G(("column", body))) if body else None,
                       ("iconAndBadge", G(("iconSource", "iconClass"), ("iconCssClasses", "fa " + e.icon),
                                          ("badgeColumn", "STATUS") if e.document else None,
                                          ("badgeLabel", "Status") if e.document else None)),
                       Comp("action", "open", ("type", "title"), ("layout", G(("sequence", 10))),
                            ("behavior", G(("type", "redirectThisApp"), ("target", target)))))
    else:
        rtarget = O(("page", e.form_page), ("items", O(("P%d_%s" % (e.form_page, e.pk), "#%s#" % e.pk))), ("clearCache", e.form_page))
        rcols = classic_cols(cols, title, rtarget)
        n = len(cols)
        for j, f in enumerate([f for f in facet_cols if f not in [c for c, _, _ in cols]], 1):
            rcols.append(Comp("column", f, ("reportColumnQueryId", n + j), ("derivedColumn", "N"), ("type", "hidden"),
                              ("layout", G(("sequence", (n + j) * 10)))))
        results = Comp("region", rid, ("name", "Hasil " + e.label_plural), ("type", "classicReport"),
                       ("source", G(("location", "localDatabase"), ("type", "sqlQuery"), ("sqlQuery", ML("sql", sql)))),
                       order_by,
                       ("layout", G(("sequence", 20), ("slot", "body"))),
                       ("appearance", G(("template", "@/standard"), ("templateOptions", A(["#DEFAULT#", "t-Region--noUI"])))),
                       region_comments("Hasil pencarian %s yang sudah difilter facet." % e.label_plural, "Faceted search results (Classic Report).",
                                       "Klik kolom judul untuk membuka form. Kolom diambil dari columns di app.yaml."),
                       ("componentAppearance", G(("template", "@/standard"), ("templateOptions", A(["#DEFAULT#", "t-Report--stretch"])))),
                       ("pagination", G(("type", "rowRangesXToYOfZWithPagination"))),
                       ("messages", G(("whenNoDataFound", "Tidak ada data."))),
                       *rcols)
    hero = Comp("region", "button-bar", ("name", e.label_plural), ("type", "staticContent"),
                ("source", G(("htmlCode", '<span class="u-text-body-sm u-text-muted-color"><span id="total_row_count">-</span> baris</span>'))),
                ("layout", G(("sequence", 10), ("slot", "breadcrumbBar"))),
                ("appearance", G(("template", "@/hero"), ("templateOptions", A(["#DEFAULT#", "t-HeroRegion--hideIcon"])))),
                region_comments("Judul halaman, jumlah hasil, dan tombol Create.", "Page header with primary action."))
    search = Comp("region", "search", ("name", "Filter"), ("type", "facetedSearch"),
                  ("source", G(("filteredRegion", "@" + rid))),
                  ("layout", G(("sequence", 10), ("slot", "leftColumn"))),
                  ("appearance", G(("template", "@/blank-with-attributes-no-grid"), ("templateOptions", "#DEFAULT#"))),
                  region_comments("Mempersempit %s berdasarkan dimensi yang bermakna." % e.label_plural, "Facets (Faceted Search).",
                                  "Facet otomatis dari kolom enum, yn, ref, dan status; atur dengan facet: true/false per kolom di app.yaml."),
                  ("settings", G(("showTotalRowCount", "selector"), ("totalRowCountSelector", "#total_row_count"))),
                  *facet_comps(app, e, num))
    comps = [hero, search, results]
    if "add" in e.operations:
        btn = [("buttonName", "CREATE"), ("label", "Create"),
               ("layout", G(("sequence", 10), ("region", "@button-bar"), ("slot", "next"))),
               ("appearance", G(("buttonTemplate", "@/text"), ("hot", True), ("templateOptions", "#DEFAULT#"))),
               ("behavior", G(("action", "redirectThisApp"), ("target", O(("page", e.form_page), ("clearCache", e.form_page))),
                              ("warnOnUnsavedChanges", "doNotCheck"))),
               auth(e.auth)]
        comps.append(Comp("button", "create", *btn))
    comps.append(refresh_on_dialog_close(rid))
    purpose, when_use, guidance, source, reqs = meta
    guidance = ("Pola faceted search (%s): facet di kolom kiri, hasil di body, dari view %s_v (MVC). Hak akses list %s, create/edit %s."
                % (e.list_type, e.table, e.view_auth, e.auth))
    page = Comp("page", str(num), ("name", e.label_plural), ("alias", e.list_alias.upper()), ("title", e.label_plural),
                ("pageGroup", "@" + e.group),
                ("appearance", G(("pageTemplate", "@/left-side-column"), ("templateOptions", "#DEFAULT#"))),
                auth(e.view_auth),
                ("help", G(("helpText", e.help))) if e.help else None,
                page_comments(purpose, when_use, guidance, source + " (list_type: %s)" % e.list_type, reqs),
                *comps)
    ctx.page(num, e.list_alias, page, e2e_title=e.label_plural)


def classic_cols(cols, link_col=None, target=None):
    """Kolom classic report: (nama, heading, kind). kind hidden | money | qty | number | ... | text."""
    out = []
    for i, (c, h, k) in enumerate(cols, 1):
        m = [("reportColumnQueryId", i), ("derivedColumn", "N")]
        if k == "hidden":
            m += [("type", "hidden"), ("layout", G(("sequence", i * 10)))]
        elif c == link_col:
            m += [("type", "link"), ("heading", G(("heading", h))), ("layout", G(("sequence", i * 10))),
                  ("link", G(("target", target), ("linkText", "#%s#" % c), ("linkAttributes", 'class="u-text-bold"')))]
        else:
            hd, lay = [("heading", h)], [("sequence", i * 10)]
            if k in ("money", "qty", "number", "int", "pct"):
                hd.append(("alignment", "end"))
                lay.append(("columnAlignment", "end"))
            m += [("type", "plainText"), ("heading", G(*hd)), ("layout", G(*lay))]
            if k in ("money", "qty"):
                m.append(("appearance", G(("formatMask", MONEY if k == "money" else QTY))))
        out.append(Comp("column", c, *m))
    return out


def display_cols(app, e, skip=()):
    """Kolom tampilan entitas (list: true), ref -> _DSP."""
    cols = []
    for c in e.columns:
        if not c.list or c.name in skip:
            continue
        if c.type == "ref":
            cols.append((c.name + "_DSP", c.label, "text"))
        else:
            cols.append((c.name, c.label, "text" if c.type == "textarea" else ir_kind(c)))
    return cols


def workspace_page(ctx, e):
    """Master-detail: daftar induk (kiri, 4 kolom) + header & baris detail (kanan, 8 kolom).
    Pola parent-child dari Oracle APEX blueprints / UX Pattern Catalog (item selection), tanpa JavaScript custom:
    pilih induk = link ke halaman yang sama dengan P<page>_<PK>."""
    app, w = ctx.app, e.workspace
    num, d = w["page"], e.document
    pk_item = "P%d_%s" % (num, e.pk)
    title = title_column(e)
    view = {a for _, a in gen_sql.entity_view_columns(app, e)}
    # --- kiri: daftar induk
    sub = next(((c, h) for c, h, _ in display_cols(app, e) if c != title), None)
    lcols = [(e.pk, "ID", "hidden"), (title, e.label, "text")] + ([(sub[0], sub[1], "text")] if sub else []) + \
            ([("STATUS", "Status", "text")] if d else [])
    lsql = "select %s\n  from %s_v" % ("\n      ,".join(c.lower() for c, _, _ in lcols if c in view), e.table)
    sort = title + (" DESC" if d else "")
    self_target = O(("page", num), ("items", O((pk_item, "#%s#" % e.pk))))
    comps = [breadcrumb_region(),
             Comp("region", "list", ("name", "Daftar " + e.label_plural), ("type", "classicReport"),
                  ("source", G(("location", "localDatabase"), ("type", "sqlQuery"), ("sqlQuery", ML("sql", lsql)))),
                  ("orderBy", G(("type", "staticValue"), ("orderByClause", sort))),
                  ("layout", G(("sequence", 10), ("slot", "body"), ("columnSpan", 4))),
                  ("appearance", G(("template", "@/standard"), ("templateOptions", A(["#DEFAULT#", "t-Region--scrollBody"])))),
                  region_comments("Memilih satu %s; pilihan disimpan di %s." % (e.label, pk_item), "Parent list (master).",
                                  "Link judul me-reload halaman ini dengan %s. Jangan menambah JavaScript seleksi; pola ini sengaja deklaratif."
                                  % pk_item),
                  ("componentAppearance", G(("template", "@/standard"), ("templateOptions", A(["#DEFAULT#", "t-Report--stretch"])))),
                  ("pagination", G(("type", "rowRangesXToYOfZWithPagination"))),
                  ("messages", G(("whenNoDataFound", "Belum ada %s." % e.label))),
                  *classic_cols(lcols, title, self_target)),
             page_item(num, e.pk, e.pk, "hidden", "list", 5, dtype="number", form=False)]
    # --- kanan: kosong / header + detail
    sel_null = ("serverSideCondition", G(("type", "itemIsNull"), ("item", pk_item)))
    sel_set = ("serverSideCondition", G(("type", "itemIsNotNull"), ("item", pk_item)))
    comps.append(Comp("region", "no-selection", ("name", "Belum dipilih"), ("type", "staticContent"),
                      ("source", G(("htmlCode", '<p class="u-text-muted-color">Pilih %s di daftar kiri untuk melihat detailnya.</p>' % e.label))),
                      ("layout", G(("sequence", 20), ("slot", "body"), ("startNewRow", False), ("columnSpan", 8))),
                      ("appearance", G(("template", "@/standard"), ("templateOptions", "#DEFAULT#"))),
                      region_comments("Empty state saat belum ada %s dipilih." % e.label, "Empty state."), sel_null))
    comps.append(Comp("region", "detail", ("name", e.label), ("type", "staticContent"),
                      ("layout", G(("sequence", 30), ("slot", "body"), ("startNewRow", False), ("columnSpan", 8))),
                      ("appearance", G(("template", "@/blank-with-attributes"), ("templateOptions", "#DEFAULT#"))),
                      region_comments("Wadah header dan baris detail untuk %s terpilih." % e.label, "Detail container (child)."),
                      sel_set))
    hcols = [(e.pk, "ID", "hidden")] + ([(d.number, "No. " + d.name, "text")] if d else []) + \
            display_cols(app, e) + ([("STATUS", "Status", "text")] if d else [])
    hsql = "select %s\n  from %s_v\n where %s = to_number(:%s)" % (
        "\n      ,".join(c.lower() for c, _, _ in hcols if c in view), e.table, e.pk.lower(), pk_item)
    comps.append(Comp("region", "header", ("name", e.label), ("type", "classicReport"),
                      ("source", G(("location", "localDatabase"), ("type", "sqlQuery"), ("sqlQuery", ML("sql", hsql)),
                                   ("pageItemsToSubmit", pk_item))),
                      ("layout", G(("sequence", 10), ("parentRegion", "@detail"), ("slot", "subRegions"))),
                      ("appearance", G(("template", "@/standard"), ("templateOptions", "#DEFAULT#"))),
                      region_comments("Ringkasan %s terpilih." % e.label, "Parent context (Contextual Info).",
                                      "Ubah data lewat tombol Edit (form %d), bukan di region ini." % e.form_page),
                      ("componentAppearance", G(("template", "@/contextual-info"),
                                                ("templateOptions", A(["#DEFAULT#", "t-ContextualInfo--hideNulls",
                                                                       "t-ContextualInfo-label--stacked", "t-Report--hideNoPagination"])))),
                      ("pagination", G(("type", "showAll"))),
                      *classic_cols(hcols)))
    comps.append(Comp("button", "edit-header", ("buttonName", "EDIT_HEADER"), ("label", "Edit"),
                      ("layout", G(("sequence", 10), ("region", "@header"), ("slot", "edit"))),
                      ("appearance", G(("buttonTemplate", "@/text"), ("templateOptions", "#DEFAULT#"))),
                      ("behavior", G(("action", "redirectThisApp"),
                                     ("target", O(("page", e.form_page), ("items", O(("P%d_%s" % (e.form_page, e.pk), "&%s." % pk_item))),
                                                  ("clearCache", e.form_page))),
                                     ("warnOnUnsavedChanges", "doNotCheck"))),
                      auth(e.auth)))
    comps.append(Comp("dynamicAction", "on-dialog-closed-header", ("name", "ON_DIALOG_CLOSED_REFRESH_HEADER"),
                      ("execution", G(("sequence", 10))),
                      ("when", G(("event", "apexafterclosedialog"), ("selectionType", "button"), ("button", "@edit-header"))),
                      Comp("action", "native-refresh", ("action", "refresh"),
                           ("affectedElements", G(("selectionType", "region"), ("region", "@header"))),
                           ("execution", G(("sequence", 10), ("fireOnInit", False))))))
    # --- baris detail per entitas anak
    for i, ch in enumerate(app.children(e), 1):
        rid, pcol = "child-%s" % kebab(ch.name), ch.parent["column"]
        cview = {a for _, a in gen_sql.entity_view_columns(app, ch)}
        ccols = [(ch.pk, "ID", "hidden")] + display_cols(app, ch, skip=(pcol,))
        csql = "select %s\n  from %s_v\n where %s = to_number(:%s)" % (
            "\n      ,".join(c.lower() for c, _, _ in ccols if c in cview), ch.table, pcol.lower(), pk_item)
        link_col = next((c for c, _, k in ccols if k != "hidden"), None)
        ctarget = O(("page", ch.form_page), ("items", O(("P%d_%s" % (ch.form_page, ch.pk), "#%s#" % ch.pk))),
                    ("clearCache", ch.form_page))
        comps.append(Comp("region", rid, ("name", ch.label_plural), ("type", "classicReport"),
                          ("source", G(("location", "localDatabase"), ("type", "sqlQuery"), ("sqlQuery", ML("sql", csql)),
                                       ("pageItemsToSubmit", pk_item))),
                          ("orderBy", G(("type", "staticValue"), ("orderByClause", ch.pk))),
                          ("layout", G(("sequence", 10 + i * 10), ("parentRegion", "@detail"), ("slot", "subRegions"))),
                          ("appearance", G(("template", "@/standard"), ("templateOptions", "#DEFAULT#"))),
                          region_comments("%s milik %s terpilih." % (ch.label_plural, e.label),
                                          "Child records (%s.%s = %s)." % (ch.name, pcol, pk_item),
                                          "Kunci baris detail ditegakkan trigger %s_trg (lock_unless: %s); tombol Create hanya penanda UI."
                                          % (ch.table, ", ".join(ch.parent["lock_unless"]))),
                          ("componentAppearance", G(("template", "@/standard"), ("templateOptions", A(["#DEFAULT#", "t-Report--stretch"])))),
                          ("pagination", G(("type", "showAll"))),
                          ("messages", G(("whenNoDataFound", "Belum ada %s." % ch.label_plural))),
                          *classic_cols(ccols, link_col, ctarget)))
        if "add" in ch.operations:
            cond = None
            if d:
                cond = ("serverSideCondition", G(("type", "rowsReturned"), ("sqlQuery", ML("sql",
                        "select 1\n  from %s\n where %s = to_number(:%s)\n   and status in (%s)"
                        % (e.table, e.pk.lower(), pk_item, ", ".join("'%s'" % s for s in ch.parent["lock_unless"]))))))
            comps.append(Comp("button", "create-" + kebab(ch.name), ("buttonName", "CREATE_" + ch.name), ("label", "Tambah"),
                              ("layout", G(("sequence", 10), ("region", "@" + rid), ("slot", "edit"))),
                              ("appearance", G(("buttonTemplate", "@/text"), ("hot", True), ("templateOptions", "#DEFAULT#"))),
                              ("behavior", G(("action", "redirectThisApp"),
                                             ("target", O(("page", ch.form_page), ("items", O(("P%d_%s" % (ch.form_page, pcol), "&%s." % pk_item))),
                                                          ("clearCache", ch.form_page))),
                                             ("warnOnUnsavedChanges", "doNotCheck"))),
                              auth(ch.auth), cond))
            comps.append(Comp("dynamicAction", "on-dialog-closed-create-" + kebab(ch.name),
                              ("name", "ON_DIALOG_CLOSED_REFRESH_" + ch.name), ("execution", G(("sequence", 20 + i * 10))),
                              ("when", G(("event", "apexafterclosedialog"), ("selectionType", "button"), ("button", "@create-" + kebab(ch.name)))),
                              Comp("action", "native-refresh", ("action", "refresh"),
                                   ("affectedElements", G(("selectionType", "region"), ("region", "@" + rid))),
                                   ("execution", G(("sequence", 10), ("fireOnInit", False))))))
        comps.append(Comp("dynamicAction", "on-dialog-closed-" + kebab(ch.name), ("name", "ON_DIALOG_CLOSED_" + ch.name),
                          ("execution", G(("sequence", 25 + i * 10))),
                          ("when", G(("event", "apexafterclosedialog"), ("selectionType", "region"), ("region", "@" + rid))),
                          Comp("action", "native-refresh", ("action", "refresh"),
                               ("affectedElements", G(("selectionType", "region"), ("region", "@" + rid))),
                               ("execution", G(("sequence", 10), ("fireOnInit", False))))))
    kids = ", ".join(c.label_plural for c in app.children(e))
    meta = ("Master-detail %s dengan %s dalam satu halaman." % (e.label_plural, kids),
            "Meninjau %s satu per satu sambil melihat dan mengubah %s-nya, tanpa pindah halaman." % (e.label_plural, kids),
            "Pola parent-child: daftar induk 4 kolom (kiri), header (Contextual Info) dan detail 8 kolom (kanan), difilter %s. "
            "Edit header membuka form %d; tambah/edit detail membuka form detail. Aturan kunci ada di trigger, bukan di halaman."
            % (pk_item, e.form_page),
            "Generated dari app.yaml entities.%s.workspace." % e.name,
            list(dict.fromkeys(app.entity_reqs(e) + [r for c in app.children(e) for r in app.entity_reqs(c)])))
    page = Comp("page", str(num), ("name", w["label"]), ("alias", w["alias"].upper()), ("title", w["label"]),
                ("pageGroup", "@" + e.group),
                ("appearance", G(("pageTemplate", "@/standard"), ("templateOptions", "#DEFAULT#"))),
                auth(e.view_auth), page_comments(*meta), *comps)
    ctx.page(num, w["alias"], page, e2e_title=w["label"])


def entity_form_page(ctx, e):
    app = ctx.app
    num, rid = e.form_page, kebab(e.name)
    d = e.document
    status_item = "P%d_STATUS" % num
    pk_item = "P%d_%s" % (num, e.pk)
    editable = "nvl(:%s,'DRAFT') in %s" % (status_item, EDITABLE)
    comps = [buttons_region(),
             Comp("region", rid, ("name", e.label), ("type", "form"),
                  ("source", G(("location", "localDatabase"), ("tableName", e.table.upper()))),
                  ("layout", G(("sequence", 10), ("slot", "contentBody"))),
                  ("appearance", G(("template", "@/blank-with-attributes"), ("templateOptions", "#DEFAULT#"))),
                  region_comments("Membuat dan mengubah satu record %s." % e.label,
                                  "Single-record form (%s)." % e.form_style,
                                  "Validasi bisnis ada di trigger %s_trg dan package; item ini hanya UI." % e.table
                                  + (" Status hanya berubah lewat approval engine." if d else "")),
                  ("edit", G(("enabled", True), ("allowedOperations", A(e.operations)))))]
    seq = 5
    comps.append(page_item(num, e.pk, e.pk, "hidden", rid, seq, dtype="number", pk=True))
    if d:
        seq += 5
        comps.append(page_item(num, d.number, "No. " + d.name, "display", rid, seq, query_only=True))
        seq += 5
        if d.operational:
            comps.append(page_item(num, "STATUS", "Status", "select", rid, seq, lov="%s-status" % kebab(e.name),
                                   default_static="DRAFT",
                                   readonly_expr="nvl(:%s,'DRAFT') not in ('APPROVED',%s)" % (status_item, ",".join("'%s'" % s for s in d.operational)),
                                   help_="Status operasional setelah approved. Approval lewat Submit for Approval."))
        else:
            comps.append(page_item(num, "STATUS", "Status", "display", rid, seq, query_only=True))
    for c in e.columns:
        if c.form == "none":
            continue
        seq += 10
        ro = c.readonly_when
        if d and c.name in d.lock:
            ro = "not (%s)" % editable
        common = dict(dtype=c.apex_dtype, req=c.required and c.form == "edit", help_=c.help)
        if c.form == "hidden":
            comps.append(page_item(num, c.name, c.label, "hidden", rid, seq, dtype=c.apex_dtype,
                                   default_static=c.default, default_sql=c.default_sql))
            continue
        if c.form == "display" or c.virtual:
            comps.append(page_item(num, c.name, c.label, "display", rid, seq, dtype=c.apex_dtype, query_only=True, help_=c.help))
            continue
        if c.type in ("text", "code"):
            sem = c.sem or {}
            item = page_item(num, c.name, c.label, "text", rid, seq, maxlen=c.maxlen, readonly_expr=ro,
                             default_static=c.default, default_sql=c.default_sql, wide=(c.size or 0) > 100,
                             subtype=sem.get("subtype"), text_case=sem.get("case"), **common)
        elif c.type == "textarea":
            item = page_item(num, c.name, c.label, "textarea", rid, seq, maxlen=c.maxlen, readonly_expr=ro, **common)
        elif c.type in ("number", "int", "money", "qty", "pct"):
            item = page_item(num, c.name, c.label, "number", rid, seq, readonly_expr=ro, min_=c.min, max_=c.max,
                             default_static=c.default, default_sql=c.default_sql, **common)
        elif c.type == "date":
            item = page_item(num, c.name, c.label, "date", rid, seq, readonly_expr=ro, default_sql=c.default_sql, **common)
        elif c.type == "yn":
            item = page_item(num, c.name, c.label, "select", rid, seq, lov="yes-no", default_static=c.default,
                             readonly_expr=ro, **common)
        elif c.type == "enum":
            item = page_item(num, c.name, c.label, "select", rid, seq, lov="%s-%s" % (kebab(e.name), kebab(c.name)),
                             default_static=c.default, readonly_expr=ro, **common)
        elif c.type == "ref":
            r = app.entity(c.ref)
            if c.lov_sql:
                item = page_item(num, c.name, c.label, "select", rid, seq, lov_sql=c.lov_sql.replace(":P_", ":P%d_" % num), cascade=c.cascade,
                                 default_sql=c.default_sql, readonly_expr=ro, **common)
            else:
                item = page_item(num, c.name, c.label, "select", rid, seq, lov=r.lov_name, default_sql=c.default_sql,
                                 readonly_expr=ro, **common)
        comps.append(item)

    def joined(base, extra):
        return base if not extra else "%s and %s" % (base, extra)

    requests = []
    comps.append(dialog_button("cancel", "CANCEL", "Cancel", 10, "close"))
    if "delete" in e.operations:
        comps.append(dialog_button("delete", "DELETE", "Delete", 20, "delete", db_action="delete",
                                   cond=joined(":%s is not null" % pk_item, "nvl(:%s,'DRAFT') = 'DRAFT'" % status_item if d else None),
                                   danger=True, confirm="&APP_TEXT$DELETE_MSG!RAW.", validations=False))
        requests.append("DELETE")
    if "update" in e.operations:
        comps.append(dialog_button("save", "SAVE", "Apply Changes", 30, "next", hot=True, db_action="update",
                                   cond=joined(":%s is not null" % pk_item,
                                               "nvl(:%s,'DRAFT') not in ('SUBMITTED','CANCELLED','CLOSED')" % status_item if d else None)))
        requests.append("SAVE")
    if "add" in e.operations:
        comps.append(dialog_button("create", "CREATE", "Create", 40, "next", hot=True, db_action="insert",
                                   cond=":%s is null" % pk_item))
        requests.append("CREATE")
    if d:
        comps.append(dialog_button("submit", "SUBMIT", "Submit for Approval", 50, "next", hot=True, db_action="update",
                                   cond=joined(":%s is not null" % pk_item, editable),
                                   confirm="Ajukan dokumen ini untuk approval? Setelah diajukan dokumen terkunci."))
        requests.append("SUBMIT")
    comps.append(cancel_da())
    save_requests = ",".join(r for r in requests if r != "DELETE")
    for i, v in enumerate(e.validations, 1):
        item = ("P%d_%s" % (num, v["item"].upper())) if v.get("item") else None
        comps.append(val_expr("check-%s-%d" % (rid, i), v.get("name", "CHECK_%s_%d" % (e.name, i)), i * 10, v["expr"].replace(":P_", ":P%d_" % num),
                              v["message"], item, requests=v.get("when", save_requests)))
    # validasi format dari semantic (sama dengan check constraint, tapi pesan ramah di item)
    for j, c in enumerate([c for c in e.columns if c.sem and c.form == "edit"], 1):
        it = "P%d_%s" % (num, c.name)
        expr = ":%s is null or regexp_like(%s, '%s')" % (it, "lower(trim(:%s))" % it if c.sem.get("case") == "lower" else "trim(:%s)" % it,
                                                         c.sem["regex"].replace("'", "''"))
        comps.append(val_expr("format-%s" % kebab(c.name), "FORMAT_%s" % c.name, 500 + j * 10, expr, c.sem["msg"], it,
                              requests=save_requests))
    comps.append(Comp("process", "init-%s-form" % rid, ("name", "INIT_%s_FORM" % e.name), ("type", "formInitialization"),
                      ("formRegion", "@" + rid), ("execution", G(("sequence", 10), ("point", "beforeHeader")))))
    comps.append(Comp("process", "save-%s" % rid, ("name", "SAVE_%s" % e.name), ("type", "formAutoRowProcessing"),
                      ("formRegion", "@" + rid), ("execution", G(("sequence", 10)))))
    if d:
        comps.append(Comp("process", "call-submit-%s" % rid, ("name", "CALL_SUBMIT_%s" % e.name), ("type", "executeCode"),
                          ("source", G(("plsqlCode", ML("plsql", "%s_approval_pkg.submit(p_doc_type => '%s', p_doc_id => :%s);"
                                                         % (app.prefix, d.type, pk_item))))),
                          ("execution", G(("sequence", 20))),
                          ("successMessage", G(("successMessage", "Dokumen diajukan untuk approval."))),
                          ("serverSideCondition", G(("whenButtonPressed", "@submit")))))
    comps.append(Comp("process", "close-dialog", ("name", "CLOSE_DIALOG"), ("type", "closeDialog"),
                      ("settings", G(("showSuccessMessages", True))), ("execution", G(("sequence", 50))),
                      ("serverSideCondition", G(("type", "requestIsContainedInValue"), ("value", ",".join(requests))))))
    if d:
        guidance = ("Dokumen ber-approval %s: DRAFT -> Submit for Approval -> APPROVED/REJECTED. Kolom %s terkunci setelah approval. "
                    "Logika ada di %s_approval_pkg dan trigger, bukan di halaman." % (d.type, ", ".join(d.lock) or "-", app.prefix))
    else:
        guidance = "Form pendek; simpan dengan Create/Apply Changes. Logika validasi di database (trigger/constraint)."
    meta = (e.purpose or "Form %s." % e.label,
            "Dibuka dari halaman list %d (%s) untuk create/edit satu record." % (e.list_page, e.list_alias),
            guidance, "Generated dari app.yaml entities.%s (form_style: %s)." % (e.name, e.form_style), app.entity_reqs(e))
    page = Comp("page", str(num), ("name", e.label), ("alias", e.form_alias.upper()), ("title", e.label),
                ("pageGroup", "@" + e.group),
                *dialog_appearance(e.form_style),
                auth(e.auth), page_comments(*meta), *comps)
    ctx.page(num, e.form_alias, page)


def report_page(ctx, r):
    cols = [(c["name"], c["label"], c["type"]) for c in r.columns]
    sql = "select %s\n  from %s" % (", ".join(c[0].lower() for c in cols), r.view)
    meta = (r.help or "Laporan %s." % r.title, "Analisis read-only; export lewat menu Actions Interactive Report.",
            "Query ada di view %s (database/custom). Ubah view-nya, lalu sesuaikan reports.columns di app.yaml." % r.view,
            "Generated dari app.yaml reports (page %d)." % r.page, r.req)
    ctx.page(r.page, r.alias, ir_page(ctx, r.page, r.title, r.alias, r.group, r.alias, sql, cols, r.auth,
                                      sort_col=r.sort or cols[0][0], help_text=r.help, meta=meta,
                                      region_meta=("Menampilkan %s." % r.title, "Read-only report (Interactive Report).")),
             e2e_title=r.title)


# ----------------------------------------------------------------------------- system pages
def home_page(ctx):
    app = ctx.app
    dash = app.dashboard
    comps = [Comp("region", "app-name", ("name", "Home"), ("title", dash.get("title", app.name)), ("type", "staticContent"),
                  ("source", G(("htmlCode", dash.get("subtitle", app.description)))),
                  ("layout", G(("sequence", 10), ("slot", "breadcrumbBar"))),
                  ("appearance", G(("template", "@/hero"), ("templateOptions", "#DEFAULT#"))),
                  ("image", G(("fileUrl", "#APP_FILES#icons/app-icon-512.png"))),
                  region_comments("Judul dan konteks singkat aplikasi.", "Dashboard header.",
                                  "Ringkas; jangan dipakai untuk instruksi panjang."))]
    kpis = dash.get("kpis", [])
    if kpis:
        comps.append(metric_cards(app, kpis, dash.get("kpi_title", "Ringkasan")))
    for i, ch in enumerate(dash.get("charts", []), 1):
        ctype = ch.get("type", "bar")
        series = []
        for j, s in enumerate(ch.get("series", []), 1):
            series.append(Comp("series", "series-%d" % j, ("name", s.get("name", "Series %d" % j)),
                               ("execution", G(("sequence", j * 10))),
                               ("source", G(("type", "sqlQuery"),
                                            ("sqlQuery", ML("sql", "select label, value\n  from %s_dash_c%d_s%d_v" % (app.prefix, i, j))))),
                               ("columnMapping", G(("label", "LABEL"), ("value", "VALUE"))),
                               ("label", G(("show", ctype == "pie"))),
                               ("performance", G(("maxRowsToProcess", 50)))))
        axes = [] if ctype == "pie" else [
            Comp("axis", "x", ("name", "x"), ("majorTicks", G(("show", "auto")))),
            Comp("axis", "y", ("name", "y"), ("value", G(("format", "decimal"), ("decimalPlaces", 0))), ("majorTicks", G(("show", "auto"))))]
        comps.append(Comp("region", "chart-%d" % i, ("name", ch.get("title", "Chart %d" % i)), ("type", "chart"),
                          ("layout", G(("sequence", 30 + i * 10), ("slot", "body"), ("startNewRow", False) if i % 2 == 0 else None)),
                          ("appearance", G(("template", "@/standard"), ("templateOptions", A(["#DEFAULT#", "t-Region--scrollBody"])))),
                          region_comments("Visualisasi %s." % ch.get("title", "data"), "Dashboard chart (%s)." % ctype,
                                          "Data dari view %s_dash_c%d_s*_v (kolom LABEL, VALUE); ubah sql-nya di dashboard.charts app.yaml."
                                          % (app.prefix, i)),
                          ("chart", G(("type", ctype))) if ctype == "pie" else None,
                          ("performance", G(("lazyLoading", False))),
                          ("value", G(("format", "decimal"), ("decimalPlaces", 0))) if ctype == "pie" else None,
                          ("legend", G(("show", len(series) > 1))),
                          *series, *axes))
    page = Comp("page", "100", ("name", "Home"), ("alias", "HOME"), ("title", "Home"), ("pageGroup", "@home"),
                ("appearance", G(("pageTemplate", "@/standard"), ("templateOptions", "#DEFAULT#"))),
                ("navigation", G(("cursorFocus", "doNotFocusCursor"))),
                ("security", G(("authorizationScheme", "@app-users"), ("pageAccessProtection", "argumentsMustHaveChecksum"),
                               ("formAutoComplete", False))),
                page_comments("Ringkasan kondisi aplikasi: KPI dan chart utama.",
                              "Halaman pertama setelah login; titik awal navigasi.",
                              "Pola dashboard: metric card di atas (2-4 KPI sebanding), chart dua kolom di bawah. "
                              "KPI dari view %s_dash_kpi_v (satu baris per KPI)." % app.prefix,
                              "Generated dari app.yaml dashboard.",
                              list(dict.fromkeys([q for k in dash.get("kpis", []) for q in k["req"]]
                                                 + [q for c in dash.get("charts", []) for q in c["req"]]))),
                *comps)
    ctx.page(100, "home", page, e2e_title="Home")


def metric_cards(app, kpis, title):
    """KPI sebagai template component Metric Card (UX Pattern Catalog p110)."""
    cols = [("SEQ", "number"), ("ICON", "varchar2"), ("LABEL", "varchar2"), ("METRIC_VALUE", "number")]
    return Comp("region", "kpi", ("name", title), ("type", "themeTemplateComponent/metricCard"),
                ("source", G(("location", "localDatabase"), ("type", "sqlQuery"),
                             ("sqlQuery", ML("sql", "select seq, icon, label, metric_value\n  from %s_dash_kpi_v" % app.prefix)))),
                ("orderBy", G(("type", "staticValue"), ("orderByClause", "SEQ"))),
                ("layout", G(("sequence", 20), ("slot", "body"))),
                ("appearance", G(("template", "@/blank-with-attributes-no-grid"),
                                 ("templateOptions", A(["#DEFAULT#", "margin-bottom-md"])))),
                ("accessibility", G(("landmarkType", "region"))),
                region_comments("KPI utama untuk dipindai cepat.", "KPI summary (Metric Card).",
                                "Pakai 2-4 KPI yang sebanding; ubah lewat dashboard.kpis (label, sql, icon) di app.yaml."),
                ("componentAppearance", G(("display", "report"))),
                ("settings", G(("metric", "&METRIC_VALUE."), ("metricCssClasses", "u-text-subheading-md"),
                               ("meta", "&LABEL."), ("layout", "2Columns" if len(kpis) <= 2 else "4Columns"))),
                ("plugin-avatar", G(("displayAvatar", True), ("icon", "&ICON."), ("style", "subtle"), ("position", "inline"))),
                *[Comp("column", c, ("layout", G(("sequence", (i + 1) * 10))), ("source", G(("databaseColumn", c), ("dataType", t))),
                       ("appearance", G(("formatMask", "999G999G999G999G990"))) if c == "METRIC_VALUE" else None)
                  for i, (c, t) in enumerate(cols)])


def approval_pages(ctx):
    app = ctx.app
    sql = ("select approval_id, doc_name, doc_no, approval_level, approver_role, amount, requested_by, requested_on,\n"
           "       status, can_act_yn, acted_by, acted_on, note\n  from %s_approvals_v" % app.prefix)
    cols = [("APPROVAL_ID", "ID", "hidden"), ("DOC_NAME", "Jenis Dokumen", "text"), ("DOC_NO", "No. Dokumen", "text"),
            ("APPROVAL_LEVEL", "Level", "number"), ("APPROVER_ROLE", "Role Approver", "text"), ("AMOUNT", "Nilai", "money"),
            ("REQUESTED_BY", "Diajukan Oleh", "text"), ("REQUESTED_ON", "Diajukan", "date"), ("STATUS", "Status", "text"),
            ("CAN_ACT_YN", "Bisa Saya Proses?", "text"), ("ACTED_BY", "Diproses Oleh", "text"), ("ACTED_ON", "Diproses", "date"),
            ("NOTE", "Catatan", "text")]
    ctx.page(190, "approval-inbox", ir_page(ctx, 190, "Approval Inbox", "approval-inbox", "home", "approvals", sql, cols,
                                            "app-users", form_page=191, pk="APPROVAL_ID", create=False,
                                            sort_col="APPROVAL_ID", sort_desc=True,
                                            help_text="Pengaju tidak dapat menyetujui dokumennya sendiri (maker-checker).",
                                            meta=("Kotak masuk approval semua jenis dokumen.",
                                                  "Approver mencari dokumen PENDING yang bisa diproses (Bisa Saya Proses? = Y).",
                                                  "Data dari %s_approvals_v; can_act_yn menegakkan role approver dan maker-checker. "
                                                  "Jangan menambah logika approval di halaman." % app.prefix,
                                                  "%s Approval engine: %s_approval_pkg." % (CORE, app.prefix)),
                                            region_meta=("Daftar langkah approval.", "Work queue (Interactive Report).")),
             e2e_title="Approval Inbox")
    can_act = "%s_approval_pkg.can_act_yn(:P191_APPROVAL_ID) = 'Y'" % app.prefix
    m = [("name", "Approval"), ("alias", "APPROVAL"), ("title", "Approval"), ("pageGroup", "@home"),
         *dialog_appearance("modal"), auth("app-users"),
         page_comments("Approve atau reject satu langkah approval.", "Dibuka dari Approval Inbox (190).",
                       "Tombol hanya tampil bila can_act_yn = Y; proses memanggil %s_approval_pkg.approve/reject. "
                       "Catatan wajib saat Reject (dicek di package)." % app.prefix, CORE),
         buttons_region(),
         Comp("region", "approval", ("name", "Approval"), ("type", "form"),
              ("source", G(("location", "localDatabase"), ("tableName", (app.prefix + "_approvals_v").upper()))),
              ("layout", G(("sequence", 10), ("slot", "contentBody"))),
              ("appearance", G(("template", "@/blank-with-attributes"), ("templateOptions", "#DEFAULT#"))))]
    m.append(page_item(191, "APPROVAL_ID", "ID", "hidden", "approval", 5, dtype="number", pk=True))
    for i, (col, lbl, dt) in enumerate([("DOC_NAME", "Jenis Dokumen", "varchar2"), ("DOC_NO", "No. Dokumen", "varchar2"),
                                        ("APPROVAL_LEVEL", "Level", "number"), ("APPROVER_ROLE", "Role Approver", "varchar2"),
                                        ("AMOUNT", "Nilai", "number"), ("REQUESTED_BY", "Diajukan Oleh", "varchar2"),
                                        ("STATUS", "Status", "varchar2"), ("CAN_ACT_YN", "Bisa Saya Proses", "varchar2")], 1):
        m.append(page_item(191, col, lbl, "display", "approval", i * 10, dtype=dt))
    m.append(page_item(191, "NOTE", "Catatan (wajib bila Reject)", "textarea", "approval", 200, maxlen=1000, form=False))
    m += [dialog_button("cancel", "CANCEL", "Close", 10, "close"),
          dialog_button("reject", "REJECT", "Reject", 20, "next", cond=can_act, danger=True, confirm="Tolak dokumen ini?"),
          dialog_button("approve", "APPROVE", "Approve", 30, "next", hot=True, cond=can_act),
          cancel_da(),
          Comp("process", "init-approval-form", ("name", "INIT_APPROVAL_FORM"), ("type", "formInitialization"),
               ("formRegion", "@approval"), ("execution", G(("sequence", 10), ("point", "beforeHeader")))),
          Comp("process", "call-approve", ("name", "CALL_APPROVE"), ("type", "executeCode"),
               ("source", G(("plsqlCode", ML("plsql", "%s_approval_pkg.approve(p_approval_id => :P191_APPROVAL_ID, p_note => :P191_NOTE);" % app.prefix)))),
               ("execution", G(("sequence", 10))), ("successMessage", G(("successMessage", "Dokumen disetujui."))),
               ("serverSideCondition", G(("whenButtonPressed", "@approve")))),
          Comp("process", "call-reject", ("name", "CALL_REJECT"), ("type", "executeCode"),
               ("source", G(("plsqlCode", ML("plsql", "%s_approval_pkg.reject(p_approval_id => :P191_APPROVAL_ID, p_note => :P191_NOTE);" % app.prefix)))),
               ("execution", G(("sequence", 20))), ("successMessage", G(("successMessage", "Dokumen ditolak."))),
               ("serverSideCondition", G(("whenButtonPressed", "@reject")))),
          Comp("process", "close-dialog", ("name", "CLOSE_DIALOG"), ("type", "closeDialog"),
               ("settings", G(("showSuccessMessages", True))), ("execution", G(("sequence", 50))),
               ("serverSideCondition", G(("type", "requestIsContainedInValue"), ("value", "APPROVE,REJECT"))))]
    ctx.page(191, "approval", Comp("page", "191", *m))


def admin_pages(ctx):
    app = ctx.app
    ctx.page(500, "users-roles", ir_page(ctx, 500, "Users & Roles", "users-roles", "administration", "users-roles",
                                         "select user_role_id, username, role_code, role_name, created_by, created_on\n  from %s_user_roles_v" % app.prefix,
                                         [("USER_ROLE_ID", "ID", "hidden"), ("USERNAME", "Username", "text"), ("ROLE_CODE", "Role", "text"),
                                          ("ROLE_NAME", "Nama Role", "text"), ("CREATED_BY", "Dibuat Oleh", "text"), ("CREATED_ON", "Dibuat", "date")],
                                         "admin-rights", form_page=501, pk="USER_ROLE_ID", sort_col="USERNAME",
                                         help_text="Selama belum ada user ber-role ADMIN, semua user dianggap ADMIN (bootstrap).",
                                         meta=("Mengatur role per user APEX.", "Admin mendaftarkan user dan role-nya.",
                                               "Otorisasi dibaca %s_sec_pkg dari %s_user_roles. Bootstrap berakhir saat ADMIN pertama terdaftar."
                                               % (app.prefix, app.prefix), CORE),
                                         region_meta=("Daftar user dan role.", "Admin list (Interactive Report).")))
    _simple_form(ctx, 501, "User Role", "user-role", "administration", "user-role", app.prefix.upper() + "_USER_ROLES",
                 "USER_ROLE_ID", "number",
                 [page_item(501, "USERNAME", "Username (APEX)", "text", "user-role", 10, req=True, maxlen=255,
                            default_sql="select :APP_USER from dual"),
                  page_item(501, "ROLE_CODE", "Role", "select", "user-role", 20, req=True, lov="roles")],
                 ["add", "update", "delete"])
    if app.documents:
        ctx.page(510, "document-types", ir_page(ctx, 510, "Document Types & Approval", "document-types", "administration", "document-types",
                                                "select doc_type, doc_name, prefix, approver1_role, approver2_role, level2_limit\n  from %s_doc_types" % app.prefix,
                                                [("DOC_TYPE", "Kode", "text"), ("DOC_NAME", "Dokumen", "text"), ("PREFIX", "Prefix Nomor", "text"),
                                                 ("APPROVER1_ROLE", "Approver 1", "text"), ("APPROVER2_ROLE", "Approver 2", "text"),
                                                 ("LEVEL2_LIMIT", "Approver 2 bila nilai >", "money")],
                                                "admin-rights", form_page=511, pk="DOC_TYPE", create=False, sort_col="DOC_TYPE",
                                                meta=("Konfigurasi approver dan limit per jenis dokumen.",
                                                      "Admin mengubah approver level 1/2 dan limit level 2 tanpa deploy ulang.",
                                                      "Nilai awal dari document di app.yaml (config seed); perubahan di sini disimpan di %s_doc_types."
                                                      % app.prefix, CORE),
                                                region_meta=("Daftar jenis dokumen.", "Admin list (Interactive Report).")))
        _simple_form(ctx, 511, "Document Type", "document-type", "administration", "document-type", app.prefix.upper() + "_DOC_TYPES",
                     "DOC_TYPE", "varchar2",
                     [page_item(511, "DOC_NAME", "Nama Dokumen", "text", "document-type", 10, req=True, maxlen=100),
                      page_item(511, "PREFIX", "Prefix Nomor", "text", "document-type", 20, req=True, maxlen=10),
                      page_item(511, "APPROVER1_ROLE", "Approver Level 1", "select", "document-type", 30, lov="roles", null_text="- Tanpa approval -"),
                      page_item(511, "APPROVER2_ROLE", "Approver Level 2", "select", "document-type", 40, lov="roles", null_text="- Tidak ada -"),
                      page_item(511, "LEVEL2_LIMIT", "Level 2 bila nilai melebihi", "number", "document-type", 50, dtype="number", req=True, min_=0)],
                     ["update"])


def _simple_form(ctx, num, name, alias_, group, rid, table, pk, pk_dtype, items, ops):
    pk_item = "P%d_%s" % (num, pk)
    comps = [buttons_region(),
             Comp("region", rid, ("name", name), ("type", "form"),
                  ("source", G(("location", "localDatabase"), ("tableName", table))),
                  ("layout", G(("sequence", 10), ("slot", "contentBody"))),
                  ("appearance", G(("template", "@/blank-with-attributes"), ("templateOptions", "#DEFAULT#"))),
                  ("edit", G(("enabled", True), ("allowedOperations", A(ops))))),
             page_item(num, pk, pk, "hidden", rid, 5, dtype=pk_dtype, pk=True)] + items
    requests = []
    comps.append(dialog_button("cancel", "CANCEL", "Cancel", 10, "close"))
    if "delete" in ops:
        comps.append(dialog_button("delete", "DELETE", "Delete", 20, "delete", db_action="delete", cond=":%s is not null" % pk_item,
                                   danger=True, confirm="&APP_TEXT$DELETE_MSG!RAW.", validations=False))
        requests.append("DELETE")
    if "update" in ops:
        comps.append(dialog_button("save", "SAVE", "Apply Changes", 30, "next", hot=True, db_action="update", cond=":%s is not null" % pk_item))
        requests.append("SAVE")
    if "add" in ops:
        comps.append(dialog_button("create", "CREATE", "Create", 40, "next", hot=True, db_action="insert", cond=":%s is null" % pk_item))
        requests.append("CREATE")
    up = rid.upper().replace("-", "_")
    comps += [cancel_da(),
              Comp("process", "init-%s-form" % rid, ("name", "INIT_%s_FORM" % up), ("type", "formInitialization"),
                   ("formRegion", "@" + rid), ("execution", G(("sequence", 10), ("point", "beforeHeader")))),
              Comp("process", "save-%s" % rid, ("name", "SAVE_%s" % up), ("type", "formAutoRowProcessing"),
                   ("formRegion", "@" + rid), ("execution", G(("sequence", 10)))),
              Comp("process", "close-dialog", ("name", "CLOSE_DIALOG"), ("type", "closeDialog"),
                   ("settings", G(("showSuccessMessages", True))), ("execution", G(("sequence", 50))),
                   ("serverSideCondition", G(("type", "requestIsContainedInValue"), ("value", ",".join(requests)))))]
    ctx.page(num, alias_, Comp("page", str(num), ("name", name), ("alias", alias_.upper()), ("title", name), ("pageGroup", "@" + group),
                               *dialog_appearance("modal"), auth("admin-rights"),
                               page_comments("Form admin %s." % name, "Dibuka dari halaman list administrasi.",
                                             "Form tabel langsung; hanya untuk role ADMIN.", CORE), *comps))


# ----------------------------------------------------------------------------- shared components
def sql_lov(ident_, name, sql):
    return Comp("lov", ident_, ("name", name.upper()), ("source", G(("type", "sqlQuery"), ("sqlQuery", ML("sql", sql)))),
                ("columnMapping", G(("return", "R"), ("display", "D"))))


def static_lov(ident_, name, values):
    entries = [Comp("entry", kebab(k) or "v%d" % i, ("sequence", (i + 1) * 10), ("display", v), ("return", k))
               for i, (k, v) in enumerate(values.items())]
    return Comp("lov", ident_, ("name", name.upper()), ("source", G(("location", "staticValues"))), *entries)


def lovs(app):
    out = [static_lov("yes-no", "YES_NO", {"Y": "Ya", "N": "Tidak"}),
           sql_lov("roles", "%s_ROLES" % app.code, "select role_code || ' - ' || role_name d, role_code r\n  from %s_roles\n order by role_code" % app.prefix)]
    for e in app.entities:
        where = []
        if e.has_active:
            where.append("active_yn = 'Y'")
        if e.lov_where:
            where.append(e.lov_where)
        sql = "select %s d, %s r\n  from %s%s\n order by 1" % (e.display, e.pk.lower(), e.table,
                                                               ("\n where " + "\n   and ".join(where)) if where else "")
        out.append(sql_lov(e.lov_name, e.table.upper(), sql))
        for c in e.columns:
            if c.type == "enum":
                out.append(static_lov("%s-%s" % (kebab(e.name), kebab(c.name)), "%s_%s" % (e.name, c.name), c.values))
        if e.document and e.document.operational:
            out.append(static_lov("%s-status" % kebab(e.name), "%s_STATUS" % e.name,
                                  {s: s.replace("_", " ").title() for s in e.document.statuses}))
    return out


def authorizations(app):
    out = [Comp("authorization", "app-users", ("name", "APP_USERS"), ("type", "plSqlFunctionBody"),
                ("settings", G(("plsqlFunctionBody", "return %s_sec_pkg.has_any_role;" % app.prefix))),
                ("error", G(("errorMessage", "Akses ditolak: akun &APP_USER. belum punya role di aplikasi ini. Admin mendaftarkannya di Administration > Users & Roles (atau tabel ..._USER_ROLES)."))))]
    for name, roles in app.authorizations.items():
        if name == "app-users":
            continue
        expr = " or ".join("%s_sec_pkg.has_role('%s')" % (app.prefix, r) for r in roles)
        out.append(Comp("authorization", name, ("name", name.upper().replace("-", "_")), ("type", "plSqlFunctionBody"),
                        ("settings", G(("plsqlFunctionBody", "return %s;" % expr))),
                        ("error", G(("errorMessage", "Akses ditolak: hanya untuk role %s." % "/".join(roles))))))
    return out


def nav_entries(app):
    """(ident, label, icon, page, parent, auth)"""
    nav = [("home", "Home", "fa-home", 100, None, None)]
    if app.documents:
        nav.append(("approval-inbox", "Approval Inbox", "fa-check-square-o", 190, None, None))
    for g, gv in app.groups.items():
        children = [(e.list_alias, e.label_plural, e.icon, e.list_page) for e in app.entities if e.group == g and e.nav]
        children += [(e.workspace["alias"], e.workspace["label"], e.workspace["icon"], e.workspace["page"])
                     for e in app.entities if e.group == g and e.workspace]
        children += [(r.alias, r.title, r.icon, r.page) for r in app.reports if r.group == g]
        children.sort(key=lambda x: x[3])
        if not children:
            continue
        nav.append(("grp-" + g, gv["name"], gv["icon"], children[0][3], None, None))
        nav += [(a, l, i, p, "grp-" + g, None) for a, l, i, p in children]
    nav.append(("grp-administration", "Administration", "fa-gear", 500, None, "admin-rights"))
    nav.append(("users-roles", "Users & Roles", "fa-user-secret", 500, "grp-administration", "admin-rights"))
    if app.documents:
        nav.append(("document-types", "Document Types & Approval", "fa-sliders", 510, "grp-administration", "admin-rights"))
    return nav


def nav_menu(app):
    entries = []
    for i, (ident_, label, icon, page, parent, au) in enumerate(nav_entries(app)):
        m = [("label", label), ("icon", G(("imageIconCssClasses", icon))),
             ("layout", G(("sequence", (i + 1) * 10), ("parentEntry", "@" + parent) if parent else None)),
             ("link", G(("target", O(("page", page)))))]
        if au:
            m.append(("security", G(("authorizationScheme", "@" + au))))
        entries.append(Comp("entry", ident_, *m))
    return Comp("list", "navigation-menu", ("name", "Navigation Menu"), *entries)


def nav_bar():
    return Comp("list", "navigation-bar", ("name", "Navigation Bar"),
                Comp("entry", "---", ("label", "---"), ("layout", G(("sequence", 20), ("parentEntry", "@app-user"))),
                     ("link", G(("target", O(("type", "url"), ("url", "separator"))))),
                     ("serverSideCondition", G(("type", "userIsAuthenticated")))),
                Comp("entry", "app-user", ("label", "&APP_USER."), ("icon", G(("imageIconCssClasses", "fa-user"))),
                     ("layout", G(("sequence", 10))), ("link", G(("target", O(("type", "url"), ("url", "#"))))),
                     ("userDefinedAttributes", G(("2", "has-username")))),
                Comp("entry", "sign-out", ("label", "Sign Out"), ("icon", G(("imageIconCssClasses", "fa-sign-out"))),
                     ("layout", G(("sequence", 30), ("parentEntry", "@app-user"))),
                     ("link", G(("target", O(("type", "url"), ("url", "&LOGOUT_URL."))))),
                     ("serverSideCondition", G(("type", "userIsAuthenticated")))))


def breadcrumbs(app):
    entries = [Comp("entry", "home", ("name", "Home"), ("pageNumber", 100), ("execution", G(("sequence", 10))),
                    ("link", G(("target", O(("page", 100))))))]
    seen, seq = {100}, 20
    for ident_, label, _i, page, parent, _a in nav_entries(app):
        if page in seen or ident_.startswith("grp-"):
            continue
        seen.add(page)
        entries.append(Comp("entry", ident_, ("name", label), ("pageNumber", page), ("execution", G(("sequence", seq))),
                            ("appearance", G(("parentEntry", "@home"))), ("link", G(("target", O(("page", page)))))))
        seq += 10
    return Comp("breadcrumb", "breadcrumb", ("name", "Breadcrumb"), *entries)


def application(app):
    return Comp("app", app.alias,
                ("name", app.name),
                ("logo", G(("type", "text"), ("text", app.logo))),
                ("navigation", G(("homeUrl", O(("page", 100))), ("loginUrl", O(("page", "LOGIN"))))),
                ("navigationMenu", G(("listTemplate", "@/side-navigation-menu"),
                                     ("templateOptions", A(["#DEFAULT#", "t-TreeNav--styleA", "js-navCollapsed--hidden"])),
                                     ("list", "@navigation-menu"))),
                ("navigationBar", G(("list", "@navigation-bar"), ("listTemplate", "@/navigation-bar"), ("templateOptions", "#DEFAULT#"))),
                ("userInterface", G(("currentTheme", "@universal-theme"), ("globalPage", 0), ("addBuiltWithApexToFooter", False))),
                ("appFormatMasks", G(("date", "DD-MON-YYYY"), ("timestamp", "DS"), ("timestampTimeZone", "DS"))),
                ("javaScript", G(("fileUrls", "#APP_FILES#js/nav-fix.js"))) if app.nav_fix else None,
                ("authentication", G(("scheme", "@oracle-apex-accounts"))),
                ("authorization", G(("scheme", "@app-users"))),
                ("runtime", G(("allowFeedback", False))))


def page_groups(app):
    groups = [("home", "Home")] + [(g, v["name"]) for g, v in app.groups.items()] + [("administration", "Administration")]
    return render(*[Comp("pageGroup", g, ("name", n)) for g, n in groups])


def generate(app):
    ctx = Ctx(app)
    ctx.put("application.apx", render(application(app)))
    ctx.put("page-groups.apx", page_groups(app))
    ctx.put("shared-components/authorizations.apx", render(*authorizations(app)))
    ctx.put("shared-components/lists/lists.apx", render(nav_bar(), nav_menu(app)))
    ctx.put("shared-components/lovs/lovs.apx", render(*lovs(app)))
    ctx.put("shared-components/breadcrumbs/breadcrumbs.apx", render(breadcrumbs(app)))
    ctx.put("supporting-objects/supporting-objects.apx",
            render(Comp("supportingObject", None, ("advanced", G(("includeInAppExport", False))))))
    home_page(ctx)
    if app.documents:
        approval_pages(ctx)
    for e in app.entities:
        entity_list_page(ctx, e)
        entity_form_page(ctx, e)
        if e.workspace:
            workspace_page(ctx, e)
    for r in app.reports:
        report_page(ctx, r)
    admin_pages(ctx)
    return ctx
