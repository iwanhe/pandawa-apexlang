--------------------------------------------------------------------------------
-- Script : 03_stock_post_trg.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Posting stock ledger (BR-05, BR-07): BU dari gudang, arah qty, biaya
--          rata-rata, stok tidak boleh minus, issue hanya ke job/proyek approved,
--          nomor GR/MI/MR/ADJ. Berjalan setelah trigger generated (audit, immutable).
--------------------------------------------------------------------------------

create or replace trigger apx_mbms_stock_txns_post_trg
before insert on apx_mbms_stock_txns
for each row
follows apx_mbms_stock_txns_trg
declare
   l_on_hand number;
   l_status  varchar2(30);
begin
   select bu_id
     into :new.bu_id
     from apx_mbms_warehouses
    where warehouse_id = :new.warehouse_id;
   :new.qty_signed := :new.qty * apx_mbms_inv_pkg.sign_of(:new.txn_type);

   -- WBS harus milik proyek yang sama
   if :new.wbs_id is not null then
      select project_id
        into :new.project_id
        from apx_mbms_wbs
       where wbs_id = :new.wbs_id;
   end if;

   -- material hanya di-issue ke job/proyek yang sudah disetujui
   if :new.txn_type in ('ISSUE', 'RETURN') then
      if :new.job_id is null and :new.project_id is null then
         raise_application_error(-20250, 'Issue/return material wajib mereferensikan Job Order atau Proyek (BR-05).');
      elsif :new.job_id is not null then
         select status into l_status from apx_mbms_job_orders where job_id = :new.job_id;
      else
         select status into l_status from apx_mbms_projects where project_id = :new.project_id;
      end if;
      if l_status not in ('APPROVED', 'IN_PROGRESS', 'COMPLETED') then
         raise_application_error(-20251, 'Material hanya dapat di-issue ke job/proyek yang sudah disetujui (status: ' || l_status || ').');
      end if;
   end if;

   -- transaksi keluar: biaya rata-rata, stok tidak boleh minus
   if :new.qty_signed < 0 then
      if :new.unit_cost is null then
         :new.unit_cost := apx_mbms_inv_pkg.avg_cost(:new.item_id);
      end if;
      l_on_hand := apx_mbms_inv_pkg.on_hand(:new.item_id, :new.warehouse_id);
      if l_on_hand < :new.qty then
         raise_application_error(-20252, 'Stok tidak cukup. On hand: ' || l_on_hand || ', diminta: ' || :new.qty);
      end if;
   elsif :new.txn_type = 'RETURN' and :new.unit_cost is null then
      :new.unit_cost := apx_mbms_inv_pkg.avg_cost(:new.item_id);
   end if;

   if :new.txn_no is null then
      :new.txn_no := apx_mbms_doc_pkg.next_no(
                        case :new.txn_type
                           when 'RECEIPT' then 'GR'
                           when 'ISSUE'   then 'MI'
                           when 'RETURN'  then 'MR'
                           else 'ADJ'
                        end
                       ,:new.txn_date);
   end if;
end;
/
