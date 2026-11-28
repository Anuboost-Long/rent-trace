import { handleGetRemoval } from "@/api/services/removals/serve-action";
import Card from "@/components/common/card";
import LoadError from "@/components/common/load-error";
import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import DecisionPanel from "@/components/removals/decision-panel";
import { RemovalStatusLabel } from "@/constants/removals";
import { RemovalStatusTone, toneFor } from "@/constants/status-tones";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Removal request · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/admin/removal-requests/[id]">>) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <Removal params={params} />
    </Suspense>
  );
}

async function Removal({
  params,
}: Readonly<Pick<PageProps<"/admin/removal-requests/[id]">, "params">>) {
  const { id } = await params;
  const { data: removal, error } = await handleGetRemoval(id);
  if (error?.status === 404) notFound();
  if (error) return <LoadError error={error} />;

  const count = removal.items.length;
  return (
    <>
      <Link
        href={Route.admin.removal_requests}
        className="text-body-sm text-fg-secondary underline-offset-2 hover:underline"
      >
        Removal requests
      </Link>
      <div className="mt-3 grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <div className="space-y-4">
          <div>
            <StatusBadge tone={toneFor(RemovalStatusTone, removal.status)}>
              {RemovalStatusLabel[removal.status]}
            </StatusBadge>
            <h1 className="mt-2 text-heading">
              Hide {count} {count === 1 ? "record" : "records"}
            </h1>
            <p className="mt-1 text-fg-secondary">
              Asked by {removal.requested_by_name} (
              {removal.requester_side === "TENANT" ? "tenant" : "landlord"}) ·{" "}
              <LocalTime iso={removal.submitted_at} />
            </p>
          </div>
          <Card title={`Records to hide · ${count}`}>
            <ul className="divide-y divide-default">
              {removal.items.map((item) => (
                <li key={item.record_id} className="py-2 first:pt-0 last:pb-0">
                  <p className="font-medium">
                    {item.title ?? "Condition record"}
                  </p>
                  <p className="text-caption text-fg-tertiary">
                    Condition record
                    {item.include_descendants &&
                      " · related records and photos too"}
                  </p>
                </li>
              ))}
            </ul>
          </Card>
          <Card title="Reason">
            <p className="whitespace-pre-line">{removal.reason}</p>
          </Card>
          <Card title="Effect">
            <p>
              Tenants and landlords will no longer see these records. Nothing is
              deleted, and admins who can see hidden records still can.
            </p>
          </Card>
        </div>
        <DecisionPanel removal={removal} />
      </div>
    </>
  );
}
