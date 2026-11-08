# Berkontribusi

Panduan untuk mengubah **toolkit** (generator, skill, template). Untuk membuat aplikasi dengan template ini, lihat [README](README.md) dan [Wiki](https://github.com/iwanhe/pandawa-apexlang/wiki).

## Persiapan

```bash
pip install pyyaml
scripts/doctor.sh                 # cek Python, PyYAML, spec, Java, SQLcl, Node, Docker, salinan skill
SQLCL_BIN=~/sqlcl/bin/sql scripts/doctor.sh --deep   # + generate ulang dan apex validate
```

## Aturan

1. **Ubah toolkit hanya di `plugins/pandawa-apexlang/skills/pandawa-apexlang/`.** Lalu `scripts/sync-skill.sh` (CI menolak salinan `.claude/skills/` yang tidak sinkron).
2. **Jangan edit file generated** (`apex/<alias>/`, `database/generated/`, `database/install.sql`, `database/admin/*_users.sql`, `tests/e2e/pages.json`, `docs/traceability.md`). Ubah generator atau spec, lalu `scripts/generate.sh` untuk `app.yaml` dan `examples/*/app.yaml`, dan commit seluruh output.
3. **Setiap fitur generator** butuh: contoh di DEMO atau MBMS, dokumentasi di `references/app-spec.md`, dan gotcha baru di `references/apexlang-gotchas.md` bila ada pelajaran sintaks/runtime.
4. **Bukti, bukan klaim.**
   - "Lolos validasi" hanya setelah CI (`apex validate` + database-test) hijau.
   - "Berfungsi" hanya setelah dicoba di oracleapex.com atau lewat E2E.
   - Laporkan hasil generator, compiler, test DB, E2E, dan uji manual terpisah. *Terdeteksi* bukan *terbukti*.
5. **Standar Pandawa** untuk SQL/PLSQL (`references/pandawa-standards.md`): objek `APX_<APP>_*`, lowercase, indentasi 3 spasi, koma di depan, `package_version`, header script.
6. **Data dummy saja**, tanpa password di repo ([SECURITY.md](SECURITY.md)).

## Alur perubahan

1. Branch dari `main`.
2. Ubah, lalu jalankan secara lokal:

   ```bash
   scripts/sync-skill.sh
   scripts/generate.sh && scripts/generate.sh examples/mbms/app.yaml
   python3 scripts/check-links.py
   SQLCL_BIN=... scripts/validate.sh && SQLCL_BIN=... scripts/validate.sh examples/mbms/app.yaml
   DB_CONN=apx/pwd@localhost:1521/FREEPDB1 SQLCL_BIN=... tests/db/run.sh            # opsional, Oracle Free di Docker
   ```

3. Push; tunggu CI hijau. Bila perubahan menyentuh halaman atau test E2E, import zip ke workspace sandbox dan jalankan workflow **E2E Playwright** di branch itu.
4. Buka PR berisi ringkasan perubahan, dampak ke proyek turunan (perlu install ulang? import ulang?), dan bukti (link run CI/E2E, uji manual).
5. Untuk rilis: naikkan `version` di `plugins/pandawa-apexlang/.claude-plugin/plugin.json`, tambahkan entri di [CHANGELOG.md](CHANGELOG.md) dengan bukti, dan perbarui `docs/wiki/Riwayat-Versi.md`.

## Wiki

Halaman wiki ada di `docs/wiki/` dan disalin ke GitHub Wiki oleh workflow **Sinkron Wiki** saat push ke `main`. Edit lewat PR; perubahan langsung di halaman wiki akan tertimpa.
