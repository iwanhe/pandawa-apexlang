# Pola Halaman

Ringkasan tabel keputusan. Versi lengkap: [`page-patterns.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/page-patterns.md). Evaluasi dari atas; baris pertama yang cocok menang.

## List

| Kondisi | Pakai |
| --- | --- |
| Butuh export, kolom/urutan bebas, volume besar | `list_type: ir` |
| Dokumen/transaksi disaring per status, department, tipe | `faceted-report` |
| Master data dicari lewat ≥ 2 dimensi, dikenali dari nama | `faceted-cards` |
| Lainnya | `ir` (default) |

## Detail dan form

| Kondisi | Pakai |
| --- | --- |
| Dokumen dengan baris detail ditinjau bersama header | `workspace` |
| Dokumen ber-approval, > 8 field, atau ada textarea | `form_style: modal` |
| Form pendek master data | `form_style: drawer` |
| Detail kaya (aktivitas, file, komentar), tree, wizard | manual di `apex-custom/` dari `ux-patterns` |

## Dashboard

| KPI | Tata letak |
| --- | --- |
| 1–2 | metric card 2 kolom |
| 3–4 | metric card 4 kolom (paling efektif) |
| ≥ 5 | pindahkan ke laporan atau dashboard manual (generator memberi `SARAN`) |

Chart: `pie` untuk komposisi ≤ 6 kategori, `bar` untuk perbandingan. Tren waktu (line) masih manual.

## SARAN otomatis

`scripts/generate.sh` mencetak `SARAN:` bila spec bertentangan dengan tabel (mis. drawer untuk form panjang, kolom EMAIL tanpa `semantic`, dokumen ber-detail tanpa `workspace`). Saran tidak menggagalkan generate. Bila sengaja menyimpang, catat alasannya di FRS; `app.advice: false` mematikan saran.
