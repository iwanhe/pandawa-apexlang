# Memilih pola halaman (tabel keputusan)

Dipakai di fase 3 (FRS → `app.yaml`) dan saat menulis halaman manual. Diadaptasi dari *Pattern Selection Decision Table* di [Oracle APEX blueprints](https://github.com/oracle/apex/tree/26.2/blueprints) dan pola di `ux-patterns/`, disesuaikan dengan fitur generator Pandawa.

Cara pakai: untuk setiap kebutuhan halaman, evaluasi tabel dari atas ke bawah. **Baris pertama yang cocok menang.** Bila FRS menyebut pola secara eksplisit, ikuti FRS (baris A).

## 1. Halaman list

| # | Kondisi (cek berurutan) | Pakai | Contoh |
| --- | --- | --- | --- |
| A | FRS menyebut pola tertentu | Pola itu | "Item tampil sebagai kartu" → `faceted-cards` |
| B | User butuh export, kolom/urutan bebas, filter ad hoc, atau volume besar | `list_type: ir` | Rekap, log audit |
| C | Dokumen/transaksi yang disaring per status, department, tipe, lalu dibuka satu per satu | `list_type: faceted-report` | Permintaan Barang, PR, stock ledger |
| D | Master data yang dicari lewat ≥ 2 dimensi (kategori, aktif, BU) dan dikenali dari nama | `list_type: faceted-cards` | Item, Warehouse |
| E | Lainnya (master kecil, ≤ 1 dimensi filter) | `list_type: ir` (default) | Department |

Kolom yang menjadi facet: `enum`, `yn`, `ref`, dan `STATUS` dokumen secara default; atur dengan `facet: true/false` per kolom. Facet efektif 2–6 per halaman. Yang terluas dan paling sering dipakai ditaruh di atas (urutan kolom di spec).

## 2. Detail dan master-detail

| # | Kondisi | Pakai |
| --- | --- | --- |
| A | Dokumen dengan baris detail yang ditinjau atau diisi bersama header (review, approval, kelengkapan) | `workspace: {page: ...}` pada entitas induk (tambahan dari halaman list, bukan pengganti) |
| B | Satu record dengan banyak informasi terkait (aktivitas, file, komentar, metrik) | Halaman manual dari `ux-patterns/pages/p00310` (ringkas) atau `p00320` (lengkap) di `apex-custom/` |
| C | Memilih dari hierarki (struktur organisasi, WBS bertingkat) | Manual dari `p00340` (tree selection) |
| D | Lainnya | Cukup list + form |

## 3. Form

| # | Kondisi | Pakai |
| --- | --- | --- |
| A | Dokumen ber-approval | `form_style: modal` (default dokumen) |
| B | > 8 field yang bisa diisi, atau ada `textarea` | `form_style: modal` |
| C | Form pendek dari list (master data) | `form_style: drawer` (default non-dokumen) |
| D | Form multi-langkah atau perlu konteks penuh satu layar | Manual: form halaman penuh (`p00410`) di `apex-custom/` |

Semua form generator berupa dialog. Kebutuhan wizard atau multi-langkah termasuk pekerjaan manual.

## 4. Dashboard (Home)

| Jumlah KPI | Tata letak | Catatan |
| --- | --- | --- |
| 1–2 | Metric card 2 kolom | |
| 3–4 | Metric card 4 kolom | Paling efektif |
| ≥ 5 | Tetap bisa, tapi pindahkan sisanya ke laporan, atau buat dashboard advanced manual (`p00120`/`p00130`) | Generator memberi `SARAN` |

KPI harus sebanding (satuan sama: jumlah dokumen, nilai rupiah). KPI "yang menunggu saya" (approval) diletakkan pertama.

| Chart | Pakai bila | `type` |
| --- | --- | --- |
| Komposisi ≤ 6 kategori | Proporsi status, kategori | `pie` |
| Perbandingan antar kategori | Nilai per department/BU | `bar` |
| Tren waktu | Per bulan/minggu | Manual (`p01130`): generator baru mendukung `pie` dan `bar` |

## 5. Laporan

| Kondisi | Pakai |
| --- | --- |
| Agregasi, join, atau kalkulasi | View custom `APX_<APP>_<NAMA>_V` + `reports:` (IR, read-only) |
| Satu baris ringkasan (nilai total, status) di atas halaman | Manual: classic report template Contextual Info (`p00310`, region key facts) |

## 6. Kolom dan input (`semantic`)

| Data | Pakai | Efek |
| --- | --- | --- |
| Email | `semantic: email` | input email, lowercase + trim, check constraint, validasi format |
| Telepon | `semantic: phone` | input telepon, trim, check constraint, validasi format |
| URL | `semantic: url` | input URL, harus `http(s)://` |
| NPWP | `semantic: npwp` | 15 digit (99.999.999.9-999.999) atau 16 digit |
| Kode | `type: code` | huruf besar otomatis |
| Uang / jumlah / persen | `money` / `qty` / `pct` | format angka, rata kanan |

## 7. Anti-pola (ditolak generator atau diberi SARAN)

| Anti-pola | Kenapa | Gantinya |
| --- | --- | --- |
| Interactive Report sebagai target faceted search | Tidak didukung APEX | Cards atau classic report (`faceted-*`) |
| Faceted search tanpa kolom facet | Hanya kotak cari; IR lebih kaya | `list_type: ir` |
| Drawer untuk form panjang | Sempit, banyak scroll | `form_style: modal` |
| Dokumen ber-detail tanpa halaman master-detail | User bolak-balik antar halaman | `workspace` |
| Kolom email/telepon/NPWP sebagai text biasa | Data kotor, tidak tervalidasi | `semantic:` |
| > 4 KPI di Home | Sulit dipindai | Laporan atau dashboard manual |
| Logic bisnis di halaman | Melanggar MVC, tidak teruji | Package/trigger + test |

## 8. Saran otomatis (`SARAN:`)

`scripts/generate.sh` mencetak `SARAN: ...` saat spec bertentangan dengan tabel ini. Contoh:

- `list_type: ir` pada master/ledger dengan ≥ 2 kolom facet;
- faceted tanpa kolom facet;
- drawer dengan > 8 field atau textarea;
- dokumen ber-detail tanpa `workspace`;
- nama kolom mengandung EMAIL/PHONE/TELP/HP/NPWP/URL/WEBSITE tanpa `semantic`;
- > 4 KPI.

Saran tidak menggagalkan generate. Bila ada alasan bisnis untuk menyimpang (contoh MBMS: 5 KPI disepakati user), catat di FRS. Matikan semua saran dengan `app.advice: false`.
