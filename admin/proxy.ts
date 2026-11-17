import { EndPoints } from "@/api/api-config";
import {
  ACCESS_COOKIE,
  clearSessionCookies,
  REFRESH_COOKIE,
  setSessionCookies,
} from "@/api/services/auth/session-cookies";
import { Route } from "@/constants/web-routes";
import type { SignedIn } from "@/types/auth/models";
import { isApiKeyFailure, logApiKeyFailure } from "@/utils/api-key-failure";
import { NextRequest, NextResponse } from "next/server";

const isPublicPage = (req: NextRequest) =>
  req.nextUrl.pathname === Route.home ||
  req.nextUrl.pathname.startsWith(Route.listings);

const redirectToSignIn = (req: NextRequest) => {
  const url = new URL(Route.auth.sign_in, req.url);
  url.searchParams.set("redirect", req.nextUrl.pathname + req.nextUrl.search);
  const response = NextResponse.redirect(url);
  clearSessionCookies(response.cookies);
  return response;
};

const withoutSession = (req: NextRequest) => {
  if (!isPublicPage(req)) return redirectToSignIn(req);
  const response = NextResponse.next();
  clearSessionCookies(response.cookies);
  return response;
};

const withCookies = (req: NextRequest, signedIn: SignedIn) => {
  const cookies = new Map(req.cookies.getAll().map((c) => [c.name, c.value]));
  cookies.set(ACCESS_COOKIE, signedIn.access_token);
  cookies.set(REFRESH_COOKIE, signedIn.refresh_token);
  const headers = new Headers(req.headers);
  headers.set(
    "cookie",
    [...cookies].map(([name, value]) => `${name}=${value}`).join("; "),
  );
  return headers;
};

export async function proxy(req: NextRequest) {
  if (req.cookies.has(ACCESS_COOKIE)) return NextResponse.next();

  const refreshToken = req.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) {
    return isPublicPage(req) ? NextResponse.next() : redirectToSignIn(req);
  }

  const clientIp = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  const refreshed = await fetch(EndPoints.auth.refresh, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": process.env.API_KEY ?? "",
      "User-Agent": req.headers.get("user-agent") ?? "",
      ...(clientIp && { "X-Forwarded-For": clientIp }),
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => null);
  if (!refreshed?.ok) {
    const body = await refreshed?.json().catch(() => null);
    if (refreshed && isApiKeyFailure(refreshed.status, body)) {
      logApiKeyFailure();
      return NextResponse.next();
    }
    return withoutSession(req);
  }

  const signedIn = (await refreshed.json()) as SignedIn;
  const response = NextResponse.next({
    request: { headers: withCookies(req, signedIn) },
  });
  setSessionCookies(response.cookies, signedIn);
  return response;
}

export const config = {
  matcher: [
    "/",
    "/properties/:path*",
    "/auth/mfa",
    "/auth/onboarding",
    "/tenant/:path*",
    "/landlord/:path*",
    "/admin/:path*",
    "/property-files/:path*",
    "/invitations/:path*",
  ],
};
