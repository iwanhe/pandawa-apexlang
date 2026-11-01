# Instruksi untuk Claude (repo pandawa-apexlang dan turunannya)

- Untuk pekerjaan aplikasi APEX di repo ini, **gunakan skill `pandawa-apexlang`** (`.claude/skills/pandawa-apexlang/SKILL.md`) dan ikuti alur fasenya.
- Sumber kebenaran aplikasi: `app.yaml` + `database/custom/` + `database/seed/`. **Jangan mengedit file generated** (`apex/<alias>/`, `database/generated/`, `database/install.sql`, `database/admin/*_users.sql`, `tests/e2e/pages.json`). Ubah spec/custom lalu jalankan `scripts/generate.sh` dan commit seluruh output.
- Ikuti standar Pandawa (skill `oracle-dev-standards`, `apex-qa-pandawa` bila tersedia; ringkasan di `references/pandawa-standards.md`).
- Untuk sintaks `.apx` manual, rujuk `.claude/skills/apexlang/26.2/` dan `references/apexlang-gotchas.md`.
- Jangan klaim "lolos validasi" sebelum CI (`apex validate` + database-test) hijau; jangan klaim "berfungsi" sebelum dicoba di oracleapex.com atau E2E.
- Mengubah toolkit itu sendiri: edit di `plugins/pandawa-apexlang/skills/pandawa-apexlang/`, lalu `scripts/sync-skill.sh`.
