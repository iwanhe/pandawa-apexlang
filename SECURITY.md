# Keamanan

## Melaporkan masalah keamanan

Jangan buka issue publik untuk celah keamanan. Laporkan lewat **Security → Report a vulnerability** (GitHub private vulnerability reporting) di repo ini, atau langsung ke maintainer Tim PANDAWA. Sertakan langkah reproduksi dengan data dummy. Jangan sertakan password, token, atau data produksi.

Contoh yang termasuk masalah keamanan:

- halaman atau form yang terbuka untuk role yang seharusnya ditolak;
- SQL dinamis di generator atau core package yang bisa disusupi input user;
- script yang membocorkan kredensial ke log, artifact, atau repo.

## Aturan untuk repo ini dan proyek turunannya

- **Data sandbox selalu dummy.** Jangan memasukkan data pelanggan, karyawan, atau transaksi asli ke seed, test, atau screenshot.
- **Password tidak pernah di-commit.** `c_password` di `database/admin/create_users.sql` hanya diisi di salinan yang di-upload. Kredensial E2E disimpan di GitHub Secrets (`APEX_APP_URL`, `APEX_USERNAME`, `APEX_PASSWORD`, `APEX_ROLE_PASSWORD`), bukan di file atau chat.
- **Akun E2E khusus test** dengan role secukupnya, di workspace sandbox.
- **Setiap halaman punya authorization scheme** (standar Pandawa). Akses per role dibuktikan dengan `tests/e2e/tests/roles.spec.ts`; aturan bisnis (approval, penguncian) ditegakkan di package/trigger dan diuji di `tests/db/`.
- **Workflow GitHub Actions:** action di-pin ke SHA commit, `persist-credentials: false`, permission minimal (`contents: read`; `contents: write` hanya untuk Sinkron Wiki).
- **Generator tidak men-deploy apa pun.** Import ke APEX dilakukan manual oleh developer ke workspace dev/sandbox. Jangan pakai template ini untuk import langsung ke produksi.

## Dependensi pihak ketiga

- Skill APEXlang Oracle (`.claude/skills/apexlang/`) dan referensi UX Pattern Catalog / icon allowlist: UPL 1.0, Oracle.
- Playwright (test E2E) dan image `gvenzl/oracle-free` (test DB di CI).
