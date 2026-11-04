"""Load, validate, and normalise an app.yaml spec (Pandawa APEXlang generator).

The spec format is documented in references/app-spec.md. Everything the
generators need is resolved here, so gen_sql.py and gen_apex.py never have
to guess defaults.
"""
import difflib
import os
import re

import yaml

STATUS_BASE = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "CANCELLED"]
COLUMN_TYPES = {"text", "code", "textarea", "number", "int", "money", "qty", "pct",
                "date", "yn", "enum", "ref"}


FORM_STYLES = ("modal", "drawer")
LIST_TYPES = ("ir", "faceted-cards", "faceted-report")
# semantic kolom text: ukuran default, pola (check constraint + validasi halaman), subtype item, normalisasi
SEMANTICS = {
    "email": {"size": 255, "subtype": "email", "case": "lower",
              "regex": r"^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$",
              "msg": "Format email tidak valid (contoh: nama@domain.co.id)."},
    "phone": {"size": 30, "subtype": "phone",
              "regex": r"^\+?[0-9(][0-9 ().-]{5,29}$",
              "msg": "Nomor telepon hanya boleh berisi angka, spasi, +, -, titik, dan tanda kurung (min. 6 karakter)."},
    "url": {"size": 500, "subtype": "url",
            "regex": r"^https?://[^[:space:]]+$",
            "msg": "URL harus diawali http:// atau https://."},
    "npwp": {"size": 20,
             "regex": r"^([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}\.?[0-9]-?[0-9]{3}\.?[0-9]{3}|[0-9]{16})$",
             "msg": "NPWP harus 15 digit (format 99.999.999.9-999.999) atau 16 digit."},
}
REQ_RE = re.compile(r"\bREQ-\d+(?:\.\d+)*[a-z]?\b")
ICON_ALLOWLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "apex-fa-icons-allowlist.txt")
_icons = None


class SpecError(Exception):
    pass


def _err(msg):
    raise SpecError(msg)


def icons():
    """Font APEX icon allowlist (oracle/apex blueprints, APEX 26.2)."""
    global _icons
    if _icons is None:
        with open(ICON_ALLOWLIST, encoding="utf-8") as f:
            _icons = {l.strip() for l in f if l.strip() and not l.startswith("#")}
    return _icons


def check_icon(icon, where):
    """The first class must be a Font APEX icon; modifiers (fa-lg, u-...) may follow."""
    first = str(icon).split()[0] if str(icon).strip() else ""
    if first not in icons():
        near = difflib.get_close_matches(first, sorted(icons()), n=3)
        _err("%s: icon %r tidak ada di Font APEX%s" % (where, first, " (mungkin: %s)" % ", ".join(near) if near else ""))


def reqs(raw, where):
    """Field req: (string atau list) -> list REQ-ID."""
    v = (raw or {}).get("req") if isinstance(raw, dict) else None
    if v is None:
        return []
    items = [v] if isinstance(v, str) else list(v)
    out = []
    for r in items:
        r = str(r).strip()
        if not REQ_RE.fullmatch(r):
            _err("%s: req %r bukan format REQ-<n>[.<n>] (mis. REQ-5.2)" % (where, r))
        out.append(r)
    return out


def parse_frs(path):
    """REQ-ID yang didefinisikan di FRS: baris tabel yang diawali '| REQ-x.y |'. -> {id: teks}."""
    found = {}
    if not os.path.isfile(path):
        return found
    with open(path, encoding="utf-8") as f:
        for line in f:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and REQ_RE.fullmatch(cells[0]):
                found[cells[0]] = cells[1]
    return found


