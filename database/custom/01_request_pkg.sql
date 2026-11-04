--------------------------------------------------------------------------------
-- Script : 01_request_pkg.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Business rule Permintaan Barang (dipanggil approval engine saat submit)
--------------------------------------------------------------------------------

create or replace package apx_demo_request_pkg as
   /**
    * Versi package (format XX.YY.ZZ).
    * @return versi
    */
   function package_version return varchar2;

   /**
    * Validasi sebelum submit: permintaan wajib punya minimal satu baris.
    * Dipanggil oleh apx_demo_approval_pkg.submit (doc_types.validate_proc).
    * @param p_doc_id  request_id
    * @throws -20201  permintaan tanpa baris (REQ-5.2)
    */
   procedure check_submit (
      p_doc_id in number
   );
end apx_demo_request_pkg;
/

create or replace package body apx_demo_request_pkg as

   function package_version return varchar2
   is
   begin
      -- Version History:
      -- 01.00.00 2026-11-01 Tim PANDAWA  Initial Version
      return '01.00.00';
   end package_version;

   procedure check_submit (
      p_doc_id in number
   )
   is
      l_count number;
   begin
      select count(*)
        into l_count
        from apx_demo_request_lines
       where request_id = p_doc_id;
      if l_count = 0 then
         raise_application_error(-20201, 'Permintaan belum memiliki baris item.');
      end if;
   end check_submit;

end apx_demo_request_pkg;
/
