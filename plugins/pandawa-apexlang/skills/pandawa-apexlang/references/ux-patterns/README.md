# Referensi pola UX (Oracle APEX UX Pattern Catalog 26.2)

Halaman `.apx` di folder ini disalin apa adanya dari [oracle/apex `sample-apps/ux-pattern-catalog`](https://github.com/oracle/apex/tree/26.2/sample-apps/ux-pattern-catalog) (branch `26.2`, commit `244dd36`). Lisensi: Universal Permissive License 1.0 (`LICENSE-oracle-apex.txt`). Halaman indeks kategori dan file gambar tidak ikut disalin.

Gunakan halaman-halaman ini sebagai **contoh sintaks APEXlang 26.2 yang terbukti valid** untuk komponen yang tidak dibuat generator: cards, content row, metric card, faceted search, contextual info, region display selector, chart varian, drawer, dan lainnya. Setiap halaman membawa `help` (Purpose / When to Use / When to Avoid / AI Guidance) dan setiap region membawa `comments` (Intent / Pattern role / AI guidance). Baca keduanya sebelum menyalin.

## Indeks pola

| Pola | File | Komponen utama | Di generator Pandawa |
| --- | --- | --- | --- |
| Dashboard sederhana | `pages/p00110-dashboard-simple.apx` | metric card, chart, content row | `dashboard:` (Home 100): metric card diambil dari sini |
| Dashboard advanced | `pages/p00120-dashboard-advanced.apx` | metric card, chart multi-seri | Manual (custom) |
| Dashboard eksekutif | `pages/p00130-dashboard-executive.apx` | metric card, chart, content row | Manual (custom) |
| Faceted search – cards | `pages/p00210-faceted-search-cards.apx` | facetedSearch, cards | `list_type: faceted-cards` |
| Faceted search – content row | `pages/p00220-faceted-search-content-row.apx` | facetedSearch, content row | Manual. Generator memakai classic report (`faceted-report`) |
| Browse – Interactive Report | `pages/p00230-browse-interactive-report.apx` | interactiveReport | `list_type: ir` (default) |
| Full page search | `pages/p00240-full-page-search.apx` | search field, content row, cards | Manual |
| AI chat | `pages/p00250-ai-chat.apx` | APEX AI Assistant | Manual. Butuh AI service di workspace; bukan untuk MVP |
| Item detail – ringkas | `pages/p00310-item-detail-summary.apx` | contextual info, metric card, content row | Manual (kandidat halaman detail dokumen) |
| Item detail – lengkap | `pages/p00320-item-detail-full.apx` | marquee, child records, comments, region display selector | Manual. Region child records menjadi acuan `workspace` |
| Item selection (split view) | `pages/p00330-item-selection.apx` | facetedSearch, content row, contextual info, `split-view-selection.js` | `workspace` (versi deklaratif tanpa JS: pilih baris = reload halaman) |
| Tree selection | `pages/p00340-tree-selection.apx` | tree, split view | Manual |
| Form sederhana (halaman penuh) | `pages/p00410-data-entry-simple-form.apx` | form, content block | Manual. Generator memakai dialog |
| Form drawer | `pages/p00420-data-entry-drawer-form.apx` | form, `@/drawer` | `form_style: drawer` |
| Primitive: content rows | `pages/p01100-content-rows.apx` | content row (banyak varian) | Referensi komponen |
| Primitive: cards | `pages/p01110-cards.apx` | cards (banyak varian) | Referensi komponen |
| Primitive: metrics | `pages/p01120-metrics.apx` | metric card, classic report | Referensi komponen |
| Primitive: charts | `pages/p01130-charts.apx` | chart (bar, line, area, pie, dll.) | Referensi komponen (lihat gotcha G2 untuk axis) |

`static-files/js/split-view-selection.js` dipakai p00330/p00340. Halaman lain tidak butuh file statis.

## Cara memakai di proyek Pandawa

1. Cari pola yang paling dekat dengan kebutuhan di tabel di atas. Bila generator sudah mendukungnya, pakai field `app.yaml` dan jangan menulis `.apx` manual.
2. Untuk halaman manual, salin region dari file pola ke halaman baru (di `apex/<alias>/pages/`), lalu sesuaikan agar memenuhi standar Pandawa:
   - Ganti `security { authentication: public }` dengan `authorizationScheme` aplikasi. Setiap halaman wajib punya skema.
   - Ganti query sampel (`from dual connect by level ...`) dengan view `APX_<APP>_*_V` (MVC: region membaca view).
   - Pakai nomor halaman dan alias sesuai rentang Pandawa (100/200/300/400/500).
   - Pertahankan konvensi `comments` (Intent / Pattern role / AI guidance) dan isi page `comments` dengan Purpose / When to Use / AI Guidance / Source.
3. Jalankan `scripts/validate.sh`. Gotcha yang sering muncul ada di `../apexlang-gotchas.md` (R6–R12).
4. Simpan halaman manual di **`apex-custom/`** (struktur sama dengan `apex/<alias>/`, mis. `apex-custom/pages/p00410-request-summary.apx`). Generator menghapus dan membuat ulang `apex/<alias>/` setiap kali dijalankan, lalu menyalin isi `apex-custom/` di atasnya. Jadi halaman manual tidak hilang, ikut masuk zip, dan halaman non-modal ikut ke `tests/e2e/pages.json` (smoke test).
   - Pakai nomor halaman yang tidak dipakai `app.yaml`. Bila file manual menimpa file hasil generate, generator mencetak `PERINGATAN`.
   - Komponen bersama yang dirujuk halaman manual (LOV, list) juga harus ada: definisikan lewat spec, atau taruh file shared component tambahan di `apex-custom/shared-components/`.
   - Catat halaman manual di README aplikasi.

Untuk melihat pola berjalan, import aplikasi catalog lengkap (`ux-pattern-catalog.zip` di repo Oracle) ke workspace sandbox.
