import { handleGetCorrection } from "@/api/services/corrections/serve-action";
import Card from "@/components/common/card";
import LoadError from "@/components/common/load-error";
import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import DecisionPanel from "@/components/corrections/decision-panel";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import { CorrectionStatusLabel } from "@/constants/corrections";
import { CorrectionStatusTone, toneFor } from "@/constants/status-tones";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Correction · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/admin/corrections/[id]">>) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <Correction params={params} />
    </Suspense>
  );
}

const Said = ({
  label,
  children,
}: Readonly<{ label: string; children: React.ReactNode }>) => (
  <div>
    <dt className="text-caption text-fg-tertiary">{label}</dt>
    <dd className="mt-0.5">{children}</dd>
  </div>
);

async function Correction({
  params,
}: Readonly<Pick<PageProps<"/admin/corrections/[id]">, "params">>) {
  const { id } = await params;
  const { data: correction, error } = await handleGetCorrection(id);
  if (error?.status === 404) notFound();
  if (error) return <LoadError error={error} />;

  const side = correction.requester_side === "TENANT" ? "tenant" : "landlord";
  const titleChanges = correction.current_title !== correction.proposed_title;
  return (
    <>
      <Link
        href={Route.admin.corrections}
        className="text-body-sm text-fg-secondary underline-offset-2 hover:underline"
      >
        Corrections
      </Link>
      <div className="mt-3 grid gap-6 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <div className="space-y-4">
          <div>
            <StatusBadge
              tone={toneFor(CorrectionStatusTone, correction.status)}
            >
              {CorrectionStatusLabel[correction.status]}
            </StatusBadge>
            <h1 className="mt-2 text-heading">
              {correction.current_title} · correction
            </h1>
            <p className="mt-1 text-fg-secondary">
              {correction.place} · asked by {correction.requested_by_name} (
              {side}) · <LocalTime iso={correction.submitted_at} />
            </p>
          </div>
          <Card title={`What the ${side} says`}>
            <dl className="space-y-3">
              <Said label="What is incorrect">
                {correction.what_is_incorrect}
              </Said>
              <Said label="Proposed replacement">
                {correction.proposed_description}
              </Said>
              <Said label="Why it is needed">
                {correction.why_change_needed}
              </Said>
            </dl>
          </Card>
          <Card title="Before and after">
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-lg bg-subtle p-3">
                <p className="text-caption text-fg-tertiary">
                  Before · current
                </p>
                <p className="mt-1 font-medium">{correction.current_title}</p>
                <p className="mt-1 whitespace-pre-line text-fg-secondary">
                  {correction.current_description ?? "No description"}
                </p>
              </div>
              <div className="rounded-lg bg-brand-subtle p-3">
                <p className="text-caption text-fg-tertiary">
                  After · if approved
                </p>
                <p className="mt-1 font-medium">{correction.proposed_title}</p>
                <p className="mt-1 whitespace-pre-line">
                  {correction.proposed_description}
                </p>
              </div>
            </div>
            {!titleChanges && (
              <p className="mt-3 text-caption text-fg-tertiary">
                Only the description changes. The title stays the same.
              </p>
            )}
          </Card>
        </div>
        <DecisionPanel correction={correction} />
      </div>
    </>
  );
}
