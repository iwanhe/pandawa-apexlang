# Cari folder generator: plugin di repo ini, skill di repo, atau skill user (~/.claude/skills).
_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
for d in "$_root/plugins/pandawa-apexlang/skills/pandawa-apexlang" \
         "$_root/.claude/skills/pandawa-apexlang" \
         "$HOME/.claude/skills/pandawa-apexlang"; do
  if [ -f "$d/scripts/apexgen/generate.py" ]; then SKILL_DIR="$d"; break; fi
done
: "${SKILL_DIR:?skill pandawa-apexlang tidak ditemukan}"
GEN="$SKILL_DIR/scripts/apexgen"
