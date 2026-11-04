import { expect, Frame, Page, TestInfo } from '@playwright/test';
import { writeFileSync } from 'fs';

export function env(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Environment variable ${name} belum di-set (GitHub Secret ${name}).`);
  return v;
}

/** Kumpulkan console, error JS, dan request gagal; dilampirkan ke report di akhir test. */
export function collectDiagnostics(page: Page) {
  const logs: string[] = [];
  const ts = () => new Date().toISOString().substring(11, 23);
  page.on('console', (m) => logs.push(`${ts()} [console.${m.type()}] ${m.text()}`));
  page.on('pageerror', (e) => logs.push(`${ts()} [pageerror] ${e.message}`));
  page.on('requestfailed', (r) => logs.push(`${ts()} [requestfailed] ${r.method()} ${r.url()} ${r.failure()?.errorText}`));
  page.on('framenavigated', (f) => {
    if (f === page.mainFrame()) logs.push(`${ts()} [navigated] ${f.url()}`);
  });
  return {
    logs,
    /** Simpan log ke test-results; cetak ke stdout (log job) hanya bila printToStdout. */
    async attach(testInfo: TestInfo, printToStdout = false) {
      writeFileSync(testInfo.outputPath('browser-log.txt'), logs.join('\n'));
      if (printToStdout) {
        console.log(`\n===== browser-log ${testInfo.project.name} ${testInfo.title} =====\n${logs.join('\n')}\n`);
      }
      await testInfo.attach('browser-log.txt', { body: logs.join('\n'), contentType: 'text/plain' });
    },
    pageErrors: () => logs.filter((l) => l.includes('[pageerror]')),
  };
}

/** Login lewat halaman login APEX (P9999_USERNAME / P9999_PASSWORD). Default: akun E2E dari secret. */
export async function login(page: Page, url = env('APEX_APP_URL'), username?: string, password?: string) {
  await page.goto(url);
  const user = page.locator('#P9999_USERNAME');
  if (await user.isVisible().catch(() => false)) {
    await user.fill(username ?? env('APEX_USERNAME'));
    await page.locator('#P9999_PASSWORD').fill(password ?? env('APEX_PASSWORD'));
    // Tunggu sampai benar-benar pindah dari halaman login. waitForLoadState('load') saja
    // langsung selesai karena halaman login sudah 'load'; bila oracleapex.com lambat
    // membuka Home, assert berikutnya gagal padahal login sukses.
    await Promise.all([
      page.waitForURL((u) => !/(\/login\b|:9999:)/i.test(u.toString()), { timeout: 60_000 }),
      page.getByRole('button', { name: /sign in/i }).click(),
    ]);
    await page.waitForLoadState('load');
  }
  await expect(page.locator('#P9999_USERNAME'), 'Login gagal: masih di halaman login').toHaveCount(0);
  await expect(page.locator('.t-Body')).toBeVisible();
}

/**
 * URL halaman lain dalam sesi yang sama, dari URL halaman saat ini.
 * Mendukung friendly URL (/ords/r/<ws>/<app>/<alias>?session=N) dan f?p=APP:PAGE:SESSION.
 */
export function pageUrl(currentUrl: string, alias: string, pageNo: number): string {
  const u = new URL(currentUrl);
  if (u.pathname.includes('/r/')) {
    const parts = u.pathname.split('/');
    parts[parts.length - 1] = alias.toLowerCase();
    u.pathname = parts.join('/');
    const session = u.searchParams.get('session');
    u.search = session ? `?session=${session}` : '';
    return u.toString();
  }
  const p = u.searchParams.get('p') ?? '';
  const [app, , session] = p.split(':');
  u.search = `?p=${app}:${pageNo}:${session ?? ''}`;
  return u.toString();
}

/** Status side navigation menu Universal Theme. */
export async function navState(page: Page) {
  return page.evaluate(() => {
    const body = document.body;
    const nav = document.querySelector('#t_Body_nav, .t-Body-nav') as HTMLElement | null;
    const r = nav?.getBoundingClientRect();
    const visible = !!r && r.width > 40 && r.right > 40 && r.left < window.innerWidth - 10 &&
      getComputedStyle(nav!).visibility !== 'hidden';
    return {
      bodyClasses: body.className,
      expandedClass: body.classList.contains('js-navExpanded'),
      navRect: r ? { x: Math.round(r.x), w: Math.round(r.width) } : null,
      navVisible: visible,
      viewport: { w: window.innerWidth, h: window.innerHeight },
    };
  });
}

/**
 * Buka halaman modal `alias` seperti user: klik pemicunya di halaman saat ini (tombol Create/Edit/Tambah,
 * link dialog di report atau kartu), lalu kembalikan frame dialog yang terbuka. null bila tidak ada pemicu.
 * Halaman modal APEX tidak bisa dibuka langsung lewat URL (HTTP 400) — butuh konteks dialog dari aplikasi.
 */
export async function openDialog(page: Page, alias: string): Promise<Frame | null> {
  const want = (u: string) => new RegExp(`/${alias.replace(/-/g, '\\-')}\\?`, 'i').test(u);
  await page.locator('a[href*="navigation.dialog"], .a-CardView-item, table.t-Report-report, .a-IRR-table').first()
    .waitFor({ state: 'attached', timeout: 5000 }).catch(() => undefined);
  const triggers = [
    page.getByRole('button', { name: /^(Create|Edit|Tambah)$/ }),
    page.locator(`a[href*="navigation.dialog"][href*="${alias}"]`),
    page.locator('a[href*="navigation.dialog"]'),
  ];
  for (const group of triggers) {
    const n = Math.min(await group.count(), 4);
    for (let i = 0; i < n; i++) {
      const el = group.nth(i);
      if (!(await el.isVisible().catch(() => false))) continue;
      await el.click().catch(() => undefined);
      const frame = await waitForFrame(page, want, 10_000);
      if (frame) {
        await frame.waitForLoadState('load').catch(() => undefined);
        await frame.locator('body').waitFor({ state: 'visible' }).catch(() => undefined);
        await page.waitForTimeout(800);
        return frame;
      }
      await closeDialogs(page);
    }
  }
  return null;
}

async function waitForFrame(page: Page, want: (u: string) => boolean, timeout: number): Promise<Frame | null> {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const f = page.frames().find((fr) => fr !== page.mainFrame() && want(fr.url()));
    if (f) return f;
    await page.waitForTimeout(250);
  }
  return null;
}

/** Tutup dialog APEX yang terbuka (tanpa menyimpan). */
export async function closeDialogs(page: Page) {
  for (let i = 0; i < 3 && (await page.locator('.ui-dialog:visible').count()) > 0; i++) {
    await page.keyboard.press('Escape');
    await page.waitForTimeout(400);
  }
}

/** Cetak link dan tombol yang mungkin membuka dialog (untuk diagnosis bila pemicu tidak ditemukan). */
export async function dumpTriggers(page: Page, label: string) {
  const info = await page
    .evaluate(() =>
      Array.from(document.querySelectorAll('a[href], button'))
        .filter((e) => /dialog|javascript|Create|Edit|Tambah/i.test((e.getAttribute('href') ?? '') + e.textContent))
        .slice(0, 25)
        .map((e) => `${e.tagName.toLowerCase()} text="${(e.textContent ?? '').trim().slice(0, 30)}" href="${(e.getAttribute('href') ?? '').slice(0, 160)}" onclick="${(e.getAttribute('onclick') ?? '').slice(0, 80)}"`),
    )
    .catch((err) => [`(gagal membaca DOM: ${err})`]);
  console.log(`\n===== TRIGGERS ${label} (${page.url()}) =====\n${info.join('\n')}\n`);
}

/** Tunggu halaman APEX siap (APEX menjaga koneksi terbuka, jadi bukan 'networkidle'). */
export async function waitApex(page: Page) {
  await page.waitForLoadState('load');
  await page.locator('body').waitFor({ state: 'visible' });
  await page.waitForTimeout(1000);
}

/** Cetak kontrol form/facet di halaman ke stdout (log job), untuk diagnosis saat test gagal. */
export async function dumpControls(page: Page, label: string) {
  const info = await page
    .evaluate(() =>
      Array.from(document.querySelectorAll('input, select, [role="checkbox"], [role="option"], button'))
        .slice(0, 80)
        .map((e) => {
          const el = e as HTMLInputElement;
          const lbl = (e.getAttribute('aria-label') || (e.id && document.querySelector(`label[for="${e.id}"]`)?.textContent) || e.textContent || '')
            .trim()
            .replace(/\s+/g, ' ')
            .slice(0, 50);
          return `${e.tagName.toLowerCase()} type=${el.type ?? ''} id=${e.id} name=${el.name ?? ''} role=${e.getAttribute('role') ?? ''} class=${(e.getAttribute('class') ?? '').slice(0, 40)} label="${lbl}"`;
        }),
    )
    .catch((err) => [`(gagal membaca DOM: ${err})`]);
  console.log(`\n===== DOM ${label} (${page.url()}) =====\n${info.join('\n')}\n`);
}
