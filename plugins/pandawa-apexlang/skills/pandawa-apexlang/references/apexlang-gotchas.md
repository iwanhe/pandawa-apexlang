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

## Import & instance oracleapex.com

| # | Gejala | Solusi |
| --- | --- | --- |
| I1 | `ORDS Authentication request failed. Reason: Not Found` saat import zip | SQL Workshop → RESTful Services → **Register Schema with ORDS**, lalu ulangi. Bisa juga masalah instance yang hilang sendiri |
| I2 | Zip ditolak | Zip berisi `application.apx` di root (bukan di subfolder). Upload zip apa adanya |
| I3 | Tabel belum ada saat import | Jalankan `database/install.sql` dulu, baru import |
| I4 | Halaman "Akses ditolak" | User belum punya role. Mode bootstrap: selama belum ada ADMIN, semua user dianggap ADMIN |

## PL/SQL & SQL

| # | Gejala | Aturan |
| --- | --- | --- |
| P1 | `PLS-00231: function 'X' may not be used in SQL` | Fungsi lokal di blok anonim tidak boleh dipakai di dalam SQL. Lookup dulu ke variabel, atau pakai prosedur lokal |
| P2 | `ORA-04091 mutating table` di trigger detail saat delete cascade | Tangkap `-4091` lalu `return` (generator melakukannya untuk `parent:`) |
| P3 | Nama fungsi `current_user` | Hindari keyword Oracle. Generator memakai `app_user` |
| P4 | `set serveroutput on` di SQL Commands | Hanya SQLcl/SQL Scripts. Di SQL Commands tempel blok `declare ... end;` saja |
| P5 | Angka di pesan error | `to_char(..., 'FM999G999...')` mengikuti NLS database (oracleapex.com: koma) |

## Playwright / E2E

| # | Gejala | Aturan |
| --- | --- | --- |
| E1 | `waitForLoadState('networkidle')` timeout | APEX menjaga koneksi terbuka. Tunggu `load` + `.t-Body` visible + jeda singkat |
| E2 | Artifact/CDN tidak bisa diunduh dari sandbox agent | Cetak diagnostik (timeline, log browser) ke stdout job hanya bila test gagal |
| E3 | Navigasi antar halaman | Friendly URL `/ords/r/<ws>/<app>/<alias>?session=<id>`. Ganti segmen alias, pertahankan `session` |
| E4 | Debug event UI | Rekam class body, `theme42layoutchanged`, dan stack trace `$.event.trigger`. Teknik ini menemukan R3 |
