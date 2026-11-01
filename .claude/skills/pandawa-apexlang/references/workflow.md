# Alur kerja per fase

Setiap fase punya input, langkah, deliverable, dan **gate**. Jangan lanjut ke fase berikutnya sebelum gate fase sebelumnya terpenuhi. Contoh prompt ditulis dari sudut pandang developer ke Claude.

---

## Fase 0: Setup

1. Buat repo proyek dari template: GitHub → `iwanhe/pandawa-apexlang` → **Use this template**. Alternatif:
   ```bash
   gh repo create <org>/<repo> --template iwanhe/pandawa-apexlang --private --clone
   ```
2. Siapkan workspace oracleapex.com (sandbox) dan catat versi APEX di Help → About. Versi harus 26.2.
3. Isi secret repo (Settings → Secrets → Actions) untuk E2E: `APEX_APP_URL`, `APEX_USERNAME`, `APEX_PASSWORD`. Boleh menyusul di fase 7.

**Gate:** repo ada, CI pertama (dengan app DEMO bawaan) hijau.

> Prompt: "Pakai skill pandawa-apexlang. Saya mau mulai proyek baru <nama>. Cek repo ini sudah dari template dan CI-nya hijau."

## Fase 1: Blueprint

- **Input:** catatan bisnis, kuesioner, dokumen existing.
- **Langkah:** salin `assets/templates/docs/01-blueprint.md` ke `docs/01-blueprint.md`, lalu isi:
  - sasaran bisnis;
  - struktur modul;
  - proses end-to-end;
  - keputusan (D-xx);
  - risiko;
  - keputusan platform (APEX 26.2, sandbox oracleapex.com → server sendiri).
- **Deliverable:** `docs/01-blueprint.md`.

**Gate:** keputusan terbuka yang memengaruhi MVP sudah dijawab user. Contoh: costing method, satu atau banyak BU, approval matrix.

> Prompt: "Dari dokumen ini susun blueprint mengikuti template Pandawa. Tandai keputusan yang masih terbuka."

## Fase 2: FRS (Functional Requirement Specification)

- **Langkah:** salin `assets/templates/docs/02-frs.md` ke `docs/02-frs.md`. Untuk **lingkup MVP**, isi:
  - daftar entitas, kolom, dan tipe datanya;
  - business rule (BR-xx) beserta lokasi penegakannya: constraint, trigger, package, atau validasi halaman;
  - approval matrix: dokumen, approver 1, approver 2, dan limit;
  - matriks role × area;
  - peta halaman (nomor mengikuti rentang Pandawa);
  - laporan dan dashboard (KPI, chart);
  - user demo dan skenario simulasi.
- Tandai yang **di luar MVP** secara eksplisit.

**Gate:** user menyetujui lingkup MVP.

## Fase 3: Spec (`app.yaml`)

- Terjemahkan FRS → `app.yaml` (`references/app-spec.md`). Pemetaannya:

  | FRS | app.yaml |
  | --- | --- |
  | Tabel | `entities[]` |
  | Approval | `document:` |
  | Header-detail | `parent:` di entitas detail |
  | Ledger yang tidak boleh diubah | `immutable: true` |
  | Laporan | `reports[]` + view di custom SQL |
  | Role dan akses | `roles` + `authorizations` |
  | User demo | `users` |

- Jalankan `scripts/generate.sh`. Perbaiki `SPEC ERROR` sampai lolos.

**Gate:** generate dan pemeriksaan struktur OK.

## Fase 4: Logic custom

Logic custom yang **tidak bisa** diekspresikan spec ditulis di `database/custom/NN_*.sql` mengikuti standar Pandawa:

- **Validate hook dokumen** (budget check, kelengkapan): `procedure check_x (p_doc_id in number)` → `raise_application_error(-202xx, 'pesan')`.
- **View laporan & costing:** `APX_<APP>_<NAMA>_V`.
- **Trigger tambahan:** mis. posting stok. Gunakan `follows apx_<app>_<tabel>_trg`.
- **Data dummy:** `database/seed/*.sql`. Bila memasukkan dokumen berstatus APPROVED, gunakan `apx_<app>_approval_pkg.set_bypass(true)`, lalu kembalikan ke false.
- **Test:** `tests/db/test_*.sql` menguji rule dengan `apx_<app>_sec_pkg.set_test_user`. Contoh: `tests/db/test_approval.sql`.

**Gate:** CI `database-test` hijau.

## Fase 5: Generate & CI

1. `scripts/generate.sh`, lalu commit **semua** output: `apex/`, `database/`, `tests/e2e/pages.json`.
2. Push. Workflow **CI** menjalankan:
   - pengecekan output generate sudah di-commit;
   - SQLcl `apex validate`;
   - install di Oracle Free + compile + test PL/SQL;
   - sinkronisasi skill.
3. Bila gagal, baca log (File/Line/Type untuk apex validate, `user_errors` untuk DB), perbaiki spec atau custom, lalu ulangi.

**Gate:** CI hijau. Artifact `apexlang-root` berisi zip siap import.

## Fase 6: Deploy sandbox (oracleapex.com)

Lihat `references/deployment-testing.md` §2:

1. Jalankan `database/install.sql` lewat SQL Workshop → SQL Scripts.
2. Import zip.
3. Jalankan `database/admin/create_users.sql`.

**Gate:** login berhasil sebagai tiap user demo, dan menu tampil sesuai role.

## Fase 7: Simulasi & E2E

1. Tulis skenario simulasi per role di README aplikasi: langkah, user, hasil yang diharapkan. Hitung angka dari data seed, misalnya sisa anggaran dan level approval.
2. Jalankan simulasi manual di browser. Pakai jendela private berbeda untuk tiap user.
3. Jalankan workflow **E2E Playwright**:
   - `mobile-chrome`: regression side menu;
   - `desktop-chrome`: smoke test semua halaman.
4. Bug UI yang sulit ditebak: tambahkan instrumentasi ke test (timeline event, stack trace) dan baca log job. **Jangan menebak berulang.**

**Gate:** skenario simulasi lulus, E2E hijau.

## Fase 8: Dokumentasi & handover

README aplikasi dibuat dari `assets/templates/docs/03-app-readme.md` dan berisi:

- isi repo;
- instalasi;
- **user yang perlu dibuat**, beserta role dan cara password sama/acak;
- skenario simulasi;
- CI/E2E;
- known issue;
- di luar MVP.

Lalu tag rilis (mis. `v0.1.0-mvp`).

---

## Perubahan berikutnya (iterasi)

- **Tambah entitas, kolom, atau halaman:** edit `app.yaml`, lalu generate, commit, CI, import (Replace Existing Application), dan jalankan E2E.
- **Ubah tampilan halaman di Page Designer:** export APEXlang → commit ke `apex/<alias>/`. Catat di README bahwa halaman tersebut tidak lagi dari generator.
- **Data:** script migrasi baru di `database/custom/` harus idempotent, atau script terpisah di `database/migration/`.
