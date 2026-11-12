import { handleGetMyContactRequests } from "@/api/services/contact-requests/serve-action";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import ContactCard from "@/components/contact-requests/contact-card";
import RequestActions from "@/components/contact-requests/request-actions";
import RequestsFilter from "@/components/contact-requests/requests-filter";
import PageHeader from "@/components/layout/page-header";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { ContactRequestStatusLabel } from "@/constants/contact-requests";
import { Route } from "@/constants/web-routes";
import type { TenantContactRequest } from "@/types/contact-requests/models";
import { formatDate } from "@/utils/format-date";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Contact requests · RentTrace" };

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<TenantContactRequest>[] = [
  {
    header: "Place",
    cell: (request) => (
      <>
        <Link
          href={Route.listing(request.listing.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {request.listing.title}
        </Link>
        <p className="text-xs text-foreground/60">
          {request.unit ? `${request.unit.name}, ` : ""}
          {request.listing.suburb} {request.listing.state}
        </p>
      </>
    ),
  },
  {
    header: "Your message",
    className: "max-w-xs",
    cell: (request) => (
      <p className="line-clamp-3 whitespace-pre-line">{request.message}</p>
    ),
  },
  { header: "Sent", cell: (request) => formatDate(request.created_at) },
  {
    header: "Status",
    cell: (request) => (
      <>
        {ContactRequestStatusLabel[request.status]}
        {request.decided_at && (
          <p className="text-xs text-foreground/60">
            {formatDate(request.decided_at)}
          </p>
        )}
      </>
    ),
  },
  {
    header: "Landlord",
    cell: (request) =>
      request.landlord ? <ContactCard contact={request.landlord} /> : "—",
  },
  {
    header: "Actions",
    className: "text-right",
    cell: (request) =>
      request.status === "PENDING" && (
        <RequestActions requestId={request.id} actions={["cancel"]} />
      ),
  },
];

export default function Page({ searchParams }: PageProps<"/tenant/requests">) {
  return (
    <>
      <PageHeader
        title="Contact requests"
        description="Places you've asked a landlord about. Their details appear once they accept."
      />
      <Suspense fallback={<ListSkeleton />}>
        <Requests searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function Requests({
  searchParams,
}: Readonly<Pick<PageProps<"/tenant/requests">, "searchParams">>) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetMyContactRequests({ status, page });

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams({ page: String(target) });
    if (status) params.set("status", status);
    return `${Route.tenant.requests}?${params}`;
  };

  return (
    <>
      <RequestsFilter action={Route.tenant.requests} status={status} />
      {error ? (
        <p role="alert" className="text-red-600">
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
                <p className="font-medium">No requests yet</p>
                <p className="mt-1 text-foreground/70">
                  Open a rental and choose Request contact to ask the landlord.
                </p>
                <Link
                  href={Route.listings}
                  className="mt-2 inline-block text-sm underline"
                >
                  Browse rentals
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
