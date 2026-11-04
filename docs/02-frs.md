# FRS – Demo Permintaan Barang (lingkup MVP)

Contoh FRS terisi untuk aplikasi DEMO di template ini. Untuk proyek baru, ganti isinya memakai template `plugins/pandawa-apexlang/skills/pandawa-apexlang/assets/templates/docs/02-frs.md` (cara menulis requirement EARS ada di sana).

Requirement memakai ID `REQ-<bagian>.<nomor>` dan kalimat EARS. Penelusurannya ke `app.yaml`, SQL custom, dan test ada di [`traceability.md`](traceability.md) (GENERATED).

## 1. Lingkup

| Termasuk MVP | Di luar MVP (fase berikutnya) |
| --- | --- |
| Master Department dan Item | Stok dan penerimaan barang di gudang |
| Permintaan barang dengan baris item | Integrasi ERP / purchase order |
| Approval 2 level (Manager, Director bila > Rp10 jt) | Notifikasi email |
| Rekap permintaan dan dashboard | Lampiran dokumen |

## 2. Aplikasi

| Atribut | Nilai |
| --- | --- |
| Kode aplikasi (prefix `APX_<KODE>_`) | DEMO |
| Alias APEX | DEMO |
| Nama | Demo Permintaan Barang |

## 3. Role & akses

| Role | Deskripsi | Area/halaman yang boleh diubah |
| --- | --- | --- |
| ADMIN | Administrator | Semua + Users & Roles + Document Types |
| REQUESTER | Pengaju permintaan | Permintaan Barang + baris |
| MANAGER | Department Manager, approver level 1 | Permintaan Barang + baris; approval |
| DIRECTOR | Approver level 2 | Approval |
| WAREHOUSE | Gudang | Master Department dan Item |

Authorization scheme yang dibutuhkan:

| Skema | Role |
| --- | --- |
| master-data | WAREHOUSE |
| requester | REQUESTER, MANAGER |
| warehouse | WAREHOUSE |

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-3.1 | Sistem harus hanya mengizinkan user dengan minimal satu role membuka halaman aplikasi. | MUST |
| REQ-3.2 | Sistem harus hanya mengizinkan role WAREHOUSE dan ADMIN membuat dan mengubah Department dan Item. | MUST |
| REQ-3.3 | Sistem harus hanya mengizinkan role REQUESTER, MANAGER, dan ADMIN membuat dan mengubah Permintaan Barang. | MUST |
| REQ-3.4 | Sistem harus hanya mengizinkan ADMIN mengelola user, role, dan konfigurasi approval. | MUST |

## 4. Entitas

### 4.1 DEPARTMENTS – Department

| Atribut | Nilai |
| --- | --- |
| Grup menu | master-data |
| Halaman (list, form) | 200 / 201 |
| Pola list / form | ir / drawer |
| Akses form | master-data |

| Kolom | Tipe | Wajib | Unik | Default | Keterangan / LOV |
| --- | --- | --- | --- | --- | --- |
| DEPARTMENT_ID | PK identity | ya | | | |
| DEPT_CODE | code (20) | ya | ya | | huruf besar |
| DEPT_NAME | text (100) | ya | | | |
| ACTIVE_YN | yn | | | Y | |

### 4.2 ITEMS – Item

| Atribut | Nilai |
| --- | --- |
| Grup menu | master-data |
| Halaman (list, form) | 210 / 211 |
| Pola list / form | faceted-cards / drawer |
| Akses form | master-data |

| Kolom | Tipe | Wajib | Unik | Default | Keterangan / LOV |
| --- | --- | --- | --- | --- | --- |
| ITEM_ID | PK identity | ya | | | |
| ITEM_CODE | code | ya | ya | | |
| ITEM_NAME | text | ya | | | |
| CATEGORY | enum | ya | | | ATK, IT, CONSUMABLE |
| UOM | code (10) | ya | | | satuan |
| STD_PRICE | money | ya | | 0 | ≥ 0 |
| ACTIVE_YN | yn | | | Y | |

### 4.3 REQUESTS – Permintaan Barang

| Atribut | Nilai |
| --- | --- |
| Grup menu | transaksi |
| Halaman (list, form) | 300 / 301; master-detail 302 |
| Pola list / form | faceted-report / modal |
| Akses form | requester |
| Dokumen ber-approval? | ya: REQ, prefix REQ, MANAGER → DIRECTOR bila nilai > 10.000.000; operasional FULFILLED, CLOSED; terkunci: DEPARTMENT_ID, PURPOSE, NEED_DATE |

