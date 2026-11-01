#!/usr/bin/env bash
# Generate database scripts + APEXlang app + E2E config dari app.yaml, lalu cek struktur.
#   scripts/generate.sh [path/ke/app.yaml]   (default: app.yaml di root repo)
set -euo pipefail
source "$(dirname "$0")/_gen_path.sh"
SPEC="${1:-$_root/app.yaml}"
python3 "$GEN/generate.py" "$SPEC"
ALIAS="$(python3 -c "import sys,yaml;a=yaml.safe_load(open(sys.argv[1]))['app'];print(a.get('alias',a['code']).lower())" "$SPEC")"
python3 "$GEN/check_apx.py" "$(dirname "$SPEC")/apex/$ALIAS"
