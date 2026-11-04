# Gotcha APEXlang 26.2 dan oracleapex.com (lessons learned MBMS)

Setiap butir di bawah pernah menyebabkan gagal validasi, gagal import, atau bug runtime. Generator sudah menanganinya. Butir-butir ini relevan saat Anda menulis atau mengedit `.apx` secara manual.

## Sintaks & validasi (`apex validate`)

| # | Gejala (pesan SQLcl) | Aturan |
| --- | --- | --- |
| G1 | `VALUE_NOT_UPPERCASE ... name` di `lovs.apx` | `lov.name` harus HURUF BESAR |
| G2 | `MINIMUM_COMPONENTS_ERROR ... "axis"` | Chart selain pie (default bar) wajib punya `axis x (...)` dan `axis y (...)`. `value { format, decimalPlaces }` diletakkan di axis y, bukan di region (`INVALID_PROPERTY: format`) |
| G3 | `DUPLICATED_COMPONENT ... executionMappingIdentifier: null` | Setiap `process` wajib punya `advanced { executionMappingIdentifier: <unik> }` |
| G4 | Validasi tidak dikenali | `validation` memakai grup `validation { type: expression  plsqlExpression: ... }`. `error { displayLocation: inlineWithFieldAndInNotification }` (perhatikan `InNotification`) |
| G5 | Inline object/group | Setiap properti satu baris. Group `name {`, object `name: {`, array `name: [`. Lihat SKILL inventory Oracle |
| G6 | Link IR | Link region memakai `items: { P11_ID: \#ID#\ }`. Link kolom memakai `#ID#` tanpa backslash |
| G7 | Exit code 0 tapi gagal | SQLcl bisa exit 0 walau validasi gagal. Script resmi `validate-apex-app.sh` mengecek teks `Validation successful` |

## Theme & runtime

| # | Gejala | Aturan |
| --- | --- | --- |
| R1 | Template contoh `example-0` memakai `baseTheme: ut-26.1` | Pakai `ut-26.2` dan `filePrefix #APEX_FILES#themes/theme_42/26.2/` |
| R2 | `compatibilityMode: 24.2` dari contoh | Hapus (pakai default versi saat ini) |
| R3 | **Side menu di HP terbuka lalu langsung tertutup** (juga terjadi di starter app Oracle) | Bug Universal Theme 26.2.1: `onExpand` → `delayResize()` → resize sintetis → `onResize` → `collapse()` di lebar < lg. Workaround: `static-files/js/nav-fix.js` (abaikan resize sintetis 800 ms setelah expand bila ukuran viewport sama), dimuat via `app javaScript fileUrls`. Dibuktikan lewat E2E Playwright. Hapus bila Oracle sudah memperbaiki |
| R4 | Template option `#DEFAULT#` side nav | Untuk Side Navigation Menu, `#DEFAULT#` = `js-defaultCollapsed`. Bukan penyebab R3 |
| R5 | Display-only item ikut tersubmit | `settings { sendOnPageSubmit: false }` + `source { queryOnly: true }` |
| R6 | Metric card (`themeTemplateComponent/metricCard`) | Atribut khusus template ada di `settings { metric, meta, layout }` dan `plugin-avatar { ... }`, tidak tercantum di inventaris APEXlang. Nilai `layout` yang terbukti (UX Pattern Catalog): `2Columns`, `4Columns`. Urutan pakai `orderBy { type: staticValue  orderByClause: SEQ }`, bukan `order by` di SQL |
| R8 | Faceted search | Halaman `pageTemplate: @/left-side-column`; region `facetedSearch` di slot `leftColumn` dengan `source { filteredRegion: @<region> }`. Target cards/classic report (bukan Interactive Report). Facet LOV `sharedComponent` atau `distinctValues`; kolom facet harus ada di query target |
| R9 | Urutan di region yang dibungkus (cards, classic report target facet, metric card) | Pakai `orderBy { type: staticValue  orderByClause: KOLOM [DESC] }`, bukan `order by` di SQL |
| R10 | Substitusi link | Classic report/IR: `#KOLOM#`. Cards action dan tombol: `&KOLOM.` / `&P1_ITEM.` |
| R11 | Pagination classic report | Nilai valid antara lain `rowRangesXToYOfZWithPagination`, `showAll` (bukan `rowRangesXToY` milik IR) |
| R12 | Slot tombol per template region | `@/standard` → `edit`; `@/hero` → `next`; `@/buttons-container` (dialog) → `next`/`close`/`delete` |
| R7 | Drawer | `dialogTemplate: @/drawer` + template option `js-dialog-class-t-Drawer--pullOutEnd` (panel dari kanan). Untuk form pendek; form panjang/dokumen tetap `@/modal-dialog` |