| Kolom | Tipe | Wajib | Unik | Default | Keterangan / LOV |
| --- | --- | --- | --- | --- | --- |
| REQUEST_ID | PK identity | ya | | | |
| REQUEST_NO | nomor dokumen | ya | ya | otomatis | REQ-YYYY-NNNN |
| DEPARTMENT_ID | ref DEPARTMENTS | ya | | | department aktif |
| REQUEST_DATE | date | ya | | hari ini | |
| NEED_DATE | date | | | | ≥ REQUEST_DATE |
| PURPOSE | text (300) | ya | | | keperluan |
| NOTES | textarea | | | | |
| STATUS | status | ya | | DRAFT | otomatis |

### 4.4 REQUEST_LINES – Baris Permintaan

| Atribut | Nilai |
| --- | --- |
| Grup menu | transaksi |
| Halaman (list, form) | 310 / 311 |
| Pola list / form | ir / drawer |
| Akses form | requester |
| Detail dari | REQUESTS (terkunci bila induk ≠ DRAFT/REJECTED) |

| Kolom | Tipe | Wajib | Unik | Default | Keterangan / LOV |
| --- | --- | --- | --- | --- | --- |
| LINE_ID | PK identity | ya | | | |
| REQUEST_ID | ref REQUESTS | ya | | | |
| ITEM_ID | ref ITEMS | ya | | | item aktif |
| QTY | qty | ya | | | ≥ 0 |
| UNIT_PRICE | money | ya | | 0 | ≥ 0 |
| LINE_AMOUNT | money (virtual) | | | | QTY × UNIT_PRICE |

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-4.1 | Sistem harus menyimpan Department dengan kode unik dan nama. | MUST |
| REQ-4.2 | Sistem harus menyimpan Item dengan kode unik, kategori (ATK, IT, Consumables), satuan, dan harga standar tidak negatif. | MUST |
| REQ-4.3 | Selama Department atau Item tidak aktif, sistem harus menyembunyikannya dari pilihan di form permintaan. | SHOULD |
| REQ-4.4 | Ketika permintaan baru disimpan, sistem harus memberi nomor dokumen dengan format REQ-YYYY-NNNN. | MUST |
| REQ-4.5 | Sistem harus menghitung jumlah setiap baris sebagai qty × harga satuan dan nilai permintaan sebagai total jumlah baris. | MUST |

## 5. Aturan bisnis & approval

| ID | Requirement (EARS) | Ditegakkan di | Pesan error |
| --- | --- | --- | --- |
| REQ-5.1 | Jika tanggal dibutuhkan lebih awal dari tanggal permintaan, maka sistem harus menolak penyimpanan. | validasi halaman 301 | Tanggal dibutuhkan tidak boleh sebelum tanggal permintaan. |
| REQ-5.2 | Jika permintaan diajukan tanpa baris item, maka sistem harus menolak pengajuan. | `apx_demo_request_pkg.check_submit` (validate hook) | Permintaan belum memiliki baris item. (-20201) |
| REQ-5.3 | Ketika permintaan diajukan, sistem harus membuat langkah approval level 1 untuk role MANAGER. | approval engine | |
| REQ-5.4 | Ketika nilai permintaan melebihi Rp10.000.000, sistem harus menambahkan approval level 2 untuk role DIRECTOR. | approval engine (`level2_limit`) | |
| REQ-5.5 | Jika pengaju mencoba menyetujui dokumennya sendiri, maka sistem harus menolak aksi tersebut. | approval engine (maker-checker) | (-20106) |
| REQ-5.6 | Selama permintaan berstatus SUBMITTED, sistem harus mencegah perubahan header dan baris permintaan. | trigger dokumen dan baris | (-20110, -20121) |
| REQ-5.7 | Ketika permintaan berstatus APPROVED, sistem harus mempertahankan Department, Keperluan, dan Tanggal Dibutuhkan, tetapi mengizinkan status FULFILLED dan CLOSED. | trigger dokumen (`lock`, `operational`) | |
| REQ-5.8 | Jika approver menolak tanpa catatan, maka sistem harus menolak aksi reject. | approval engine | (-20108) |
| REQ-5.9 | Jika status dokumen diubah di luar approval engine dan bukan transisi operasional, maka sistem harus menolak perubahan itu. | trigger dokumen | (-20112) |

