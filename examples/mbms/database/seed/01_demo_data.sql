--------------------------------------------------------------------------------
-- Script : 01_demo_data.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Data dummy MBMS (sandbox saja): BU, gudang, customer, vendor, item,
--          stok awal, job order brosur 10.000 (APPROVED), proyek conveyor + 6 WBS
--          (APPROVED), material issue, 1 PR draft.
--------------------------------------------------------------------------------

insert into apx_mbms_business_units (bu_code, bu_name) values ('PRT', 'Printing');
insert into apx_mbms_business_units (bu_code, bu_name) values ('ENG', 'Engineering');

insert into apx_mbms_warehouses (wh_code, wh_name, bu_id, location_type)
select 'WH-PRINT', 'Gudang Printing', bu_id, 'MAIN' from apx_mbms_business_units where bu_code = 'PRT';
insert into apx_mbms_warehouses (wh_code, wh_name, bu_id, location_type)
select 'WH-PRINT-SUB01', 'Lokasi Vendor Laminasi (dummy)', bu_id, 'VENDOR' from apx_mbms_business_units where bu_code = 'PRT';
insert into apx_mbms_warehouses (wh_code, wh_name, bu_id, location_type)
select 'WH-ENG', 'Gudang Engineering', bu_id, 'MAIN' from apx_mbms_business_units where bu_code = 'ENG';
insert into apx_mbms_warehouses (wh_code, wh_name, bu_id, location_type)
select 'WH-ENG-SITE01', 'Site Proyek Conveyor (dummy)', bu_id, 'SITE' from apx_mbms_business_units where bu_code = 'ENG';

insert into apx_mbms_customers (customer_code, customer_name, npwp, city, contact_person, phone, payment_term_days)
values ('C-0001', 'PT Contoh Retail Nusantara', '00.000.000.0-000.001', 'Jakarta', 'Budi', '021-0000001', 30);
insert into apx_mbms_customers (customer_code, customer_name, npwp, city, contact_person, phone, payment_term_days)
values ('C-0002', 'PT Contoh Pangan Makmur', '00.000.000.0-000.002', 'Bekasi', 'Sari', '021-0000002', 45);
insert into apx_mbms_customers (customer_code, customer_name, npwp, city, contact_person, phone, payment_term_days)
values ('C-0003', 'PT Contoh Logistik Andal', '00.000.000.0-000.003', 'Karawang', 'Andi', '0267-000003', 30);

insert into apx_mbms_vendors (vendor_code, vendor_name, vendor_type, city) values ('V-0001', 'CV Contoh Kertas Jaya', 'GOODS', 'Jakarta');
insert into apx_mbms_vendors (vendor_code, vendor_name, vendor_type, city) values ('V-0002', 'UD Contoh Laminasi', 'SUBCON', 'Tangerang');
insert into apx_mbms_vendors (vendor_code, vendor_name, vendor_type, city) values ('V-0003', 'PT Contoh Baja Perkasa', 'GOODS', 'Cilegon');

insert into apx_mbms_items (item_code, item_name, item_category, uom, bu_id, min_stock, std_cost)
select 'PRT-PAP-AP150', 'Kertas Art Paper 150gsm 65x100', 'RAW', 'LEMBAR', bu_id, 5000, 1600 from apx_mbms_business_units where bu_code = 'PRT';
insert into apx_mbms_items (item_code, item_name, item_category, uom, bu_id, min_stock, std_cost)
select 'PRT-INK-CMYK', 'Tinta Offset CMYK', 'RAW', 'KG', bu_id, 20, 120000 from apx_mbms_business_units where bu_code = 'PRT';
insert into apx_mbms_items (item_code, item_name, item_category, uom, bu_id, min_stock, std_cost)
select 'ENG-STL-UNP100', 'Besi UNP 100', 'RAW', 'BTG', bu_id, 20, 650000 from apx_mbms_business_units where bu_code = 'ENG';
insert into apx_mbms_items (item_code, item_name, item_category, uom, bu_id, min_stock, std_cost)
select 'ENG-STL-PLT6', 'Plat Baja 6mm 4x8', 'RAW', 'LBR', bu_id, 10, 2100000 from apx_mbms_business_units where bu_code = 'ENG';
insert into apx_mbms_items (item_code, item_name, item_category, uom, bu_id, min_stock, std_cost)
select 'ENG-CON-ELD', 'Elektroda Las RB26 2.6mm', 'CONSUMABLE', 'KG', bu_id, 25, 45000 from apx_mbms_business_units where bu_code = 'ENG';

declare
   l_prt  apx_mbms_business_units.bu_id%type;
   l_eng  apx_mbms_business_units.bu_id%type;
   l_c1   apx_mbms_customers.customer_id%type;
   l_c2   apx_mbms_customers.customer_id%type;
   l_c3   apx_mbms_customers.customer_id%type;
   l_job  apx_mbms_job_orders.job_id%type;
   l_prj  apx_mbms_projects.project_id%type;
   l_wbs2 apx_mbms_wbs.wbs_id%type;
   l_pr   apx_mbms_purchase_reqs.pr_id%type;

   -- PLS-00231: fungsi lokal tidak boleh dipakai di SQL, jadi lookup di prosedur lokal
   procedure txn (
      p_type in varchar2
     ,p_wh   in varchar2
     ,p_item in varchar2
     ,p_qty  in number
     ,p_cost in number default null
     ,p_job  in number default null
     ,p_prj  in number default null
     ,p_wbs  in number default null
     ,p_ref  in varchar2 default null
   )
   is
      l_wh   apx_mbms_warehouses.warehouse_id%type;
      l_item apx_mbms_items.item_id%type;
   begin
      select warehouse_id into l_wh from apx_mbms_warehouses where wh_code = p_wh;
      select item_id into l_item from apx_mbms_items where item_code = p_item;
      insert into apx_mbms_stock_txns (txn_type, warehouse_id, item_id, qty, unit_cost, job_id, project_id, wbs_id, reference)
      values (p_type, l_wh, l_item, p_qty, p_cost, p_job, p_prj, p_wbs, p_ref);
   end txn;

   procedure pr_line (
      p_pr    in number
     ,p_item  in varchar2
     ,p_qty   in number
     ,p_price in number
   )
   is
      l_item apx_mbms_items.item_id%type;
   begin
      select item_id into l_item from apx_mbms_items where item_code = p_item;
      insert into apx_mbms_pr_lines (pr_id, item_id, qty, unit_price) values (p_pr, l_item, p_qty, p_price);
   end pr_line;
