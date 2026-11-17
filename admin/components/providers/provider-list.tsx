import {
  handleGetProviders,
  handleGetServiceCategories,
} from "@/api/services/providers/serve-action";
import ButtonLink from "@/components/common/button-link";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import { Route } from "@/constants/web-routes";
import type { ServiceProvider } from "@/types/providers/models";
import { Plus } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";

import ProviderFilter from "./provider-filter";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

type ProviderListProp = Readonly<{ searchParams: SearchParams }>;

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columns: Column<ServiceProvider>[] = [
  {
    header: "Business",
    cell: (provider) => (
      <>
        <Link
          href={Route.landlord.provider(provider.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {provider.business_name}
        </Link>
        {provider.contact_name && (
          <p className="text-xs text-foreground/60">{provider.contact_name}</p>
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
          <p className="text-xs text-foreground/60">{provider.email}</p>
        )}
        {!provider.phone_number && !provider.email && "—"}
      </>
    ),
  },
  {
    header: "Properties",
    cell: (provider) => provider.properties.length,
  },
];

export default function ProviderListPage({ searchParams }: ProviderListProp) {
  return (
    <>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Tradespeople</h1>
          <p className="mt-1 text-foreground/70">
            Plumbers, electricians and others you call. Link them to your
            properties so tenants know who to contact.
          </p>
        </div>
        <ButtonLink href={Route.landlord.provider_new} className="gap-2">
          <Plus aria-hidden className="size-4" />
          Add tradesperson
        </ButtonLink>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <ProviderList searchParams={searchParams} />
      </Suspense>
    </>
  );
}

async function ProviderList({ searchParams }: ProviderListProp) {
  const query = await searchParams;
  const filters = { q: first(query.q), category: first(query.category) };
  const page = Number(first(query.page)) || 1;
  const [providers, categories] = await Promise.all([
    handleGetProviders({ ...filters, page }),
    handleGetServiceCategories(),
  ]);
  const { data, error } = providers;

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.landlord.providers}?${params}`;
  };

  return (
    <>
      <ProviderFilter
        action={Route.landlord.providers}
        categories={categories.data ?? []}
        {...filters}
      />
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Tradespeople"
            columns={columns}
            rows={data.results}
            rowKey={(provider) => provider.id}
            empty={
              <>
                <p className="font-medium">No tradespeople yet</p>
                <ButtonLink
                  href={Route.landlord.provider_new}
                  variant="quiet"
                  className="mt-2"
                >
                  Add your first tradesperson
                </ButtonLink>
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
