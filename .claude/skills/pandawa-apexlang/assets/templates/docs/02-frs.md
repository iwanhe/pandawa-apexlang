# FRS – <Nama Aplikasi> (lingkup MVP)

Referensi: `docs/01-blueprint.md`. Dokumen ini adalah sumber `app.yaml`.

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

## 4. Entitas

Ulangi tabel ini untuk setiap entitas.

### 4.x <NAMA_ENTITAS> – <Label>

| Atribut | Nilai |
| --- | --- |
| Grup menu | master-data / transaksi / ... |
| Halaman (list, form) | 2xx / 3xx |
| Akses form | <skema> |
| Dokumen ber-approval? | ya/tidak (jenis, prefix, approver 1/2, limit, status operasional, kolom terkunci) |
| Detail dari | <entitas induk> (terkunci bila induk ≠ DRAFT/REJECTED) |
| Immutable | ya/tidak |

| Kolom | Tipe | Wajib | Unik | Default | Keterangan / LOV |
| --- | --- | --- | --- | --- | --- |
| <ENTITAS>_ID | PK identity | ya | | | |

## 5. Business rules

| No | Rule | Ditegakkan di | Pesan error |
| --- | --- | --- | --- |
| BR-01 | | constraint / trigger / `APX_<APP>_..._PKG.check_x` (validate hook) / validasi halaman | |

## 6. Laporan & dashboard

| Halaman | Judul | View | Kolom |
| --- | --- | --- | --- |
| 4xx | | `APX_<APP>_..._V` | |

KPI home: ...

Chart: ...

## 7. Peta halaman

| No | Alias | Judul | Tipe | Skema |
| --- | --- | --- | --- | --- |
| 100 | home | Home | Dashboard | app-users |
| 190/191 | approval-inbox | Approval Inbox | IR + modal | app-users |
| 500/501 | users-roles | Users & Roles | IR + modal | admin-rights |

## 8. User demo & skenario simulasi

| Username | Role |
| --- | --- |

| Skenario | User | Langkah | Hasil yang diharapkan |
| --- | --- | --- | --- |

## 9. Keputusan terbuka

| No | Pertanyaan | Dampak bila ditunda |
| --- | --- | --- |
