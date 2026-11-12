import { handleGetLandlordContactRequests } from "@/api/services/contact-requests/serve-action";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import ContactCard from "@/components/contact-requests/contact-card";
import RequestActions from "@/components/contact-requests/request-actions";
import RequestsFilter from "@/components/contact-requests/requests-filter";
import ContentSkeleton from "@/components/layout/content-skeleton";
import PageHeader from "@/components/layout/page-header";
import {
  ContactRequestStatusLabel,
  type RequestAction,
} from "@/constants/contact-requests";
import { Route } from "@/constants/web-routes";
import type { LandlordContactRequest } from "@/types/contact-requests/models";
import { formatDate } from "@/utils/format-date";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Contact requests · RentTrace" };

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const actionsFor = (status: string): RequestAction[] => {
  if (status === "PENDING") return ["decline", "accept"];
  return status === "ACCEPTED" ? ["revoke"] : [];
};

const columns: Column<LandlordContactRequest>[] = [
  {
    header: "Tenant",
    cell: (request) => {
      const name = `${request.tenant.first_name} ${request.tenant.last_name}`;
      return request.tenant_contact ? (
        <ContactCard contact={{ name, ...request.tenant_contact }} />
      ) : (
        name
      );
    },
  },
  {
    header: "Place",
    cell: (request) => (
      <>
        <p className="font-medium">{request.listing.title}</p>
        <p className="text-xs text-foreground/60">
          {request.unit ? `${request.unit.name}, ` : ""}
          {request.listing.suburb} {request.listing.state}
        </p>
      </>
    ),
  },
  {
    header: "Message",
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
    header: "Actions",
    className: "text-right",
    cell: (request) => {
      const actions = actionsFor(request.status);
      return (
        actions.length > 0 && (
          <RequestActions requestId={request.id} actions={actions} />
        )
      );
    },
  },
];

export default function Page({
  searchParams,
}: PageProps<"/landlord/requests">) {
  return (
    <>
      <PageHeader
        title="Contact requests"
        description="Tenants who want to get in touch about your listed properties. Your details are shared only if you accept."
      />
      <Suspense fallback={<ContentSkeleton />}>
        <Requests searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function Requests({
  searchParams,
}: Readonly<Pick<PageProps<"/landlord/requests">, "searchParams">>) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetLandlordContactRequests({
    status,
    page,
  });

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams({ page: String(target) });
    if (status) params.set("status", status);
    return `${Route.landlord.requests}?${params}`;
  };

  return (
    <>
      <RequestsFilter action={Route.landlord.requests} status={status} />
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
                  They appear here when a tenant asks about one of your listed
                  properties.
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
