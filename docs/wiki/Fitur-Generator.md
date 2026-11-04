# Fitur Generator (`app.yaml`)

Ringkasan. Format lengkap: [`app-spec.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/app-spec.md).

## Struktur spec

| Bagian | Isi |
| --- | --- |
| `app` | kode (prefix `APX_<CODE>_`), alias, nama, `frs`, `req`, `advice`, `nav_fix` |
| `roles`, `authorizations` | role dan skema otorisasi; `app-users` dan `admin-rights` otomatis, ADMIN lolos semua |
| `groups` | grup menu |
| `entities` | tabel + halaman list + form (detail di bawah) |
| `reports` | laporan read-only dari view custom (halaman 4xx) |
| `dashboard` | KPI (metric card) dan chart (pie/bar) di Home |
| `users` | user demo untuk `create_users.sql` dan E2E per role |
| `custom_sql`, `seed_sql` | file SQL tambahan dan data dummy |

## Fitur entitas

| Field | Fungsi |
| --- | --- |
| `columns` | tipe `text`, `code`, `textarea`, `number`, `int`, `money`, `qty`, `pct`, `date`, `yn`, `enum`, `ref`; `required`, `unique`, `min/max`, `virtual`, `default_sql`, ... |
| `semantic` (kolom) | `email`, `phone`, `url`, `npwp`: check constraint, normalisasi, jenis input, validasi format |
| `document` | dokumen ber-approval: nomor `PREFIX-YYYY-NNNN`, approver level 1/2 + limit, validate hook, status operasional, kolom terkunci |
| `parent` | entitas detail; terkunci bila status induk di luar `lock_unless` |
| `immutable` | ledger: update/delete ditolak trigger |
| `list_type` | `ir`, `faceted-cards`, `faceted-report`; `facet: true/false` per kolom |
| `form_style` | `drawer` (default non-dokumen) atau `modal` (default dokumen) |
| `workspace` | halaman master-detail: daftar induk + header + baris detail |
| `validations` | validasi halaman dengan ekspresi PL/SQL |
| `req` | REQ-ID FRS yang direalisasikan (juga di kolom, validasi, dokumen, laporan, KPI, chart) |

## Yang dibuat otomatis di setiap halaman

- authorization scheme, alias, breadcrumb, menu;
- metadata AI di `comments` (Purpose / When to Use / AI Guidance / Source / Requirements) agar Claude dan developer paham maksud halaman;
- validasi ikon terhadap allowlist Font APEX.

## Halaman manual

Halaman yang belum didukung generator ditulis di `apex-custom/` (struktur sama dengan `apex/<alias>/`). Generator menyalinnya di atas hasil generate, jadi tidak hilang. Contoh pola yang valid: [`references/ux-patterns/`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/ux-patterns).
