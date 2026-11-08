# Acceptance – <Nama Aplikasi> versi <x.y.z>

Satu file per rilis aplikasi (atau satu bagian per versi). Isi **hanya dengan bukti yang bisa dibuka ulang**: link run CI/E2E, nama file test, catatan uji manual (tanggal, user, hasil). Generator tidak menulis file ini.

## Status

| Status | Arti |
| --- | --- |
| **Terbukti** | Ada bukti yang dijalankan terhadap versi ini dan hasilnya lulus |
| **Belum** | Sudah dibuat, tetapi belum dijalankan/diamati untuk versi ini |
| **Terblokir** | Tidak bisa dibuktikan karena hambatan yang disebut (akses, data, lingkungan) |

Aturan:

- *Terdeteksi* bukan *terbukti*. SQLcl terpasang, test sudah ditulis, atau import berhasil **tidak** membuktikan halaman berfungsi.
- Hasil generator, compiler (`apex validate`), test database, E2E, dan uji manual dilaporkan terpisah. Satu tidak menggantikan yang lain.
- Bukti harus untuk commit yang dirilis. Run untuk commit lain dicatat sebagai **Belum**.
- Rilis ke pengguna baru boleh dilakukan bila semua kriteria MUST berstatus **Terbukti**, atau penyimpangan disetujui dan dicatat di bagian Keputusan.

## Identitas rilis

| Atribut | Nilai |
| --- | --- |
| Commit | `<sha>` |
| Tanggal | |
| Zip aplikasi | `dist/<alias>-apexlang.zip` (artifact CI run ...) |
| Lingkungan uji | mis. oracleapex.com workspace `<ws>` |

## Kriteria

| # | Kriteria | Prioritas | Bukti | Status |
| --- | --- | --- | --- | --- |
| A1 | Output generate sinkron dengan `app.yaml` | MUST | CI run `<link>` (job generate-validate) atau `scripts/doctor.sh --deep` | |
| A2 | `apex validate` lolos | MUST | CI run `<link>` | |
| A3 | Install + test database lolos di Oracle Free | MUST | CI run `<link>` (job database-test), file `tests/db/test_*.sql` | |
| A4 | Import ke lingkungan uji tanpa error | MUST | Catatan manual (tanggal, versi zip) | |
| A5 | Smoke test semua halaman | MUST | E2E run `<link>` (`smoke.spec.ts`) | |
| A6 | Akses per role sesuai skema (halaman dan form) | MUST | E2E run `<link>` (`roles.spec.ts`, laporan per user) | |
| A7 | Fungsi spesifik aplikasi | MUST | E2E run `<link>` (`features.spec.ts`) | |
| A8 | Simulasi skenario per role (FRS §8) | MUST | Catatan manual per skenario | |
| A9 | Tampilan HP (side menu, form, filter) | SHOULD | E2E `nav-menu.spec.ts` + cek manual | |
| A10 | Traceability: tidak ada REQ MUST "Belum direalisasi" | MUST | `docs/traceability.md` pada commit ini | |

## Uji manual

| Tanggal | Penguji | Skenario / halaman | Hasil | Catatan |
| --- | --- | --- | --- | --- |

## Batasan diketahui

| Hal yang belum terbukti | Alasan | Rencana |
| --- | --- | --- |

## Keputusan

| Keputusan | Disetujui oleh | Tanggal |
| --- | --- | --- |
