--------------------------------------------------------------------------------
-- Script : 05_stock_doc_types.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Jenis dokumen tanpa approval untuk penomoran stock ledger (GR/MI/MR/ADJ)
--------------------------------------------------------------------------------

merge into apx_mbms_doc_types t
using (select 'GR'  doc_type, 'Goods Receipt'    doc_name from dual union all
       select 'MI'  doc_type, 'Material Issue'   doc_name from dual union all
       select 'MR'  doc_type, 'Material Return'  doc_name from dual union all
       select 'ADJ' doc_type, 'Stock Adjustment' doc_name from dual) s
   on (t.doc_type = s.doc_type)
 when not matched then
      insert (doc_type, doc_name, prefix, table_name, pk_column, number_column, status_column)
      values (s.doc_type, s.doc_name, s.doc_type, 'APX_MBMS_STOCK_TXNS', 'TXN_ID', 'TXN_NO', 'STATUS');
commit;
