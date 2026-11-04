# Requirement dan Traceability

## Menulis requirement (EARS)

Setiap requirement di `docs/02-frs.md` punya ID `REQ-<bagian>.<nomor>` dan satu kalimat dengan pola EARS:

| Pola | Bentuk |
| --- | --- |
| Umum | Sistem harus &lt;respons&gt;. |
| Pemicu | Ketika &lt;pemicu&gt;, sistem harus &lt;respons&gt;. |
| Keadaan | Selama &lt;keadaan&gt;, sistem harus &lt;respons&gt;. |
| Tidak diinginkan | Jika &lt;kondisi&gt;, maka sistem harus &lt;respons&gt;. |
| Opsional | Di mana &lt;fitur&gt;, sistem harus &lt;respons&gt;. |

Satu baris tabel = satu requirement (`| REQ-5.2 | Jika ... |`). ID tidak diubah setelah disepakati. Template: [`02-frs.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/assets/templates/docs/02-frs.md). Contoh terisi: [`docs/02-frs.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/docs/02-frs.md).

## Menelusuri

| Bukti | Tulis di |
| --- | --- |
| Realisasi di spec | `req:` di `app.yaml` (app, entitas, kolom, validasi, dokumen, laporan, KPI, chart) |
| Realisasi manual | komentar di `database/custom/*.sql` atau `apex-custom/` (`-- REQ-6.1: ...`) |
| Verifikasi | pesan assert `tests/db/*.sql` atau judul test `tests/e2e/tests/*.ts` |

## Hasil

`scripts/generate.sh`:

- gagal bila `app.yaml` merujuk REQ-ID yang tidak ada di FRS;
- menulis `## Requirements` di `comments` halaman;
- membuat [`docs/traceability.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/docs/traceability.md): per REQ-ID lokasi di spec, halaman, realisasi, test, dan status **OK / Belum diuji / Belum direalisasi / Tidak di FRS**.

Status **OK** berarti realisasi dan test sudah ada. Bukti lulus tetap dari CI dan E2E yang hijau.
