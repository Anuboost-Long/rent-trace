import { handleGetProperties } from "@/api/services/properties/serve-action";
import ButtonLink from "@/components/common/button-link";
import Can from "@/components/common/can";
import StatusBadge from "@/components/common/status-badge";
import DataTable, { type Column } from "@/components/common/table/data-table";
import Pagination from "@/components/common/table/pagination";
import { ListSkeleton } from "@/components/layout/page-skeletons";
import {
  PropertyAccess,
  PropertyRoutes,
  PropertyStatusLabel,
  PropertyTypeLabel,
} from "@/constants/properties";
import type {
  PropertyAudience,
  PropertySummary,
} from "@/types/properties/models";
import { PropertyStatusTone, toneFor } from "@/constants/status-tones";
import { ownerName, propertyTitle } from "@/utils/property-address";
import { Plus } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";

import PropertiesFilter from "./properties-filter";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

type PropertyListProp = Readonly<{
  audience: PropertyAudience;
  searchParams: SearchParams;
}>;

const COPY = {
  admin: "Properties set up for landlords.",
  landlord: "Properties and units you own.",
};

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

const columnsFor = (audience: PropertyAudience): Column<PropertySummary>[] => [
  {
    header: "Property",
    cell: (property) => (
      <>
        <Link
          href={PropertyRoutes[audience].detail(property.id)}
          className="font-medium underline-offset-2 hover:underline"
        >
          {propertyTitle(property)}
        </Link>
        <p className="text-xs text-fg-tertiary">
          {property.suburb} {property.state} {property.postcode}
        </p>
      </>
    ),
  },
  {
    header: "Type",
    cell: (property) => PropertyTypeLabel[property.property_type],
  },
  ...(audience === "admin"
    ? [
        {
          header: "Owner",
          cell: (property: PropertySummary) =>
            property.owner ? ownerName(property.owner) : "—",
        },
      ]
    : []),
  { header: "Units", cell: (property) => property.unit_count },
  {
    header: "Status",
    cell: (property) => (
      <StatusBadge tone={toneFor(PropertyStatusTone, property.property_status)}>
        {PropertyStatusLabel[property.property_status]}
      </StatusBadge>
    ),
  },
];

export default function PropertyListPage({
  audience,
  searchParams,
}: PropertyListProp) {
  return (
    <>
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-heading">Properties</h1>
          <p className="mt-1 text-fg-secondary">{COPY[audience]}</p>
        </div>
        <Can permission={PropertyAccess[audience].create}>
          <ButtonLink href={PropertyRoutes[audience].create} className="gap-2">
            <Plus aria-hidden className="size-4" />
            New property
          </ButtonLink>
        </Can>
      </div>
      <Suspense fallback={<ListSkeleton />}>
        <PropertyList audience={audience} searchParams={searchParams} />
      </Suspense>
    </>
  );
}

const hasFilter = (filters: { q?: string; status?: string }) =>
  Boolean(filters.q || filters.status);

async function PropertyList({ audience, searchParams }: PropertyListProp) {
  const query = await searchParams;
  const filters = { q: first(query.q), status: first(query.status) };
  const page = Number(first(query.page)) || 1;
  const { data, error } = await handleGetProperties(
    { ...filters, page },
    audience,
  );

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${PropertyRoutes[audience].list}?${params}`;
  };

  return (
    <>
      <PropertiesFilter audience={audience} {...filters} />
      {error ? (
        <p role="alert" className="text-error">
          {error.message}
        </p>
      ) : (
        <>
          <DataTable
            caption="Properties"
            columns={columnsFor(audience)}
            rows={data.results}
            rowKey={(property) => property.id}
            empty={
              hasFilter(filters) ? (
                <>
                  <p className="font-medium">
                    No properties match these filters
                  </p>
                  <Link
                    href={PropertyRoutes[audience].list}
                    className="mt-2 inline-block text-sm underline"
                  >
                    Clear filters
                  </Link>
                </>
              ) : (
                <>
                  <p className="font-medium">No properties yet</p>
                  <Can permission={PropertyAccess[audience].create}>
                    <ButtonLink
                      href={PropertyRoutes[audience].create}
                      variant="quiet"
                      className="mt-2"
                    >
                      Add your first property
                    </ButtonLink>
                  </Can>
                </>
              )
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
