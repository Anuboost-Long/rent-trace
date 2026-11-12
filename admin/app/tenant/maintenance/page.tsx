import { handleGetMyTenancies } from "@/api/services/tenancies/serve-action";
import IssueListBody from "@/components/maintenance/issue-list";
import ReportIssueButton from "@/components/maintenance/report-issue-button";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Maintenance · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/tenant/maintenance">>) {
  return (
    <>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Maintenance</h1>
          <p className="mt-1 text-foreground/70">
            Report something that needs fixing and follow what happens.
          </p>
        </div>
        <Suspense>
          <ReportButton />
        </Suspense>
      </div>
      <IssueListBody audience="tenant" searchParams={searchParams} />
    </>
  );
}

async function ReportButton() {
  const { data } = await handleGetMyTenancies();
  const tenancies = (data ?? [])
    .filter((tenancy) => tenancy.is_current && tenancy.status === "ACTIVE")
    .map((tenancy) => ({
      id: tenancy.id,
      label: `${tenancy.property.name ?? tenancy.property.suburb}, ${tenancy.unit.name}`,
    }));
  return <ReportIssueButton tenancies={tenancies} />;
}
