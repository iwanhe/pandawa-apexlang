"""Load, validate, and normalise an app.yaml spec (Pandawa APEXlang generator).

The spec format is documented in references/app-spec.md. Everything the
generators need is resolved here, so gen_sql.py and gen_apex.py never have
to guess defaults.
"""
import os
import re

import yaml

STATUS_BASE = ["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "CANCELLED"]
COLUMN_TYPES = {"text", "code", "textarea", "number", "int", "money", "qty", "pct",
                "date", "yn", "enum", "ref"}


class SpecError(Exception):
    pass


def _err(msg):
    raise SpecError(msg)


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
        self.validations = raw.get("validations", [])
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
        self.users = raw.get("users", [])
        self.custom_sql = raw.get("custom_sql", [])
        self.seed_sql = raw.get("seed_sql", [])
        self.validate()

    def entity(self, name):
        for e in self.entities:
            if e.name == ident(name):
                return e
        _err("unknown entity %s" % name)

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

        for e in self.entities:
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
            if r.group not in self.groups:
                _err("report %s: unknown group %s" % (r.title, r.group))
        types = [d.document.type for d in self.documents]
        if len(set(types)) != len(types):
            _err("document types must be unique")
        for f in self.custom_sql + self.seed_sql:
            if not os.path.isfile(os.path.join(self.base_dir, f)):
                _err("file not found: %s" % f)


def load(path):
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return App(raw, os.path.dirname(os.path.abspath(path)))
