--------------------------------------------------------------------------------
-- Script : test_mbms_formats.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-04
-- Purpose: Test format kolom semantic (email, phone, npwp) di master Customer.
--          Check constraint dan normalisasi trigger dibuat generator dari
--          'semantic:' di app.yaml.
--------------------------------------------------------------------------------
declare
   l_email apx_mbms_customers.email%type;

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

   function ins (
      p_code  in varchar2
     ,p_npwp  in varchar2
     ,p_phone in varchar2
     ,p_email in varchar2
   ) return varchar2
   is
   begin
      return 'insert into apx_mbms_customers (customer_code, customer_name, npwp, phone, email, payment_term_days) values ('''
             || p_code || ''', ''Test format'', ' || nvl('''' || p_npwp || '''', 'null') || ', '
             || nvl('''' || p_phone || '''', 'null') || ', ' || nvl('''' || p_email || '''', 'null') || ', 30)';
   end ins;
begin
   assert_true(expect_error(ins('T-E1', null, null, 'bukan-email'), -2290), 'email tanpa @ ditolak');
   assert_true(expect_error(ins('T-E2', null, null, 'a b@contoh.co.id'), -2290), 'email dengan spasi ditolak');
   assert_true(expect_error(ins('T-P1', null, '12', null), -2290), 'telepon terlalu pendek ditolak');
   assert_true(expect_error(ins('T-P2', null, '021-ABC', null), -2290), 'telepon berisi huruf ditolak');
   assert_true(expect_error(ins('T-N1', '12.345', null, null), -2290), 'NPWP tidak lengkap ditolak');

   execute immediate ins('T-OK1', '01.234.567.8-901.234', '+62 21 555-0101', '  Budi.Santoso@Contoh.CO.ID ');
   select email
     into l_email
     from apx_mbms_customers
    where customer_code = 'T-OK1';
   assert_true(l_email = 'budi.santoso@contoh.co.id', 'email valid diterima dan dinormalisasi (trim + lowercase)');
   execute immediate ins('T-OK2', '0123456789012345', '(021) 5550102', null);
   assert_true(true, 'NPWP 16 digit dan telepon dengan kurung diterima');
   execute immediate ins('T-OK3', null, null, null);
   assert_true(true, 'kolom semantic kosong (null) diterima');

   rollback;
   dbms_output.put_line('test_mbms_formats: LULUS');
exception
   when others then
      rollback;
      raise;
end;
/
