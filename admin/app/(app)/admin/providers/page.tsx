import {
  handleGetAdminProviders,
  handleGetAdminServiceCategories,
} from "@/api/services/providers/serve-action";
import LoadError from "@/components/common/load-error";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import PageHeader from "@/components/layout/page-header";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import ProviderFilter from "@/components/providers/provider-filter";
import { Route } from "@/constants/web-routes";
import type { AdminServiceProvider } from "@/types/providers/models";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Tradespeople · RentTrace" };

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<AdminServiceProvider>[] = [
  {
    header: "Business",
    cell: (provider) => (
      <>
        <p className="font-medium">{provider.business_name}</p>
        {provider.contact_name && (
          <p className="text-xs text-fg-tertiary">{provider.contact_name}</p>
        )}
      </>
    ),
  },
  {
    header: "Trades",
    cell: (provider) =>
      provider.categories.map((category) => category.name).join(", ") || "—",
  },
  {
    header: "Contact",
    cell: (provider) => (
      <>
        {provider.phone_number && <p>{provider.phone_number}</p>}
        {provider.email && (
          <p className="text-xs text-fg-tertiary">{provider.email}</p>
        )}
        {!provider.phone_number && !provider.email && "—"}
      </>
    ),
  },
  {
    header: "Landlord",
    cell: (provider) =>
      `${provider.owner.first_name} ${provider.owner.last_name}`,
  },
  {
    header: "Properties",
    cell: (provider) =>
      provider.properties.length === 0
        ? "—"
        : provider.properties
            .map(
              (link) =>
                `${link.property_name}${link.is_recommended ? " (preferred)" : ""}`,
            )
            .join(", "),
  },
];

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/providers">>) {
  return (
    <>
      <PageHeader
        title="Tradespeople"
        description="Plumbers, electricians and others that landlords keep on their lists."
      />
      <Suspense fallback={<ListSkeleton />}>
        <Providers searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function Providers({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/providers">, "searchParams">>) {
  const query = await searchParams;
  const filters = { q: first(query.q), category: first(query.category) };
  const page = Number(first(query.page)) || 1;
  const [providers, categories] = await Promise.all([
    handleGetAdminProviders({ ...filters, page }),
    handleGetAdminServiceCategories(),
  ]);
  const { data, error } = providers;

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.admin.providers}?${params}`;
  };

  return (
    <>
      <ProviderFilter
        action={Route.admin.providers}
        categories={categories.data ?? []}
        {...filters}
      />
      {error ? (
        <LoadError error={error} />
      ) : (
        <>
          <DataTable
            caption="Tradespeople"
            columns={columns}
            rows={data.results}
            rowKey={(provider) => provider.id}
            empty={<p className="font-medium">No tradespeople found</p>}
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
