# Alur Kerja

| Fase | Deliverable | Gate |
| --- | --- | --- |
| 0. Setup | Repo dari template, secret CI | CI berjalan |
| 1. Blueprint | `docs/01-blueprint.md` | Keputusan terbuka untuk MVP sudah dijawab |
| 2. FRS | `docs/02-frs.md` dengan requirement `REQ-x.y` gaya EARS | User menyetujui lingkup MVP dan daftar REQ-ID |
| 3. Spec | `app.yaml` (pola halaman dari [[Pola Halaman|Pola-Halaman]]) | Generate tanpa `SPEC ERROR`, `SARAN` ditindaklanjuti |
| 4. Logic custom | `database/custom/`, `database/seed/`, `tests/db/test_*.sql` | CI database-test hijau |
| 5. Generate & CI | Output generate di-commit | CI hijau |
| 6. Deploy sandbox | Aplikasi jalan di oracleapex.com | Login dan menu berfungsi |
| 7. Simulasi & E2E | Skenario per role, E2E hijau | E2E hijau, traceability tanpa "Belum direalisasi" |
| 8. Dokumentasi | README aplikasi, `docs/04-acceptance.md` | Install, user & role, simulasi, known issue tertulis; setiap kriteria acceptance punya bukti atau dicatat sebagai batasan |

## Aturan penting

- **Jangan edit file hasil generate**: `apex/<alias>/`, `database/generated/`, `database/install.sql`, `database/admin/*_users.sql`, `tests/e2e/pages.json`, `docs/traceability.md`. Ubah `app.yaml`, `database/custom/`, atau `apex-custom/`, lalu generate ulang.
- **Standar Pandawa**: objek `APX_<APP>_*`, rentang halaman (100 home, 200 master, 300 transaksi, 400 laporan, 500 admin), setiap halaman punya alias dan authorization scheme, MVC (region membaca view, logic di package).
- **Approval** selalu lewat core engine; status dokumen tidak diubah dengan update langsung.
- **Data sandbox dummy**; password tidak pernah di-commit.

Detail per fase, checklist, dan contoh prompt: [`workflow.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/workflow.md).
