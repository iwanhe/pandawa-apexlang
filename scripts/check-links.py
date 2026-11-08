#!/usr/bin/env python3
"""Cek link di dokumentasi repo (offline, tanpa jaringan).

    python3 scripts/check-links.py

Yang dicek:
  - link Markdown relatif [teks](path) -> file/folder ada (anchor #... diabaikan);
  - link ke repo ini https://github.com/iwanhe/pandawa-apexlang/blob|tree/main/<path> -> path ada;
  - link wiki [[Teks|Halaman]] di docs/wiki -> docs/wiki/Halaman.md ada.
Link http(s) lain tidak dicek (butuh jaringan). Exit 1 bila ada link rusak.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = re.compile(r"^https://github\.com/iwanhe/pandawa-apexlang/(?:blob|tree)/main/(.+)$")
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKI_LINK = re.compile(r"\[\[([^\]]+)\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)

FILES = ["README.md", "CLAUDE.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md"]
GLOBS = ["docs/**/*.md", "examples/**/README.md", ".github/**/*.md",
         "plugins/pandawa-apexlang/skills/pandawa-apexlang/**/*.md"]
# template berisi placeholder (<alias>, <x.y.z>) yang memang bukan link nyata
SKIP_DIRS = ["plugins/pandawa-apexlang/skills/pandawa-apexlang/assets/templates/"]


def targets():
    seen = []
    for f in FILES:
        if os.path.isfile(os.path.join(ROOT, f)):
            seen.append(f)
    for g in GLOBS:
        for p in glob.glob(os.path.join(ROOT, g), recursive=True):
            rel = os.path.relpath(p, ROOT)
            if rel not in seen and not any(rel.startswith(s) for s in SKIP_DIRS):
                seen.append(rel)
    return sorted(seen)


def check(rel):
    broken = []
    path = os.path.join(ROOT, rel)
    text = CODE.sub("", open(path, encoding="utf-8").read())
    for m in MD_LINK.finditer(text):
        t = m.group(1)
        if t.startswith(("mailto:", "#")):
            continue
        r = REPO_URL.match(t)
        if r:
            target = os.path.join(ROOT, r.group(1).split("#")[0])
        elif re.match(r"^[a-z]+://", t):
            continue
        else:
            target = os.path.normpath(os.path.join(os.path.dirname(path), t.split("#")[0]))
        if not os.path.exists(target):
            broken.append(t)
    if rel.startswith("docs/wiki/"):
        for m in WIKI_LINK.finditer(text):
            page = m.group(1).split("|")[-1].strip().replace(" ", "-")
            if not os.path.isfile(os.path.join(ROOT, "docs", "wiki", page + ".md")):
                broken.append("[[%s]]" % m.group(1))
    return broken


def main():
    files = targets()
    bad = 0
    for rel in files:
        for t in check(rel):
            print("%s: link rusak -> %s" % (rel, t))
            bad += 1
    print("%d file dicek, %d link rusak." % (len(files), bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
