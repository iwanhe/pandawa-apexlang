import { expect, test } from '@playwright/test';
import { collectDiagnostics, login, pageUrl } from './helpers';
import { APP_PAGES } from './pages';

/** Smoke test: semua halaman di pages.json terbuka tanpa ORA-, tanpa error JS, tanpa terlempar ke login. */
test.describe('smoke', () => {
  test.skip(({ isMobile }) => isMobile, 'Smoke test cukup di desktop');

  test('semua halaman utama terbuka tanpa error', async ({ page }, testInfo) => {
    const diag = collectDiagnostics(page);
    const failures: string[] = [];
    try {
      await login(page);
      const base = page.url();
      for (const p of APP_PAGES) {
        await test.step(`${p.no} ${p.alias}`, async () => {
          const before = diag.pageErrors().length;
          await page.goto(pageUrl(base, p.alias, p.no));
          // APEX menjaga koneksi tetap terbuka, jadi 'networkidle' tidak pernah tercapai.
          await page.waitForLoadState('load');
          await page.locator('.t-Body, #P9999_USERNAME').first().waitFor({ state: 'visible' });
          await page.waitForTimeout(1500);
          const body = await page.locator('body').innerText();
          const title = await page.title();
          await page.screenshot({ path: testInfo.outputPath(`p${String(p.no).padStart(5, '0')}.png`), fullPage: true });
          if (await page.locator('#P9999_USERNAME').count()) failures.push(`${p.alias}: diarahkan ke login (sesi hilang)`);
          if (/ORA-\d{5}/.test(body)) failures.push(`${p.alias}: ${body.match(/ORA-\d{5}[^\n]*/)?.[0]}`);
          if (/Akses ditolak|not authorized/i.test(body)) failures.push(`${p.alias}: akses ditolak (cek role user test)`);
          if (!title.toLowerCase().includes(p.title.toLowerCase().split(' ')[0])) failures.push(`${p.alias}: judul halaman "${title}"`);
          if (diag.pageErrors().length > before) failures.push(`${p.alias}: ${diag.pageErrors().slice(before).join(' | ')}`);
        });
      }
    } finally {
      await diag.attach(testInfo, failures.length > 0);
      await testInfo.attach('smoke-failures.txt', { body: failures.join('\n') || 'OK', contentType: 'text/plain' });
    }
    expect(failures, failures.join('\n')).toEqual([]);
  });
});
