import { servePropertyFile } from "../../../serve-property-file";

export async function GET(
  _request: Request,
  { params }: RouteContext<"/property-files/[audience]/[propertyId]/[fileId]">,
) {
  return servePropertyFile(await params);
}
