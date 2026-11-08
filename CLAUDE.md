# Instruksi untuk Claude (repo pandawa-apexlang dan turunannya)

- Untuk pekerjaan aplikasi APEX di repo ini, **gunakan skill `pandawa-apexlang`** (`.claude/skills/pandawa-apexlang/SKILL.md`) dan ikuti alur fasenya. Mulai dengan `scripts/doctor.sh`.
- Sumber kebenaran aplikasi: `app.yaml` + `database/custom/` + `database/seed/` + `apex-custom/` (halaman manual). **Jangan mengedit file generated** (`apex/<alias>/`, `database/generated/`, `database/install.sql`, `database/admin/*_users.sql`, `tests/e2e/pages.json`, `docs/traceability.md`). Ubah spec/custom lalu jalankan `scripts/generate.sh` dan commit seluruh output.
- Ikuti standar Pandawa (skill `oracle-dev-standards`, `apex-qa-pandawa` bila tersedia; ringkasan di `references/pandawa-standards.md`).
- Untuk sintaks `.apx` manual, rujuk `.claude/skills/apexlang/26.2/`, contoh pola `references/ux-patterns/` (Oracle UX Pattern Catalog), dan `references/apexlang-gotchas.md`. Halaman manual disimpan di `apex-custom/`.
- Jangan klaim "lolos validasi" sebelum CI (`apex validate` + database-test) hijau; jangan klaim "berfungsi" sebelum dicoba di oracleapex.com atau E2E. Laporkan hasil generator, compiler, test DB, E2E, dan uji manual terpisah, dan catat buktinya di `docs/04-acceptance.md`.
- Mengubah toolkit itu sendiri: ikuti `CONTRIBUTING.md` (edit di `plugins/pandawa-apexlang/skills/pandawa-apexlang/`, lalu `scripts/sync-skill.sh`; entri `CHANGELOG.md` beserta bukti untuk rilis).
