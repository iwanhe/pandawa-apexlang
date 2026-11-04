---
name: pandawa-apexlang
description: Metodologi & toolkit Tim PANDAWA untuk membangun aplikasi Oracle APEX 26.2 dengan APEXlang secara end-to-end. Alurnya Blueprint → FRS → app.yaml (spec) → generator (DDL, package core approval/security/penomoran, trigger, view, aplikasi APEXlang, script user) → apex validate + test database di GitHub Actions → import ke oracleapex.com → simulasi & E2E Playwright → dokumentasi. Gunakan saat user ingin membuat aplikasi APEX baru, MVP, prototype, menambah modul/entitas/halaman/approval ke aplikasi APEXlang, menulis/menyusun app.yaml, men-generate ulang aplikasi, menyiapkan CI apex validate atau E2E Playwright untuk APEX, atau menyebut "template pandawa", "pandawa-apexlang", "generate APEX dari spec", "approval engine APEX", "MVP APEX", "blueprint ke APEX". Bukan untuk review QA aplikasi existing (pakai apex-qa-pandawa) atau EBS.
---

# Pandawa APEXlang: dari Blueprint sampai E2E

Toolkit ini membakukan cara Tim PANDAWA membangun aplikasi APEX 26.2. Spesifikasinya ditulis sekali di `app.yaml`, lalu **generator** menghasilkan:

- database: tabel, constraint, trigger, view, dan package core;
- aplikasi APEXlang: halaman list dan form, approval inbox, admin, dashboard;
- script user;
- konfigurasi E2E.

Logika bisnis khusus ditulis manual di `database/custom/*.sql`, mengikuti MVC Pandawa (query di view, logic di package).

Asal toolkit ini adalah proyek MBMS (PT. Multisarana Niaga Mandiri). Semua aturan dan *gotcha* di sini sudah terbukti di sana: `apex validate`, import ke oracleapex.com, dan E2E di HP.

## Lokasi

- **Template repo:** `https://github.com/iwanhe/pandawa-apexlang`. Untuk proyek baru, klik **Use this template**.
- **Generator:** `scripts/apexgen/` di folder skill ini.
- **Wrapper di template repo:** `scripts/generate.sh`, `scripts/validate.sh`, dan `scripts/sync-skill.sh`.
- **Referensi sintaks APEXlang (skill Oracle):** `.claude/skills/apexlang/26.2/`. Bila tidak ada, install `apex@oracle-skills`.

Bila user belum punya repo proyek, sarankan membuat repo dari template dulu. Repo template sudah membawa CI, E2E, `tests/db`, dan skill APEXlang Oracle. Tanpa repo, generator tetap bisa dijalankan langsung:

```bash
python3 <skill>/scripts/apexgen/generate.py path/app.yaml
```

Generator butuh Python 3 + PyYAML.

## Alur kerja (ikuti berurutan, tandai deliverable tiap fase)

| Fase | Deliverable | Cara |
| --- | --- | --- |
| 0. Setup | Repo dari template, secret CI | `references/deployment-testing.md` §1 |
| 1. Blueprint | `docs/01-blueprint.md` | Template `assets/templates/docs/01-blueprint.md`. Isi: sasaran, modul, keputusan (D-xx), risiko, platform. |
| 2. FRS | `docs/02-frs.md` | Template `assets/templates/docs/02-frs.md`. Isi: entitas & kolom, business rule (BR-xx), approval matrix, role × akses, peta halaman (rentang nomor Pandawa). |
| 3. Spec | `app.yaml` | Terjemahkan FRS ke spec (`references/app-spec.md`). Satu tabel FRS = satu `entities:`, approval = `document:`, laporan = `reports:` + view custom. |
| 4. Logic custom | `database/custom/*.sql`, `database/seed/*.sql`, `tests/db/test_*.sql` | Package `APX_<APP>_<NAMA>_PKG`, view laporan, validate hook, data dummy, test PL/SQL. Wajib standar Pandawa (`references/pandawa-standards.md`). |
| 5. Generate & CI | Output generate di-commit; CI hijau | `scripts/generate.sh`, commit, push. CI menjalankan: generate-up-to-date, **SQLcl `apex validate`**, **install + test di Oracle Free**, cek sinkron skill. |
| 6. Deploy sandbox | Aplikasi jalan di oracleapex.com | `database/install.sql` di SQL Workshop → import `dist/<alias>-apexlang.zip` → `database/admin/create_users.sql` (`references/deployment-testing.md` §2) |
| 7. Simulasi & E2E | Skenario demo per role, E2E hijau | README bagian Simulasi. Workflow **E2E Playwright** (manual) dengan secret `APEX_APP_URL`, `APEX_USERNAME`, `APEX_PASSWORD`. |
| 8. Dokumentasi | `README.md` aplikasi, `docs/03-mvp.md` | Template `assets/templates/docs/03-app-readme.md`: install, user & role, simulasi, known issue |

