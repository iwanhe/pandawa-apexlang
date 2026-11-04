--------------------------------------------------------------------------------
-- Script : test_master_reports.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-04
-- Purpose: Test master data (constraint) dan view laporan/dashboard DEMO.
--          Setiap assert menyebut REQ-ID FRS agar tercatat di docs/traceability.md.
-- Jalankan setelah install.sql (lihat tests/db/run.sh). Raise error bila gagal.
-- SESUAIKAN dengan entitas aplikasi Anda bila app.yaml diganti.
--------------------------------------------------------------------------------
declare
   l_req    apx_demo_requests.request_id%type;
   l_total  number;
   l_lines  number;
   l_count  number;

   procedure assert_true (
      p_ok  in boolean
     ,p_msg in varchar2
   )
   is
   begin
      if not p_ok then
         raise_application_error(-20900, 'TEST GAGAL: ' || p_msg);
      end if;
      dbms_output.put_line('  ok  ' || p_msg);
   end assert_true;

   function expect_error (
      p_block in varchar2
     ,p_code  in number
   ) return boolean
   is
   begin
      execute immediate p_block;
      return false;
   exception
      when others then
         if sqlcode <> p_code then
            dbms_output.put_line('  (error lain: ' || sqlerrm || ')');
         end if;
         return sqlcode = p_code;
   end expect_error;
begin
   -- master data: constraint dari app.yaml (unique, min)
   assert_true(expect_error('insert into apx_demo_departments (dept_code, dept_name) '
                            || 'select dept_code, ''duplikat'' from apx_demo_departments where rownum = 1', -1),
               'REQ-4.1 kode department unik');
   assert_true(expect_error('insert into apx_demo_items (item_code, item_name, category, uom, std_price) '
                            || 'values (''T-NEG'', ''harga negatif'', ''ATK'', ''PCS'', -1)', -2290),
               'REQ-4.2 harga standar item tidak boleh negatif');
   assert_true(expect_error('insert into apx_demo_items (item_code, item_name, category, uom, std_price) '
                            || 'values (''T-CAT'', ''kategori salah'', ''LAIN'', ''PCS'', 0)', -2290),
               'REQ-4.2 kategori item hanya ATK, IT, CONSUMABLE');

   -- laporan rekap: total = jumlah baris (qty x harga)
   select min(request_id)
     into l_req
     from apx_demo_requests;
   select nvl(sum(qty * unit_price), 0)
         ,count(*)
     into l_total
         ,l_lines
     from apx_demo_request_lines
    where request_id = l_req;
   select count(*)
     into l_count
     from apx_demo_request_summary_v s
         ,apx_demo_requests r
    where r.request_id   = l_req
      and s.request_no   = r.request_no
      and s.total_amount = l_total
      and s.line_count   = l_lines
      and s.status       = r.status;
   assert_true(l_count = 1, 'REQ-6.1 rekap: total nilai, jumlah baris, dan status per permintaan');

   -- dashboard: satu baris per KPI, nilai sesuai data
   select count(*)
     into l_count
     from apx_demo_dash_kpi_v;
   assert_true(l_count = 3, 'REQ-6.2 view KPI berisi 3 KPI');
   select count(*)
     into l_count
     from apx_demo_dash_kpi_v k
    where k.label        = 'Permintaan Draft'
      and k.metric_value = (select count(*) from apx_demo_requests where status = 'DRAFT');
   assert_true(l_count = 1, 'REQ-6.2 KPI Permintaan Draft sesuai jumlah dokumen DRAFT');
   select count(*)
     into l_count
     from apx_demo_dash_c1_s1_v;
   assert_true(l_count >= 1, 'REQ-6.3 data chart permintaan per status tersedia');

   rollback;
   dbms_output.put_line('test_master_reports: LULUS');
exception
   when others then
      rollback;
      raise;
end;
/
