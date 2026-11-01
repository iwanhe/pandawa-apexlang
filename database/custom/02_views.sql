--------------------------------------------------------------------------------
-- Script : 02_views.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: View laporan (dipakai halaman report di app.yaml)
--------------------------------------------------------------------------------

create or replace force view apx_demo_request_summary_v as
select r.request_id
      ,r.request_no
      ,d.dept_name
      ,r.request_date
      ,r.purpose
      ,(select count(*) from apx_demo_request_lines l where l.request_id = r.request_id) line_count
      ,(select nvl(sum(l.line_amount), 0) from apx_demo_request_lines l where l.request_id = r.request_id) total_amount
      ,r.status
  from apx_demo_requests r
  join apx_demo_departments d on d.department_id = r.department_id;
