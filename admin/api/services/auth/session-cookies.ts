import type { SignedIn } from "@/types/auth/models";

export const ACCESS_COOKIE = "access_token";
export const REFRESH_COOKIE = "refresh_token";

const REFRESH_LIFETIME_SECONDS = 30 * 24 * 60 * 60;

type CookieJar = {
  set: (name: string, value: string, options: object) => unknown;
  delete: (name: string) => unknown;
};

const base = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production",
  path: "/",
};

export const setSessionCookies = (
  jar: CookieJar,
  { access_token, expires_in, refresh_token }: SignedIn,
) => {
  jar.set(ACCESS_COOKIE, access_token, { ...base, maxAge: expires_in });
  jar.set(REFRESH_COOKIE, refresh_token, {
    ...base,
    maxAge: REFRESH_LIFETIME_SECONDS,
  });
};

export const clearSessionCookies = (jar: CookieJar) => {
  jar.delete(ACCESS_COOKIE);
  jar.delete(REFRESH_COOKIE);
};
