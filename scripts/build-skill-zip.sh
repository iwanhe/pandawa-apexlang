#!/usr/bin/env bash
# Paket skill untuk diupload ke claude.ai (Settings > Capabilities > Skills, atau Skills organisasi).
#   scripts/build-skill-zip.sh   -> dist/pandawa-apexlang-skill.zip
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
src="$root/plugins/pandawa-apexlang/skills"
mkdir -p "$root/dist"; out="$root/dist/pandawa-apexlang-skill.zip"; rm -f "$out"
(cd "$src" && zip -qr -X "$out" pandawa-apexlang -x '*/__pycache__/*' '*.pyc')
echo "OK: dist/pandawa-apexlang-skill.zip ($(du -h "$out" | cut -f1))"