def kebab(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def ident(s):
    return re.sub(r"[^A-Z0-9_]", "_", s.upper())


class Column:
    def __init__(self, raw, entity):
        self.raw = raw
        self.name = ident(raw.get("name") or _err("%s: column without name" % entity.name))
        self.type = raw.get("type", "text")
        if self.type not in COLUMN_TYPES:
            _err("%s.%s: unknown type %r (allowed: %s)" % (entity.name, self.name, self.type, ", ".join(sorted(COLUMN_TYPES))))
        self.label = raw.get("label", self.name.replace("_", " ").title())
        self.required = bool(raw.get("required", False))
        self.unique = bool(raw.get("unique", False))
        self.default = raw.get("default")
        self.default_sql = raw.get("default_sql")          # SQL query returning one value (form default)
        self.size = raw.get("size")
        self.list = raw.get("list", True)                  # show in list IR
        self.form = raw.get("form", "edit")                # edit | display | hidden | none
        if self.form is True:
            self.form = "edit"
        if self.form is False:
            self.form = "none"
        self.help = raw.get("help")
        self.virtual = raw.get("virtual")                  # SQL expression -> virtual column
        self.values = raw.get("values")                    # enum values: list or {CODE: label}
        self.ref = raw.get("ref")                          # entity name for type: ref
        self.lov_sql = raw.get("lov_sql")                  # override LOV (select d, r ...)
        self.cascade = raw.get("cascade")                  # parent item column for cascading LOV
        self.readonly_when = raw.get("readonly_when")      # PL/SQL expression
        self.on_delete = raw.get("on_delete")              # cascade | None (for ref)
        self.min = raw.get("min")
        self.max = raw.get("max")
        self.req = reqs(raw, "%s.%s" % (entity.name, self.name))
        # semantic: email | phone | url | npwp (hanya type text/code)
        self.semantic = raw.get("semantic")
        if self.semantic:
            if self.semantic not in SEMANTICS:
                _err("%s.%s: semantic harus %s" % (entity.name, self.name, " | ".join(SEMANTICS)))
            if self.type not in ("text", "code"):
                _err("%s.%s: semantic %s hanya untuk type text/code" % (entity.name, self.name, self.semantic))
            if self.size is None:
                self.size = SEMANTICS[self.semantic]["size"]
        # facet di halaman faceted search (default: enum, yn, ref)
        self.facet = bool(raw.get("facet", self.type in ("enum", "yn", "ref")))
        if self.virtual:
            self.form = "display" if self.form == "edit" else self.form
            self.required = False
        if self.type == "enum":
            if not self.values:
                _err("%s.%s: enum needs values" % (entity.name, self.name))
            if isinstance(self.values, list):
                self.values = {str(v): str(v).replace("_", " ").title() for v in self.values}
            else:
                self.values = {str(k): str(v) for k, v in self.values.items()}
        if self.type == "ref" and not self.ref:
            _err("%s.%s: type ref needs ref: <ENTITY>" % (entity.name, self.name))
        if self.type == "yn" and self.default is None:
            self.default = "Y"

    @property
    def sql_type(self):
        t = self.type
        if t == "text":
            return "varchar2(%d)" % (self.size or 200)
        if t == "code":
            return "varchar2(%d)" % (self.size or 30)
        if t == "textarea":
            return "varchar2(%d)" % (self.size or 1000)
        if t in ("number", "money", "qty", "pct", "ref"):
            return "number"
        if t == "int":
            return "number(10)"
        if t == "date":
            return "date"
        if t == "yn":
            return "varchar2(1)"
        if t == "enum":
            return "varchar2(%d)" % max(20, max(len(k) for k in self.values))
        _err("type %s" % t)

    @property
    def sem(self):
        return SEMANTICS.get(self.semantic) if self.semantic else None

    @property
    def apex_dtype(self):
        return {"date": "date"}.get(self.type, "number" if self.sql_type.startswith("number") else "varchar2")

    @property
    def maxlen(self):
        m = re.match(r"varchar2\((\d+)\)", self.sql_type)
        return int(m.group(1)) if m else None


class Document:
    def __init__(self, raw, entity):
        self.type = ident(raw.get("type") or _err("%s.document: type required" % entity.name))
        self.name = raw.get("name", entity.label)
        self.prefix = raw.get("prefix", self.type)
        self.number = ident(raw.get("number", self.type + "_NO"))
        self.amount = raw.get("amount", "0")              # SQL expr over alias t (or scalar subquery)
        self.approver1 = raw.get("approver1")
        self.approver2 = raw.get("approver2")
        self.level2_limit = raw.get("level2_limit", 0)
        self.validate = raw.get("validate")                # pkg.proc(p_doc_id in number)
        self.operational = [ident(s) for s in raw.get("operational", [])]
        self.lock = [ident(c) for c in raw.get("lock", [])]  # columns frozen after approval
        self.statuses = STATUS_BASE + [s for s in self.operational if s not in STATUS_BASE]
        self.req = reqs(raw, "%s.document" % entity.name)


class Entity:
    def __init__(self, raw, app):
        self.raw = raw
        self.name = ident(raw.get("name") or _err("entity without name"))
        self.table = "%s_%s" % (app.prefix, self.name.lower())
        self.label = raw.get("label", self.name.replace("_", " ").title())
        self.label_plural = raw.get("label_plural", self.label + "s")
        self.pk = ident(raw.get("pk") or _err("%s: pk required (e.g. CUSTOMER_ID)" % self.name))
        self.group = raw.get("group") or _err("%s: group required" % self.name)
        pages = raw.get("pages") or _err("%s: pages [list, form] required" % self.name)
        if len(pages) != 2:
            _err("%s: pages must be [list_page, form_page]" % self.name)
        self.list_page, self.form_page = int(pages[0]), int(pages[1])
        self.list_alias = raw.get("list_alias", kebab(self.label_plural))
        self.form_alias = raw.get("form_alias", kebab(self.label))
        self.icon = raw.get("icon", "fa-table")
        self.auth = raw.get("auth", "app-users")           # form + create
        self.view_auth = raw.get("view_auth", "app-users") # list page
        self.display = raw.get("display")                  # LOV display expression
        self.lov_where = raw.get("lov_where")
        self.operations = raw.get("operations", ["add", "update", "delete"])
        self.immutable = bool(raw.get("immutable", False)) # block update/delete in DB
        self.nav = raw.get("nav", True)
        self.help = raw.get("help")
        self.purpose = raw.get("purpose")                  # 1 kalimat tujuan bisnis (metadata AI di comments)
        self.validations = raw.get("validations", [])
        self.req = reqs(raw, self.name)
        for i, v in enumerate(self.validations, 1):
            v["req"] = reqs(v, "%s.validations[%d]" % (self.name, i))
        self.columns = [Column(c, self) for c in raw.get("columns", [])]
        names = [c.name for c in self.columns]
        if len(set(names)) != len(names):
            _err("%s: duplicate column names" % self.name)
        self.document = Document(raw["document"], self) if raw.get("document") else None
        p = raw.get("parent")
        self.parent = None
        if p:
            self.parent = {"entity": ident(p["entity"]), "column": ident(p["column"]),
                           "lock_unless": [ident(s) for s in p.get("lock_unless", ["DRAFT", "REJECTED"])]}
        # drawer: form pendek di panel samping; modal: dokumen/form panjang (UX Pattern Catalog p420)
        self.form_style = raw.get("form_style", "modal" if self.document else "drawer")
        if self.form_style not in FORM_STYLES:
            _err("%s: form_style harus %s" % (self.name, " | ".join(FORM_STYLES)))
        # ir: Interactive Report; faceted-*: faceted search (UX Pattern Catalog p210/p220)
        self.list_type = raw.get("list_type", "ir")
        if self.list_type not in LIST_TYPES:
            _err("%s: list_type harus %s" % (self.name, " | ".join(LIST_TYPES)))
        # workspace: halaman master-detail (daftar induk kiri, header + detail kanan)
        w = raw.get("workspace")
        self.workspace = None
        if w:
            w = {"page": w} if isinstance(w, int) else dict(w)
            if not w.get("page"):
                _err("%s.workspace: page wajib" % self.name)
            self.workspace = {"page": int(w["page"]),
                              "label": w.get("label", "Detail " + self.label_plural),
                              "alias": w.get("alias", kebab(self.label_plural) + "-detail"),
                              "icon": w.get("icon", "fa-columns")}
        if not self.display:
            first = next((c for c in self.columns if c.type in ("code", "text")), None)
            self.display = first.name.lower() if first else self.pk.lower()

    def col(self, name):
        for c in self.columns:
            if c.name == name:
                return c
        return None

    @property
    def has_active(self):
        c = self.col("ACTIVE_YN")
        return c is not None and c.type == "yn"

    @property
    def lov_name(self):
        return kebab(self.name)


class Report:
    def __init__(self, raw, app):
        self.page = int(raw.get("page") or _err("report: page required"))
        self.title = raw.get("title") or _err("report %d: title required" % self.page)
        self.alias = raw.get("alias", kebab(self.title))
        self.group = raw.get("group") or _err("report %s: group required" % self.title)
        view = ident(raw.get("view") or _err("report %s: view required" % self.title))
        self.view = view.lower() if view.lower().startswith(app.prefix) else "%s_%s" % (app.prefix, view.lower())
        self.auth = raw.get("auth", "app-users")
        self.icon = raw.get("icon", "fa-bar-chart")
        self.help = raw.get("help")
        self.sort = raw.get("sort")
        self.req = reqs(raw, "report %s" % self.title)
        self.columns = []
        for c in raw.get("columns") or _err("report %s: columns required" % self.title):
            self.columns.append({"name": ident(c["name"]), "label": c.get("label", c["name"].replace("_", " ").title()),
                                 "type": c.get("type", "text")})


class App:
    def __init__(self, raw, base_dir):
        a = raw.get("app") or _err("app: section required")
        self.code = ident(a.get("code") or _err("app.code required"))
        if not re.match(r"^[A-Z][A-Z0-9]{1,9}$", self.code):
            _err("app.code must be 2-10 chars A-Z0-9 (Pandawa: APX_<CODE>_...)")
        self.prefix = "apx_%s" % self.code.lower()
        self.name = a.get("name", self.code)
        self.alias = ident(a.get("alias", self.code)).replace("_", "-")
        self.logo = a.get("logo", self.code)
        self.author = a.get("author", "Tim PANDAWA")
        self.date = str(a.get("date", "lihat git log"))  # tanggal di header script (deterministik)
        self.description = a.get("description", self.name)
        self.nav_fix = a.get("nav_fix", True)
        self.advice_on = a.get("advice", True)              # SARAN pola halaman saat generate
        self.req = reqs(a, "app")
        self.frs_path = os.path.join(base_dir, a.get("frs", "docs/02-frs.md"))
        self.base_dir = base_dir
        self.roles = {ident(k): v for k, v in (raw.get("roles") or {}).items()}
        self.roles.setdefault("ADMIN", "Administrator")
        self.authorizations = {"app-users": None, "admin-rights": ["ADMIN"]}
        for k, v in (raw.get("authorizations") or {}).items():
            roles = [ident(r) for r in v]
            for r in roles:
                if r not in self.roles:
                    _err("authorization %s: unknown role %s" % (k, r))
            self.authorizations[kebab(k)] = roles
        self.groups = {}
        for k, v in (raw.get("groups") or {}).items():
            v = v or {}
            self.groups[kebab(k)] = {"name": v.get("name", k.replace("-", " ").title()), "icon": v.get("icon", "fa-folder")}
        self.entities = [Entity(e, self) for e in raw.get("entities", [])]
        self.reports = [Report(r, self) for r in raw.get("reports", [])]
        self.dashboard = raw.get("dashboard") or {}
        for i, k in enumerate(self.dashboard.get("kpis", []), 1):
            if not k.get("label") or not k.get("sql"):
                _err("dashboard.kpis[%d]: label dan sql wajib" % i)
            k.setdefault("icon", "fa-dashboard")
            k["req"] = reqs(k, "dashboard.kpis[%d]" % i)
        for i, c in enumerate(self.dashboard.get("charts", []), 1):
            c["req"] = reqs(c, "dashboard.charts[%d]" % i)
        self.users = raw.get("users", [])
        self.custom_sql = raw.get("custom_sql", [])
        self.seed_sql = raw.get("seed_sql", [])
        self.validate()

    def entity(self, name):
        for e in self.entities:
            if e.name == ident(name):
                return e
        _err("unknown entity %s" % name)

    def advice(self):
        """Saran pola halaman (tidak menggagalkan generate). Aturan: references/page-patterns.md."""
        if not self.advice_on:
            return []
        out = []
        sem_hint = {"EMAIL": "email", "PHONE": "phone", "TELP": "phone", "HP": "phone", "NPWP": "npwp",
                    "URL": "url", "WEBSITE": "url"}
        for e in self.entities:
            facetable = [c for c in e.columns if c.facet and not c.virtual]
            editable = [c for c in e.columns if c.form == "edit" and not c.virtual]
            if e.list_type != "ir" and not facetable and not e.document:
                out.append("%s: list_type %s tanpa kolom facet (hanya pencarian). Pakai list_type: ir, "
                           "atau tandai kolom dengan facet: true." % (e.name, e.list_type))
            if e.list_type == "ir" and not e.document and not e.parent and len(facetable) >= 2:
                txn = e.immutable or any(c.type == "date" for c in e.columns)
                out.append("%s: %s dengan %d kolom facet (%s); pertimbangkan list_type: %s."
                           % (e.name, "data transaksi" if txn else "master data", len(facetable),
                              ", ".join(c.name for c in facetable), "faceted-report" if txn else "faceted-cards"))
            if e.form_style == "drawer" and (len(editable) > 8 or any(c.type == "textarea" for c in editable)):
                out.append("%s: form drawer dengan %d field%s; form panjang lebih nyaman dengan form_style: modal."
                           % (e.name, len(editable), " termasuk textarea" if any(c.type == "textarea" for c in editable) else ""))
            if e.document and self.children(e) and not e.workspace:
                out.append("%s: dokumen dengan baris detail (%s); pertimbangkan workspace: {page: ...} (master-detail)."
                           % (e.name, ", ".join(c.name for c in self.children(e))))
            for c in e.columns:
                if c.type in ("text", "code") and not c.semantic:
                    hit = next((v for k, v in sem_hint.items() if k in c.name.split("_")), None)
                    if hit:
                        out.append("%s.%s: tambahkan semantic: %s (validasi format + jenis input)." % (e.name, c.name, hit))
        n = len(self.dashboard.get("kpis", []))
        if n > 4:
            out.append("dashboard: %d KPI; metric card paling efektif 2-4 KPI. Pindahkan sisanya ke laporan "
                       "atau buat dashboard advanced manual (references/ux-patterns p00120)." % n)
        return out

    def entity_reqs(self, e):
        """Semua REQ-ID entitas: entitas, kolom, validasi, dokumen (urut, unik)."""
        out = list(e.req)
        for c in e.columns:
            out += c.req
        for v in e.validations:
            out += v["req"]
        if e.document:
            out += e.document.req
        return list(dict.fromkeys(out))

    def trace(self):
        """[(req, lokasi di app.yaml, [halaman])] untuk matriks traceability."""
        rows = [(r, "app", []) for r in self.req]
        for e in self.entities:
            pages = [e.list_page, e.form_page] + ([e.workspace["page"]] if e.workspace else [])
            rows += [(r, "entities.%s" % e.name, pages) for r in e.req]
            for c in e.columns:
                rows += [(r, "entities.%s.columns.%s" % (e.name, c.name), [e.list_page, e.form_page]) for r in c.req]
            for i, v in enumerate(e.validations, 1):
                rows += [(r, "entities.%s.validations.%s" % (e.name, v.get("name", i)), [e.form_page]) for r in v["req"]]
            if e.document:
                rows += [(r, "entities.%s.document" % e.name, [e.form_page, 190, 191]) for r in e.document.req]
        for r in self.reports:
            rows += [(q, "reports.%s" % r.alias, [r.page]) for q in r.req]
        for i, k in enumerate(self.dashboard.get("kpis", []), 1):
            rows += [(q, "dashboard.kpis.%s" % k["label"], [100]) for q in k["req"]]
        for i, c in enumerate(self.dashboard.get("charts", []), 1):
            rows += [(q, "dashboard.charts.%s" % c.get("title", i), [100]) for q in c["req"]]
        return rows

    def children(self, e):
        return [c for c in self.entities if c.parent and c.parent["entity"] == e.name]

    @property
    def documents(self):
        return [e for e in self.entities if e.document]

    def validate(self):
        pages = {100: "home", 190: "approval inbox", 191: "approval", 500: "users & roles", 501: "user role",
                 510: "document types", 511: "document type", 9999: "login", 0: "global"}
        aliases = {"home", "approval-inbox", "approval", "users-roles", "user-role", "document-types", "document-type", "login"}

        def take(no, what):
            if no in pages:
                _err("page %d used twice (%s and %s)" % (no, pages[no], what))
            pages[no] = what

        def take_alias(a, what):
            if a in aliases:
                _err("page alias %r used twice (%s)" % (a, what))
            aliases.add(a)

        for g, v in self.groups.items():
            check_icon(v["icon"], "groups.%s" % g)
        for i, k in enumerate(self.dashboard.get("kpis", []), 1):
            check_icon(k["icon"], "dashboard.kpis[%d] %s" % (i, k["label"]))
        for e in self.entities:
            check_icon(e.icon, e.name)
            take(e.list_page, e.name)
            take(e.form_page, e.name)
            take_alias(e.list_alias, e.name)
            take_alias(e.form_alias, e.name)
            for g in (e.group,):
                if g not in self.groups:
                    _err("%s: unknown group %s" % (e.name, g))
            for a in (e.auth, e.view_auth):
                if kebab(a) not in self.authorizations:
                    _err("%s: unknown authorization %s" % (e.name, a))
            for c in e.columns:
                if c.type == "ref":
                    self.entity(c.ref)
            if e.workspace:
                take(e.workspace["page"], e.name + " workspace")
                take_alias(e.workspace["alias"], e.name + " workspace")
                check_icon(e.workspace["icon"], e.name + ".workspace")
                if not self.children(e):
                    _err("%s.workspace: tidak ada entitas dengan parent: {entity: %s}" % (e.name, e.name))
            if e.parent:
                self.entity(e.parent["entity"])
                if not e.col(e.parent["column"]):
                    _err("%s.parent.column %s not a column" % (e.name, e.parent["column"]))
            if e.document:
                d = e.document
                for r in (d.approver1, d.approver2):
                    if r and ident(r) not in self.roles:
                        _err("%s.document: unknown role %s" % (e.name, r))
                for c in d.lock:
                    if not e.col(c):
                        _err("%s.document.lock: unknown column %s" % (e.name, c))
        for r in self.reports:
            take(r.page, r.title)
            take_alias(r.alias, r.title)
            check_icon(r.icon, "report %s" % r.title)
            if r.group not in self.groups:
                _err("report %s: unknown group %s" % (r.title, r.group))
        types = [d.document.type for d in self.documents]
        if len(set(types)) != len(types):
            _err("document types must be unique")
        self.frs = parse_frs(self.frs_path)
        if self.frs:
            unknown = sorted({r for r, _, _ in self.trace()} - set(self.frs))
            if unknown:
                _err("req tidak ada di %s: %s" % (os.path.relpath(self.frs_path, self.base_dir), ", ".join(unknown)))
        for f in self.custom_sql + self.seed_sql:
            if not os.path.isfile(os.path.join(self.base_dir, f)):
                _err("file not found: %s" % f)


def load(path):
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return App(raw, os.path.dirname(os.path.abspath(path)))
