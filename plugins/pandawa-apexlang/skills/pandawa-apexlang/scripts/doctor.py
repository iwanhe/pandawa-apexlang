#!/usr/bin/env python3
"""Pandawa APEXlang doctor: cek kesiapan lingkungan kerja tanpa mengubah apa pun.

    python3 doctor.py [path/ke/app.yaml] [--deep] [--json]

Setiap pemeriksaan melaporkan status dan tingkat bukti:
  terbukti   = benar-benar dijalankan dan berhasil (mis. import PyYAML, spec dimuat, apex validate)
  terdeteksi = hanya ditemukan/versinya terbaca (mis. java -version); belum membuktikan alur kerja jalan

--deep  generate ulang di folder sementara lalu bandingkan dengan output yang di-commit, dan
        (bila SQLcl ada) jalankan apex validate. Working tree tidak diubah.
Exit code 1 bila ada pemeriksaan wajib yang GAGAL.
"""
import argparse
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
GEN = os.path.join(HERE, "apexgen")

OK, WARN, FAIL, SKIP = "OK", "WARN", "GAGAL", "LEWAT"
results = []


def add(status, name, detail, evidence="", required=False):
    results.append({"status": status, "name": name, "detail": detail, "evidence": evidence, "required": required})


def run(cmd, timeout=60, cwd=None, env=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return None, "tidak ditemukan"
    except subprocess.TimeoutExpired:
        return None, "timeout %ds" % timeout


def check_python():
    v = sys.version_info
    status = OK if v >= (3, 9) else FAIL
    add(status, "Python", "%d.%d.%d%s" % (v.major, v.minor, v.micro, "" if status == OK else " (butuh 3.9+)"),
        "terbukti (doctor berjalan)", required=True)


def check_pyyaml():
    try:
        import yaml  # noqa: F401
        add(OK, "PyYAML", yaml.__version__, "terbukti (import berhasil)", required=True)
        return True
    except ImportError:
        add(FAIL, "PyYAML", "belum terpasang: pip install pyyaml", required=True)
        return False


def check_spec(spec, have_yaml):
    if not spec:
        add(SKIP, "Spec app.yaml", "tidak ada app.yaml di folder ini (berikan path sebagai argumen)")
        return None
    if not have_yaml:
        add(SKIP, "Spec app.yaml", "butuh PyYAML")
        return None
    sys.path.insert(0, GEN)
    try:
        import spec as specmod
        app = specmod.load(spec)
    except Exception as ex:  # SpecError atau error lain
        add(FAIL, "Spec app.yaml", "%s: %s" % (os.path.relpath(spec), ex), required=True)
        return None
    tips = app.advice()
    detail = "%s (%s): %d entitas, %d dokumen, %d laporan" % (app.name, app.code, len(app.entities), len(app.documents), len(app.reports))
    if app.frs:
        detail += ", %d REQ-ID di FRS" % len(app.frs)
    add(OK, "Spec app.yaml", detail, "terbukti (spec dimuat dan divalidasi)", required=True)
    if tips:
        add(WARN, "Saran pola halaman", "%d SARAN (jalankan scripts/generate.sh untuk detail)" % len(tips))
    return app


def check_git():
    rc, out = run(["git", "--version"])
    if rc == 0:
        add(OK, "Git", out.strip().replace("git version ", ""), "terdeteksi")
    else:
        add(WARN, "Git", "tidak ditemukan; dibutuhkan untuk commit dan CI")


def java_major():
    rc, out = run(["java", "-version"])
    if rc is None:
        return None, out
    lines = [l for l in out.splitlines() if l.strip() and not l.startswith("Picked up")]
    m = re.search(r'version "(\d+)(?:\.(\d+))?', out)
    if not m:
        return None, lines[0] if lines else "versi tidak terbaca"
    major = int(m.group(1))
    if major == 1 and m.group(2):
        major = int(m.group(2))
    line = next((l for l in lines if "version" in l), lines[0] if lines else "")
    return major, line.strip()


def check_java():
    major, line = java_major()
    if major is None:
        add(WARN, "Java", "tidak ditemukan (SQLcl butuh Java 17 atau 21). CI tetap menjalankan apex validate")
    elif major in (17, 21) or major > 21:
        add(OK, "Java", line, "terdeteksi")
    else:
        add(WARN, "Java", "%s: SQLcl butuh Java 17 atau 21" % line, "terdeteksi")


def sqlcl_bin():
    b = os.environ.get("SQLCL_BIN")
    if b:
        return b if os.access(b, os.X_OK) else None, "SQLCL_BIN=%s" % b
    w = shutil.which("sql")
    return w, "PATH"


def check_sqlcl():
    b, src = sqlcl_bin()
    if not b:
        add(WARN, "SQLcl", "tidak ditemukan (%s). Set SQLCL_BIN ke SQLcl 26.2+ untuk apex validate lokal; "
                           "CI tetap menjalankannya" % src)
        return None
    rc, out = run([b, "-V"], timeout=120)
    m = re.search(r"SQLcl: Release ([\d.]+)", out or "")
    ver = m.group(1) if m else None
    if not ver:
        add(WARN, "SQLcl", "%s ditemukan (%s) tapi versi tidak terbaca" % (b, src), "terdeteksi")
        return b
    major = tuple(int(x) for x in ver.split(".")[:2])
    if major >= (26, 2):
        add(OK, "SQLcl", "%s (%s)" % (ver, src), "terdeteksi; --deep membuktikan dengan apex validate")
    else:
        add(WARN, "SQLcl", "%s (%s): butuh 26.2+ untuk APEX 26.2" % (ver, src), "terdeteksi")
    return b


def check_node(root):
    rc, out = run(["node", "--version"])
    if rc != 0:
        add(WARN, "Node.js", "tidak ditemukan; hanya perlu untuk menjalankan E2E Playwright secara lokal")
        return
    ver = out.strip().lstrip("v")
    major = int(ver.split(".")[0]) if ver.split(".")[0].isdigit() else 0
    add(OK if major >= 18 else WARN, "Node.js", ver + ("" if major >= 18 else " (butuh 18+)"), "terdeteksi")
    e2e = os.path.join(root, "tests", "e2e")
    if os.path.isdir(e2e):
        nm = os.path.isdir(os.path.join(e2e, "node_modules", "@playwright", "test"))
        add(OK if nm else SKIP, "Playwright (tests/e2e)",
            "terpasang" if nm else "belum: cd tests/e2e && npm install && npx playwright install chromium",
            "terdeteksi" if nm else "")


def check_docker():
    rc, out = run(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=20)
    if rc == 0:
        add(OK, "Docker", "server %s (untuk test DB lokal dengan Oracle Free)" % out.strip(), "terbukti (daemon menjawab)")
    elif rc is None and out == "tidak ditemukan":
        add(SKIP, "Docker", "tidak ditemukan; opsional (test DB lokal). CI menjalankan test DB di Oracle Free")
    else:
        add(SKIP, "Docker", "terpasang tapi daemon tidak berjalan; opsional")


def check_skill_sync(root):
    src = os.path.join(root, "plugins", "pandawa-apexlang", "skills", "pandawa-apexlang")
    dst = os.path.join(root, ".claude", "skills", "pandawa-apexlang")
    if not (os.path.isdir(src) and os.path.isdir(dst)):
        return

    def diff(dc, rel=""):
        out = [os.path.join(rel, n) for n in dc.left_only + dc.right_only + dc.diff_files if n != "__pycache__"]
        for name, sub in dc.subdirs.items():
            if name != "__pycache__":
                out += diff(sub, os.path.join(rel, name))
        return out
    d = diff(filecmp.dircmp(src, dst, ignore=["__pycache__"]))
    if d:
        add(FAIL, "Salinan skill", "%d file beda dengan plugin (mis. %s): jalankan scripts/sync-skill.sh" % (len(d), d[0]),
            "terbukti (dibandingkan)", required=True)
    else:
        add(OK, "Salinan skill", ".claude/skills sama dengan plugin", "terbukti (dibandingkan)")


def check_secrets(root):
    if not shutil.which("gh"):
        add(SKIP, "Secret E2E (GitHub)", "gh CLI tidak ada; cek manual: APEX_APP_URL, APEX_USERNAME, APEX_PASSWORD, APEX_ROLE_PASSWORD")
        return
    rc, out = run(["gh", "secret", "list"], timeout=30, cwd=root)
    if rc != 0:
        add(SKIP, "Secret E2E (GitHub)", "tidak bisa membaca daftar secret (butuh login gh dengan akses admin repo)")
        return
    names = {l.split()[0] for l in out.splitlines() if l.strip()}
    need = ["APEX_APP_URL", "APEX_USERNAME", "APEX_PASSWORD"]
    missing = [n for n in need if n not in names]
    opt = "APEX_ROLE_PASSWORD" in names
    if missing:
        add(WARN, "Secret E2E (GitHub)", "belum ada: %s" % ", ".join(missing), "terdeteksi (nama secret)")
    else:
        add(OK, "Secret E2E (GitHub)", "lengkap%s" % ("" if opt else "; APEX_ROLE_PASSWORD belum ada (test per role di-skip)"),
            "terdeteksi (nama secret, isi tidak dicek)")


def deep(spec, root, sqlcl):
    """Generate di folder sementara, bandingkan dengan output yang di-commit, lalu apex validate."""
    base = os.path.dirname(os.path.abspath(spec))
    tmp = tempfile.mkdtemp(prefix="pandawa-doctor-")
    try:
        work = os.path.join(tmp, "proj")
        shutil.copytree(base, work, ignore=shutil.ignore_patterns(".git", "node_modules", "dist", "playwright-report",
                                                                  "test-results", "__pycache__"))
        rc, out = run([sys.executable, os.path.join(GEN, "generate.py"), os.path.join(work, os.path.basename(spec)), "--no-zip"],
                      timeout=300)
        if rc != 0:
            add(FAIL, "Generate (deep)", out.strip().splitlines()[-1] if out.strip() else "gagal", required=True)
            return
        targets = ["database/generated", "database/install.sql", "database/admin", "tests/e2e/pages.json", "docs/traceability.md"]
        app_dirs = [d for d in os.listdir(os.path.join(work, "apex"))] if os.path.isdir(os.path.join(work, "apex")) else []
        targets += ["apex/" + d for d in app_dirs]
        changed = []
        for t in targets:
            a, b = os.path.join(base, t), os.path.join(work, t)
            if not os.path.exists(b):
                continue
            if os.path.isfile(b):
                if not os.path.exists(a) or not filecmp.cmp(a, b, shallow=False):
                    changed.append(t)
                continue
            for dp, _dn, fns in os.walk(b):
                for fn in fns:
                    rel = os.path.relpath(os.path.join(dp, fn), work)
                    ra = os.path.join(base, rel)
                    if not os.path.exists(ra) or not filecmp.cmp(ra, os.path.join(dp, fn), shallow=False):
                        changed.append(rel)
        if changed:
            add(FAIL, "Output generate (deep)", "%d file belum sinkron dengan spec (mis. %s): jalankan scripts/generate.sh lalu commit"
                % (len(changed), changed[0]), "terbukti (generate ulang di folder sementara)", required=True)
        else:
            add(OK, "Output generate (deep)", "output yang di-commit sama dengan hasil generate", "terbukti (generate ulang)")
        validator = None
        for c in [os.path.join(root, ".claude", "skills", "apexlang", "26.2", "apexlang-compile", "scripts", "validate-apex-app.sh")]:
            if os.path.isfile(c):
                validator = c
        if not sqlcl:
            add(SKIP, "apex validate (deep)", "SQLcl tidak ada; CI menjalankannya")
        elif not validator:
            add(SKIP, "apex validate (deep)", "validate-apex-app.sh (skill APEXlang Oracle) tidak ditemukan")
        else:
            for d in app_dirs:
                env = dict(os.environ, SQLCL_BIN=sqlcl)
                rc, out = run([validator, os.path.join(work, "apex", d)], timeout=600, env=env)
                ok = rc == 0 and "Validation successful" in out
                tail = [l for l in out.splitlines() if l.strip() and not l.startswith("Picked up")][-3:]
                add(OK if ok else FAIL, "apex validate (deep) apex/%s" % d,
                    "Validation successful" if ok else " | ".join(tail), "terbukti (SQLcl apex validate)", required=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="path ke app.yaml (default: ./app.yaml bila ada)")
    ap.add_argument("--deep", action="store_true", help="generate ulang di folder sementara dan jalankan apex validate")
    ap.add_argument("--json", action="store_true", help="keluaran JSON")
    args = ap.parse_args()
    spec = args.spec or ("app.yaml" if os.path.isfile("app.yaml") else None)
    root = os.path.dirname(os.path.abspath(spec)) if spec else os.getcwd()
    # repo template: naik sampai menemukan plugins/ (spec di examples/<x>/)
    probe = root
    while probe != os.path.dirname(probe) and not os.path.isdir(os.path.join(probe, "plugins", "pandawa-apexlang")):
        probe = os.path.dirname(probe)
    repo = probe if os.path.isdir(os.path.join(probe, "plugins", "pandawa-apexlang")) else root

    check_python()
    have_yaml = check_pyyaml()
    app = check_spec(spec, have_yaml)
    check_git()
    check_java()
    sqlcl = check_sqlcl()
    check_node(root)
    check_docker()
    check_skill_sync(repo)
    check_secrets(repo)
    if args.deep:
        if app:
            deep(spec, repo, sqlcl)
        else:
            add(SKIP, "Deep check", "butuh spec yang valid")

    failed = [r for r in results if r["status"] == FAIL and r["required"]]
    if args.json:
        print(json.dumps({"ok": not failed, "results": results}, indent=2, ensure_ascii=False))
    else:
        w = max(len(r["name"]) for r in results)
        for r in results:
            ev = "  [%s]" % r["evidence"] if r["evidence"] else ""
            print("%-6s %-*s  %s%s" % (r["status"], w, r["name"], r["detail"], ev))
        print()
        if failed:
            print("Belum siap: %d pemeriksaan wajib gagal." % len(failed))
        else:
            warns = sum(1 for r in results if r["status"] == WARN)
            print("Siap untuk generate%s. %s" % (
                "" if any(r["name"] == "SQLcl" and r["status"] == OK for r in results) else " (apex validate lokal belum siap; CI tetap menjalankannya)",
                "%d peringatan." % warns if warns else "Tidak ada peringatan."))
            if not args.deep:
                print("Tambah --deep untuk membuktikan output generate sinkron dan apex validate lolos.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
