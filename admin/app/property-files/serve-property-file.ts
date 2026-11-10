import { EndPoints } from "@/api/api-config";
import { ACCESS_COOKIE } from "@/api/services/auth/session-cookies";
import { cookies } from "next/headers";

const NUMERIC = /^\d+$/;

type FileAddress = {
  audience: string;
  propertyId: string;
  fileId: string;
  unitId?: string;
};

export const servePropertyFile = async ({
  audience,
  propertyId,
  fileId,
  unitId,
}: FileAddress) => {
  if (
    (audience !== "admin" && audience !== "landlord") ||
    ![propertyId, fileId, unitId ?? "0"].every((part) => NUMERIC.test(part))
  ) {
    return new Response(null, { status: 404 });
  }
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) return new Response(null, { status: 401 });

  const upstream = await fetch(
    EndPoints.property_files[audience].content(propertyId, fileId, unitId),
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
      "Content-Disposition":
        upstream.headers.get("content-disposition") ?? "inline",
      "Cache-Control": "private, max-age=3600",
      "X-Content-Type-Options": "nosniff",
    },
  });
};
