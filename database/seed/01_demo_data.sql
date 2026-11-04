--------------------------------------------------------------------------------
-- Script : 01_demo_data.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Data dummy untuk sandbox (jangan dipakai di produksi)
--------------------------------------------------------------------------------

insert into apx_demo_departments (dept_code, dept_name) values ('FIN', 'Finance');
insert into apx_demo_departments (dept_code, dept_name) values ('OPS', 'Operations');
insert into apx_demo_departments (dept_code, dept_name) values ('IT', 'Information Technology');
-- department nonaktif: tidak boleh muncul di pilihan form permintaan (REQ-4.3, tests/e2e)
insert into apx_demo_departments (dept_code, dept_name, active_yn) values ('HR', 'Human Resources (nonaktif)', 'N');

insert into apx_demo_items (item_code, item_name, category, uom, std_price) values ('ATK-001', 'Kertas A4 80gsm', 'ATK', 'RIM', 55000);
insert into apx_demo_items (item_code, item_name, category, uom, std_price) values ('ATK-002', 'Pulpen Hitam', 'ATK', 'BOX', 30000);
insert into apx_demo_items (item_code, item_name, category, uom, std_price) values ('IT-001', 'Laptop 14 inch', 'IT', 'UNIT', 12500000);
insert into apx_demo_items (item_code, item_name, category, uom, std_price) values ('IT-002', 'Mouse Wireless', 'IT', 'UNIT', 150000);
insert into apx_demo_items (item_code, item_name, category, uom, std_price) values ('CON-001', 'Toner Printer', 'CONSUMABLE', 'PCS', 450000);

declare
   l_ops  apx_demo_departments.department_id%type;
   l_it   apx_demo_departments.department_id%type;
   l_req  apx_demo_requests.request_id%type;

   procedure add_line (
      p_request_id in number
     ,p_item_code  in varchar2
     ,p_qty        in number
   )
   is
      l_item  apx_demo_items.item_id%type;
      l_price apx_demo_items.std_price%type;
   begin
      select item_id
            ,std_price
        into l_item
            ,l_price
        from apx_demo_items
       where item_code = p_item_code;
      insert into apx_demo_request_lines (request_id, item_id, qty, unit_price)
      values (p_request_id, l_item, p_qty, l_price);
   end add_line;
begin
   select department_id into l_ops from apx_demo_departments where dept_code = 'OPS';
   select department_id into l_it from apx_demo_departments where dept_code = 'IT';

   -- Draft kecil (< 10 jt): approval Manager saja
   insert into apx_demo_requests (department_id, request_date, need_date, purpose)
   values (l_ops, trunc(sysdate), trunc(sysdate) + 7, 'ATK kantor bulan ini')
   returning request_id into l_req;
   add_line(l_req, 'ATK-001', 20);
   add_line(l_req, 'ATK-002', 5);

   -- Draft besar (> 10 jt): approval Manager lalu Director
   insert into apx_demo_requests (department_id, request_date, need_date, purpose)
   values (l_it, trunc(sysdate), trunc(sysdate) + 14, 'Laptop karyawan baru')
   returning request_id into l_req;
   add_line(l_req, 'IT-001', 2);
   add_line(l_req, 'IT-002', 2);
end;
/

commit;
