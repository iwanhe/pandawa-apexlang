#!/usr/bin/env bash
# Salin skill kanonik (plugins/pandawa-apexlang/skills/pandawa-apexlang) ke .claude/skills/pandawa-apexlang.
#   scripts/sync-skill.sh          salin
#   scripts/sync-skill.sh --check  gagal bila salinan tidak sama (dipakai CI)
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
src="$root/plugins/pandawa-apexlang/skills/pandawa-apexlang"
dst="$root/.claude/skills/pandawa-apexlang"
if [ "${1:-}" = "--check" ]; then
  diff -r -x __pycache__ "$src" "$dst" && echo "OK: .claude/skills/pandawa-apexlang sinkron" && exit 0
  echo "TIDAK SINKRON: jalankan scripts/sync-skill.sh lalu commit" >&2; exit 1
fi
rm -rf "$dst"; mkdir -p "$(dirname "$dst")"; cp -r "$src" "$dst"; find "$dst" -name __pycache__ -prune -exec rm -rf {} +
echo "OK: disalin ke .claude/skills/pandawa-apexlang"
