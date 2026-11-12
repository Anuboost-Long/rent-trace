import {
  handleGetListings,
  handleGetPlaces,
} from "@/api/services/listings/serve-action";
import Pagination from "@/components/common/table/pagination";
import ListingCard from "@/components/site/listing-card";
import ListingFilters from "@/components/site/listing-filters";
import { CardGridSkeleton } from "@/components/site/skeletons";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Rentals · RentTrace" };

const PAGE_SIZE = 12;

const first = (value: string | string[] | undefined) =>
  typeof value === "string" ? value : undefined;

export default function BrowsePage({ searchParams }: PageProps<"/properties">) {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6">
      <h1 className="text-3xl font-semibold tracking-tight">Rentals</h1>
      <Suspense fallback={<CardGridSkeleton />}>
        <Results searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

async function Results({
  searchParams,
}: Readonly<Pick<PageProps<"/properties">, "searchParams">>) {
  const query = await searchParams;
  const filters = {
    q: first(query.q),
    state: first(query.state),
    suburb: first(query.suburb),
    type: first(query.type),
    min_rent: first(query.min_rent),
    max_rent: first(query.max_rent),
    sort: first(query.sort),
  };
  const page = Number(first(query.page)) || 1;
  const [listings, places] = await Promise.all([
    handleGetListings({ ...filters, page, page_size: PAGE_SIZE }),
    handleGetPlaces(),
  ]);

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams(
      Object.entries({ ...filters, page: target }).flatMap(([key, value]) =>
        value ? [[key, String(value)]] : [],
      ),
    );
    return `${Route.listings}?${params}`;
  };

  return (
    <>
      <p className="mt-1 mb-6 text-foreground/70">
        {listings.data
          ? `${listings.data.count} ${listings.data.count === 1 ? "place" : "places"} to rent`
          : "Places to rent"}
      </p>
      <ListingFilters places={places.data ?? []} values={filters} />
      <div className="mt-10">
        {listings.error ? (
          <p role="alert" className="text-red-600">
            {listings.error.message}
          </p>
        ) : listings.data.results.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-foreground/25 p-10">
            <p className="text-lg font-medium">
              No rentals match these filters.
            </p>
            <p className="mt-1 text-foreground/70">
              Try a different suburb or widen the rent range.
            </p>
            <Link
              href={Route.listings}
              className="mt-4 inline-block text-sm font-medium underline underline-offset-2"
            >
              Clear filters
            </Link>
          </div>
        ) : (
          <>
            <ul className="grid gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-3">
              {listings.data.results.map((listing, index) => (
                <ListingCard
                  key={listing.id}
                  listing={listing}
                  priority={index < 3}
                />
              ))}
            </ul>
            <Pagination
              page={listings.data.page}
              totalPages={listings.data.total_pages}
              count={listings.data.count}
              hrefForPage={hrefForPage}
            />
          </>
        )}
      </div>
    </>
  );
}