begin
   select bu_id into l_prt from apx_mbms_business_units where bu_code = 'PRT';
   select bu_id into l_eng from apx_mbms_business_units where bu_code = 'ENG';
   select customer_id into l_c1 from apx_mbms_customers where customer_code = 'C-0001';
   select customer_id into l_c2 from apx_mbms_customers where customer_code = 'C-0002';
   select customer_id into l_c3 from apx_mbms_customers where customer_code = 'C-0003';

   txn('RECEIPT', 'WH-PRINT', 'PRT-PAP-AP150', 20000, 1600, p_ref => 'Saldo awal (dummy)');
   txn('RECEIPT', 'WH-PRINT', 'PRT-INK-CMYK', 50, 120000, p_ref => 'Saldo awal (dummy)');
   txn('RECEIPT', 'WH-ENG', 'ENG-STL-UNP100', 60, 650000, p_ref => 'Saldo awal (dummy)');
   txn('RECEIPT', 'WH-ENG', 'ENG-STL-PLT6', 15, 2100000, p_ref => 'Saldo awal (dummy)');
   txn('RECEIPT', 'WH-ENG', 'ENG-CON-ELD', 80, 45000, p_ref => 'Saldo awal (dummy)');

   apx_mbms_approval_pkg.set_bypass(true);
   insert into apx_mbms_job_orders (bu_id, customer_id, job_type, product_desc, qty_order, ups_per_sheet, insheet_pct, due_date,
                                    selling_price, est_paper, est_ink, est_plate, est_machine, est_finishing, est_labor, est_overhead, status)
   values (l_prt, l_c1, 'MTO', 'Brosur A4 4/4 Art Paper 150gsm, laminasi doff', 10000, 4, 5, trunc(sysdate) + 14,
           19500000, 8000000, 1200000, 800000, 2000000, 1500000, 500000, 1000000, 'APPROVED')
   returning job_id into l_job;
   insert into apx_mbms_job_orders (bu_id, customer_id, job_type, product_desc, qty_order, ups_per_sheet, insheet_pct, due_date,
                                    selling_price, est_paper, est_ink, est_plate, est_machine, est_finishing, est_labor, est_overhead, status)
   values (l_prt, l_c2, 'MTO', 'Kemasan karton lipat 3 warna', 5000, 2, 7, trunc(sysdate) + 21,
           14000000, 6000000, 900000, 600000, 1800000, 1200000, 400000, 800000, 'DRAFT');

   insert into apx_mbms_projects (bu_id, customer_id, project_name, project_type, contract_value, retention_pct,
                                  start_date, end_date, progress_pct, project_manager, status)
   values (l_eng, l_c3, 'Conveyor System Gudang Karawang', 'FABRICATION', 230000000, 5,
           trunc(sysdate) - 30, trunc(sysdate) + 60, 25, 'PM.DUMMY', 'APPROVED')
   returning project_id into l_prj;
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, cost_category, budget_amount) values (l_prj, '1.0', 'Engineering & Design', 'LABOR', 15000000);
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, cost_category, budget_amount) values (l_prj, '2.0', 'Procurement Material', 'MATERIAL', 80000000) returning wbs_id into l_wbs2;
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, cost_category, budget_amount) values (l_prj, '3.0', 'Workshop Fabrication', 'LABOR', 40000000);
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, cost_category, budget_amount) values (l_prj, '4.0', 'Surface Treatment', 'SUBCON', 10000000);
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, cost_category, budget_amount) values (l_prj, '5.0', 'Site Installation', 'SUBCON', 30000000);
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, cost_category, budget_amount) values (l_prj, '6.0', 'Testing & Commissioning', 'OTHER', 10000000);
   apx_mbms_approval_pkg.set_bypass(false);

   txn('ISSUE', 'WH-PRINT', 'PRT-PAP-AP150', 2650, p_job => l_job, p_ref => 'Issue kertas + insheet 5%');
   txn('ISSUE', 'WH-PRINT', 'PRT-INK-CMYK', 8, p_job => l_job, p_ref => 'Issue tinta');
   txn('ISSUE', 'WH-ENG', 'ENG-STL-UNP100', 40, p_prj => l_prj, p_wbs => l_wbs2, p_ref => 'Frame conveyor');
   txn('ISSUE', 'WH-ENG', 'ENG-STL-PLT6', 8, p_prj => l_prj, p_wbs => l_wbs2, p_ref => 'Plat dudukan');

   insert into apx_mbms_purchase_reqs (bu_id, purpose, project_id, wbs_id, need_date, description)
   values (l_eng, 'PROJECT', l_prj, l_wbs2, trunc(sysdate) + 7, 'Tambahan material frame conveyor')
   returning pr_id into l_pr;
   pr_line(l_pr, 'ENG-STL-UNP100', 10, 650000);
   pr_line(l_pr, 'ENG-CON-ELD', 20, 45000);
exception
   when others then
      apx_mbms_approval_pkg.set_bypass(false);
      raise;
end;
/

commit;