## Import & instance oracleapex.com

| # | Gejala | Solusi |
| --- | --- | --- |
| I1 | `ORDS Authentication request failed. Reason: Not Found` saat import zip | SQL Workshop → RESTful Services → **Register Schema with ORDS**, lalu ulangi. Bisa juga masalah instance yang hilang sendiri |
| I2 | Zip ditolak | Zip berisi `application.apx` di root (bukan di subfolder). Upload zip apa adanya |
| I3 | Tabel belum ada saat import | Jalankan `database/install.sql` dulu, baru import |
| I4 | Halaman "Akses ditolak ... APP_USERS" tepat setelah `create_users.sql` | Begitu ADMIN pertama terdaftar, mode bootstrap berakhir: akun yang tidak punya role ditolak. `create_users.sql` kini otomatis mendaftarkan akun yang menjalankannya sebagai ADMIN; untuk akun lain: `insert into apx_<app>_user_roles (username, role_code) values ('<USER>', 'ADMIN'); commit;` |

## PL/SQL & SQL

| # | Gejala | Aturan |
| --- | --- | --- |
| P1 | `PLS-00231: function 'X' may not be used in SQL` | Fungsi lokal di blok anonim tidak boleh dipakai di dalam SQL. Lookup dulu ke variabel, atau pakai prosedur lokal |
| P2 | `ORA-04091 mutating table` di trigger detail saat delete cascade | Tangkap `-4091` lalu `return` (generator melakukannya untuk `parent:`) |
| P3 | Nama fungsi `current_user` | Hindari keyword Oracle. Generator memakai `app_user` |
| P4 | `set serveroutput on` di SQL Commands | Hanya SQLcl/SQL Scripts. Di SQL Commands tempel blok `declare ... end;` saja |
| P6 | `ORA-04091 mutating` di trigger yang membaca tabelnya sendiri (mis. cek stok on hand) | Hanya aman untuk `INSERT ... VALUES` satu baris (form APEX, seed). Jangan `INSERT ... SELECT` ke tabel ledger; untuk bulk pakai loop atau compound trigger |
| P5 | Angka di pesan error | `to_char(..., 'FM999G999...')` mengikuti NLS database (oracleapex.com: koma) |

## Playwright / E2E

| # | Gejala | Aturan |
| --- | --- | --- |
| E1 | `waitForLoadState('networkidle')` timeout | APEX menjaga koneksi terbuka. Tunggu `load` + `.t-Body` visible + jeda singkat |
| E2 | Artifact/CDN tidak bisa diunduh dari sandbox agent | Cetak diagnostik (timeline, log browser) ke stdout job hanya bila test gagal |
| E3 | Navigasi antar halaman | Friendly URL `/ords/r/<ws>/<app>/<alias>?session=<id>`. Ganti segmen alias, pertahankan `session` |
| E5 | Halaman modal dibuka langsung lewat URL → HTTP 400, form tidak tampil | Buka seperti user: klik pemicunya (tombol Create/Edit/Tambah, link dialog di report) lalu bekerja di frame dialog: `openDialog()` di `tests/e2e/tests/helpers.ts`. Halaman pembuka tiap modal ada di `pages.json` (`access[].openers`). Di APEX 26 link report/kartu ke halaman modal berbentuk `href="#action$a-dialog-open?url=%2Fords%2Fr%2F...%2F<alias>%3F...%26cs%3D..."` (bukan `javascript:apex.navigation.dialog`). Field wajib yang kosong ditolak di browser sebelum validasi server berjalan: isi semua field wajib saat menguji validasi server |
| E6 | Selector facet `input[type=checkbox]` / `name=Pnn_KOLOM` tidak ketemu | Checkbox facet tersembunyi (`u-hidden`); yang diklik user adalah elemen role **option** dengan label + jumlah (mis. "Alat Tulis Kantor2"): `page.getByRole('option', { name: /^Alat Tulis Kantor/ })`. Bila gagal, `dumpControls()` mencetak kontrol DOM ke log job |
| E4 | Debug event UI | Rekam class body, `theme42layoutchanged`, dan stack trace `$.event.trigger`. Teknik ini menemukan R3 |
