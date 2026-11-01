#!/usr/bin/env bash
# Jalankan database/install.sql + semua tests/db/test_*.sql ke database Oracle
# (mis. container Oracle Free di GitHub Actions).
#   DB_CONN="apx/password@localhost:1521/FREEPDB1" SQLCL_BIN=/opt/sqlcl/bin/sql tests/db/run.sh [folder-proyek]
# folder-proyek = folder berisi app.yaml (default: root repo). Test: <folder>/tests/db/test_*.sql
# Gagal (exit != 0) bila ada error SQL, objek INVALID, atau test yang raise error.
set -euo pipefail
cd "$(dirname "$0")/../.."
cd "${1:-.}"
: "${DB_CONN:?set DB_CONN user/password@host:port/service}"
SQL="${SQLCL_BIN:-sql}"
PREFIX="$(python3 -c "import yaml;print('APX_'+yaml.safe_load(open('app.yaml'))['app']['code'].upper())")"

run_sql() {
  echo "==> $1"
  "$SQL" -S "$DB_CONN" <<SQLEOF
set define off
set serveroutput on
whenever sqlerror exit failure rollback
@$1
exit
SQLEOF
}

run_sql database/install.sql

echo "==> compile & cek objek INVALID (${PREFIX}_%)"
"$SQL" -S "$DB_CONN" <<SQLEOF
set define off
set serveroutput on
set linesize 200
whenever sqlerror exit failure rollback
exec dbms_utility.compile_schema(schema => user, compile_all => false)
column name format a40
column text format a120
select name, type, line, text from user_errors where name like '${PREFIX}\_%' escape '\' order by name, sequence;
declare
   l_invalid number;
begin
   select count(*) into l_invalid from user_objects where status = 'INVALID' and object_name like '${PREFIX}\_%' escape '\';
   if l_invalid > 0 then
      raise_application_error(-20999, l_invalid || ' objek INVALID, lihat user_errors di atas.');
   end if;
   dbms_output.put_line('OK: semua objek ${PREFIX}_* VALID');
end;
/
exit
SQLEOF

for t in tests/db/test_*.sql; do
  [ -e "$t" ] || continue
  run_sql "$t"
done
echo "SEMUA TEST DATABASE LULUS"
