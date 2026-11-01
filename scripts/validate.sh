#!/usr/bin/env bash
# Validasi aplikasi APEXlang dengan SQLcl `apex validate` (tanpa database).
#   SQLCL_BIN=/path/sqlcl/bin/sql scripts/validate.sh [path/ke/app.yaml]
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
SPEC="${1:-$root/app.yaml}"
ALIAS="$(python3 -c "import sys,yaml;a=yaml.safe_load(open(sys.argv[1]))['app'];print(a.get('alias',a['code']).lower())" "$SPEC")"
: "${SQLCL_BIN:?set SQLCL_BIN ke executable SQLcl 26.2+}"
"$root/.claude/skills/apexlang/26.2/apexlang-compile/scripts/validate-apex-app.sh" "$(dirname "$SPEC")/apex/$ALIAS"
