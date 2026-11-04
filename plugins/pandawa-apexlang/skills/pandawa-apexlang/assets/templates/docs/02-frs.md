# FRS – <Nama Aplikasi> (lingkup MVP)

Referensi: `docs/01-blueprint.md`. Dokumen ini adalah sumber `app.yaml`.

## Cara menulis requirement (EARS)

Setiap requirement punya **ID unik** `REQ-<bagian>.<nomor>` (mis. `REQ-5.2`) dan ditulis dalam satu kalimat dengan salah satu pola EARS:

| Pola | Bentuk kalimat | Contoh |
| --- | --- | --- |
| Umum | Sistem harus <respons>. | Sistem harus menyimpan Item dengan kode unik. |
| Pemicu (event) | Ketika <pemicu>, sistem harus <respons>. | Ketika permintaan diajukan, sistem harus membuat approval untuk MANAGER. |
| Keadaan (state) | Selama <keadaan>, sistem harus <respons>. | Selama permintaan berstatus SUBMITTED, sistem harus mencegah perubahan. |
| Tidak diinginkan | Jika <kondisi>, maka sistem harus <respons>. | Jika pengaju menyetujui dokumennya sendiri, maka sistem harus menolak. |
| Opsional | Di mana <fitur/konfigurasi>, sistem harus <respons>. | Di mana approver level 2 diisi, sistem harus ... |

Aturan:

- Satu baris tabel = satu requirement. Kolom pertama berisi ID, kolom kedua kalimat EARS. Generator membaca baris seperti ini.
- ID tidak boleh dipakai ulang atau diubah setelah disepakati. Requirement yang dibatalkan: biarkan ID-nya, tulis "(dibatalkan)".
- Telusuri setiap ID:
  - **realisasi:** field `req:` di `app.yaml` (app, entitas, kolom, validasi, dokumen, laporan, KPI, chart), atau sebut ID di komentar `database/custom/*.sql` / `apex-custom/`;
  - **verifikasi:** sebut ID di test (`tests/db/*.sql`, `tests/e2e/tests/*.ts`), mis. di pesan assert.
- `scripts/generate.sh` membuat `docs/traceability.md` (status OK / Belum diuji / Belum direalisasi) dan gagal bila `app.yaml` merujuk ID yang tidak ada di FRS.

## 1. Lingkup

| Termasuk MVP | Di luar MVP (fase berikutnya) |
| --- | --- |

## 2. Aplikasi

| Atribut | Nilai |
| --- | --- |
| Kode aplikasi (prefix `APX_<KODE>_`) | |
| Alias APEX | |
| Nama | |

## 3. Role & akses

| Role | Deskripsi | Area/halaman yang boleh diubah |
| --- | --- | --- |
| ADMIN | Administrator | Semua + Users & Roles + Document Types |

Authorization scheme yang dibutuhkan:

| Skema | Role |
| --- | --- |

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-3.1 | Sistem harus hanya mengizinkan user dengan minimal satu role membuka halaman aplikasi. | MUST |

## 4. Entitas

Ulangi tabel ini untuk setiap entitas.

### 4.x <NAMA_ENTITAS> – <Label>

| Atribut | Nilai |
| --- | --- |
| Grup menu | master-data / transaksi / ... |
| Halaman (list, form) | 2xx / 3xx |
| Pola list | ir / faceted-cards / faceted-report (lihat "Memilih pola halaman" di app-spec) |
| Form | drawer / modal |
| Akses form | <skema> |
| Dokumen ber-approval? | ya/tidak (jenis, prefix, approver 1/2, limit, status operasional, kolom terkunci) |
| Detail dari | <entitas induk> (terkunci bila induk ≠ DRAFT/REJECTED) |
| Halaman master-detail | <nomor halaman workspace> / - |
| Immutable | ya/tidak |

| Kolom | Tipe | Wajib | Unik | Default | Keterangan / LOV |
| --- | --- | --- | --- | --- | --- |
| <ENTITAS>_ID | PK identity | ya | | | |

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-4.1 | | MUST |

## 5. Aturan bisnis & approval

| ID | Requirement (EARS) | Ditegakkan di | Pesan error |
| --- | --- | --- | --- |
| REQ-5.1 | Jika <kondisi>, maka sistem harus menolak <aksi>. | constraint / trigger / `APX_<APP>_..._PKG.check_x` (validate hook) / validasi halaman | |

## 6. Laporan & dashboard

| Halaman | Judul | View | Kolom |
| --- | --- | --- | --- |
| 4xx | | `APX_<APP>_..._V` | |

KPI home: ...

Chart: ...

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-6.1 | | MUST |

## 7. Peta halaman & UI

| No | Alias | Judul | Tipe | Skema |
| --- | --- | --- | --- | --- |
| 100 | home | Home | Dashboard | app-users |
| 190/191 | approval-inbox | Approval Inbox | IR + modal | app-users |
| 500/501 | users-roles | Users & Roles | IR + modal | admin-rights |

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-7.1 | Ketika side menu dibuka di layar HP, sistem harus tetap menampilkannya sampai user menutupnya. | MUST |

## 8. User demo & skenario simulasi

| Username | Role |
| --- | --- |

| Skenario | User | Langkah | Hasil yang diharapkan | REQ |
| --- | --- | --- | --- | --- |

## 9. Keputusan terbuka

| No | Pertanyaan | Dampak bila ditunda |
| --- | --- | --- |
