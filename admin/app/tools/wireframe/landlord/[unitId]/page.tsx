import CallForm, { DownloadForm } from "../../call-form";
import { requireWireframe } from "../../enabled";
import { landlordCalls } from "../../spec";

export default async function Page({
  params,
}: Readonly<PageProps<"/tools/wireframe/landlord/[unitId]">>) {
  await requireWireframe();
  const { unitId } = await params;
  return (
    <main>
      <h1>Landlord wireframe, unit {unitId}</h1>
      <p>
        <a href="/tools/wireframe">Back</a>
      </p>
      {landlordCalls(unitId).map((call) => (
        <CallForm key={`${call.method}${call.title}`} call={call} />
      ))}
      <DownloadForm role="landlord" />
    </main>
  );
}
