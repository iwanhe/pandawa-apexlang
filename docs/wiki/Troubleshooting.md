# Troubleshooting

Mulai dengan `scripts/doctor.sh` (tambah `--deep` untuk membuktikan output generate sinkron dan `apex validate` lolos). Daftar lengkap ada di skill: [`references/troubleshooting.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/troubleshooting.md).

| Gejala | Penyebab paling mungkin | Solusi |
| --- | --- | --- |
| `SPEC ERROR: ...` | `app.yaml` tidak valid (halaman bentrok, role/ikon/REQ-ID tidak dikenal, file custom tidak ada) | Baca pesan; ikon salah ketik diberi saran terdekat |
| CI "Output generator berbeda" | Lupa generate/commit | `scripts/generate.sh`, lalu commit semua output |
| `apex validate` gagal | Sintaks `.apx` | Lihat File/Line/Type; [`apexlang-gotchas.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/apexlang-gotchas.md) |
| CI database-test: objek INVALID | Error di SQL custom/view | `user_errors` tercetak di log |
| `PLS-00231` | Fungsi lokal blok anonim dipakai di SQL | Pakai variabel atau prosedur lokal |
| `ORA-04091 mutating table` | Trigger membaca tabelnya sendiri pada `INSERT ... SELECT` | Insert per baris (`VALUES`) atau compound trigger |
| Import: `ORDS Authentication request failed. Reason: Not Found` | Schema belum terdaftar di ORDS | SQL Workshop → RESTful Services → Register Schema with ORDS |
| Halaman "Akses ditolak ... APP_USERS" | User belum punya role; mode bootstrap berakhir saat ADMIN pertama terdaftar | Administration → Users & Roles, atau insert ke `APX_<APP>_USER_ROLES` |
| Side menu di HP langsung menutup | Bug Universal Theme 26.2.1 | `app.nav_fix: true` (default) memuat `nav-fix.js` |
| E2E: `networkidle` timeout | APEX menjaga koneksi terbuka | Tunggu `load` + `.t-Body` (helper sudah melakukannya) |
| E2E: "Login gagal: masih di halaman login" padahal kredensial benar | Redirect lambat | Helper menunggu URL keluar dari login (maks. 60 s) |
| Check constraint `_CKn` dilanggar saat input | Format kolom `semantic` | Pesan validasi di form menjelaskan formatnya |