## 6. Laporan & dashboard

| Halaman | Judul | View | Kolom |
| --- | --- | --- | --- |
| 400 | Rekap Permintaan | `APX_DEMO_REQUEST_SUMMARY_V` | No, Department, Tanggal, Keperluan, Jml Baris, Total, Status |

KPI home: approval menunggu user, permintaan draft, permintaan menunggu approval.

Chart: permintaan per status (pie), nilai per department (bar).

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-6.1 | Sistem harus menampilkan rekap total nilai dan jumlah baris per permintaan beserta statusnya. | MUST |
| REQ-6.2 | Ketika user membuka Home, sistem harus menampilkan jumlah approval yang menunggu user tersebut, permintaan draft, dan permintaan yang menunggu approval. | MUST |
| REQ-6.3 | Ketika user membuka Home, sistem harus menampilkan grafik permintaan per status dan nilai permintaan per department. | SHOULD |

## 7. Peta halaman & UI

| No | Alias | Judul | Tipe | Skema |
| --- | --- | --- | --- | --- |
| 100 | home | Home | Dashboard | app-users |
| 190/191 | approval-inbox | Approval Inbox | IR + modal | app-users |
| 200/201 | departments | Departments | IR + drawer | app-users / master-data |
| 210/211 | items | Items | Faceted cards + drawer | app-users / master-data |
| 300/301 | requests | Permintaan Barang | Faceted report + modal | app-users / requester |
| 302 | permintaan-barang-detail | Detail Permintaan | Master-detail | app-users |
| 310/311 | request-lines | Baris Permintaan | IR + drawer | app-users / requester |
| 400 | rekap-permintaan | Rekap Permintaan | IR | app-users |
| 500/501 | users-roles | Users & Roles | IR + modal | admin-rights |
| 510/511 | document-types | Document Types & Approval | IR + modal | admin-rights |

| ID | Requirement (EARS) | Prioritas |
| --- | --- | --- |
| REQ-7.1 | Sistem harus memungkinkan user menyaring Item berdasarkan kategori dan status aktif. | SHOULD |
| REQ-7.2 | Sistem harus memungkinkan user menyaring Permintaan Barang berdasarkan status dan department. | SHOULD |
| REQ-7.3 | Sistem harus menampilkan header permintaan beserta baris itemnya dalam satu halaman, dan mengizinkan penambahan baris selama permintaan berstatus DRAFT atau REJECTED. | SHOULD |
| REQ-7.4 | Ketika side menu dibuka di layar HP, sistem harus tetap menampilkannya sampai user menutupnya. | MUST |
| REQ-7.5 | Sistem harus membuka setiap halaman utama tanpa error untuk user yang punya role. | MUST |

## 8. User demo & skenario simulasi

| Username | Role |
| --- | --- |
| DEMO_ADMIN | ADMIN |
| DEMO_REQ | REQUESTER |
| DEMO_MGR | MANAGER |
| DEMO_DIR | DIRECTOR |
| DEMO_WH | WAREHOUSE |
| DEMO_E2E | REQUESTER (akun E2E) |

| Skenario | User | Langkah | Hasil yang diharapkan | REQ |
| --- | --- | --- | --- | --- |
| Permintaan kecil | DEMO_REQ → DEMO_MGR | Buat permintaan, tambah baris < 10 jt, submit; Manager approve | APPROVED setelah level 1 | REQ-5.3 |
| Permintaan besar | DEMO_REQ → DEMO_MGR → DEMO_DIR | Baris > 10 jt, submit; Manager lalu Director approve | Level 2 dibuat; APPROVED setelah Director | REQ-5.4 |
| Maker-checker | DEMO_MGR | Ajukan sendiri lalu coba approve | Ditolak | REQ-5.5 |
| Reject | DEMO_MGR | Reject tanpa catatan, lalu dengan catatan | Pertama ditolak; kedua REJECTED | REQ-5.8 |

## 9. Keputusan terbuka

| No | Pertanyaan | Dampak bila ditunda |
| --- | --- | --- |
| - | (tidak ada untuk DEMO) | |
