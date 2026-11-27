import { BaseUrl } from "@/api/api-config";
import { ACCESS_COOKIE } from "@/api/services/auth/session-cookies";
import { cookies } from "next/headers";

import { requireWireframe } from "../enabled";

const NUMERIC = /^\d+$/;

const pathFor = (params: URLSearchParams) => {
  const role = params.get("role");
  const file = params.get("file") ?? "";
  const tenancy = params.get("tenancy") ?? "";
  const kind = params.get("kind");
  if (!NUMERIC.test(file)) return null;
  if (kind === "avatar") return `auth/users/${file}/picture/`;
  const documents = kind === "document";
  switch (role) {
    case "tenant":
      return NUMERIC.test(tenancy)
        ? `tenant/tenancies/${tenancy}/${documents ? "documents" : "condition-evidence"}/${documents ? "" : "photos/"}${documents ? `files/${file}/` : `${file}/`}`
        : null;
    case "landlord":
      return documents
        ? `landlord/documents/files/${file}/`
        : `landlord/condition-evidence/photos/${file}/`;
    case "admin":
      return documents
        ? `admin/documents/files/${file}/`
        : `admin/review-cases/photos/${file}/`;
    default:
      return null;
  }
};

export async function GET(request: Request) {
  await requireWireframe();
  const path = pathFor(new URL(request.url).searchParams);
  if (!path) return new Response(null, { status: 404 });
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) return new Response(null, { status: 401 });

  const upstream = await fetch(`${BaseUrl}/${path}`, {
    cache: "no-store",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "X-API-Key": process.env.API_KEY ?? "",
    },
  }).catch(() => null);
  if (!upstream?.ok || !upstream.body) {
    return new Response(null, { status: upstream?.status === 404 ? 404 : 502 });
  }
  return new Response(upstream.body, {
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") ?? "application/octet-stream",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
