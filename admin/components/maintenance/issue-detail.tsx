import { handleGetIssue } from "@/api/services/maintenance/serve-action";
import LocalTime from "@/components/common/local-time";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { DetailSkeleton } from "@/components/layout/page-skeletons";
import {
  ClosureOutcomeLabel,
  IssuePriorityLabel,
  IssueRoutes,
  IssueStatusLabel,
} from "@/constants/maintenance";
import type { MaintenanceAudience } from "@/types/maintenance/models";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";
import { Suspense } from "react";

import IssueActions from "./issue-actions";
import IssueProvider from "./issue-provider";
import IssueTimeline from "./issue-timeline";

type IssueDetailProp = Readonly<{
  audience: MaintenanceAudience;
  params: Promise<{ id: string }>;
}>;

export default function IssueDetailPage(props: IssueDetailProp) {
  return (
    <Suspense fallback={<DetailSkeleton />}>
      <IssueDetail {...props} />
    </Suspense>
  );
}

async function IssueDetail({ audience, params }: IssueDetailProp) {
  const { id } = await params;
  const { data: issue, error } = await handleGetIssue(id, audience);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }

  const details: [string, ReactNode][] = [
    ["Status", IssueStatusLabel[issue.status]],
    ["Priority", IssuePriorityLabel[issue.priority]],
    ...(issue.category
      ? ([["Kind of problem", issue.category.name]] as [string, ReactNode][])
      : []),
    [
      "Where",
      `${issue.property.name ?? issue.property.suburb}, ${issue.unit.name}`,
    ],
    [
      "Reported",
      <>
        <LocalTime iso={issue.reported_at} /> by {issue.reported_by_name}
      </>,
    ],
    ...(issue.closure_outcome
      ? ([["Outcome", ClosureOutcomeLabel[issue.closure_outcome]]] as [
          string,
          string,
        ][])
      : []),
    ["Details", issue.description],
  ];

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Maintenance", href: IssueRoutes[audience].list },
          { label: issue.title },
        ]}
      />
      <div className="mt-4 mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-heading">{issue.title}</h1>
        {(audience !== "admin" || issue.actions.length > 0) && (
          <IssueActions audience={audience} issue={issue} />
        )}
      </div>
      {issue.open_closure && (
        <section
          aria-labelledby="closure-heading"
          className="mb-8 rounded-xl border border-default p-5"
        >
          <h2 id="closure-heading" className="text-section">
            Closing was proposed
          </h2>
          <p className="mt-1 text-sm text-fg-secondary">
            {issue.open_closure.proposed_by} proposed:{" "}
            {ClosureOutcomeLabel[issue.open_closure.outcome]}
          </p>
          <p className="mt-3 whitespace-pre-line">
            {issue.open_closure.reason}
          </p>
        </section>
      )}
      {issue.assignment && <IssueProvider assignment={issue.assignment} />}
      <dl className="divide-y divide-default rounded-xl border border-default">
        {details.map(([label, value]) => (
          <div key={label} className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]">
            <dt className="text-sm text-fg-secondary">{label}</dt>
            <dd className="whitespace-pre-line">{value}</dd>
          </div>
        ))}
      </dl>
      <IssueTimeline history={issue.history} />
    </>
  );
}
