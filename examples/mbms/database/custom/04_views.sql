--------------------------------------------------------------------------------
-- Script : 04_views.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: View laporan & costing (dipakai halaman report dan dashboard)
--------------------------------------------------------------------------------

-- Posisi stok per item per gudang/lokasi
create or replace force view apx_mbms_stock_on_hand_v as
select w.warehouse_id
      ,w.wh_code
      ,w.wh_name
      ,i.item_id
      ,i.item_code
      ,i.item_name
      ,i.uom
      ,i.min_stock
      ,s.qty_on_hand
      ,apx_mbms_inv_pkg.avg_cost(i.item_id) avg_cost
      ,round(s.qty_on_hand * apx_mbms_inv_pkg.avg_cost(i.item_id), 2) stock_value
      ,case when s.qty_on_hand < i.min_stock then 'Y' else 'N' end below_min_yn
  from (select item_id
              ,warehouse_id
              ,sum(qty_signed) qty_on_hand
          from apx_mbms_stock_txns
         group by item_id, warehouse_id) s
  join apx_mbms_items i on i.item_id = s.item_id
  join apx_mbms_warehouses w on w.warehouse_id = s.warehouse_id;

-- Actual costing per job (D-07)
create or replace force view apx_mbms_job_cost_v as
select j.job_id
      ,j.job_no
      ,c.customer_name
      ,j.status
      ,j.qty_order
      ,j.qty_produced
      ,j.qty_reject
      ,j.insheet_pct
      ,case when j.qty_produced + j.qty_reject > 0
            then round(100 * j.qty_reject / (j.qty_produced + j.qty_reject), 2) end waste_pct
      ,j.selling_price
      ,j.est_hpp
      ,nvl(m.act_material, 0) act_material
      ,nvl(m.act_material, 0) + j.act_other_cost act_hpp
      ,j.est_hpp - (nvl(m.act_material, 0) + j.act_other_cost) hpp_variance
      ,case when j.selling_price > 0
            then round(100 * (j.selling_price - (nvl(m.act_material, 0) + j.act_other_cost)) / j.selling_price, 2) end act_margin_pct
  from apx_mbms_job_orders j
  left join apx_mbms_customers c on c.customer_id = j.customer_id
  left join (select job_id
                   ,-sum(qty_signed * nvl(unit_cost, 0)) act_material
               from apx_mbms_stock_txns
              where job_id is not null
                and txn_type in ('ISSUE', 'RETURN')
              group by job_id) m on m.job_id = j.job_id;

-- Budget vs actual per WBS
create or replace force view apx_mbms_wbs_budget_v as
select p.project_id
      ,p.project_no
      ,w.wbs_id
      ,w.wbs_code
      ,w.wbs_name
      ,w.budget_amount
      ,nvl(a.actual_amount, 0) actual_amount
      ,nvl(c.committed_amount, 0) committed_amount
      ,w.budget_amount - nvl(a.actual_amount, 0) - nvl(c.committed_amount, 0) remaining_amount
      ,case when w.budget_amount > 0
            then round(100 * (nvl(a.actual_amount, 0) + nvl(c.committed_amount, 0)) / w.budget_amount, 1) end used_pct
  from apx_mbms_wbs w
  join apx_mbms_projects p on p.project_id = w.project_id
  left join (select wbs_id
                   ,-sum(qty_signed * nvl(unit_cost, 0)) actual_amount
               from apx_mbms_stock_txns
              where wbs_id is not null
                and txn_type in ('ISSUE', 'RETURN')
              group by wbs_id) a on a.wbs_id = w.wbs_id
  left join (select r.wbs_id
                   ,sum(l.line_amount) committed_amount
               from apx_mbms_purchase_reqs r
               join apx_mbms_pr_lines l on l.pr_id = r.pr_id
              where r.wbs_id is not null
                and r.status in ('SUBMITTED', 'APPROVED')
              group by r.wbs_id) c on c.wbs_id = w.wbs_id;

-- Ringkasan proyek: kontrak, retensi, budget, aktual, peringatan
create or replace force view apx_mbms_project_summary_v as
select p.project_id
      ,p.project_no
      ,p.project_name
      ,c.customer_name
      ,p.status
      ,p.progress_pct
      ,p.contract_value
      ,round(p.contract_value * p.retention_pct / 100, 2) retention_amount
      ,nvl(b.budget_amount, 0) budget_amount
      ,nvl(a.actual_amount, 0) actual_amount
      ,nvl(b.budget_amount, 0) - nvl(a.actual_amount, 0) cost_variance
      ,case when nvl(b.budget_amount, 0) > p.contract_value then 'Y' else 'N' end loss_warning_yn
      ,case when p.end_date < trunc(sysdate) and p.status not in ('COMPLETED', 'CLOSED', 'CANCELLED') then 'Y' else 'N' end overdue_yn
  from apx_mbms_projects p
  join apx_mbms_customers c on c.customer_id = p.customer_id
  left join (select project_id, sum(budget_amount) budget_amount from apx_mbms_wbs group by project_id) b
         on b.project_id = p.project_id
  left join (select project_id
                   ,-sum(qty_signed * nvl(unit_cost, 0)) actual_amount
               from apx_mbms_stock_txns
              where project_id is not null
                and txn_type in ('ISSUE', 'RETURN')
              group by project_id) a on a.project_id = p.project_id;
