import { EndPoints } from "@/api/api-config";

const NUMERIC = /^\d+$/;

export async function GET(
  _request: Request,
  { params }: RouteContext<"/listing-photos/[listingId]/[fileId]">,
) {
  const { listingId, fileId } = await params;
  if (!NUMERIC.test(listingId) || !NUMERIC.test(fileId)) {
    return new Response(null, { status: 404 });
  }

  const upstream = await fetch(EndPoints.listings.photo(listingId, fileId), {
    headers: { "X-API-Key": process.env.API_KEY ?? "" },
  }).catch(() => null);
  if (!upstream?.ok || !upstream.body) {
    return new Response(null, { status: upstream?.status === 404 ? 404 : 502 });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") ?? "application/octet-stream",
      "Cache-Control": "public, max-age=3600",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
