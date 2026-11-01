import { readFileSync } from 'fs';
import * as path from 'path';

/** Daftar halaman dari tests/e2e/pages.json (dibuat oleh generator dari app.yaml). */
export interface AppPage {
  alias: string;
  no: number;
  title: string;
}

const data = JSON.parse(readFileSync(path.resolve(__dirname, '../pages.json'), 'utf8')) as { app: string; pages: AppPage[] };

export const APP_PAGES: AppPage[] = data.pages;
export const HOME: AppPage = APP_PAGES.find((p) => p.no === 100) ?? APP_PAGES[0];
/** Halaman daftar pertama selain home/inbox, untuk regression test side menu. */
export const FIRST_LIST: AppPage | undefined = APP_PAGES.find((p) => p.no >= 200 && p.no < 500);
