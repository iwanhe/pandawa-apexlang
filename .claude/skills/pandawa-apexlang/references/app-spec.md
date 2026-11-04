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
| `icon` | | `fa-table` | Ikon menu (Font APEX). Divalidasi terhadap allowlist |
| `display` | | kolom text pertama | Ekspresi SQL tampilan LOV, mis. `"code \|\| ' - ' \|\| name"` |
| `lov_where` | | | Filter tambahan LOV (bila ada kolom `ACTIVE_YN`, filter `= 'Y'` otomatis) |
| `operations` | | `[add, update, delete]` | Operasi form |
| `immutable` | | `false` | Trigger menolak UPDATE/DELETE (mis. ledger/transaksi stok) |
| `parent` | | | `{entity, column, lock_unless: [DRAFT, REJECTED]}`: baris detail terkunci bila dokumen induk tidak berstatus itu. FK otomatis `on delete cascade` |
| `validations` | | | `[{name, expr, message, item, when}]`. `expr` = ekspresi PL/SQL dengan `:P_KOLOM` (diganti nomor halaman otomatis). `when` = request (default CREATE,SAVE,SUBMIT) |
| `nav` | | `true` | Tampilkan di menu |
| `help` | | | Teks bantuan halaman list (tampil ke user) |
| `purpose` | | otomatis | Satu kalimat tujuan bisnis. Masuk ke `comments` halaman (metadata AI, tidak tampil ke user) |
| `list_type` | | `ir` | Halaman list: `ir` (Interactive Report), `faceted-cards` (faceted search + cards), `faceted-report` (faceted search + classic report). Lihat **Memilih pola halaman** |
| `workspace` | | | Halaman master-detail untuk entitas yang punya anak (`parent:`). `{page, label, alias, icon}` atau cukup nomor halaman. Lihat bawah |
| `form_style` | | `drawer` (non-dokumen), `modal` (dokumen) | `drawer`: panel kanan untuk form pendek, konteks list tetap terlihat. `modal`: dialog tengah untuk dokumen atau form panjang |
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
| `facet` | Jadikan facet di halaman faceted search. Default `true` untuk `enum`, `yn`, `ref` (plus `STATUS` dokumen); `false` untuk lainnya |

### `workspace` (master-detail)

```yaml
- name: REQUESTS
  pages: [300, 301]
  workspace: {page: 302, label: Detail Permintaan}   # alias default: <label_plural>-detail
```

Halaman 302 berisi:

- kiri (4 kolom): daftar induk; klik judul memilih baris (`P302_<PK>`);
- kanan (8 kolom): header (template Contextual Info) dengan tombol **Edit** (form induk), lalu satu region per entitas anak (`parent.entity = REQUESTS`) dengan tombol **Tambah** dan link edit ke form anak.

Tombol **Tambah** hanya tampil bila status induk ada di `lock_unless` (untuk dokumen). Penguncian tetap ditegakkan trigger. Halaman masuk menu di grup yang sama dan ke `tests/e2e/pages.json`. Pola ini deklaratif: memilih baris me-reload halaman, tanpa JavaScript custom.

### Memilih pola halaman

| Kebutuhan user | Pakai |
| --- | --- |
| Data banyak, user butuh sort/filter bebas, export, kolom bisa diatur | `list_type: ir` (default) |
| Master data yang dicari lewat beberapa dimensi (kategori, status, aktif) dan dikenali dari nama | `faceted-cards` |
| Dokumen/transaksi yang disaring per status/department lalu dibuka satu per satu | `faceted-report` |
| Dokumen dengan baris detail yang ditinjau atau diisi bersama header | `workspace` (sebagai tambahan halaman list) |
| Form pendek master data | `form_style: drawer` (default non-dokumen) |
| Form dokumen atau form panjang | `form_style: modal` (default dokumen) |

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
  kpis:                      # -> view APX_<APP>_DASH_KPI_V (1 baris per KPI: SEQ, ICON, LABEL, METRIC_VALUE)
    - {label: Approval Menunggu Anda, icon: fa-check-square-o, sql: "select count(*) from apx_x_approvals_v where status = 'PENDING' and can_act_yn = 'Y'"}
  charts:                    # tiap series -> view APX_<APP>_DASH_C<n>_S<m>_V (kolom LABEL, VALUE)
    - title: ...
      type: pie | bar
      series:
        - {name: ..., sql: "select x label, sum(y) value from ... group by x"}
```

KPI tampil sebagai **Metric Card** (template component Universal Theme): 1–2 KPI dua kolom, 3 KPI atau lebih empat kolom. `icon` opsional (default `fa-dashboard`). Sebaiknya 2–4 KPI yang sebanding.

## Ikon

Semua `icon:` (`groups`, `entities`, `reports`, `dashboard.kpis`) dicek terhadap `assets/apex-fa-icons-allowlist.txt` (1.488 ikon Font APEX, dari `oracle/apex` blueprints, lisensi UPL). Kelas pertama harus ikon yang valid; modifier seperti `fa-lg` boleh menyusul. Bila salah ketik: `SPEC ERROR: ITEMS: icon 'fa-tags-x' tidak ada di Font APEX (mungkin: fa-tags, fa-tag, fa-taxi)`.

## Metadata AI (`comments`)

Setiap halaman dan region hasil generate membawa `comments` (tidak tampil ke user), mengikuti konvensi Oracle APEX UX Pattern Catalog:

```text
## Purpose / ## When to Use / ## AI Guidance / ## Source     (halaman)
Intent: ... / Pattern role: ... / AI guidance: ...            (region)
```

Isinya diturunkan dari spec (`purpose`, `help`, `document`, `auth`, view sumber). `## Source` menyebut bagian `app.yaml` asal halaman itu.

## `users`

Daftar `{username, roles: [..], name}` untuk `database/admin/create_users.sql`. Sertakan akun E2E dengan **minimal satu role**. Setelah ADMIN pertama terdaftar, user tanpa role ditolak skema `app-users` di semua halaman, sehingga smoke test gagal.

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
| `workspace.page` | Master-detail per entitas yang punya `workspace` |
| 9999 | Login |
| 0 | Global page |
