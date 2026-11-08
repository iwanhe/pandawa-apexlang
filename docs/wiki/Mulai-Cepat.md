# Mulai Cepat

## 1. Siapkan repo

Pilih salah satu:

| Cara | Langkah |
| --- | --- |
| **Repo template** (disarankan) | GitHub → **Use this template → Create a new repository**. Skill sudah ada di `.claude/skills/`. |
| **Plugin Claude Code** | `claude plugin marketplace add iwanhe/pandawa-apexlang` lalu `claude plugin install pandawa-apexlang@pandawa` |
| **Skill claude.ai** | Unduh `pandawa-apexlang-skill.zip` dari artifact workflow **CI**, upload di Settings → Capabilities → Skills |

## 2. Tulis spesifikasi

1. Susun blueprint dan FRS di `docs/` (template ada di skill: `assets/templates/docs/`). Lihat [[Requirement dan Traceability|Requirement-dan-Traceability]].
2. Ganti isi `app.yaml` (contoh bawaan: DEMO Permintaan Barang). Lihat [[Fitur Generator|Fitur-Generator]].
3. Logic yang tidak bisa ditulis di spec: `database/custom/*.sql`. Data dummy: `database/seed/*.sql`.

Dengan Claude Code cukup minta: *"Pakai skill pandawa-apexlang, buat aplikasi &lt;X&gt; dari blueprint ini."*

## 3. Generate dan push

```bash
pip install pyyaml
scripts/doctor.sh                   # cek kesiapan (--deep: + generate ulang dan apex validate)
scripts/generate.sh                 # perhatikan SPEC ERROR dan SARAN
git add -A && git commit -m "Generate" && git push
```

CI menjalankan `apex validate` dan test database di Oracle Free. Jangan klaim "lolos" sebelum CI hijau.

## 4. Deploy ke oracleapex.com

1. SQL Workshop → SQL Scripts → jalankan `database/install.sql`.
2. App Builder → Import → `dist/<alias>-apexlang.zip` (artifact CI atau hasil generate lokal).
3. Salin `database/admin/create_users.sql`, isi `c_password` (password bersama, **jangan di-commit**) dan `c_extra_admin`, lalu jalankan.
4. Login dengan user demo dan jalankan skenario simulasi di FRS.

Bila import gagal dengan `ORDS Authentication request failed`, daftarkan schema lewat SQL Workshop → RESTful Services. Lihat [[Troubleshooting]].

## 5. E2E

Set secret GitHub `APEX_APP_URL`, `APEX_USERNAME`, `APEX_PASSWORD` (dan opsional `APEX_ROLE_PASSWORD`), lalu jalankan workflow **E2E Playwright**. Lihat [[Testing]].

Detail: [`deployment-testing.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/deployment-testing.md).
