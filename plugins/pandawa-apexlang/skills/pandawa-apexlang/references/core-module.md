# Core module (dibuat generator untuk setiap aplikasi)

## Tabel

| Tabel | Isi |
| --- | --- |
| `APX_<APP>_ROLES` | Master role (dari `roles:`) |
| `APX_<APP>_USER_ROLES` | User APEX ↔ role. Username disimpan UPPERCASE |
| `APX_<APP>_DOC_TYPES` | Jenis dokumen: prefix nomor, tabel/kolom sumber, `amount_expr`, `validate_proc`, approver 1/2, `level2_limit` |
| `APX_<APP>_DOC_SEQ` | Counter nomor per jenis dokumen per tahun |
| `APX_<APP>_APPROVALS` | Langkah approval: level, role, nilai, requester, status, `acted_by`, catatan |

View: `APX_<APP>_APPROVALS_V` (+ `can_act_yn`) dan `APX_<APP>_USER_ROLES_V`.

## `APX_<APP>_SEC_PKG`

| API | Fungsi |
| --- | --- |
| `app_user` | `APP_USER` (APEX) atau `SESSION_USER`, uppercase |
| `has_role(p_role [, p_username])` / `has_role_yn` | ADMIN lolos semua. Mode bootstrap (belum ada ADMIN) → TRUE |
| `has_any_role([p_username])` | User terdaftar. Dipakai skema `app-users` |
| `bootstrap_mode` | TRUE bila belum ada user ber-role ADMIN |
| `set_test_user(p_username)` | **Hanya untuk unit test** di luar APEX |

## `APX_<APP>_DOC_PKG`

`next_no(p_doc_type [, p_date])` → `PREFIX-YYYY-NNNN`. Dipanggil trigger saat insert dokumen.

## `APX_<APP>_APPROVAL_PKG`

| API | Fungsi |
| --- | --- |
| `submit(p_doc_type, p_doc_id)` | Hanya dari DRAFT/REJECTED. Menjalankan `validate_proc`, lalu status `SUBMITTED` dan langkah level 1 dibuat. Tanpa approver1, langsung `APPROVED` |
| `approve(p_approval_id [, p_note])` | Cek maker-checker + role. Level 1 dengan `amount > level2_limit` dan approver2 → buat level 2. Bila tidak, dokumen `APPROVED` |
| `reject(p_approval_id, p_note)` | Catatan wajib. Dokumen `REJECTED` dan bisa diedit/diajukan ulang |
| `can_act_yn(p_approval_id)` | `Y` bila PENDING, bukan pengaju, dan punya role |
| `doc_amount(p_doc_type, p_doc_id)` | Evaluasi `amount_expr` |
| `bypass` / `set_bypass(bool)` | Trigger guard mengizinkan perubahan status saat TRUE. Hanya untuk engine & seed |

Perubahan status dokumen dilakukan lewat dynamic SQL. Nama tabel dan kolom berasal dari `DOC_TYPES` dan divalidasi `dbms_assert`. `amount_expr` berasal dari generator (`app.yaml`), bukan input user, dan tidak bisa diedit di halaman admin.

## Kode error

| Kode | Arti |
| --- | --- |
| -20100 | Jenis dokumen tidak dikenal |
| -20101 | Submit dari status selain DRAFT/REJECTED |
| -20105 | Approval sudah diproses |
| -20106 | Maker-checker: pengaju approve sendiri |
| -20107 | Tidak punya role approver |
| -20108 | Reject tanpa catatan |
| -20110 | Dokumen SUBMITTED terkunci |
| -20111 | Dokumen sudah CANCELLED/CLOSED |
| -20112 | Transisi status tidak diizinkan |
| -20120 | Entitas immutable diubah/dihapus |
| -20121 | Baris detail diubah saat induk terkunci |
| -202xx | Disarankan untuk validate hook & rule custom aplikasi |

## Trigger per entitas (`APX_<APP>_<TABEL>_TRG`)

- Mengisi kolom audit (`created_*` / `updated_*`) dan meng-UPPERCASE kolom bertipe `code`.
- Untuk entitas dokumen:
  - memaksa DRAFT saat insert dan memberi nomor;
  - mengunci dokumen SUBMITTED;
  - menolak transisi status ilegal;
  - mengembalikan kolom `lock` setelah approval.
- `parent:` mengunci baris detail bila induk tidak di `lock_unless`, dan aman terhadap delete cascade.
- `immutable:` menolak UPDATE/DELETE.
