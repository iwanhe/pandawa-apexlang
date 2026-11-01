# Blueprint <Nama Sistem> – <Nama Perusahaan>

<Tanggal> · <Penyusun> · Versi <x.y>

## 1. Ringkasan eksekutif

<!-- 1 paragraf: sistem apa, untuk siapa, platform (Oracle APEX 26.2 + Database), tahap (sandbox oracleapex.com → server). -->

Keputusan inti:

- **<Keputusan 1>:** ...
- **Platform:** Oracle APEX 26.2 (APEXlang) + PL/SQL, modular monolith; sandbox oracleapex.com dengan data dummy.

## 2. Sasaran bisnis & prinsip desain

| Sasaran | Hasil yang diharapkan |
| --- | --- |
| <mis. Cost control> | <mis. HPP aktual per job> |

Prinsip desain (contoh):

- Shared core, separate operations.
- One transaction, one source of truth.
- Approval before execution.
- Traceability.
- Role-based access.

### Struktur modular

| Kelompok | Modul |
| --- | --- |
| <A. ...> | <...> |
| Shared services | Master data, approval, user & role, reporting |

## 3. Proses bisnis utama

### 3.1 <Alur A>

1. **<Langkah>:** ...

### 3.2 Functional requirements ringkas

| Modul | Fitur utama | Output |
| --- | --- | --- |

## 4. Approval, kontrol internal, business rule

### 4.1 Approval matrix

| Transaksi | Requester | Approver 1 | Approver 2 (bila > limit) |
| --- | --- | --- | --- |

Kontrol wajib:

- maker-checker;
- audit trail;
- dokumen terkunci saat menunggu approval;
- koreksi lewat transaksi reversal;
- period closing (bila relevan).

### 4.2 Akses berbasis peran

| Role | Area A | Area B | Shared |
| --- | --- | --- | --- |

### 4.3 Business rules

| No | Rule | Penjelasan |
| --- | --- | --- |
| BR-01 | | |

### 4.4 Penomoran dokumen

Format default generator: `PREFIX-YYYY-NNNN`.

| Dokumen | Prefix |
| --- | --- |

## 5. Keputusan platform

| Komponen | Pilihan | Catatan |
| --- | --- | --- |
| Database | <Oracle AI Database Free / ADB / SE2> | |
| Application | Oracle APEX 26.2 (APEXlang) | Template `pandawa-apexlang` |
| Source control & CI | GitHub + Actions | `apex validate`, test DB Oracle Free, E2E Playwright |

## 6. Roadmap & risiko

| Fase | Durasi | Isi |
| --- | --- | --- |
| 0 Sandbox/MVP | | |

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |

## 7. Keputusan (decision log)

| No | Keputusan | Hasil | Dampak |
| --- | --- | --- | --- |
| D-01 | | | |
