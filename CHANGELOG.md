# Changelog

Semua perubahan toolkit pandawa-apexlang (generator, skill, template repo). Versi mengikuti `version` di [`plugins/pandawa-apexlang/.claude-plugin/plugin.json`](plugins/pandawa-apexlang/.claude-plugin/plugin.json). Setiap versi mencantumkan bukti pengujiannya; "belum diuji" ditulis apa adanya.

Proyek yang dibuat dari versi lama: ambil skill terbaru, jalankan `scripts/generate.sh`, lalu commit hasilnya.

## 1.6.0 – 2026-11-08

- `scripts/doctor.sh` (skill: `scripts/doctor.py`): cek kesiapan lingkungan dengan tingkat bukti *terbukti* / *terdeteksi*; `--deep` generate ulang di folder sementara dan menjalankan `apex validate`.
- Matriks acceptance per rilis: template `assets/templates/docs/04-acceptance.md` dan contoh DEMO `docs/04-acceptance.md`.
- Kebersihan repo: CHANGELOG, SECURITY, CONTRIBUTING, issue template; action GitHub di-pin ke SHA dengan `persist-credentials: false`; `scripts/check-links.py` di CI.
- `SKILL.md` diringkas; detail dipindah ke `references/`.

Bukti: lihat PR #7.

## 1.5.0 – 2026-11-04

- E2E akses per role (`roles.spec.ts`): satu user demo per role; halaman dan form (dibuka lewat dialog seperti user) harus terbuka atau "Akses ditolak" sesuai skema. Secret opsional `APEX_ROLE_PASSWORD`.
- Test fitur DEMO (`features.spec.ts`): REQ-4.3, 5.1, 7.1, 7.2, 7.3. Seed DEMO: department HR nonaktif.
- Generator menulis matriks akses dan halaman pembuka form ke `tests/e2e/pages.json`.
- Wiki di `docs/wiki/`, disinkronkan oleh workflow **Sinkron Wiki**.
- Gotcha E5 (halaman modal: HTTP 400, link `a-dialog-open`, field wajib) dan E6 (facet `role=option`).

Bukti: [CI 41924437313](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41924437313), [E2E 41924718277](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41924718277) (21 lulus). PR #5, #6. Run E2E pertama setelah PR #5 gagal karena asumsi test yang keliru; diperbaiki di PR #6.

## 1.4.0 – 2026-11-04

- Tabel keputusan pola halaman (`references/page-patterns.md`) dan `SARAN:` saat generate.
- Kolom `semantic: email | phone | url | npwp`: check constraint, normalisasi, jenis input, validasi format.

Bukti: [CI 41800404267](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41800404267). Validasi format di form MBMS belum dicoba di oracleapex.com. PR #4.

## 1.3.0 – 2026-11-04

- Referensi 18 halaman Oracle APEX UX Pattern Catalog 26.2 di skill (`references/ux-patterns/`).
- Overlay `apex-custom/` untuk halaman manual.
- FRS dengan REQ-ID gaya EARS, field `req:`, dan `docs/traceability.md`.

Bukti: [CI 41796375194](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41796375194). PR #3.

## 1.2.0 – 2026-11-04

- Faceted search (`list_type: faceted-cards | faceted-report`).
- Halaman master-detail (`workspace`).

Bukti: [CI 41789783914](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41789783914), [E2E 41794238601](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41794238601); import DEMO 1.2 ke oracleapex.com dicek manual. PR #2.

## 1.1.0 – 2026-11-04

- Metadata AI di `comments` halaman dan region.
- KPI dashboard sebagai metric card.
- Form drawer (`form_style`).
- Validasi ikon terhadap allowlist Font APEX.

Bukti: [CI 41782899815](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41782899815), [E2E 41787946791](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41787946791); metric card dan drawer dicek manual di oracleapex.com. PR #1.

## 1.0.0 – 2026-11-02

- Template awal: generator `app.yaml` → DDL, core security/penomoran/approval, trigger, view, aplikasi APEXlang, script user, konfigurasi E2E.
- CI: `apex validate` (SQLcl) dan install + test di Oracle Free. E2E Playwright (side menu HP, smoke test).
- Skill `pandawa-apexlang`, plugin marketplace, zip skill. Contoh DEMO dan MBMS.

Bukti: [CI 41338543814](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41338543814), [E2E 41426426517](https://github.com/iwanhe/pandawa-apexlang/actions/runs/41426426517); approval DEMO dicek manual di oracleapex.com.
