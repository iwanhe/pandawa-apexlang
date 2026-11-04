import { expect, test } from '@playwright/test';
import { collectDiagnostics, env, login, pageUrl } from './helpers';
import { ACCESS, APP_PAGES, AppUser, isAllowed, USERS } from './pages';

/**
 * Akses per role (REQ-3.1, REQ-3.2, REQ-3.3, REQ-3.4).
 *
 * Untuk satu user demo per kombinasi role (users: di app.yaml, dibuat oleh database/admin/create_users.sql):
 *   - setiap halaman (termasuk form modal dan admin) terbuka bila skemanya mengizinkan role user,
 *     dan menampilkan "Akses ditolak" bila tidak;
 *   - tombol Create di halaman list tampil hanya bila skema create mengizinkan.
 * Matriks skema -> role dan daftar halaman dibaca dari pages.json (GENERATED dari app.yaml).
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

test.describe('akses per role', () => {
  test.skip(({ isMobile }) => isMobile, 'Matriks akses cukup di desktop');
  test.skip(!PASSWORD, 'Secret APEX_ROLE_PASSWORD belum di-set: test akses per role dilewati');

  for (const u of ROLE_USERS) {
    test(`${u.username} (${u.roles.join(', ')})`, async ({ page }, testInfo) => {
      test.setTimeout(10 * 60_000);
      const diag = collectDiagnostics(page);
      const failures: string[] = [];
      try {
        await login(page, env('APEX_APP_URL'), u.username, PASSWORD);
        const base = page.url();
        for (const p of ACCESS) {
          const expected = isAllowed(p.auth, u.roles);
          await test.step(`${p.no} ${p.alias}: ${expected ? 'boleh' : 'ditolak'}`, async () => {
            await page.goto(pageUrl(base, p.alias, p.no));
            await page.waitForLoadState('load');
            await page.locator('body').waitFor({ state: 'visible' });
            await page.waitForTimeout(1000);
            const body = await page.locator('body').innerText();
            if (await page.locator('#P9999_USERNAME').count()) {
              failures.push(`${p.alias}: diarahkan ke login (sesi hilang)`);
              return;
            }
            const denied = /Akses ditolak/i.test(body);
            if (expected && denied) failures.push(`${p.alias} (${p.auth}): seharusnya BOLEH, tapi ditolak`);
            if (!expected && !denied) failures.push(`${p.alias} (${p.auth}): seharusnya DITOLAK, tapi terbuka`);
            if (expected && /ORA-\d{5}/.test(body)) failures.push(`${p.alias}: ${body.match(/ORA-\d{5}[^\n]*/)?.[0]}`);

            const listPage = APP_PAGES.find((x) => x.no === p.no);
            if (expected && listPage?.create_auth !== undefined) {
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
        await testInfo.attach('akses-failures.txt', { body: failures.join('\n') || 'OK', contentType: 'text/plain' });
      }
      expect(failures, failures.join('\n')).toEqual([]);
    });
  }
});
