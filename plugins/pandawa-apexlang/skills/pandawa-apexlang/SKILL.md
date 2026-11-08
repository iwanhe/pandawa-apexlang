---
name: pandawa-apexlang
description: Metodologi & toolkit Tim PANDAWA untuk membangun aplikasi Oracle APEX 26.2 dengan APEXlang secara end-to-end. Alurnya Blueprint → FRS → app.yaml (spec) → generator (DDL, package core approval/security/penomoran, trigger, view, aplikasi APEXlang, script user) → apex validate + test database di GitHub Actions → import ke oracleapex.com → simulasi & E2E Playwright → dokumentasi. Gunakan saat user ingin membuat aplikasi APEX baru, MVP, prototype, menambah modul/entitas/halaman/approval ke aplikasi APEXlang, menulis/menyusun app.yaml, men-generate ulang aplikasi, menyiapkan CI apex validate atau E2E Playwright untuk APEX, atau menyebut "template pandawa", "pandawa-apexlang", "generate APEX dari spec", "approval engine APEX", "MVP APEX", "blueprint ke APEX". Bukan untuk review QA aplikasi existing (pakai apex-qa-pandawa) atau EBS.
---

# Pandawa APEXlang

Spesifikasi aplikasi ditulis sekali di `app.yaml`. Generator (`scripts/apexgen/`) menghasilkan DDL, package core (security, penomoran, approval), trigger, view, aplikasi APEXlang, script user, konfigurasi E2E, dan matriks traceability. Logic khusus ditulis di `database/custom/*.sql` (MVC: query di view, logic di package); halaman yang belum didukung generator di `apex-custom/`.

Untuk proyek baru, sarankan repo dari template `https://github.com/iwanhe/pandawa-apexlang` (**Use this template**): sudah membawa CI, E2E, `tests/db`, dan skill APEXlang Oracle. Tanpa repo: `python3 <skill>/scripts/apexgen/generate.py path/app.yaml` (Python 3 + PyYAML).

## Cara kerja

1. **Cek lingkungan dulu:** `scripts/doctor.sh` (atau `python3 <skill>/scripts/doctor.py app.yaml`). Laporkan yang *terbukti* terpisah dari yang hanya *terdeteksi*.
2. **Ikuti fase** dan deliverable-nya (detail, checklist, prompt: `references/workflow.md`):

   | Fase | Deliverable |
   | --- | --- |
   | 0 Setup | Repo dari template, secret CI |
   | 1 Blueprint | `docs/01-blueprint.md` |
   | 2 FRS | `docs/02-frs.md` dengan requirement `REQ-x.y` gaya EARS |
   | 3 Spec | `app.yaml`; pola halaman dari `references/page-patterns.md`; `SARAN:` ditindaklanjuti |
   | 4 Logic custom | `database/custom/`, `database/seed/`, `tests/db/test_*.sql` |
   | 5 Generate & CI | Output generate di-commit; CI hijau |
   | 6 Deploy sandbox | `install.sql` → import zip → `create_users.sql` |
   | 7 Simulasi & E2E | Skenario per role; E2E hijau |
   | 8 Dokumentasi | README aplikasi, `docs/04-acceptance.md` |

3. **Hemat referensi:** baca paling banyak 3 rujukan per perubahan, pilih dari peta di bawah. Jangan memuat seluruh folder `references/` atau skill Oracle sekaligus.
4. **Compiler adalah penentu.** Jangan menebak properti APEXlang. Ubah spec atau `.apx`, jalankan `scripts/validate.sh` (atau tunggu CI), lalu perbaiki dari pesan File/Line/Type. Tulis pelajaran baru ke `references/apexlang-gotchas.md`.
5. **Laporkan hasil terpisah:** generator, `apex validate`, test database, import, E2E, dan uji manual. Satu tidak membuktikan yang lain. Catat bukti di `docs/04-acceptance.md` (Terbukti / Belum / Terblokir).

## Aturan wajib

1. **Jangan edit file generated:** `apex/<alias>/`, `database/generated/`, `database/install.sql`, `database/admin/*_users.sql`, `tests/e2e/pages.json`, `docs/traceability.md`. Ubah `app.yaml`, `database/custom/`, atau `apex-custom/`, lalu `scripts/generate.sh`. Setelah aplikasi diubah lewat Page Designer, export APEXlang menjadi sumber kebenaran halaman itu; catat di README.
2. **Standar Pandawa** (`references/pandawa-standards.md`): objek `APX_<APP>_*` (`_PKG`, `_V`, `_TRG`, `_U1`, `_N1`); lowercase, indentasi 3 spasi, koma di depan, `package_version`, JavaDoc, header script. Halaman 100 home, 200 master, 300 transaksi, 400 laporan, 500 admin; setiap halaman punya alias dan authorization scheme.
3. **MVC.** Region membaca view; logic dan validasi berat di package; inline SQL halaman hanya untuk LOV sederhana.
4. **Approval** selalu lewat `APX_<APP>_APPROVAL_PKG` (maker-checker, level 2 berdasarkan limit, `document.validate`). Status dokumen tidak diubah dengan update langsung.
5. **Data dummy, tanpa password di repo.** `c_password` hanya di salinan yang di-upload; kredensial E2E di GitHub Secrets.
6. **Metadata AI** di `comments` halaman (Purpose / When to Use / AI Guidance / Source / Requirements) dan region (Intent / Pattern role / AI guidance). Baca sebelum mengubah `.apx`; ikuti pola yang sama di halaman manual; jangan taruh di `help`.
7. **Traceability.** Rujuk REQ-ID di `req:`, komentar SQL custom, dan pesan assert test. Laporkan REQ yang masih **Belum diuji** / **Belum direalisasi** dari `docs/traceability.md`.
8. **Ikon** harus ada di Font APEX (dicek generator).
9. **Jangan klaim selesai tanpa bukti.** "Lolos validasi" hanya dari `apex validate` + test DB (CI hijau). "Berfungsi" hanya setelah dicoba di oracleapex.com atau E2E. Bila belum, katakan belum diuji.

## Peta rujukan

| Kebutuhan | Baca |
| --- | --- |
| Format `app.yaml` (entitas, dokumen, `list_type`, `workspace`, `semantic`, `req`) | `references/app-spec.md` |
| Memilih list/form/detail/dashboard | `references/page-patterns.md` |
| Menulis `.apx` manual | `references/apexlang-gotchas.md` (wajib), `references/ux-patterns/` (contoh valid), `.claude/skills/apexlang/26.2/` (sintaks Oracle; bila tidak ada, install `apex@oracle-skills`) |
| Core approval / security / penomoran | `references/core-module.md` |
| Standar SQL/PLSQL dan halaman | `references/pandawa-standards.md` |
| Deploy, CI, test DB, E2E, secret | `references/deployment-testing.md` |
| Error dan gejala umum | `references/troubleshooting.md` |
| Template dokumen (blueprint, FRS, README, acceptance) | `assets/templates/docs/` |
