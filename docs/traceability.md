# Traceability requirement (GENERATED)

Dibuat oleh generator dari `docs/02-frs.md`, `app.yaml` (field `req:`), `database/custom/`, `apex-custom/`, dan `tests/`. Jangan edit manual; jalankan `scripts/generate.sh`.

Ringkasan: 26 requirement. OK: 18, Belum diuji: 8.

Status: **OK** = ada realisasi dan test; **Belum diuji** = ada realisasi tanpa test; **Belum direalisasi** = belum dirujuk di spec/custom; **Tidak di FRS** = ID dirujuk tapi tidak didefinisikan di FRS.

| REQ | Requirement | app.yaml | Halaman | Realisasi lain | Test | Status |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-3.1 | Sistem harus hanya mengizinkan user dengan minimal satu role membuka halaman aplikasi. | `app` | - | - | `tests/e2e/tests/smoke.spec.ts` | OK |
| REQ-3.2 | Sistem harus hanya mengizinkan role WAREHOUSE dan ADMIN membuat dan mengubah Department dan Item. | `entities.DEPARTMENTS`<br>`entities.ITEMS` | 200, 201, 210, 211 | - | - | Belum diuji |
| REQ-3.3 | Sistem harus hanya mengizinkan role REQUESTER, MANAGER, dan ADMIN membuat dan mengubah Permintaan Barang. | `entities.REQUESTS`<br>`entities.REQUEST_LINES` | 300, 301, 302, 310, 311 | - | - | Belum diuji |
| REQ-3.4 | Sistem harus hanya mengizinkan ADMIN mengelola user, role, dan konfigurasi approval. | `app` | - | - | - | Belum diuji |
| REQ-4.1 | Sistem harus menyimpan Department dengan kode unik dan nama. | `entities.DEPARTMENTS` | 200, 201 | - | `tests/db/test_master_reports.sql` | OK |
| REQ-4.2 | Sistem harus menyimpan Item dengan kode unik, kategori (ATK, IT, Consumables), satuan, dan harga standar tidak negatif. | `entities.ITEMS` | 210, 211 | - | `tests/db/test_master_reports.sql` | OK |
| REQ-4.3 | Selama Department atau Item tidak aktif, sistem harus menyembunyikannya dari pilihan di form permintaan. | `entities.DEPARTMENTS.columns.ACTIVE_YN`<br>`entities.ITEMS.columns.ACTIVE_YN` | 200, 201, 210, 211 | - | - | Belum diuji |
| REQ-4.4 | Ketika permintaan baru disimpan, sistem harus memberi nomor dokumen dengan format REQ-YYYY-NNNN. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-4.5 | Sistem harus menghitung jumlah setiap baris sebagai qty × harga satuan dan nilai permintaan sebagai total jumlah baris. | `entities.REQUEST_LINES.columns.LINE_AMOUNT` | 310, 311 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.1 | Jika tanggal dibutuhkan lebih awal dari tanggal permintaan, maka sistem harus menolak penyimpanan. | `entities.REQUESTS.validations.NEED_DATE_AFTER_REQUEST_DATE` | 301 | - | - | Belum diuji |
| REQ-5.2 | Jika permintaan diajukan tanpa baris item, maka sistem harus menolak pengajuan. | `entities.REQUESTS.document` | 190, 191, 301 | `database/custom/01_request_pkg.sql` | `tests/db/test_approval.sql` | OK |
| REQ-5.3 | Ketika permintaan diajukan, sistem harus membuat langkah approval level 1 untuk role MANAGER. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.4 | Ketika nilai permintaan melebihi Rp10.000.000, sistem harus menambahkan approval level 2 untuk role DIRECTOR. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.5 | Jika pengaju mencoba menyetujui dokumennya sendiri, maka sistem harus menolak aksi tersebut. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.6 | Selama permintaan berstatus SUBMITTED, sistem harus mencegah perubahan header dan baris permintaan. | `entities.REQUESTS.document`<br>`entities.REQUEST_LINES` | 190, 191, 301, 310, 311 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.7 | Ketika permintaan berstatus APPROVED, sistem harus mempertahankan Department, Keperluan, dan Tanggal Dibutuhkan, tetapi mengizinkan status FULFILLED dan CLOSED. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.8 | Jika approver menolak tanpa catatan, maka sistem harus menolak aksi reject. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-5.9 | Jika status dokumen diubah di luar approval engine dan bukan transisi operasional, maka sistem harus menolak perubahan itu. | `entities.REQUESTS.document` | 190, 191, 301 | - | `tests/db/test_approval.sql` | OK |
| REQ-6.1 | Sistem harus menampilkan rekap total nilai dan jumlah baris per permintaan beserta statusnya. | `reports.rekap-permintaan` | 400 | `database/custom/02_views.sql` | `tests/db/test_master_reports.sql` | OK |
| REQ-6.2 | Ketika user membuka Home, sistem harus menampilkan jumlah approval yang menunggu user tersebut, permintaan draft, dan permintaan yang menunggu approval. | `dashboard.kpis.Approval Menunggu Anda`<br>`dashboard.kpis.Permintaan Draft`<br>`dashboard.kpis.Menunggu Approval` | 100 | - | `tests/db/test_master_reports.sql` | OK |
| REQ-6.3 | Ketika user membuka Home, sistem harus menampilkan grafik permintaan per status dan nilai permintaan per department. | `dashboard.charts.Permintaan per Status`<br>`dashboard.charts.Nilai per Department` | 100 | - | `tests/db/test_master_reports.sql` | OK |
| REQ-7.1 | Sistem harus memungkinkan user menyaring Item berdasarkan kategori dan status aktif. | `entities.ITEMS` | 210, 211 | - | - | Belum diuji |
| REQ-7.2 | Sistem harus memungkinkan user menyaring Permintaan Barang berdasarkan status dan department. | `entities.REQUESTS` | 300, 301, 302 | - | - | Belum diuji |
| REQ-7.3 | Sistem harus menampilkan header permintaan beserta baris itemnya dalam satu halaman, dan mengizinkan penambahan baris selama permintaan berstatus DRAFT atau REJECTED. | `entities.REQUESTS` | 300, 301, 302 | - | - | Belum diuji |
| REQ-7.4 | Ketika side menu dibuka di layar HP, sistem harus tetap menampilkannya sampai user menutupnya. | `app` | - | - | `tests/e2e/tests/nav-menu.spec.ts` | OK |
| REQ-7.5 | Sistem harus membuka setiap halaman utama tanpa error untuk user yang punya role. | `app` | - | - | `tests/e2e/tests/smoke.spec.ts` | OK |
