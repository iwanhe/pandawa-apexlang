# Testing

| Lapisan | Dijalankan | Isi |
| --- | --- | --- |
| Generate + cek struktur | CI (push/PR) | output generate sudah di-commit, struktur `.apx` valid |
| `apex validate` | CI | SQLcl memvalidasi aplikasi APEXlang |
| Test database | CI, Oracle Free | install + compile + `tests/db/test_*.sql` (approval, lock, constraint, view laporan) |
| E2E Playwright | manual (workflow **E2E Playwright**) | aplikasi sungguhan di oracleapex.com |

## E2E

| File | Isi | Akun |
| --- | --- | --- |
| `smoke.spec.ts` | semua halaman non-modal terbuka tanpa error | `APEX_USERNAME` |
| `nav-menu.spec.ts` | side menu di HP tetap terbuka (regression Universal Theme 26.2.1) | `APEX_USERNAME` |
| `roles.spec.ts` | matriks akses per role: setiap halaman terbuka atau "Akses ditolak" sesuai skema, tombol Create sesuai role | user demo + `APEX_ROLE_PASSWORD` |
| `features.spec.ts` | fungsi spesifik aplikasi (contoh DEMO: validasi, LOV aktif, facet, master-detail) | `APEX_USERNAME` |

Secret (Settings → Secrets and variables → Actions):

| Secret | Isi |
| --- | --- |
| `APEX_APP_URL` | URL aplikasi, mis. `https://oracleapex.com/ords/r/<ws>/<alias>` |
| `APEX_USERNAME`, `APEX_PASSWORD` | akun khusus test, minimal 1 role |
| `APEX_ROLE_PASSWORD` (opsional) | password bersama user demo dari `create_users.sql`; tanpa ini `roles.spec.ts` di-skip |

Matriks akses dibaca dari `tests/e2e/pages.json` (GENERATED dari `app.yaml`), jadi ikut menyesuaikan saat spec berubah. Test fungsional baru: tambahkan di `features.spec.ts` dengan REQ-ID di judul test.

Report HTML, trace, video, dan screenshot tersedia sebagai artifact `playwright-report`; log browser dicetak ke log job bila test gagal.

Detail: [`deployment-testing.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/deployment-testing.md).
