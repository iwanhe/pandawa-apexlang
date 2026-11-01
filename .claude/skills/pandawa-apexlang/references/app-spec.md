# Referensi `app.yaml`

Contoh lengkap ada di `app.yaml` pada template repo (aplikasi DEMO Permintaan Barang). Generator memvalidasi spec dan berhenti dengan `SPEC ERROR: ...` bila ada yang salah.

## `app`

| Field | Wajib | Default | Keterangan |
| --- | --- | --- | --- |
| `code` | ya | | 2–10 karakter A–Z0–9. Prefix objek DB: `APX_<CODE>_` (standar Pandawa) |
| `alias` | | `code` | Alias aplikasi APEX. Folder output `apex/<alias>/` dan zip `dist/<alias>-apexlang.zip` |
| `name` | | `code` | Nama aplikasi |
| `logo` | | `code` | Teks logo di header |
| `author` | | `Tim PANDAWA` | Dipakai di header script & version history |
| `date` | | `lihat git log` | Tanggal di header script. Tetap, supaya output deterministik |
| `description` | | `name` | Subjudul home |
| `nav_fix` | | `true` | Muat `js/nav-fix.js` (workaround side menu HP, Universal Theme 26.2.1) |

## `roles`

Format `KODE: Nama`. `ADMIN` selalu ditambahkan. Role disimpan di `APX_<APP>_ROLES`; user ↔ role di `APX_<APP>_USER_ROLES`.

## `authorizations`

Format `nama-skema: [ROLE, ...]`. Dua skema selalu tersedia:

- `app-users`: user terdaftar, yaitu punya minimal 1 role (atau mode bootstrap).
- `admin-rights`: role `ADMIN`.

Role `ADMIN` lolos semua skema.

## `groups`

Format `kode-grup: {name, icon}`. Urutan grup menentukan urutan menu dan page group. Grup `home` dan `administration` dibuat otomatis.

## `entities`

Satu entitas menghasilkan:

- tabel `APX_<APP>_<NAME>`, trigger `_TRG`, view `_V`, LOV;
- halaman list (Interactive Report) dan form (modal);
- menu dan breadcrumb.

| Field | Wajib | Default | Keterangan |
| --- | --- | --- | --- |
| `name` | ya | | Nama tabel tanpa prefix, mis. `CUSTOMERS` |
| `pk` | ya | | Kolom PK identity, mis. `CUSTOMER_ID`. Pandawa: item `P201_CUSTOMER_ID`, bukan `P201_ID` |
| `group` | ya | | Kode grup menu |
| `pages` | ya | | `[list, form]`. Ikuti rentang Pandawa: 200 master, 300 transaksi |
| `label` / `label_plural` | | dari name | Judul halaman/menu |
| `list_alias` / `form_alias` | | kebab dari label | Alias halaman (friendly URL) |
| `auth` | | `app-users` | Skema untuk halaman form + tombol Create |
| `view_auth` | | `app-users` | Skema untuk halaman list |
| `icon` | | `fa-table` | Ikon menu (Font APEX) |
| `display` | | kolom text pertama | Ekspresi SQL tampilan LOV, mis. `"code \|\| ' - ' \|\| name"` |
| `lov_where` | | | Filter tambahan LOV (bila ada kolom `ACTIVE_YN`, filter `= 'Y'` otomatis) |
| `operations` | | `[add, update, delete]` | Operasi form |
| `immutable` | | `false` | Trigger menolak UPDATE/DELETE (mis. ledger/transaksi stok) |
| `parent` | | | `{entity, column, lock_unless: [DRAFT, REJECTED]}`: baris detail terkunci bila dokumen induk tidak berstatus itu. FK otomatis `on delete cascade` |
| `validations` | | | `[{name, expr, message, item, when}]`. `expr` = ekspresi PL/SQL dengan `:P_KOLOM` (diganti nomor halaman otomatis). `when` = request (default CREATE,SAVE,SUBMIT) |
| `nav` | | `true` | Tampilkan di menu |
| `help` | | | Teks bantuan halaman list |
| `document` | | | Jadikan entitas dokumen ber-approval (lihat bawah) |
| `columns` | ya | | Daftar kolom |

### `columns`

