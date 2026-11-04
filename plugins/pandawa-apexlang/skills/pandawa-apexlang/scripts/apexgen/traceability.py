"""Matriks traceability: REQ-ID di FRS -> app.yaml, halaman, SQL custom, halaman manual, test.

Sumber:
  - FRS (docs/02-frs.md): baris tabel '| REQ-x.y | teks |'
  - app.yaml: field req: (app, entitas, kolom, validasi, dokumen, laporan, KPI, chart)
  - teks REQ-x.y di database/custom/, apex-custom/ (realisasi) dan tests/ (verifikasi)
"""
import os

from spec import REQ_RE

REALIZE_DIRS = [("database/custom", (".sql",)), ("apex-custom", (".apx",))]
VERIFY_DIRS = [("tests/db", (".sql",)), ("tests/e2e/tests", (".ts",))]


def _scan(root, dirs):
    """{req: [path relatif]} dari file yang menyebut REQ-ID."""
    hits = {}
    for d, exts in dirs:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dp, _dn, fns in os.walk(base):
            for fn in sorted(fns):
                if not fn.endswith(exts):
                    continue
                full = os.path.join(dp, fn)
                with open(full, encoding="utf-8", errors="replace") as f:
                    found = set(REQ_RE.findall(f.read()))
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                for r in found:
                    hits.setdefault(r, []).append(rel)
    return hits


def _key(req):
    return [int(p) if p.isdigit() else p for p in req[4:].replace("-", ".").split(".")]


def build(app):
    """Markdown traceability, atau None bila FRS tidak punya REQ-ID."""
    if not app.frs:
        return None
    root = app.base_dir
    spec_rows = {}
    for r, where, pages in app.trace():
        spec_rows.setdefault(r, []).append((where, pages))
    realize = _scan(root, REALIZE_DIRS)
    verify = _scan(root, VERIFY_DIRS)
    ids = sorted(set(app.frs) | set(realize) | set(verify), key=_key)
    lines = ["# Traceability requirement (GENERATED)", "",
             "Dibuat oleh generator dari `%s`, `app.yaml` (field `req:`), `database/custom/`, `apex-custom/`, dan `tests/`. "
             "Jangan edit manual; jalankan `scripts/generate.sh`." % os.path.relpath(app.frs_path, root).replace(os.sep, "/"), "",
             "Status: **OK** = ada realisasi dan test; **Belum diuji** = ada realisasi tanpa test; "
             "**Belum direalisasi** = belum dirujuk di spec/custom; **Tidak di FRS** = ID dirujuk tapi tidak didefinisikan di FRS.", "",
             "| REQ | Requirement | app.yaml | Halaman | Realisasi lain | Test | Status |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    counts = {}
    for r in ids:
        specs = spec_rows.get(r, [])
        pages = sorted({p for _, ps in specs for p in ps})
        real = realize.get(r, [])
        tests = verify.get(r, [])
        if r not in app.frs:
            status = "Tidak di FRS"
        elif (specs or real) and tests:
            status = "OK"
        elif specs or real:
            status = "Belum diuji"
        else:
            status = "Belum direalisasi"
        counts[status] = counts.get(status, 0) + 1
        text = app.frs.get(r, "").replace("|", "\\|")
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r, text,
            "<br>".join("`%s`" % w for w, _ in specs) or "-",
            ", ".join(str(p) for p in pages) or "-",
            "<br>".join("`%s`" % f for f in real) or "-",
            "<br>".join("`%s`" % f for f in tests) or "-",
            status))
    summary = ", ".join("%s: %d" % (k, counts[k]) for k in ("OK", "Belum diuji", "Belum direalisasi", "Tidak di FRS") if k in counts)
    lines[4:4] = ["Ringkasan: %d requirement. %s." % (len(ids), summary), ""]
    return "\n".join(lines) + "\n"
