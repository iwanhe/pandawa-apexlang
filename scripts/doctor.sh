#!/usr/bin/env bash
# Cek kesiapan lingkungan kerja (Python, PyYAML, spec, Java, SQLcl, Node, Docker, salinan skill, secret E2E).
#   scripts/doctor.sh [path/ke/app.yaml] [--deep] [--json]
#   --deep: generate ulang di folder sementara, bandingkan dengan output yang di-commit, dan jalankan apex validate.
set -euo pipefail
source "$(dirname "$0")/_gen_path.sh"
cd "$_root"
exec python3 "$SKILL_DIR/scripts/doctor.py" "$@"
