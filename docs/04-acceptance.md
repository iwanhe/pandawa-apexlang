# Acceptance – Demo Permintaan Barang (template pandawa-apexlang 1.6.0)

Contoh matriks acceptance terisi untuk aplikasi DEMO. Template kosong: `plugins/pandawa-apexlang/skills/pandawa-apexlang/assets/templates/docs/04-acceptance.md`. Status hanya **Terbukti** bila ada bukti yang bisa dibuka ulang untuk versi ini.

## Identitas rilis

| Atribut | Nilai |
| --- | --- |
| Commit | `75fa873` (merge PR #7); CI dan E2E di bawah dijalankan pada commit ini |
| Tanggal | 2026-11-08 |
| Zip yang terpasang di lingkungan uji | `demo-apexlang.zip` DEMO 1.2 (commit `e455163`) + patch data department HR nonaktif |
| Lingkungan uji | oracleapex.com, workspace `kcsi`, aplikasi `demo` |

Selisih zip terpasang dengan `75fa873` di `apex/demo`: 44 baris teks `## Requirements` di `comments` halaman (metadata, tidak tampil dan tidak dieksekusi). Dicek dengan `git diff e455163 75fa873 -- apex/demo`.

## Kriteria

| # | Kriteria | Prioritas | Bukti | Status |
| --- | --- | --- | --- | --- |
| A1 | Output generate sinkron dengan `app.yaml` | MUST | [CI 42452746890](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42452746890), job generate-validate (.) | Terbukti |
| A2 | `apex validate` lolos | MUST | [CI 42452746890](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42452746890) | Terbukti |
| A3 | Install + test database lolos di Oracle Free | MUST | [CI 42452746890](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42452746890), `tests/db/test_approval.sql`, `tests/db/test_master_reports.sql` | Terbukti |
| A4 | Import ke lingkungan uji tanpa error | MUST | Import zip DEMO 1.2 oleh pemilik repo (2026-11-04); E2E di bawah berjalan terhadap aplikasi itu | Terbukti (zip 1.2; lihat selisih di atas) |
| A5 | Smoke test semua halaman | MUST | [E2E 42468463639](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42468463639), `smoke.spec.ts` | Terbukti |
| A6 | Akses per role sesuai skema (halaman dan form) | MUST | [E2E 42468463639](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42468463639), `roles.spec.ts`: 5 user, form dibuka lewat dialog; hasil sama dengan [E2E 41924718277](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41924718277) (2026-11-04) | Terbukti, kecuali form Approval (191) |
| A7 | Fungsi spesifik aplikasi (REQ-4.3, 5.1, 7.1, 7.2, 7.3) | MUST | [E2E 42468463639](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42468463639), `features.spec.ts` | Terbukti |
| A8 | Simulasi skenario per role (FRS §8) | MUST | Uji approval manual oleh pemilik repo pada versi awal DEMO (2026-11-02) | Belum (belum diulang untuk versi ini) |
| A9 | Tampilan HP | SHOULD | [E2E 42468463639](https://github.com/iwanhe/pandawa-apexlang/actions/runs/42468463639), `nav-menu.spec.ts`; cek manual metric card dan drawer (DEMO 1.1–1.2) | Terbukti untuk side menu; tampilan lain hanya cek manual |
| A10 | Traceability: tidak ada REQ MUST "Belum direalisasi" | MUST | `docs/traceability.md` pada `75fa873`: 26/26 OK | Terbukti |

## Uji manual

| Tanggal | Penguji | Skenario / halaman | Hasil | Catatan |
| --- | --- | --- | --- | --- |
| 2026-11-02 | Pemilik repo | Approval Manager/Director (DEMO awal) | Berhasil | Versi sebelum metric card, faceted search, dan workspace |
| 2026-11-04 | Pemilik repo | Import DEMO 1.1, metric card dan drawer | Tampil normal | |
| 2026-11-04 | Pemilik repo | Import DEMO 1.2, faceted search dan Detail Permintaan | Tampil normal | |

## Batasan diketahui

| Hal yang belum terbukti | Alasan | Rencana |
| --- | --- | --- |
| Form Approval (191) per role | Approval Inbox kosong saat E2E | Ajukan satu permintaan sebelum E2E bila ingin dibuktikan; aturan approval diuji di test database |
| Simulasi skenario FRS §8 pada versi ini | Belum diulang sejak DEMO awal | Ulangi dengan user demo sebelum DEMO dipakai untuk pelatihan |
| Tombol Tambah di halaman 302 setelah header diubah | Baru menyesuaikan setelah reload | Diterima; penguncian dijaga trigger |

## Keputusan

| Keputusan | Disetujui oleh | Tanggal |
| --- | --- | --- |
| Test E2E tetap read-only; approval UI (191) tidak diotomasi | Pemilik repo | November 2026 |
