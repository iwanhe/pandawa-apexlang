#!/usr/bin/env python3
"""Pandawa APEXlang generator: app.yaml -> database scripts + APEXlang app + E2E config + zip.

    python3 generate.py path/to/app.yaml [--no-zip]

Output (relatif terhadap folder app.yaml):
    database/generated/*.sql        DDL, core packages, trigger, view, config seed, deinstall
    database/install.sql            gabungan generated + custom_sql + config + seed_sql
    database/admin/create_users.sql akun workspace + role (dari users: di app.yaml)
    database/admin/remove_users.sql
    apex/<alias>/                   source APEXlang (APEX 26.2)
    dist/<alias>-apexlang.zip       siap App Builder > Import
    tests/e2e/pages.json            daftar halaman untuk smoke test Playwright
    docs/traceability.md            matriks REQ-ID FRS -> spec/halaman/SQL/test (bila docs/02-frs.md punya REQ-ID)

Halaman/komponen manual: taruh di apex-custom/ (struktur sama dengan apex/<alias>/).
Isinya disalin di atas hasil generate, jadi tidak hilang saat generate ulang.
"""
import re
import argparse
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_apex  # noqa: E402
import gen_sql  # noqa: E402
import spec as specmod  # noqa: E402
import traceability  # noqa: E402

BASE = os.path.join(HERE, "..", "..", "assets", "apex-base")


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def build_apex(app, root):
    out = os.path.join(root, "apex", app.alias.lower())
    if os.path.isdir(out):
        shutil.rmtree(out)
    shutil.copytree(BASE, out, ignore=shutil.ignore_patterns("LICENSE-*"))
    sf = os.path.join(out, "shared-components", "static-files.apx")
    if app.nav_fix:
        with open(sf, "a", encoding="utf-8") as f:
            f.write('\nfile "js/nav-fix.js" (\n    mimeType: text/javascript\n    charSet: utf-8\n)\n')
    else:
        os.remove(os.path.join(out, "shared-components", "static-files", "js", "nav-fix.js"))
    ctx = gen_apex.generate(app)
    for rel, content in ctx.files.items():
        write(os.path.join(out, rel), content)
    overlay_custom(app, root, out, ctx)
    return out, ctx


def overlay_custom(app, root, out, ctx):
    """Salin apex-custom/ ke atas hasil generate; halaman manual ikut ke pages.json (E2E)."""
    src = os.path.join(root, "apex-custom")
    if not os.path.isdir(src):
        return
    generated = {int(p["no"]) for p in ctx.e2e_pages}
    for dp, _dn, fns in os.walk(src):
        for fn in sorted(fns):
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, src)
            dst = os.path.join(out, rel)
            if os.path.exists(dst):
                print("PERINGATAN: apex-custom/%s menimpa file hasil generate" % rel, file=sys.stderr)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(full, dst)
            m = re.match(r"pages/p(\d+)-.*\.apx$", rel.replace(os.sep, "/"))
            if m and int(m.group(1)) not in (0, 9999):
                with open(full, encoding="utf-8") as f:
                    txt = f.read()
                no = int(m.group(1))
                alias = re.search(r"^\s+alias: (\S+)", txt, re.M)
                name = re.search(r"^\s+name: (.+)$", txt, re.M)
                modal = re.search(r"pageMode: modalDialog", txt)
                if alias and name and not modal and no not in generated:
                    ctx.e2e_pages.append({"alias": alias.group(1).lower(), "no": no, "title": name.group(1).strip()})


def zip_dir(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        os.remove(dst)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _dn, fns in os.walk(src):
            for fn in sorted(fns):
                full = os.path.join(dp, fn)
                z.write(full, os.path.relpath(full, src))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path ke app.yaml")
    ap.add_argument("--no-zip", action="store_true", help="jangan buat dist/*.zip")
    args = ap.parse_args()

    try:
        app = specmod.load(args.spec)
    except specmod.SpecError as ex:
        print("SPEC ERROR: %s" % ex, file=sys.stderr)
        sys.exit(2)
    root = app.base_dir

    def read_rel(rel):
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return f.read()

    files = gen_sql.generate(app)
    gdir = os.path.join(root, "database", "generated")
    if os.path.isdir(gdir):
        shutil.rmtree(gdir)
    for name, content in files.items():
        write(os.path.join(gdir, name), content)
    write(os.path.join(root, "database", "install.sql"), gen_sql.install_script(app, files, read_rel))
    write(os.path.join(root, "database", "admin", "create_users.sql"), gen_sql.users_script(app))
    write(os.path.join(root, "database", "admin", "remove_users.sql"), gen_sql.remove_users_script(app))

    out, ctx = build_apex(app, root)
    write(os.path.join(root, "tests", "e2e", "pages.json"),
          json.dumps({"app": app.alias, "pages": ctx.e2e_pages}, indent=2) + "\n")

    tr = traceability.build(app)
    if tr:
        write(os.path.join(root, "docs", "traceability.md"), tr)

    zip_path = os.path.join(root, "dist", "%s-apexlang.zip" % app.alias.lower())
    if not args.no_zip:
        zip_dir(out, zip_path)

    n_pages = len([f for f in ctx.files if f.startswith("pages/")]) + 2  # + global page & login
    print("OK  %s (%s): %d entitas, %d dokumen, %d laporan, %d halaman"
          % (app.name, app.code, len(app.entities), len(app.documents), len(app.reports), n_pages))
    print("    database/install.sql, database/admin/create_users.sql")
    if tr:
        print("    docs/traceability.md (%s)" % tr.split("\n")[4].replace("Ringkasan: ", ""))
    print("    %s" % os.path.relpath(out, root))
    if not args.no_zip:
        print("    %s" % os.path.relpath(zip_path, root))


if __name__ == "__main__":
    main()
