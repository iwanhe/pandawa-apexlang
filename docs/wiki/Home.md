# Pandawa APEXlang

Template dan skill Tim PANDAWA untuk membangun aplikasi **Oracle APEX 26.2** dengan **APEXlang**, dari blueprint sampai aplikasi yang teruji di oracleapex.com.

```
Blueprint → FRS (REQ-ID, EARS) → app.yaml → generator → apex validate + test DB (CI)
          → import oracleapex.com → E2E Playwright → dokumentasi
```

Satu file spesifikasi (`app.yaml`) menghasilkan:

- tabel, constraint, trigger, view, dan data konfigurasi;
- **core module**: security per role, penomoran dokumen, approval engine 2 level dengan maker-checker;
- aplikasi APEXlang: dashboard, list (Interactive Report atau faceted search), form (drawer/modal), halaman master-detail, approval inbox, admin;
- script user, konfigurasi E2E, dan matriks traceability requirement.

## Mulai dari mana

| Saya ingin... | Baca |
| --- | --- |
| Membuat aplikasi baru | [[Mulai Cepat|Mulai-Cepat]] |
| Memahami fase kerja dan deliverable | [[Alur Kerja|Alur-Kerja]] |
| Tahu apa saja yang bisa ditulis di `app.yaml` | [[Fitur Generator|Fitur-Generator]] |
| Memilih list, form, atau dashboard yang tepat | [[Pola Halaman|Pola-Halaman]] |
| Menulis FRS dan menelusuri requirement | [[Requirement dan Traceability|Requirement-dan-Traceability]] |
| Menyiapkan CI dan E2E | [[Testing]] |
| Mengatasi error | [[Troubleshooting]] |
| Melihat perubahan per versi | [[Riwayat Versi|Riwayat-Versi]] |

## Sumber kebenaran

Wiki ini ringkasan. Detail resmi ada di repo:

- [`SKILL.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/SKILL.md): aturan dan alur untuk Claude;
- [`references/app-spec.md`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references/app-spec.md): format lengkap `app.yaml`;
- [`references/`](https://github.com/iwanhe/pandawa-apexlang/blob/main/plugins/pandawa-apexlang/skills/pandawa-apexlang/references): standar Pandawa, gotcha APEXlang, pola halaman, deployment & testing.

Contoh: [`app.yaml`](https://github.com/iwanhe/pandawa-apexlang/blob/main/app.yaml) (DEMO Permintaan Barang) dan [`examples/mbms`](https://github.com/iwanhe/pandawa-apexlang/blob/main/examples/mbms) (MBMS).
