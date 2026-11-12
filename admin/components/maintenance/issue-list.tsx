import { handleGetIssues } from "@/api/services/maintenance/serve-action";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import ContentSkeleton from "@/components/layout/content-skeleton";
import {
  IssuePriorityLabel,
  IssueRoutes,
  IssueStatusLabel,
} from "@/constants/maintenance";
import type {
  IssueSummary,
  MaintenanceAudience,
} from "@/types/maintenance/models";
import { formatDate } from "@/utils/format-date";
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
        <p className="text-xs text-foreground/60">
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
        {IssueStatusLabel[issue.status]}
        {issue.has_open_closure && (
          <p className="text-xs text-foreground/60">Closure waiting</p>
        )}
      </>
    ),
  },
  ...(audience === "landlord"
    ? [
        {
          header: "Reported by",
          cell: (issue: IssueSummary) => issue.reported_by_name,
        },
      ]
    : []),
  { header: "Reported", cell: (issue) => formatDate(issue.reported_at) },
];

export default function IssueListBody({
  audience,
  searchParams,
}: IssueListProp) {
  return (
    <Suspense fallback={<ContentSkeleton />}>
      <IssueList audience={audience} searchParams={searchParams} />
    </Suspense>
  );
}

async function IssueList({ audience, searchParams }: IssueListProp) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetIssues({ status, page });

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ status, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${IssueRoutes[audience].list}?${params}`;
  };

  return (
    <>
      <IssuesFilter audience={audience} status={status} />
      {error ? (
        <p role="alert" className="text-red-600">
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
                <p className="mt-1 text-sm text-foreground/70">
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
