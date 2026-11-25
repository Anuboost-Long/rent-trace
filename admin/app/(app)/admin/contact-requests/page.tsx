import { handleGetAdminContactRequests } from "@/api/services/contact-requests/serve-action";
import LocalTime from "@/components/common/local-time";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import RequestsFilter from "@/components/contact-requests/requests-filter";
import PageHeader from "@/components/layout/page-header";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { ContactRequestStatusLabel } from "@/constants/contact-requests";
import { Route } from "@/constants/web-routes";
import type { AdminContactRequest } from "@/types/contact-requests/models";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Contact requests · RentTrace" };

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const fullName = (person: { first_name: string; last_name: string }) =>
  `${person.first_name} ${person.last_name}`;

const columns: Column<AdminContactRequest>[] = [
  { header: "Tenant", cell: (request) => fullName(request.tenant) },
  {
    header: "Place",
    cell: (request) => (
      <>
        <p className="font-medium">{request.listing.title}</p>
        <p className="text-xs text-fg-tertiary">
          {request.unit ? `${request.unit.name}, ` : ""}
          {request.listing.suburb} {request.listing.state}
        </p>
      </>
    ),
  },
  {
    header: "Landlord",
    cell: (request) => (request.landlord ? fullName(request.landlord) : "—"),
  },
  {
    header: "Message",
    className: "max-w-xs",
    cell: (request) => (
      <p className="line-clamp-3 whitespace-pre-line">{request.message}</p>
    ),
  },
  { header: "Sent", cell: (request) => <LocalTime iso={request.created_at} /> },
  {
    header: "Status",
    cell: (request) => (
      <>
        {ContactRequestStatusLabel[request.status]}
        {request.decided_at && (
          <p className="text-xs text-fg-tertiary">
            <LocalTime iso={request.decided_at} />
          </p>
        )}
      </>
    ),
  },
];

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/contact-requests">>) {
  return (
    <>
      <PageHeader
        title="Contact requests"
        description="Tenants asking landlords about listed properties. Contact details are shared only between the two of them."
      />
      <Suspense fallback={<ListSkeleton />}>
        <Requests searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function Requests({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/contact-requests">, "searchParams">>) {
  const query = await searchParams;
  const status = first(query.status);
  const q = first(query.q);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetAdminContactRequests({
    status,
    q,
    page,
  });

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams({ page: String(target) });
    if (status) params.set("status", status);
    if (q) params.set("q", q);
    return `${Route.admin.contact_requests}?${params}`;
  };

  return (
    <>
      <RequestsFilter
        action={Route.admin.contact_requests}
        status={status}
        q={q}
        canSearch
      />
      {error ? (
        <p role="alert" className="text-error">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Contact requests"
            columns={columns}
            rows={data.results}
            rowKey={(request) => request.id}
            empty={
              <>
                <p className="font-medium">No requests found</p>
                <p className="mt-1 text-fg-secondary">
                  They appear here when a tenant asks about a listed property.
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
