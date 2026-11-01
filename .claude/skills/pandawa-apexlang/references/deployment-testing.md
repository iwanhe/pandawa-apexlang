# Deploy, CI, dan testing

## 1. CI (GitHub Actions, sudah ada di template)

| Workflow | Trigger | Isi |
| --- | --- | --- |
| `ci.yml` | push/PR | Untuk setiap `app.yaml` (root dan `examples/*`): generate → pastikan output sudah di-commit → SQLcl `apex validate` (tanpa DB) → artifact zip. **database-test**: container `gvenzl/oracle-free` → `database/install.sql` → compile schema, gagal bila ada objek INVALID → `tests/db/test_*.sql`. **skill**: `.claude/skills/pandawa-apexlang` sinkron dengan plugin, artifact zip skill |
| `e2e-playwright.yml` | manual | Playwright ke aplikasi di oracleapex.com: regression side menu (HP/desktop) dan smoke test semua halaman di `tests/e2e/pages.json` |

Secret untuk E2E: `APEX_APP_URL` (mis. `https://oracleapex.com/ords/r/<ws>/<alias>`), `APEX_USERNAME`, `APEX_PASSWORD`. Gunakan akun khusus test, mis. `<APP>_E2E`. Beri role yang cukup agar semua halaman di smoke test terbuka. Halaman list default memakai `app-users` = minimal 1 role.

## 2. Deploy ke oracleapex.com

1. **Database:** SQL Workshop → SQL Scripts → Upload `database/install.sql` → Run, pastikan 0 error.
   Instal ulang dari nol: jalankan dulu `database/generated/99_deinstall.sql`, yang menghapus semua objek `APX_<APP>_*`.
2. **Aplikasi:** App Builder → Import → `dist/<alias>-apexlang.zip` (dari generate lokal atau artifact CI `apexlang-root`). Upload apa adanya, jangan diekstrak.
   - Upgrade: pilih **Replace Existing Application**.
   - Bila muncul error ORDS, lihat gotcha I1.
3. **User:** SQL Workshop → SQL Scripts → `database/admin/create_users.sql` → Run → View Results (password tercetak di sini).
   - `c_password` (di salinan, jangan commit): password sama untuk semua user.
   - `c_extra_admin`: akun workspace Anda sebagai ADMIN.
   - Script aman dijalankan ulang. Untuk menghapus user: `remove_users.sql`.
4. **Uji:** login per user, lalu jalankan skenario simulasi di README.

## 3. Test lokal (opsional)

```bash
pip install pyyaml
scripts/generate.sh                                  # generate + cek struktur
SQLCL_BIN=~/sqlcl/bin/sql scripts/validate.sh        # apex validate (SQLcl 26.2+, Java 17/21)
DB_CONN=apx/pwd@localhost:1521/FREEPDB1 SQLCL_BIN=~/sqlcl/bin/sql tests/db/run.sh
cd tests/e2e && npm install && npx playwright install chromium
APEX_APP_URL=... APEX_USERNAME=... APEX_PASSWORD=... npx playwright test --project=mobile-chrome
```

Oracle Free lokal:

```bash
docker run -d -p 1521:1521 -e ORACLE_PASSWORD=x -e APP_USER=apx -e APP_USER_PASSWORD=pwd gvenzl/oracle-free:23-slim-faststart
```

## 4. Diagnosa bug UI tanpa akses browser user

1. Reproduksi dulu dengan Playwright di CI, misalnya emulasi HP Pixel 7.
2. Instrumentasi: rekam perubahan class body, event `theme42layoutchanged`, stack trace dari `apex.jQuery.event.trigger`, dan event pointer/focus/resize.
3. Cetak ke log job (artifact bisa tidak terjangkau dari sandbox agent).
4. Bandingkan dengan aplikasi wizard Oracle di workspace yang sama untuk membedakan bug platform dan bug aplikasi.
5. Uji workaround dengan menyuntikkan script (`page.addScriptTag`) ke aplikasi live **sebelum** deploy.

Teknik ini menemukan bug side menu Universal Theme 26.2.1 di MBMS setelah tiga tebakan gagal.
