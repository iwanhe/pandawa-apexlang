import { expect, Page, test, TestInfo } from '@playwright/test';
import { collectDiagnostics, dialogUrl, dumpControls, login, pageUrl, waitApex } from './helpers';
import { APP_ALIAS } from './pages';

/**
 * Test fungsional aplikasi DEMO (Permintaan Barang), login sebagai akun E2E (role REQUESTER).
 * Semua test read-only: tidak ada data yang tersimpan (validasi sengaja dibuat gagal).
 * Form (halaman modal) dibuka lewat dialog URL ber-checksum dari halaman list, seperti dari aplikasi.
 * SESUAIKAN atau hapus file ini bila app.yaml diganti dengan aplikasi Anda.
 */
test.describe('fitur DEMO', () => {
  test.skip(APP_ALIAS !== 'DEMO', 'Khusus aplikasi DEMO');
  test.skip(({ isMobile }) => isMobile, 'Cukup di desktop');

  async function open(page: Page, alias: string, no: number) {
    await page.goto(pageUrl(page.url(), alias, no));
    await waitApex(page);
  }

  /** Buka form Permintaan Barang (301) lewat tombol Create di halaman 300. */
  async function openRequestForm(page: Page) {
    await open(page, 'requests', 300);
    const url = await dialogUrl(page, 'request');
    expect(url, 'dialog URL form Permintaan (tombol Create) tidak ditemukan di halaman 300').not.toBeNull();
    await page.goto(url!);
    await waitApex(page);
  }

  /** Jalankan isi test; bila gagal, cetak kontrol DOM ke log job lalu lempar ulang. */
  async function run(page: Page, testInfo: TestInfo, body: () => Promise<void>) {
    const diag = collectDiagnostics(page);
    try {
      await body();
    } catch (err) {
      await dumpControls(page, testInfo.title);
      throw err;
    } finally {
      await diag.attach(testInfo, testInfo.status !== testInfo.expectedStatus);
    }
  }

  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('REQ-5.1 tanggal dibutuhkan sebelum tanggal permintaan ditolak', async ({ page }, testInfo) => {
    await run(page, testInfo, async () => {
      await openRequestForm(page);
      await expect(page.locator('#P301_DEPARTMENT_ID')).toBeAttached();
      // Keperluan (wajib) sengaja dikosongkan: walau validasi tanggal tidak jalan, data tetap tidak tersimpan.
      await page.evaluate(() => {
        const apex = (window as any).apex;
        const sel = document.querySelector('#P301_DEPARTMENT_ID') as HTMLSelectElement;
        const first = Array.from(sel.options).find((o) => o.value);
        apex.item('P301_DEPARTMENT_ID').setValue(first?.value);
        apex.item('P301_REQUEST_DATE').setValue('10-JAN-2026');
        apex.item('P301_NEED_DATE').setValue('01-JAN-2026');
      });
      await page.getByRole('button', { name: 'Create', exact: true }).click();
      await waitApex(page);
      await expect(page.getByText('Tanggal dibutuhkan tidak boleh sebelum tanggal permintaan').first()).toBeVisible();
    });
  });

  test('REQ-4.3 department nonaktif tidak muncul di pilihan form permintaan', async ({ page }, testInfo) => {
    await run(page, testInfo, async () => {
      await openRequestForm(page);
      const options = await page.locator('#P301_DEPARTMENT_ID option').allInnerTexts();
      const real = options.filter((o) => o.trim() && !o.includes('Pilih'));
      expect(real.length, 'pilihan department kosong').toBeGreaterThan(0);
      // Seed DEMO: HR - Human Resources (nonaktif), ACTIVE_YN = N
      expect(real.filter((o) => o.startsWith('HR - ')), 'department nonaktif muncul di LOV').toEqual([]);
    });
  });

  test('REQ-7.1 Item bisa disaring per kategori dan status aktif', async ({ page }, testInfo) => {
    await run(page, testInfo, async () => {
      await open(page, 'items', 210);
      await expect(page.getByText('Kategori', { exact: true }).first()).toBeVisible();
      await expect(page.getByText('Aktif', { exact: true }).first()).toBeVisible();
      const cards = page.locator('.a-CardView-item');
      await expect(cards.first()).toBeVisible();
      const before = await cards.count();
      // Facet Kategori memakai LOV statis: label "Alat Tulis Kantor" (ATK)
      await page.getByRole('checkbox', { name: /Alat Tulis Kantor/ }).first().check();
      await expect
        .poll(async () => cards.count(), { timeout: 15_000, message: 'filter kategori tidak mempersempit hasil' })
        .toBeLessThan(before);
      expect(await cards.count(), 'filter kategori tidak menyisakan kartu').toBeGreaterThan(0);
    });
  });

  test('REQ-7.2 Permintaan Barang bisa disaring per status dan department', async ({ page }, testInfo) => {
    await run(page, testInfo, async () => {
      await open(page, 'requests', 300);
      await expect(page.getByText('Status', { exact: true }).first()).toBeVisible();
      await expect(page.getByText('Department', { exact: true }).first()).toBeVisible();
      await expect(page.getByRole('checkbox', { name: /DRAFT/ }).first()).toBeVisible();
      await expect(page.getByRole('checkbox', { name: /Operations|Finance|Information Technology/ }).first()).toBeVisible();
    });
  });

  test('REQ-7.3 header dan baris permintaan tampil di satu halaman; Tambah hanya untuk DRAFT/REJECTED', async ({ page }, testInfo) => {
    await run(page, testInfo, async () => {
      await open(page, 'permintaan-barang-detail', 302);
      await expect(page.getByText('Pilih Permintaan Barang di daftar kiri').first()).toBeVisible();
      const list = page.locator('.t-Region', { hasText: 'Daftar Permintaan Barang' }).first();
      const rows = list.locator('table.t-Report-report tbody tr');
      await expect(rows.first()).toBeVisible();
      const texts = await rows.allInnerTexts();
      const editable = texts.findIndex((t) => /\b(DRAFT|REJECTED)\b/.test(t));
      const locked = texts.findIndex((t) => /\b(SUBMITTED|APPROVED|FULFILLED|CLOSED|CANCELLED)\b/.test(t));
      expect(editable, 'tidak ada permintaan DRAFT/REJECTED di data').toBeGreaterThanOrEqual(0);

      await rows.nth(editable).locator('a').first().click();
      await waitApex(page);
      await expect(page.getByRole('heading', { name: 'Baris Permintaan' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Edit', exact: true })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Tambah', exact: true })).toBeVisible();

      if (locked >= 0) {
        await open(page, 'permintaan-barang-detail', 302);
        await page
          .locator('.t-Region', { hasText: 'Daftar Permintaan Barang' })
          .first()
          .locator('table.t-Report-report tbody tr')
          .nth(locked)
          .locator('a')
          .first()
          .click();
        await waitApex(page);
        await expect(page.getByRole('heading', { name: 'Baris Permintaan' })).toBeVisible();
        await expect(page.getByRole('button', { name: 'Tambah', exact: true })).toHaveCount(0);
      } else {
        testInfo.annotations.push({ type: 'info', description: 'Belum ada permintaan non-DRAFT; cek tombol Tambah tersembunyi dilewati.' });
      }
    });
  });
});
