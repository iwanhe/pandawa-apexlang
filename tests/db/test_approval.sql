--------------------------------------------------------------------------------
-- Script : test_approval.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Test approval engine (contoh DEMO): submit, maker-checker, 2 level,
--          lock dokumen & baris, validate hook, status operasional, reject.
-- Jalankan setelah install.sql (lihat tests/db/run.sh). Raise error bila gagal.
-- SESUAIKAN dengan entitas aplikasi Anda bila app.yaml diganti.
--------------------------------------------------------------------------------
declare
   l_small  apx_demo_requests.request_id%type;
   l_big    apx_demo_requests.request_id%type;
   l_empty  apx_demo_requests.request_id%type;
   l_appr   apx_demo_approvals.approval_id%type;
   l_status apx_demo_requests.status%type;
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

   function status_of (
      p_id in number
   ) return varchar2
   is
      l_s apx_demo_requests.status%type;
   begin
      select status into l_s from apx_demo_requests where request_id = p_id;
      return l_s;
   end status_of;

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

   function pending_for (
      p_id in number
   ) return number
   is
      l_id apx_demo_approvals.approval_id%type;
   begin
      select approval_id
        into l_id
        from apx_demo_approvals
       where doc_type = 'REQ'
         and doc_id   = p_id
         and status   = 'PENDING';
      return l_id;
   end pending_for;
begin
   -- role test (mode bootstrap berakhir begitu ada ADMIN)
   insert into apx_demo_user_roles (username, role_code) values ('T_ADMIN', 'ADMIN');
   insert into apx_demo_user_roles (username, role_code) values ('T_REQ', 'REQUESTER');
   insert into apx_demo_user_roles (username, role_code) values ('T_MGR', 'MANAGER');
   insert into apx_demo_user_roles (username, role_code) values ('T_DIR', 'DIRECTOR');

   select min(request_id)
         ,max(request_id)
     into l_small
         ,l_big
     from apx_demo_requests;
   assert_true(status_of(l_small) = 'DRAFT', 'seed: permintaan berstatus DRAFT');
   assert_true(apx_demo_approval_pkg.doc_amount('REQ', l_small) = 20 * 55000 + 5 * 30000, 'doc_amount = total baris (1.250.000)');

   -- 1. validate hook: permintaan tanpa baris ditolak
   apx_demo_sec_pkg.set_test_user('T_REQ');
   insert into apx_demo_requests (department_id, request_date, purpose)
   values ((select min(department_id) from apx_demo_departments), trunc(sysdate), 'tanpa baris')
   returning request_id into l_empty;
   assert_true(expect_error('begin apx_demo_approval_pkg.submit(''REQ'', ' || l_empty || '); end;', -20201),
         'submit tanpa baris ditolak oleh validate hook');

   -- 2. submit kecil -> 1 level (MANAGER)
   apx_demo_approval_pkg.submit('REQ', l_small);
   assert_true(status_of(l_small) = 'SUBMITTED', 'submit -> SUBMITTED');
   assert_true(expect_error('update apx_demo_requests set purpose = ''x'' where request_id = ' || l_small, -20110),
         'dokumen SUBMITTED terkunci (trigger guard)');
   assert_true(expect_error('update apx_demo_request_lines set qty = 1 where request_id = ' || l_small, -20121),
         'baris dokumen SUBMITTED terkunci (parent lock)');
   l_appr := pending_for(l_small);
   assert_true(apx_demo_approval_pkg.can_act_yn(l_appr) = 'N', 'maker-checker: pengaju tidak bisa memproses');
   assert_true(expect_error('begin apx_demo_approval_pkg.approve(' || l_appr || '); end;', -20106), 'approve oleh pengaju ditolak');
   apx_demo_sec_pkg.set_test_user('T_DIR');
   assert_true(expect_error('begin apx_demo_approval_pkg.approve(' || l_appr || '); end;', -20107),
         'role salah (DIRECTOR untuk level 1 MANAGER) ditolak');
   apx_demo_sec_pkg.set_test_user('T_MGR');
   assert_true(apx_demo_approval_pkg.can_act_yn(l_appr) = 'Y', 'MANAGER bisa memproses');
   apx_demo_approval_pkg.approve(l_appr, 'ok');
   assert_true(status_of(l_small) = 'APPROVED', 'nilai < limit: APPROVED setelah level 1');

   -- 3. submit besar -> 2 level (MANAGER, DIRECTOR)
   apx_demo_sec_pkg.set_test_user('T_REQ');
   apx_demo_approval_pkg.submit('REQ', l_big);
   apx_demo_sec_pkg.set_test_user('T_MGR');
   apx_demo_approval_pkg.approve(pending_for(l_big));
   select count(*)
     into l_count
     from apx_demo_approvals
    where doc_id = l_big
      and approval_level = 2
      and status = 'PENDING';
   assert_true(l_count = 1 and status_of(l_big) = 'SUBMITTED', 'nilai > limit: level 2 DIRECTOR dibuat');
   apx_demo_sec_pkg.set_test_user('T_DIR');
   apx_demo_approval_pkg.approve(pending_for(l_big));
   assert_true(status_of(l_big) = 'APPROVED', 'level 2 approve -> APPROVED');

   -- 4. kolom lock setelah approval, status operasional diizinkan
   apx_demo_sec_pkg.set_test_user('T_REQ');
   update apx_demo_requests
      set purpose = 'diubah'
         ,status  = 'FULFILLED'
    where request_id = l_big;
   select status
     into l_status
     from apx_demo_requests
    where request_id = l_big
      and purpose <> 'diubah';
   assert_true(l_status = 'FULFILLED', 'kolom lock dikembalikan, status operasional FULFILLED diterima');
   assert_true(expect_error('update apx_demo_requests set status = ''DRAFT'' where request_id = ' || l_big, -20112),
         'transisi status ilegal ditolak');

   -- 5. reject wajib catatan, dokumen kembali REJECTED
   insert into apx_demo_request_lines (request_id, item_id, qty, unit_price)
   values (l_empty, (select min(item_id) from apx_demo_items), 1, 1000);
   apx_demo_approval_pkg.submit('REQ', l_empty);
   apx_demo_sec_pkg.set_test_user('T_MGR');
   l_appr := pending_for(l_empty);
   assert_true(expect_error('begin apx_demo_approval_pkg.reject(' || l_appr || ', null); end;', -20108), 'reject tanpa catatan ditolak');
   apx_demo_approval_pkg.reject(l_appr, 'kurang lengkap');
   assert_true(status_of(l_empty) = 'REJECTED', 'reject -> REJECTED');

   -- 6. penomoran dokumen
   select count(*)
     into l_count
     from apx_demo_requests
    where request_no like 'REQ-' || to_char(sysdate, 'YYYY') || '-____';
   assert_true(l_count = 3, 'penomoran REQ-YYYY-NNNN');

   apx_demo_sec_pkg.set_test_user(null);
   rollback;
   dbms_output.put_line('test_approval: LULUS');
exception
   when others then
      apx_demo_sec_pkg.set_test_user(null);
      rollback;
      raise;
end;
/