| Field | Keterangan |
| --- | --- |
| `name` | Nama kolom (UPPERCASE) |
| `type` | `text` (varchar2 200), `code` (varchar2 30, otomatis UPPER), `textarea` (1000), `number`, `int`, `money`, `qty`, `pct`, `date`, `yn` (Y/N, default Y), `enum`, `ref` |
| `size` | Panjang varchar2 |
| `label` | Label item/kolom |
| `required` | NOT NULL + item wajib |
| `unique` | Constraint `_Un` |
| `default` | Default kolom & item (literal) |
| `default_sql` | Default item dari query (mis. `select trunc(sysdate) from dual`) |
| `min` / `max` | Check constraint + batas number field |
| `values` | Untuk `enum`: list atau `{KODE: Label}`, menghasilkan check constraint + LOV statis |
| `ref` | Untuk `ref`: nama entitas. Menghasilkan FK + index `_Nn`, select list LOV entitas, kolom `<KOLOM>_DSP` di view |
| `lov_sql` / `cascade` | LOV inline khusus (`select d, r ...`). Pakai `:P_KOLOM` untuk item di halaman yang sama (diganti `:P<page>_KOLOM`). `cascade: KOLOM_INDUK` untuk cascading LOV (mis. WBS per proyek) |
| `virtual` | Ekspresi kolom virtual (mis. `qty * unit_price`). Tampil read-only |
| `form` | `edit` (default), `display`, `hidden`, `none` |
| `list` | Tampil di IR (default true) |
| `readonly_when` | Ekspresi PL/SQL read-only item |
| `on_delete` | `cascade` untuk FK ref |
| `help` | Inline help item |

### `document` (approval)

| Field | Keterangan |
| --- | --- |
| `type` | Kode jenis dokumen (unik), mis. `REQ`. Disimpan di `APX_<APP>_DOC_TYPES` |
| `name`, `prefix` | Nama dan prefix nomor. Nomor: `PREFIX-YYYY-NNNN` |
| `number` | Kolom nomor dokumen (dibuat otomatis, unik) |
| `amount` | Ekspresi SQL nilai dokumen dengan alias tabel `t`, boleh scalar subquery |
| `approver1`, `approver2`, `level2_limit` | Role approver level 1 & 2. Level 2 hanya bila `amount > level2_limit` |
| `validate` | `paket.prosedur`, signature `(p_doc_id in number)`. Dipanggil saat submit, `raise_application_error` untuk menolak |
| `operational` | Status setelah APPROVED yang boleh diubah user (mis. `[IN_PROGRESS, COMPLETED, CLOSED]`) |
| `lock` | Kolom yang dibekukan setelah approval (trigger mengembalikan nilai lama, item read-only) |

Kolom `STATUS` dibuat otomatis. Status dasar: `DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `CANCELLED`, ditambah `operational`.

Trigger menegakkan aturan berikut:

- Dokumen baru selalu `DRAFT`.
- Dokumen `SUBMITTED` terkunci.
- Perubahan status hanya lewat approval engine. Pengecualian: transisi operasional, dan `CANCELLED` dari DRAFT/REJECTED.

Approver dan limit bisa diubah admin di halaman **Document Types & Approval** (510).

## `reports`

Halaman IR read-only dari view custom (`database/custom/*.sql`).

| Field | Keterangan |
| --- | --- |
| `page`, `title`, `group` | Wajib. Rentang 400 |
| `view` | Nama view, tanpa prefix boleh (`JOB_COST_V` → `apx_<app>_job_cost_v`) |
| `columns` | `[{name, label, type}]`, type: `text`, `number`, `money`, `qty`, `pct`, `date`, `hidden`. Harus sama dengan kolom view |
| `sort`, `auth`, `icon`, `help` | Opsional |

## `dashboard` (halaman 100)

```yaml
dashboard:
  title: ...
  subtitle: ...
  kpis:                      # -> view APX_<APP>_DASH_KPI_V
    - {label: Approval Menunggu Anda, sql: "select count(*) from apx_x_approvals_v where status = 'PENDING' and can_act_yn = 'Y'"}
  charts:                    # tiap series -> view APX_<APP>_DASH_C<n>_S<m>_V (kolom LABEL, VALUE)
    - title: ...
      type: pie | bar
      series:
        - {name: ..., sql: "select x label, sum(y) value from ... group by x"}
```

## `users`

Daftar `{username, roles: [..], name}` untuk `database/admin/create_users.sql`. Sertakan akun E2E tanpa role, atau dengan role bila smoke test perlu membuka halaman ber-otorisasi.

## `custom_sql`, `seed_sql`

Daftar file relatif ke folder `app.yaml`. Urutan di `database/install.sql`:

1. generated (tabel, package core, trigger, view)
2. `custom_sql`
3. config seed (role, doc types)
4. `seed_sql`

Custom SQL boleh membuat view/package/trigger tambahan dengan prefix yang sama. Untuk trigger tambahan pada tabel generated, gunakan `follows apx_<app>_<tabel>_trg`.

## Halaman yang selalu dibuat

| Halaman | Isi |
| --- | --- |
| 100 | Home/dashboard |
| 190/191 | Approval inbox / aksi (bila ada dokumen) |
| 500/501 | Users & Roles |
| 510/511 | Document Types & Approval (bila ada dokumen) |
| 9999 | Login |
| 0 | Global page |
