import { expect, test } from '@playwright/test';
import { closeDialogs, collectDiagnostics, dumpTriggers, env, login, openDialog, pageUrl, waitApex } from './helpers';
import { ACCESS, AccessPage, APP_PAGES, AppUser, isAllowed, USERS } from './pages';

/**
 * Akses per role (REQ-3.1, REQ-3.2, REQ-3.3, REQ-3.4).
 *
 * Untuk satu user demo per kombinasi role (users: di app.yaml, dibuat oleh database/admin/create_users.sql):
 *   - halaman non-modal dibuka langsung: harus terbuka bila skemanya mengizinkan role user,
 *     dan menampilkan "Akses ditolak" bila tidak;
 *   - halaman modal (form) tidak bisa dibuka langsung lewat URL (HTTP 400). Test membukanya seperti user:
 *     klik pemicunya (tombol Create/Edit/Tambah, link dialog di report/kartu) di halaman pembuka, lalu
 *     menilai isi dialog: harus "Akses ditolak" bila skema form tidak mengizinkan. Bila halaman pembuka
 *     ditolak atau tidak punya pemicu, form memang tidak terjangkau dari aplikasi (dicatat sebagai info);
 *   - tombol Create di halaman list tampil hanya bila skema create mengizinkan.
 * Matriks skema -> role, halaman, dan halaman pembuka dibaca dari pages.json (GENERATED dari app.yaml).
 *
 * Password: secret APEX_ROLE_PASSWORD (password bersama yang dipakai saat menjalankan create_users.sql).
 * Tanpa secret ini test di-skip.
 */
const PASSWORD = process.env.APEX_ROLE_PASSWORD;

/** Satu user per kombinasi role; user tanpa role dilewati. */
const ROLE_USERS: AppUser[] = [];
for (const u of USERS) {
  const key = [...u.roles].sort().join(',');
  if (key && !ROLE_USERS.some((x) => [...x.roles].sort().join(',') === key)) ROLE_USERS.push(u);
}

function snippet(body: string): string {
  return body.replace(/\s+/g, ' ').trim().slice(0, 160);
}

test.describe('akses per role', () => {
  test.skip(({ isMobile }) => isMobile, 'Matriks akses cukup di desktop');
  test.skip(!PASSWORD, 'Secret APEX_ROLE_PASSWORD belum di-set: test akses per role dilewati');

  for (const u of ROLE_USERS) {
    test(`${u.username} (${u.roles.join(', ')})`, async ({ page }, testInfo) => {
      test.setTimeout(15 * 60_000);
      const diag = collectDiagnostics(page);
      const failures: string[] = [];
      const notes: string[] = [];
      let base = '';

      /** Buka halaman (sekali coba ulang bila oracleapex.com lambat); kembalikan status HTTP dan teks body. */
      async function visit(url: string): Promise<{ status: number; body: string; login: boolean }> {
        const resp = await page.goto(url).catch(async () => page.goto(url));
        await waitApex(page);
        const loginPage = (await page.locator('#P9999_USERNAME').count()) > 0;
        return { status: resp?.status() ?? 0, body: await page.locator('body').innerText(), login: loginPage };
      }

      function judge(p: AccessPage, expected: boolean, r: { status: number; body: string; login: boolean }) {
        if (r.login) {
          failures.push(`${p.alias}: diarahkan ke login (sesi hilang)`);
          return;
        }
        const denied = /Akses ditolak/i.test(r.body);
        if (expected && denied) failures.push(`${p.alias} (${p.auth}): seharusnya BOLEH, tapi ditolak`);
        else if (!expected && !denied) {
          failures.push(`${p.alias} (${p.auth}): seharusnya DITOLAK, tapi terbuka (HTTP ${r.status}): "${snippet(r.body)}"`);
        } else if (expected && r.status >= 400) failures.push(`${p.alias}: HTTP ${r.status}: "${snippet(r.body)}"`);
        else if (expected && /ORA-\d{5}/.test(r.body)) failures.push(`${p.alias}: ${r.body.match(/ORA-\d{5}[^\n]*/)?.[0]}`);
      }

      async function modal(p: AccessPage, expected: boolean) {
        let openerAllowed = false;
        for (const no of p.openers ?? []) {
          const op = ACCESS.find((x) => x.no === no);
          if (!op || !isAllowed(op.auth, u.roles)) continue;
          openerAllowed = true;
          await page.goto(pageUrl(base, op.alias, op.no)).catch(async () => page.goto(pageUrl(base, op.alias, op.no)));
          await waitApex(page);
          const frame = await openDialog(page, p.alias);
          if (!frame) continue;
          const body = await frame.locator('body').innerText().catch(() => '');
          judge(p, expected, { status: 200, body, login: false });
          if (!expected && !/Akses ditolak/i.test(body)) await dumpTriggers(page, `${u.username} ${p.alias}`);
          notes.push(`${p.alias}: diuji lewat dialog dari halaman ${no} (${/Akses ditolak/i.test(body) ? 'ditolak' : 'terbuka'})`);
          await closeDialogs(page);
          return;
        }
        const why = openerAllowed ? 'tidak ada pemicu dialog di halaman pembuka' : 'halaman pembuka ditolak';
        if (openerAllowed) await dumpTriggers(page, `${u.username} ${p.alias}`);
        notes.push(`${p.alias}: tidak terjangkau dari aplikasi (${why})${expected ? ' - TIDAK TERVERIFIKASI' : ''}`);
      }

      try {
        await login(page, env('APEX_APP_URL'), u.username, PASSWORD);
        base = page.url();
        for (const p of ACCESS) {
          const expected = isAllowed(p.auth, u.roles);
          await test.step(`${p.no} ${p.alias}: ${expected ? 'boleh' : 'ditolak'}`, async () => {
            if (p.modal) {
              await modal(p, expected);
              return;
            }
            const r = await visit(pageUrl(base, p.alias, p.no));
            judge(p, expected, r);
            const listPage = APP_PAGES.find((x) => x.no === p.no);
            if (expected && !r.login && listPage?.create_auth !== undefined) {
              const canCreate = isAllowed(listPage.create_auth, u.roles);
              const shown = await page.getByRole('button', { name: 'Create', exact: true }).isVisible();
              if (shown !== canCreate) {
                failures.push(`${p.alias}: tombol Create ${shown ? 'tampil' : 'tidak tampil'}, seharusnya ${canCreate ? 'tampil' : 'tersembunyi'} (${listPage.create_auth})`);
              }
            }
          });
        }
      } finally {
        await diag.attach(testInfo, failures.length > 0);
        const report = [...failures.map((f) => `GAGAL  ${f}`), ...notes.map((n) => `info   ${n}`)].join('\n') || 'OK';
        await testInfo.attach('akses.txt', { body: report, contentType: 'text/plain' });
        console.log(`\n===== akses ${u.username} =====\n${report}\n`);
      }
      expect(failures, failures.join('\n')).toEqual([]);
    });
  }
});

