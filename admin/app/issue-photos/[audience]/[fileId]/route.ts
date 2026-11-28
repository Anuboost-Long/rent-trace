import { EndPoints } from "@/api/api-config";
import { ACCESS_COOKIE } from "@/api/services/auth/session-cookies";
import { cookies } from "next/headers";

const NUMERIC = /^\d+$/;

export async function GET(
  request: Request,
  { params }: RouteContext<"/issue-photos/[audience]/[fileId]">,
) {
  const { audience, fileId } = await params;
  const issueId = new URL(request.url).searchParams.get("issue") ?? "0";
  if (
    !["tenant", "landlord", "admin"].includes(audience) ||
    ![fileId, issueId].every((part) => NUMERIC.test(part))
  ) {
    return new Response(null, { status: 404 });
  }
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) return new Response(null, { status: 401 });

  const url =
    audience === "admin"
      ? EndPoints.admin_maintenance.photo(issueId, fileId)
      : EndPoints.maintenance.photo(issueId, fileId);
  const upstream = await fetch(url, {
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
      "Cache-Control": "private, max-age=3600",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
