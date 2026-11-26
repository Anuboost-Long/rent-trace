import { EndPoints } from "@/api/api-config";
import { ACCESS_COOKIE } from "@/api/services/auth/session-cookies";
import { cookies } from "next/headers";

const NUMERIC = /^\d+$/;
const AUDIENCES = ["tenant", "landlord", "admin"] as const;

export async function GET(
  request: Request,
  { params }: RouteContext<"/evidence-photos/[audience]/[fileId]">,
) {
  const { audience, fileId } = await params;
  const tenancyId = new URL(request.url).searchParams.get("tenancy") ?? "0";
  const known = AUDIENCES.find((name) => name === audience);
  if (!known || ![fileId, tenancyId].every((part) => NUMERIC.test(part))) {
    return new Response(null, { status: 404 });
  }
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) return new Response(null, { status: 401 });

  const upstream = await fetch(
    EndPoints.evidence.photo[known](tenancyId, fileId),
    {
      cache: "no-store",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "X-API-Key": process.env.API_KEY ?? "",
      },
    },
  ).catch(() => null);
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
