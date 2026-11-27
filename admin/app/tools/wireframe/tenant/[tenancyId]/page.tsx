import CallForm, { DownloadForm } from "../../call-form";
import { requireWireframe } from "../../enabled";
import { profileCalls, tenantCalls } from "../../spec";

export default async function Page({
  params,
}: Readonly<PageProps<"/tools/wireframe/tenant/[tenancyId]">>) {
  await requireWireframe();
  const { tenancyId } = await params;
  return (
    <main>
      <h1>Tenant wireframe, tenancy {tenancyId}</h1>
      <p>
        <a href="/tools/wireframe">Back</a>
      </p>
      {[...tenantCalls(tenancyId), ...profileCalls].map((call) => (
        <CallForm key={`${call.method}${call.title}`} call={call} />
      ))}
      <DownloadForm role="tenant" tenancy={tenancyId} />
    </main>
  );
}
