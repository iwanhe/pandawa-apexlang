--------------------------------------------------------------------------------
-- Script : 01_inv_pkg.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Stock ledger helper (on hand, biaya rata-rata) - BR-04, BR-07
--------------------------------------------------------------------------------

create or replace package apx_mbms_inv_pkg as
   /**
    * Versi package (format XX.YY.ZZ).
    * @return versi
    */
   function package_version return varchar2;

   /**
    * Arah transaksi: +1 untuk RECEIPT/RETURN/ADJ_IN, -1 lainnya.
    * @param p_txn_type  tipe transaksi
    * @return 1 atau -1
    */
   function sign_of (
      p_txn_type in varchar2
   ) return number;

   /**
    * Stok on hand item di gudang/lokasi.
    * @param p_item_id       item
    * @param p_warehouse_id  gudang/lokasi
    * @return qty on hand
    */
   function on_hand (
      p_item_id      in number
     ,p_warehouse_id in number
   ) return number;

   /**
    * Biaya rata-rata (moving average dari transaksi masuk), fallback std cost.
    * @param p_item_id  item
    * @return biaya per unit
    */
   function avg_cost (
      p_item_id in number
   ) return number;
end apx_mbms_inv_pkg;
/

create or replace package body apx_mbms_inv_pkg as

   function package_version return varchar2
   is
   begin
      -- Version History:
      -- 01.00.00 2026-11-01 Tim PANDAWA  Port dari MBMS MVP (mnm-poc)
      return '01.00.00';
   end package_version;

   function sign_of (
      p_txn_type in varchar2
   ) return number
   is
   begin
      return case when p_txn_type in ('RECEIPT', 'RETURN', 'ADJ_IN') then 1 else -1 end;
   end sign_of;

   function on_hand (
      p_item_id      in number
     ,p_warehouse_id in number
   ) return number
   is
      l_qty number;
   begin
      select nvl(sum(qty_signed), 0)
        into l_qty
        from apx_mbms_stock_txns
       where item_id      = p_item_id
         and warehouse_id = p_warehouse_id;
      return l_qty;
   end on_hand;

   function avg_cost (
      p_item_id in number
   ) return number
   is
      l_cost number;
   begin
      select case when sum(qty) > 0 then round(sum(qty * nvl(unit_cost, 0)) / sum(qty), 2) end
        into l_cost
        from apx_mbms_stock_txns
       where item_id = p_item_id
         and txn_type in ('RECEIPT', 'ADJ_IN');
      if l_cost is null then
         select std_cost
           into l_cost
           from apx_mbms_items
          where item_id = p_item_id;
      end if;
      return l_cost;
   end avg_cost;

end apx_mbms_inv_pkg;
/
