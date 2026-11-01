# Contoh: MBMS (PT. Multisarana Niaga Mandiri)

Contoh referensi besar hasil port MVP MBMS ke template pandawa-apexlang. Versi pertamanya ditulis tanpa template di repo `iwanhe/mnm-poc`.

| Bagian | Isi |
| --- | --- |
| Master | Business Unit, Customer, Vendor, Item, Gudang & lokasi (site/vendor subkon) |
| Printing | Job Order (dokumen JO, approval PRINT_MGR) dengan estimasi HPP 7 komponen. Costing aktual di laporan Job Costing |
| Engineering | Project (dokumen PRJ, ENG_MGR → DIRECTOR > 100 jt) + WBS budget (terkunci saat proyek diajukan) |
| Procurement | Purchase Requisition (dokumen PR, PROCUREMENT → DIRECTOR > 50 jt) + baris. Budget control BR-03 di `apx_mbms_rules_pkg.check_pr_submit` |
| Inventory | Stock ledger immutable. Posting di trigger custom `apx_mbms_stock_txns_post_trg`: BU dari gudang, biaya rata-rata, stok tidak minus, issue hanya ke job/proyek approved |
| Laporan | Job Costing, Project Summary, Budget vs Actual, Stock On Hand |

Generate:

```bash
scripts/generate.sh examples/mbms/app.yaml
```

Install mengikuti README utama, dengan file dari folder ini. Test rule ada di `tests/db/test_mbms_rules.sql` dan dijalankan CI di Oracle Free.
