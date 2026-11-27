import CallForm, { DownloadForm } from "../call-form";
import { requireWireframe } from "../enabled";
import { adminCalls } from "../spec";

export default async function Page({
  searchParams,
}: Readonly<PageProps<"/tools/wireframe/admin">>) {
  await requireWireframe();
  const unit = (await searchParams).unit;
  const unitId = typeof unit === "string" ? unit : "";
  return (
    <main>
      <h1>Admin wireframe{unitId ? `, unit ${unitId}` : ""}</h1>
      <p>
        <a href="/tools/wireframe">Back</a>
      </p>
      {adminCalls(unitId).map((call) => (
        <CallForm key={`${call.method}${call.title}`} call={call} />
      ))}
      <DownloadForm role="admin" />
    </main>
  );
}
