set serveroutput on

-- Hapus akun workspace yang dibuat create_users.sql beserta role-nya. HANYA untuk sandbox.
declare
   c_workspace constant varchar2(100) := null;
   l_users     apex_t_varchar2 := apex_t_varchar2('DEMO_ADMIN', 'DEMO_REQ', 'DEMO_MGR', 'DEMO_DIR', 'DEMO_WH', 'DEMO_E2E');
   l_exists    number;
begin
   if c_workspace is not null then
      apex_util.set_workspace(p_workspace => c_workspace);
   end if;
   for i in 1 .. l_users.count
   loop
      continue when l_users(i) is null;
      delete from apx_demo_user_roles where username = l_users(i);
      select count(*) into l_exists from apex_workspace_apex_users where user_name = l_users(i);
      if l_exists > 0 then
         apex_util.remove_user(p_user_name => l_users(i));
         dbms_output.put_line(rpad(l_users(i), 20) || ' dihapus');
      end if;
   end loop;
   commit;
end;
/
