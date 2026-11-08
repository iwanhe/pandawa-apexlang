# Troubleshooting

Mulai dengan `scripts/doctor.sh` (atau `python3 <skill>/scripts/doctor.py app.yaml`). Tambah `--deep` untuk membuktikan output generate sinkron dan `apex validate` lolos.

| Gejala | Penyebab paling mungkin | Solusi / rujukan |
| --- | --- | --- |
| `SPEC ERROR: ...` | `app.yaml` tidak valid: halaman bentrok, role/ikon/REQ-ID tidak dikenal, file custom tidak ada | Baca pesannya; ikon salah ketik diberi saran terdekat. `app-spec.md` |
| `SARAN: ...` saat generate | Spec bertentangan dengan tabel pola halaman | Ikuti saran, atau catat alasan menyimpang di FRS. `page-patterns.md` §8 |
| CI "Output generator berbeda" | Lupa generate/commit, atau file generated diedit manual | `scripts/generate.sh`, commit semua output; `scripts/doctor.sh --deep` menunjukkan filenya |
| `apex validate` gagal | Sintaks `.apx` | Baca File/Line/Type dan nilai valid yang disebut; `apexlang-gotchas.md`. Jangan menebak properti |
| CI database-test: objek INVALID | Error di custom SQL/view | `user_errors` tercetak di log |
| `PLS-00231` | Fungsi lokal blok anonim dipakai di SQL | Pakai variabel atau prosedur lokal (gotcha P1) |
| `ORA-04091 mutating table` | Trigger membaca tabelnya sendiri pada `INSERT ... SELECT` | Insert per baris (`VALUES`) atau compound trigger (P2, P6) |
| Submit ditolak `-201xx` | Validate hook / aturan bisnis custom | Pesan error dari package custom |
| Import: `ORDS Authentication request failed. Reason: Not Found` | Schema belum terdaftar di ORDS | SQL Workshop → RESTful Services → Register Schema with ORDS (I1) |
| Halaman "Akses ditolak ... APP_USERS" | User belum punya role; mode bootstrap berakhir saat ADMIN pertama terdaftar | Administration → Users & Roles, atau insert ke `APX_<APP>_USER_ROLES` (I4) |
| Side menu di HP langsung menutup | Bug Universal Theme 26.2.1 | `app.nav_fix: true` (default) memuat `nav-fix.js` (R3) |
| Check constraint `_CKn` dilanggar | Format kolom `semantic` | Pesan validasi di form menjelaskan formatnya |
| E2E: `networkidle` timeout | APEX menjaga koneksi terbuka | Tunggu `load` + `.t-Body` (E1) |
| E2E: form tidak tampil / HTTP 400 | Halaman modal dibuka langsung lewat URL | `openDialog()`: klik pemicunya (E5) |
| E2E: kontrol facet tidak ketemu | Checkbox facet tersembunyi | `getByRole('option', ...)` (E6) |
| E2E: "Login gagal" padahal kredensial benar | Redirect lambat | Helper menunggu URL keluar dari login (maks. 60 s) |
| E2E akses per role di-skip | Secret `APEX_ROLE_PASSWORD` belum di-set | Isi dengan password bersama dari `create_users.sql` |
