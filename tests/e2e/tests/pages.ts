import { readFileSync } from 'fs';
import * as path from 'path';

/** Daftar halaman dari tests/e2e/pages.json (dibuat oleh generator dari app.yaml). */
export interface AppPage {
  alias: string;
  no: number;
  title: string;
  auth?: string | null;
  create_auth?: string | null;
}

/** Semua halaman (termasuk modal & admin) dengan authorization scheme-nya. */
export interface AccessPage {
  alias: string;
  no: number;
  auth: string | null;
  modal: boolean;
}

export interface AppUser {
  username: string;
  roles: string[];
}

const data = JSON.parse(readFileSync(path.resolve(__dirname, '../pages.json'), 'utf8')) as {
  app: string;
  schemes?: Record<string, string[] | null>;
  users?: AppUser[];
  pages: AppPage[];
  access?: AccessPage[];
};

export const APP_ALIAS: string = data.app;
export const APP_PAGES: AppPage[] = data.pages;
/** Skema -> role yang diizinkan; null = semua user yang punya minimal satu role. */
export const SCHEMES: Record<string, string[] | null> = data.schemes ?? {};
export const USERS: AppUser[] = data.users ?? [];
export const ACCESS: AccessPage[] = data.access ?? [];

/** Aturan yang sama dengan APX_<APP>_SEC_PKG: ADMIN lolos semua skema. */
export function isAllowed(scheme: string | null | undefined, roles: string[]): boolean {
  if (!scheme) return true;
  if (roles.includes('ADMIN')) return true;
  if (!(scheme in SCHEMES)) return true;
  const allowed = SCHEMES[scheme];
  if (allowed === null) return roles.length > 0;
  return roles.some((r) => allowed.includes(r));
}
export const HOME: AppPage = APP_PAGES.find((p) => p.no === 100) ?? APP_PAGES[0];
/** Halaman daftar pertama selain home/inbox, untuk regression test side menu. */
export const FIRST_LIST: AppPage | undefined = APP_PAGES.find((p) => p.no >= 200 && p.no < 500);
