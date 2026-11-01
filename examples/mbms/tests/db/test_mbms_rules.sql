--------------------------------------------------------------------------------
-- Script : test_mbms_rules.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Test rule MBMS: costing, budget control PR (BR-03), approval proyek
--          2 level, stok tidak minus & ledger immutable (BR-07), WBS terkunci.
--------------------------------------------------------------------------------
declare
   l_pr     apx_mbms_purchase_reqs.pr_id%type;
   l_pr2    apx_mbms_purchase_reqs.pr_id%type;
   l_prj    apx_mbms_projects.project_id%type;
   l_wbs2   apx_mbms_wbs.wbs_id%type;
   l_appr   apx_mbms_approvals.approval_id%type;
   l_num    number;
   l_status varchar2(30);

   procedure check (p_ok in boolean, p_msg in varchar2)
   is
   begin
      if not p_ok then
         raise_application_error(-20900, 'TEST GAGAL: ' || p_msg);
      end if;
      dbms_output.put_line('  ok  ' || p_msg);
   end check;

   function expect_error (p_block in varchar2, p_code in number) return boolean
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

   function pending_for (p_type in varchar2, p_id in number) return number
   is
      l_id apx_mbms_approvals.approval_id%type;
   begin
      select approval_id into l_id from apx_mbms_approvals
       where doc_type = p_type and doc_id = p_id and status = 'PENDING';
      return l_id;
   end pending_for;
begin
   insert into apx_mbms_user_roles (username, role_code) values ('T_ADMIN', 'ADMIN');
   insert into apx_mbms_user_roles (username, role_code) values ('T_PM', 'PROJECT_MGR');
   insert into apx_mbms_user_roles (username, role_code) values ('T_ENG', 'ENG_MGR');
   insert into apx_mbms_user_roles (username, role_code) values ('T_DIR', 'DIRECTOR');
   insert into apx_mbms_user_roles (username, role_code) values ('T_PROC', 'PROCUREMENT');

   -- costing: material aktual job brosur = 2650 x 1.600 + 8 x 120.000
   select act_material into l_num from apx_mbms_job_cost_v where qty_order = 10000;
   check(l_num = 2650 * 1600 + 8 * 120000, 'job costing: material aktual 5.200.000');

   select project_id into l_prj from apx_mbms_projects where project_name like 'Conveyor%';
   select wbs_id into l_wbs2 from apx_mbms_wbs where project_id = l_prj and wbs_code = '2.0';
   select remaining_amount into l_num from apx_mbms_wbs_budget_v where wbs_id = l_wbs2;
   check(l_num = 80000000 - (40 * 650000 + 8 * 2100000), 'WBS 2.0 sisa anggaran 37.200.000');

   -- PR draft (7,4 jt) lolos budget, approval PROCUREMENT saja
   select pr_id into l_pr from apx_mbms_purchase_reqs where status = 'DRAFT';
   apx_mbms_sec_pkg.set_test_user('T_PM');
   apx_mbms_approval_pkg.submit('PR', l_pr);
   apx_mbms_sec_pkg.set_test_user('T_PROC');
   apx_mbms_approval_pkg.approve(pending_for('PR', l_pr));
   select status into l_status from apx_mbms_purchase_reqs where pr_id = l_pr;
   check(l_status = 'APPROVED', 'PR 7,4 jt: approved PROCUREMENT (tanpa level 2)');

   -- PR kedua 31,5 jt > sisa 29,8 jt -> ditolak budget control
   apx_mbms_sec_pkg.set_test_user('T_PM');
   insert into apx_mbms_purchase_reqs (bu_id, purpose, project_id, wbs_id, description)
   values ((select bu_id from apx_mbms_business_units where bu_code = 'ENG'), 'PROJECT', l_prj, l_wbs2, 'test over budget')
   returning pr_id into l_pr2;
   insert into apx_mbms_pr_lines (pr_id, item_id, qty, unit_price)
   values (l_pr2, (select item_id from apx_mbms_items where item_code = 'ENG-STL-PLT6'), 15, 2100000);
   check(expect_error('begin apx_mbms_approval_pkg.submit(''PR'', ' || l_pr2 || '); end;', -20201), 'PR melebihi sisa anggaran ditolak (BR-03)');

   -- proyek baru > 100 jt -> ENG_MGR lalu DIRECTOR
   insert into apx_mbms_projects (bu_id, customer_id, project_name, contract_value)
   values ((select bu_id from apx_mbms_business_units where bu_code = 'ENG'), (select min(customer_id) from apx_mbms_customers), 'Ducting test', 150000000)
   returning project_id into l_prj;
   check(expect_error('begin apx_mbms_approval_pkg.submit(''PRJ'', ' || l_prj || '); end;', -20204), 'proyek tanpa WBS ditolak');
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, budget_amount) values (l_prj, '1.0', 'Design', 15000000);
   insert into apx_mbms_wbs (project_id, wbs_code, wbs_name, budget_amount) values (l_prj, '2.0', 'Material', 100000000);
   apx_mbms_approval_pkg.submit('PRJ', l_prj);
   check(expect_error('update apx_mbms_wbs set budget_amount = 1 where project_id = ' || l_prj, -20121), 'WBS terkunci saat proyek SUBMITTED');
   apx_mbms_sec_pkg.set_test_user('T_ENG');
   apx_mbms_approval_pkg.approve(pending_for('PRJ', l_prj));
   apx_mbms_sec_pkg.set_test_user('T_DIR');
   apx_mbms_approval_pkg.approve(pending_for('PRJ', l_prj));
   select status into l_status from apx_mbms_projects where project_id = l_prj;
   check(l_status = 'APPROVED', 'proyek 115 jt: ENG_MGR + DIRECTOR -> APPROVED');

   -- stock ledger
   check(expect_error('begin insert into apx_mbms_stock_txns (txn_type, warehouse_id, item_id, qty, job_id) '
                      || 'select ''ISSUE'', w.warehouse_id, i.item_id, 999999, j.job_id from apx_mbms_warehouses w, apx_mbms_items i, apx_mbms_job_orders j '
                      || 'where w.wh_code = ''WH-PRINT'' and i.item_code = ''PRT-PAP-AP150'' and j.qty_order = 10000; end;', -20252)
         , 'issue melebihi stok ditolak');
   check(expect_error('update apx_mbms_stock_txns set qty = 1 where rownum = 1', -20120), 'ledger immutable: update ditolak');
   select count(*) into l_num from apx_mbms_stock_txns where txn_no like 'MI-' || to_char(sysdate, 'YYYY') || '-____';
   check(l_num = 4, 'nomor material issue MI-YYYY-NNNN');

   apx_mbms_sec_pkg.set_test_user(null);
   rollback;
   dbms_output.put_line('test_mbms_rules: LULUS');
exception
   when others then
      apx_mbms_sec_pkg.set_test_user(null);
      rollback;
      raise;
end;
/
