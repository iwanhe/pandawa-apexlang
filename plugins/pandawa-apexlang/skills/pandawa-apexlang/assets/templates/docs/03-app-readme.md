# <Nama Aplikasi> (MVP)

<1–2 kalimat: apa aplikasinya, untuk siapa.> Dibangun dengan template [pandawa-apexlang](https://github.com/iwanhe/pandawa-apexlang) di Oracle APEX 26.2.

Data di sandbox **dummy**.

Rancangan:

- [`docs/01-blueprint.md`](docs/01-blueprint.md)
- [`docs/02-frs.md`](docs/02-frs.md)

## Isi repository

| Path | Isi |
| --- | --- |
| `app.yaml` | Spesifikasi aplikasi (sumber generator) |
| `database/install.sql` | Install gabungan (generated + custom + seed) |
| `database/custom/`, `database/seed/` | Logic bisnis manual & data dummy |
| `database/admin/create_users.sql` | Buat user demo + role |
| `apex/<alias>/` | Source APEXlang (generated) |
| `tests/db/`, `tests/e2e/` | Test PL/SQL (CI) & Playwright |

## Instalasi di oracleapex.com

1. **Database:** SQL Workshop → SQL Scripts → Upload `database/install.sql` → Run, pastikan 0 error.
2. **Aplikasi:** App Builder → Import → `<alias>-apexlang.zip`. Ambil dari artifact CI `apexlang-root`, atau jalankan `scripts/generate.sh`. Pilih **Replace Existing Application** saat upgrade.
3. **User:** SQL Workshop → SQL Scripts → `database/admin/create_users.sql` → Run → **View Results** untuk melihat password.
   - Password **sama untuk semua user**: isi `c_password` di salinan file sebelum upload. Jangan di-commit. Password harus lolos password policy workspace.
   - `c_extra_admin`: username workspace Anda untuk didaftarkan sebagai ADMIN.
   - Mengganti password user yang sudah ada: jalankan `remove_users.sql`, lalu jalankan `create_users.sql` lagi.

## User & role

| Username | Role | Dipakai untuk |
| --- | --- | --- |

| Area | Role yang diizinkan |
| --- | --- |

Aturan umum:

- Maker-checker selalu berlaku.
- `ADMIN` lolos semua role.
- Selama belum ada ADMIN, semua user dianggap ADMIN (bootstrap).

## Simulasi

Gunakan jendela private berbeda untuk tiap user.

### A. <Skenario>

| # | User | Langkah | Hasil yang diharapkan |
| --- | --- | --- | --- |

## CI & test

- **CI:** generate up to date, `apex validate`, install + test PL/SQL di Oracle Free.
- **E2E Playwright (manual):** secret `APEX_APP_URL`, `APEX_USERNAME`, `APEX_PASSWORD`.

## Known issues

- **Side menu HP:** workaround `nav-fix.js` untuk bug Universal Theme 26.2.1.

## Di luar MVP

-
