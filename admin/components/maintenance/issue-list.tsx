import { handleGetIssues } from "@/api/services/maintenance/serve-action";
import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { IssueStatusTone, toneFor } from "@/constants/status-tones";
import {
  IssuePriorityLabel,
  IssueRoutes,
  IssueStatusLabel,
} from "@/constants/maintenance";
import type {
  IssueSummary,
  MaintenanceAudience,
} from "@/types/maintenance/models";
import Link from "next/link";
import { Suspense } from "react";

import IssuesFilter from "./issues-filter";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

type IssueListProp = Readonly<{
  audience: MaintenanceAudience;
  searchParams: SearchParams;
}>;

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columnsFor = (audience: MaintenanceAudience): Column<IssueSummary>[] => [
  {
    header: "Issue",
    cell: (issue) => (
      <>
        <Link
          href={IssueRoutes[audience].detail(issue.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {issue.title}
        </Link>
        <p className="text-xs text-fg-tertiary">
          {issue.property.name ?? issue.property.suburb} · {issue.unit.name}
        </p>
      </>
    ),
  },
  { header: "Priority", cell: (issue) => IssuePriorityLabel[issue.priority] },
  {
    header: "Status",
    cell: (issue) => (
      <>
        <StatusBadge tone={toneFor(IssueStatusTone, issue.status)}>
          {IssueStatusLabel[issue.status]}
        </StatusBadge>
        {issue.has_open_closure && (
          <p className="text-xs text-fg-tertiary">Closure waiting</p>
        )}
      </>
    ),
  },
  ...(audience !== "tenant"
    ? [
        {
          header: "Reported by",
          cell: (issue: IssueSummary) => issue.reported_by_name,
        },
      ]
    : []),
  {
    header: "Reported",
    cell: (issue) => <LocalTime iso={issue.reported_at} />,
  },
];

export default function IssueListBody({
  audience,
  searchParams,
}: IssueListProp) {
  return (
    <Suspense fallback={<ListSkeleton />}>
      <IssueList audience={audience} searchParams={searchParams} />
    </Suspense>
  );
}

async function IssueList({ audience, searchParams }: IssueListProp) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const q = first(query.q);
  const { data, error } = await handleGetIssues({ status, q, page }, audience);

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ status, q, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${IssueRoutes[audience].list}?${params}`;
  };

  return (
    <>
      <IssuesFilter audience={audience} status={status} q={q} />
      {error ? (
        <p role="alert" className="text-error">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Maintenance issues"
            columns={columnsFor(audience)}
            rows={data.results}
            rowKey={(issue) => issue.id}
            empty={
              <>
                <p className="font-medium">
                  {status ? "No issues with this status" : "No issues yet"}
                </p>
                <p className="mt-1 text-sm text-fg-secondary">
                  {audience === "tenant"
                    ? "Report something that needs fixing and your landlord is told."
                    : "When a tenant reports something it shows up here."}
                </p>
              </>
            }
          />
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            count={data.count}
            hrefForPage={hrefForPage}
          />
        </>
      )}
    </>
  );
}
