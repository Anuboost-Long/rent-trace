import { EndPoints } from "@/api/api-config";
import {
  ACCESS_COOKIE,
  clearSessionCookies,
  REFRESH_COOKIE,
  setSessionCookies,
} from "@/api/services/auth/session-cookies";
import { audienceFor } from "@/constants/audience";
import { Route } from "@/constants/web-routes";
import type { Me, SignedIn, User } from "@/types/auth/models";
import { isApiKeyFailure, logApiKeyFailure } from "@/utils/api-key-failure";
import { NextRequest, NextResponse } from "next/server";

const redirectToSignIn = (req: NextRequest) => {
  const url = new URL(Route.auth.sign_in, req.url);
  url.searchParams.set("redirect", req.nextUrl.pathname + req.nextUrl.search);
  const response = NextResponse.redirect(url);
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

const apiHeaders = (req: NextRequest, accessToken?: string) => {
  const clientIp = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  return {
    "Content-Type": "application/json",
    "X-API-Key": process.env.API_KEY ?? "",
    "User-Agent": req.headers.get("user-agent") ?? "",
    ...(clientIp && { "X-Forwarded-For": clientIp }),
    ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
  };
};

const homeRedirect = (
  req: NextRequest,
  user: Pick<User, "roles" | "is_admin">,
) => {
  const audience = audienceFor(user);
  return req.nextUrl.pathname === Route.home && audience
    ? NextResponse.redirect(new URL(`/${audience}`, req.url))
    : null;
};

const signedInUser = async (req: NextRequest, accessToken: string) => {
  const response = await fetch(EndPoints.auth.me, {
    headers: apiHeaders(req, accessToken),
  }).catch(() => null);
  return response?.ok ? ((await response.json()) as Me) : null;
};

export async function proxy(req: NextRequest) {
  const accessToken = req.cookies.get(ACCESS_COOKIE)?.value;
  if (accessToken) {
    if (req.nextUrl.pathname !== Route.home) return NextResponse.next();
    const user = await signedInUser(req, accessToken);
    return (user && homeRedirect(req, user)) || NextResponse.next();
  }

  const refreshToken = req.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) return redirectToSignIn(req);

  const refreshed = await fetch(EndPoints.auth.refresh, {
    method: "POST",
    headers: apiHeaders(req),
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => null);
  if (!refreshed?.ok) {
    const body = await refreshed?.json().catch(() => null);
    if (refreshed && isApiKeyFailure(refreshed.status, body)) {
      logApiKeyFailure();
      return NextResponse.next();
    }
    return redirectToSignIn(req);
  }

  const signedIn = (await refreshed.json()) as SignedIn;
  const response =
    homeRedirect(req, signedIn.user) ??
    NextResponse.next({ request: { headers: withCookies(req, signedIn) } });
  setSessionCookies(response.cookies, signedIn);
  return response;
}

export const config = {
  matcher: [
    "/",
    "/auth/mfa",
    "/auth/onboarding",
    "/tenant/:path*",
    "/landlord/:path*",
    "/admin/:path*",
    "/property-files/:path*",
  ],
};
