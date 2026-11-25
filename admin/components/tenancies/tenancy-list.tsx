import { handleGetTenancies } from "@/api/services/tenancies/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import {
  TenancyAccess,
  TenancyRoutes,
  TenancyStatusLabel,
} from "@/constants/tenancies";
import { TenancyStatusTone, toneFor } from "@/constants/status-tones";
import type { TenancyAudience, TenancySummary } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import { Plus } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";

import TenanciesFilter from "./tenancies-filter";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

type TenancyListProp = Readonly<{
  audience: TenancyAudience;
  searchParams: SearchParams;
}>;

const COPY = {
  admin: "Every tenancy, with who lives there and who is invited.",
  landlord:
    "Tenancies on your properties, with who lives there and who is invited.",
};

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columnsFor = (audience: TenancyAudience): Column<TenancySummary>[] => [
  {
    header: "Tenancy",
    cell: (tenancy) => (
      <>
        <Link
          href={TenancyRoutes[audience].detail(tenancy.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {tenancy.reference_no}
        </Link>
        <p className="text-xs text-fg-tertiary">
          {tenancy.property.name ?? tenancy.property.suburb} ·{" "}
          {tenancy.unit.name}
        </p>
      </>
    ),
  },
  {
    header: "Status",
    cell: (tenancy) => (
      <StatusBadge tone={toneFor(TenancyStatusTone, tenancy.status)}>
        {TenancyStatusLabel[tenancy.status]}
      </StatusBadge>
    ),
  },
  {
    header: "Dates",
    cell: (tenancy) =>
      `${formatDate(tenancy.start_date)} – ${tenancy.end_date ? formatDate(tenancy.end_date) : "open"}`,
  },
  { header: "Tenants", cell: (tenancy) => tenancy.tenant_count },
  { header: "Pending invites", cell: (tenancy) => tenancy.pending_invitations },
];

export default function TenancyListPage({
  audience,
  searchParams,
}: TenancyListProp) {
  return (
    <>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-heading">Tenancies</h1>
          <p className="mt-1 text-fg-secondary">{COPY[audience]}</p>
        </div>
        <Can permission={TenancyAccess[audience].create}>
          <ButtonLink href={TenancyRoutes[audience].create} className="gap-2">
            <Plus aria-hidden className="size-4" />
            New tenancy
          </ButtonLink>
        </Can>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <TenancyList audience={audience} searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function TenancyList({ audience, searchParams }: TenancyListProp) {
  const query = await searchParams;
  const filters = { q: first(query.q), status: first(query.status) };
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetTenancies(
    { ...filters, page },
    audience,
  );

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${TenancyRoutes[audience].list}?${params}`;
  };

  return (
    <>
      <TenanciesFilter audience={audience} {...filters} />
      {error ? (
        <p role="alert" className="text-error">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Tenancies"
            columns={columnsFor(audience)}
            rows={data.results}
            rowKey={(tenancy) => tenancy.id}
            empty={
              <>
                <p className="font-medium">No tenancies match these filters</p>
                <Link
                  href={TenancyRoutes[audience].list}
                  className="mt-2 inline-block text-sm underline"
                >
                  Clear filters
                </Link>
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
