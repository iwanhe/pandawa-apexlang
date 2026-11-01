# Standar Pandawa yang diterapkan generator

Ringkasan dari skill `oracle-dev-standards` dan `apex-qa-pandawa`, sebatas yang dipakai template ini. Untuk detail lengkap, rujuk skill tersebut.

## Penamaan objek database (prefix `APX_<APP>_`)

| Objek | Format | Contoh (APP = DEMO) |
| --- | --- | --- |
| Tabel | `APX_<APP>_<NAMA>` | `apx_demo_requests` |
| View | `..._V` | `apx_demo_requests_v`, `apx_demo_request_summary_v` |
| Package | `..._PKG` | `apx_demo_approval_pkg`, `apx_demo_request_pkg` |
| Trigger | `..._TRG` | `apx_demo_requests_trg` |
| PK / unique / check / FK | `<tabel>_PK`, `_U1`, `_CK1`, `_FK1` | `apx_demo_requests_u1` |
| Index non-unique | `<tabel>_N1` | `apx_demo_request_lines_n1` |

## PL/SQL

- **Format:**
  - lowercase;
  - indentasi 3 spasi;
  - koma di depan;
  - satu perintah per baris;
  - `loop`, `else`, `when` di baris baru.
- **Variabel:**
  - `l_` lokal, `g_` global, `k_` konstanta;
  - `p_` parameter in, `x_` parameter out;
  - `r_` record, `t_` tabel, `e_` exception.
- **Deklarasi:** anchored (`%type`, `%rowtype`).
- **Setiap package:**
  - fungsi `package_version` (format `XX.YY.ZZ` + version history);
  - JavaDoc di setiap function/procedure.
- **Setiap script:** header berisi Script, Author, Date, Purpose.
- **Exception:** jangan `when others then null`. Selalu `raise` ulang atau tangani spesifik.
- **Dynamic SQL:** bind variable. Untuk nama objek dari konfigurasi, pakai `dbms_assert.simple_sql_name` / `qualified_sql_name`.

## APEX

- **Nomor halaman:**

  | Rentang | Isi |
  | --- | --- |
  | 1–99 | Sistem |
  | 100–199 | Home, dashboard, approval inbox |
  | 200–299 | Master data |
  | 300–399 | Transaksi |
  | 400–499 | Laporan |
  | 500–599 | Admin |

  Pengecualian: login tetap 9999 (konvensi APEX).
- **Setiap halaman wajib punya:**
  - alias (kebab-case);
  - page group;
  - authorization scheme.

  Generator memasang `app-users` sebagai default.
- **Page item:** `P<page>_<KOLOM>`, sama dengan nama kolom tabel/view.
- **Process:** `INIT_<X>_FORM` (pre-render), `SAVE_<X>` (DML), `CALL_<AKSI>` (eksekusi package), `CLOSE_DIALOG`.
- **Dynamic action:** deskriptif, mis. `ON_DIALOG_CLOSED_REFRESH_REPORT`, `ON_CLICK_CANCEL_CLOSE_DIALOG`.
- **MVC:**
  - Region IR membaca view `*_V`.
  - Dashboard membaca view `*_DASH_*_V`.
  - Approval dan validasi memanggil package.
  - Untuk filter berbasis page item, pakai pola dynamic view dengan `/*+ MATERIALIZE */` dan `APEX_UTIL.GET_SESSION_STATE` (lihat `apex-qa-pandawa`).
- **Authorization scheme:** berbasis package function (`APX_<APP>_SEC_PKG.has_role`).

## Checklist sebelum commit

- [ ] `scripts/generate.sh` sudah dijalankan dan outputnya ikut di-commit.
- [ ] Custom SQL: header, `package_version` di-bump, JavaDoc, format Pandawa.
- [ ] Tidak ada literal password atau data nyata.
- [ ] Test PL/SQL di `tests/db/` diperbarui untuk rule baru.
- [ ] README aplikasi: user/role dan skenario simulasi diperbarui.
