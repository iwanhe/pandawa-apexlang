--------------------------------------------------------------------------------
-- Script : 02_rules_pkg.sql
-- Author : Tim PANDAWA
-- Date   : 2026-11-01
-- Purpose: Validate hook approval engine (BR-03 budget control, kelengkapan dokumen)
--------------------------------------------------------------------------------

create or replace package apx_mbms_rules_pkg as
   /**
    * Versi package (format XX.YY.ZZ).
    * @return versi
    */
   function package_version return varchar2;

   /**
    * Validasi submit budget proyek: wajib punya WBS.
    * @param p_doc_id  project_id
    * @throws -20204  proyek tanpa WBS
    */
   procedure check_project_submit (
      p_doc_id in number
   );

   /**
    * Validasi submit PR: wajib punya baris; PR proyek tidak boleh melebihi
    * sisa anggaran (budget - aktual - committed PR lain) - BR-03.
    * @param p_doc_id  pr_id
    * @throws -20203  PR tanpa baris
    * @throws -20201  anggaran tidak cukup
    */
   procedure check_pr_submit (
      p_doc_id in number
   );
end apx_mbms_rules_pkg;
/

create or replace package body apx_mbms_rules_pkg as

   function package_version return varchar2
   is
   begin
      -- Version History:
      -- 01.00.00 2026-11-01 Tim PANDAWA  Port dari MBMS MVP (mnm-poc)
      return '01.00.00';
   end package_version;

   procedure check_project_submit (
      p_doc_id in number
   )
   is
      l_count number;
   begin
      select count(*)
        into l_count
        from apx_mbms_wbs
       where project_id = p_doc_id;
      if l_count = 0 then
         raise_application_error(-20204, 'Proyek belum memiliki WBS/budget.');
      end if;
   end check_project_submit;

   procedure check_pr_submit (
      p_doc_id in number
   )
   is
      l_project_id apx_mbms_purchase_reqs.project_id%type;
      l_wbs_id     apx_mbms_purchase_reqs.wbs_id%type;
      l_lines      number;
      l_amount     number;
      l_budget     number;
      l_used       number;
      l_committed  number;
   begin
      select project_id
            ,wbs_id
        into l_project_id
            ,l_wbs_id
        from apx_mbms_purchase_reqs
       where pr_id = p_doc_id;

      select count(*)
            ,nvl(sum(line_amount), 0)
        into l_lines
            ,l_amount
        from apx_mbms_pr_lines
       where pr_id = p_doc_id;
      if l_lines = 0 then
         raise_application_error(-20203, 'PR belum memiliki baris item.');
      end if;

      if l_project_id is null then
         return;
      end if;

      select nvl(sum(budget_amount), 0)
        into l_budget
        from apx_mbms_wbs
       where project_id = l_project_id
         and (l_wbs_id is null or wbs_id = l_wbs_id);

      select nvl(-sum(qty_signed * nvl(unit_cost, 0)), 0)
        into l_used
        from apx_mbms_stock_txns
       where project_id = l_project_id
         and (l_wbs_id is null or wbs_id = l_wbs_id)
         and txn_type in ('ISSUE', 'RETURN');

      select nvl(sum(l.line_amount), 0)
        into l_committed
        from apx_mbms_purchase_reqs r
        join apx_mbms_pr_lines l on l.pr_id = r.pr_id
       where r.project_id = l_project_id
         and (l_wbs_id is null or r.wbs_id = l_wbs_id)
         and r.status in ('SUBMITTED', 'APPROVED')
         and r.pr_id <> p_doc_id;

      if l_amount > l_budget - l_used - l_committed then
         raise_application_error(-20201,
            'Anggaran tidak cukup. Sisa anggaran: ' || to_char(l_budget - l_used - l_committed, 'FM999G999G999G990')
            || ', nilai PR: ' || to_char(l_amount, 'FM999G999G999G990'));
      end if;
   end check_pr_submit;

end apx_mbms_rules_pkg;
/
