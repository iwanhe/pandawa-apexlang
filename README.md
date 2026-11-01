# pandawa-apexlang

[![CI](https://github.com/iwanhe/pandawa-apexlang/actions/workflows/ci.yml/badge.svg)](https://github.com/iwanhe/pandawa-apexlang/actions/workflows/ci.yml)

Template dan skill **Tim PANDAWA** untuk membangun aplikasi **Oracle APEX 26.2** dengan **APEXlang**, dari Blueprint sampai E2E testing.

```
Blueprint → FRS → app.yaml → generator → CI (apex validate + test DB Oracle) → oracleapex.com → simulasi & E2E Playwright
```

Spesifikasi aplikasi ditulis sekali di [`app.yaml`](app.yaml). Generator membuat semua bagian berikut, mengikuti **standar Pandawa** (`APX_<APP>_*`, rentang halaman, MVC, `package_version`, authorization di setiap halaman):

- tabel, constraint, trigger, dan view;
- **core module**: security/role, penomoran dokumen, approval engine 2 level dengan maker-checker;
- aplikasi APEXlang: home/dashboard, list + form, approval inbox, admin;
- script user;
- konfigurasi E2E.

Toolkit ini lahir dari proyek MBMS (PT. Multisarana Niaga Mandiri). Semua *lessons learned* dari proyek itu sudah ditanam di generator dan skill.

---

## Tiga cara memakai

### 1. Repository template: untuk proyek baru

1. Klik **Use this template → Create a new repository**. Alternatif: `gh repo create <org>/<repo> --template iwanhe/pandawa-apexlang --private --clone`.
2. Buka repo dengan Claude Code. Skill `pandawa-apexlang` dan skill APEXlang Oracle (26.2) otomatis aktif dari `.claude/skills/`.
3. Minta Claude: *"Pakai skill pandawa-apexlang, buat aplikasi <X> dari blueprint ini"*. Atau kerjakan manual mengikuti [alur kerja](plugins/pandawa-apexlang/skills/pandawa-apexlang/references/workflow.md).

### 2. Plugin Claude Code: dipakai di repo mana pun

```bash
claude plugin marketplace add iwanhe/pandawa-apexlang
claude plugin install pandawa-apexlang@pandawa
```

Di dalam sesi: `/plugin marketplace add iwanhe/pandawa-apexlang`. Skill tersedia sebagai `pandawa-apexlang:pandawa-apexlang`.

### 3. Skill di claude.ai

1. Unduh `pandawa-apexlang-skill.zip` dari artifact workflow **CI**, atau jalankan `scripts/build-skill-zip.sh`.
2. Upload di claude.ai → Settings → Capabilities → Skills, atau sebagai skill organisasi.

---

## Mulai cepat

```bash
pip install pyyaml
scripts/generate.sh            # app.yaml -> database/, apex/<alias>/, tests/e2e/pages.json, dist/<alias>-apexlang.zip
git add -A && git commit -m "Generate" && git push   # CI: apex validate + test database
```

Deploy ke oracleapex.com:

1. SQL Workshop → SQL Scripts → `database/install.sql`.
2. App Builder → Import → `dist/<alias>-apexlang.zip`.
3. SQL Workshop → SQL Scripts → `database/admin/create_users.sql`.

Lihat [deployment-testing.md](plugins/pandawa-apexlang/skills/pandawa-apexlang/references/deployment-testing.md).

`app.yaml` bawaan berisi contoh **DEMO Permintaan Barang**:

- master Department & Item;
- dokumen Permintaan dengan approval Manager → Director (> 10 jt);
- baris detail terkunci saat diajukan;
- laporan rekap;
- dashboard.

Ganti isinya dengan aplikasi Anda.

## Struktur

| Path | Isi |
| --- | --- |
| `app.yaml` | **Spesifikasi aplikasi Anda** (format: [app-spec.md](plugins/pandawa-apexlang/skills/pandawa-apexlang/references/app-spec.md)) |
| `docs/` | Blueprint & FRS proyek (template: `assets/templates/docs/` di skill) |
| `database/custom/`, `database/seed/` | Logic bisnis manual (package, view laporan, validate hook) & data dummy |
| `database/generated/`, `database/install.sql`, `database/admin/` | **Generated.** Jangan diedit |
| `apex/<alias>/` | **Generated** source APEXlang |
| `tests/db/` | Runner + test PL/SQL (dijalankan CI di Oracle Free) |
| `tests/e2e/` | Playwright: regression side menu (HP) & smoke test semua halaman |
| `scripts/` | `generate.sh`, `validate.sh`, `sync-skill.sh`, `build-skill-zip.sh` |
| `plugins/pandawa-apexlang/` | **Plugin & skill kanonik:** `SKILL.md`, `references/`, `assets/`, `scripts/apexgen/` (generator) |
| `.claude/skills/pandawa-apexlang/` | Salinan skill (disinkronkan `scripts/sync-skill.sh`, dicek CI) |
| `.claude/skills/apexlang/` | Skill APEXlang resmi Oracle (folder 26.2, UPL) |
| `.claude-plugin/marketplace.json` | Marketplace plugin `pandawa` |
| `examples/` | Contoh aplikasi lain |

## CI

| Workflow | Isi |
| --- | --- |
| **CI** (`ci.yml`, push/PR) | Untuk setiap `app.yaml`: generate → output sudah di-commit → SQLcl `apex validate` → artifact zip. Install di **Oracle Free** + compile + `tests/db/test_*.sql`. Skill sinkron + artifact zip skill |
| **E2E Playwright** (manual) | Butuh secret `APEX_APP_URL`, `APEX_USERNAME`, `APEX_PASSWORD` |

## Mengembangkan toolkit ini

1. Ubah generator, skill, atau referensi **hanya** di `plugins/pandawa-apexlang/skills/pandawa-apexlang/`.
2. Jalankan `scripts/sync-skill.sh` dan `scripts/generate.sh`.
3. Commit, lalu push. CI memastikan semua contoh tetap lolos `apex validate` dan test database.
4. Naikkan `version` di `plugins/pandawa-apexlang/.claude-plugin/plugin.json` untuk rilis plugin.

Lisensi skill APEXlang Oracle: UPL 1.0 (`.claude/skills/apexlang/LICENSE.txt`).
