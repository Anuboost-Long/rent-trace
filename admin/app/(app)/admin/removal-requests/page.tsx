import { handleGetRemovals } from "@/api/services/removals/serve-action";
import FilterChips from "@/components/common/filter-chips";
import LoadError from "@/components/common/load-error";
import LocalTime from "@/components/common/local-time";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import PageHeader from "@/components/layout/page-header";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { RemovalFilters, RemovalStatusLabel } from "@/constants/removals";
import { RemovalStatusTone, toneFor } from "@/constants/status-tones";
import { Route } from "@/constants/web-routes";
import type { Removal } from "@/types/removals/models";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Removal requests · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/removal-requests">>) {
  return (
    <>
      <PageHeader
        title="Removal requests"
        description="Tenants and landlords ask for records to be hidden. Nothing is deleted: approved records are hidden but kept for history and the audit log."
      />
      <Suspense fallback={<ListSkeleton />}>
        <RemovalList searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<Removal>[] = [
  { header: "Request", cell: (removal) => `R-${removal.id}` },
  {
    header: "Records",
    cell: (removal) => {
      const [firstItem] = removal.items;
      return (
        <>
          <p className="font-medium">
            {removal.items.length === 1
              ? (firstItem?.title ?? "A record")
              : `${removal.items.length} records`}
          </p>
          {removal.items.length > 1 && (
            <p className="text-caption text-fg-tertiary">
              {firstItem?.title ?? "A record"} and others
            </p>
          )}
        </>
      );
    },
  },
  {
    header: "Asked by",
    cell: (removal) => (
      <>
        {removal.requested_by_name}
        <p className="text-caption text-fg-tertiary">
          {removal.requester_side === "TENANT" ? "Tenant" : "Landlord"}
        </p>
      </>
    ),
  },
  {
    header: "Status",
    cell: (removal) => (
      <StatusBadge tone={toneFor(RemovalStatusTone, removal.status)}>
        {RemovalStatusLabel[removal.status]}
      </StatusBadge>
    ),
  },
  {
    header: "Asked",
    cell: (removal) => <LocalTime iso={removal.submitted_at} />,
  },
];

async function RemovalList({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/removal-requests">, "searchParams">>) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetRemovals({ status, page });
  if (error) return <LoadError error={error} />;

  const hrefFor = (target: { status?: string; page?: number }) => {
    const params = new URLSearchParams(
      Object.entries(target).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.removal_requests}?${params}`;
  };

  return (
    <div className="space-y-4">
      <FilterChips
        label="Filter removal requests"
        chips={RemovalFilters.map((filter) => ({
          label: filter.label,
          href: hrefFor({ status: filter.status }),
          active: filter.status === status,
        }))}
      />
      <DataTable
        caption="Removal requests"
        columns={columns}
        rows={data.results}
        rowKey={(removal) => removal.id}
        rowHref={(removal) => Route.admin.removal_request(removal.id)}
        empty={
          <>
            <p className="font-medium">
              {status ? "Nothing here" : "No removal requests waiting"}
            </p>
            <p className="mt-1 text-body-sm text-fg-secondary">
              When someone asks to hide a record, it shows up here.
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
