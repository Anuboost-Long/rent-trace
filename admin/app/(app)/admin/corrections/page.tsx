import { handleGetCorrections } from "@/api/services/corrections/serve-action";
import FilterChips from "@/components/common/filter-chips";
import LoadError from "@/components/common/load-error";
import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import PageHeader from "@/components/layout/page-header";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import {
  CorrectionFilters,
  CorrectionStatusLabel,
} from "@/constants/corrections";
import { CorrectionStatusTone, toneFor } from "@/constants/status-tones";
import { Route } from "@/constants/web-routes";
import type { Correction } from "@/types/corrections/models";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Corrections · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/corrections">>) {
  return (
    <>
      <PageHeader
        title="Corrections"
        description="A tenant or landlord asked to change a locked condition note. You can only decide between what the parties submitted."
      />
      <Suspense fallback={<ListSkeleton />}>
        <CorrectionList searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<Correction>[] = [
  {
    header: "Case",
    cell: (correction) => (
      <>
        <p className="font-medium">{correction.current_title}</p>
        <p className="text-caption text-fg-tertiary">
          Correction · C-{correction.id}
        </p>
      </>
    ),
  },
  { header: "Property", cell: (correction) => correction.place },
  {
    header: "Asked by",
    cell: (correction) => (
      <>
        {correction.requested_by_name}
        <p className="text-caption text-fg-tertiary">
          {correction.requester_side === "TENANT" ? "Tenant" : "Landlord"}
        </p>
      </>
    ),
  },
  {
    header: "Status",
    cell: (correction) => (
      <StatusBadge tone={toneFor(CorrectionStatusTone, correction.status)}>
        {CorrectionStatusLabel[correction.status]}
      </StatusBadge>
    ),
  },
  {
    header: "Opened",
    cell: (correction) => <LocalTime iso={correction.submitted_at} />,
  },
];

async function CorrectionList({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/corrections">, "searchParams">>) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetCorrections({ status, page });
  if (error) return <LoadError error={error} />;

  const hrefFor = (target: { status?: string; page?: number }) => {
    const params = new URLSearchParams(
      Object.entries(target).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.corrections}?${params}`;
  };

  return (
    <div className="space-y-4">
      <FilterChips
        label="Filter corrections"
        chips={CorrectionFilters.map((filter) => ({
          label: filter.label,
          href: hrefFor({ status: filter.status }),
          active: filter.status === status,
        }))}
      />
      <DataTable
        caption="Corrections"
        columns={columns}
        rows={data.results}
        rowKey={(correction) => correction.id}
        rowHref={(correction) => Route.admin.correction(correction.id)}
        empty={
          <>
            <p className="font-medium">
              {status ? "Nothing here" : "No corrections waiting"}
            </p>
            <p className="mt-1 text-body-sm text-fg-secondary">
              When someone asks to correct a condition note, it shows up here.
            </p>
          </>
        }
      />
      <Pagination
        page={data.page}
        totalPages={data.total_pages}
        count={data.count}
        hrefForPage={(target) => hrefFor({ status, page: target })}
      />
    </div>
  );
}