Detail langkah, checklist, dan contoh prompt per fase ada di `references/workflow.md`.

## Aturan wajib

1. **Jangan edit file hasil generate:** `apex/<alias>/`, `database/generated/`, `database/install.sql`, `database/admin/*_users.sql`, dan `tests/e2e/pages.json`. Ubah `app.yaml` atau `database/custom/`, lalu generate ulang. CI menolak perubahan yang tidak sinkron.
   - Pengecualian: setelah aplikasi diubah lewat Page Designer, export APEXlang dari APEX menjadi sumber kebenaran untuk halaman itu. Pindahkan logic-nya ke spec atau custom bila memungkinkan, dan catat di README.
2. **Standar Pandawa:**
   - Objek DB `APX_<APP>_*` dengan suffix `_PKG`, `_V`, `_TRG`, `_U1`, `_N1`. Lowercase, indentasi 3 spasi, koma di depan, `package_version`, JavaDoc, header script.
   - Halaman di rentang 100 home, 200 master, 300 transaksi, 400 laporan, 500 admin. Setiap halaman punya alias dan **authorization scheme**.
3. **MVC.** Region membaca view (`*_V`). Proses dan validasi berat ada di package. Inline SQL di halaman hanya untuk LOV sederhana.
4. **Approval** selalu lewat core engine (`APX_<APP>_APPROVAL_PKG`):
   - maker-checker;
   - level 2 berdasarkan limit;
   - validasi per dokumen lewat `document.validate` (procedure `p_doc_id in number`).

   Jangan mengubah status dokumen dengan update langsung.
5. **Data sandbox selalu dummy.** Password tidak boleh di-commit (`c_password` hanya di salinan yang diupload).
6. **Metadata AI di setiap halaman dan region** (konvensi Oracle APEX UX Pattern Catalog). Generator mengisi `comments` otomatis:
   - halaman: `## Purpose / ## When to Use / ## AI Guidance / ## Source`;
   - region: `Intent: / Pattern role: / AI guidance:`.

   Baca `comments` ini sebelum mengubah `.apx`. Saat menulis halaman manual, ikuti pola yang sama. Jangan taruh metadata ini di `help` (itu teks untuk user).
7. **Ikon** harus ada di Font APEX. Generator mengecek `icon:` terhadap `assets/apex-fa-icons-allowlist.txt` dan memberi saran ikon terdekat.
8. **Jangan klaim selesai sebelum CI hijau.** Klaim "lolos validasi" hanya dari hasil `apex validate` dan test DB. Klaim "berfungsi" hanya setelah dicoba di oracleapex.com atau E2E. Bila belum, katakan belum diuji.

## Gotcha APEXlang 26.2 (wajib dibaca sebelum menulis `.apx` manual)

Ringkasan, detailnya di `references/apexlang-gotchas.md`:

- **LOV:** `name` harus HURUF BESAR.
- **Chart:** chart bar/line wajib punya komponen `axis x` dan `axis y`. Format angka diletakkan di axis y, bukan di region.
- **Process:** setiap process butuh `advanced.executionMappingIdentifier` yang unik.
- **Metric card dan drawer:** sintaks diambil dari UX Pattern Catalog (`themeTemplateComponent/metricCard`, `dialogTemplate: @/drawer`). `settings.layout` metric card yang terbukti: `2Columns`, `4Columns`.
- **Theme dan runtime:**
  - Pakai `baseTheme: ut-26.2` dan prefix `theme_42/26.2/`.
  - Jangan set `compatibilityMode` lama.
  - Universal Theme 26.2.1 menutup side menu di HP. Workaround-nya `nav-fix.js` (`app.nav_fix: true`).
- **PL/SQL:** fungsi lokal di blok anonim tidak boleh dipanggil di dalam SQL (PLS-00231).
- **Import:** bila muncul `ORDS Authentication request failed. Reason: Not Found`, daftarkan schema lewat SQL Workshop → RESTful Services.
- **Playwright di APEX:** jangan menunggu `networkidle`. Tunggu `load` + `.t-Body`.

## Troubleshooting cepat

| Gejala | Penyebab paling mungkin | Rujukan |
| --- | --- | --- |
| `SPEC ERROR: ...` | app.yaml tidak valid (page bentrok, role tidak dikenal, file custom tidak ada) | `references/app-spec.md` |
| CI "Output generator berbeda" | Lupa generate/commit | `scripts/generate.sh` lalu commit |
| `apex validate` gagal | Lihat pesan File/Line/Type | `references/apexlang-gotchas.md` |
| CI database-test: objek INVALID | Error di custom SQL/view | `user_errors` tercetak di log |
| Halaman "Akses ditolak" | User belum punya role di `APX_<APP>_USER_ROLES` | `create_users.sql` / Administration → Users & Roles |
| Submit ditolak `-201xx` | Validate hook / budget rule | Pesan error dari package custom |
