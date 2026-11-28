import { handleGetDocumentCases } from "@/api/services/documents/serve-action";
import FilterChips from "@/components/common/filter-chips";
import LoadError from "@/components/common/load-error";
import Pagination from "@/components/common/table/pagination";
import DocumentCaseItem from "@/components/documents/document-case-item";
import PageHeader from "@/components/layout/page-header";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Document cases · RentTrace" };

const FILTERS = [
  { label: "Waiting", status: undefined },
  { label: "Confirmed", status: "APPROVED" },
  { label: "Flag upheld", status: "REJECTED" },
] as const;

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/document-cases">>) {
  return (
    <>
      <PageHeader
        title="Document cases"
        description="Papers a tenant flagged, or that nobody answered, that someone asked an admin to decide."
      />
      <Suspense fallback={<ListSkeleton />}>
        <Cases searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function Cases({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/document-cases">, "searchParams">>) {
  const query = await searchParams;
  const status = first(query.status);
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetDocumentCases({ status, page });
  if (error) return <LoadError error={error} />;

  const hrefFor = (target: { status?: string; page?: number }) => {
    const params = new URLSearchParams(
      Object.entries(target).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.document_cases}?${params}`;
  };

  return (
    <div className="space-y-4">
      <FilterChips
        label="Filter document cases"
        chips={FILTERS.map((filter) => ({
          label: filter.label,
          href: hrefFor({ status: filter.status }),
          active: filter.status === status,
        }))}
      />
      {data.results.length === 0 ? (
        <div className="rounded-xl border border-default bg-background py-12 text-center">
          <p className="font-medium">
            {status ? "Nothing here" : "Nothing waiting for a decision"}
          </p>
          <p className="mt-1 text-body-sm text-fg-secondary">
            When someone asks an admin to decide on a paper, it shows up here.
          </p>
        </div>
      ) : (
        <ul className="divide-y divide-default overflow-hidden rounded-xl border border-default bg-background">
          {data.results.map((item) => (
            <li key={item.id}>
              <DocumentCaseItem item={item} />
            </li>
          ))}
        </ul>
      )}
      <Pagination
        page={data.page}
        totalPages={data.total_pages}
        count={data.count}
        hrefForPage={(target) => hrefFor({ status, page: target })}
      />
    </div>
  );
}
