import {
  handleGetListings,
  handleGetPlaces,
} from "@/api/services/listings/serve-action";
import ButtonLink from "@/components/common/button-link";
import HeroPhotos from "@/components/site/hero-photos";
import ListingCard from "@/components/site/listing-card";
import SearchForm from "@/components/site/search-form";
import { HomeSkeleton } from "@/components/site/skeletons";
import { audienceFor } from "@/constants/audience";
import { Route } from "@/constants/web-routes";
import type { ListingSummary } from "@/types/listings/models";
import { getViewer } from "@/utils/viewer";
import Link from "next/link";
import { Suspense } from "react";

const LATEST_COUNT = 5;

export default function HomePage() {
  return (
    <Suspense fallback={<HomeSkeleton />}>
      <Home />
    </Suspense>
  );
}

async function Home() {
  const [places, latest] = await Promise.all([
    handleGetPlaces(),
    handleGetListings({ page_size: LATEST_COUNT }),
  ]);
  const listings = latest.data?.results ?? [];

  return (
    <>
      <section className="mx-auto grid w-full max-w-7xl gap-10 px-4 pt-10 pb-16 sm:px-6 lg:grid-cols-12 lg:gap-12 lg:pt-16">
        <div className="flex flex-col justify-center lg:col-span-7">
          <h1 className="text-4xl leading-none font-semibold tracking-tighter text-balance sm:text-5xl lg:text-6xl">
            Rent with a record you can trust.
          </h1>
          <p className="mt-5 max-w-[52ch] text-lg text-foreground/70">
            Browse rentals from landlords who keep clear records. No account
            needed to look around.
          </p>
          <div className="mt-8">
            <SearchForm places={places.data ?? []} />
          </div>
        </div>
        <div className="lg:col-span-5">
          <HeroPhotos listings={listings} />
        </div>
      </section>

      <section
        aria-labelledby="latest-heading"
        className="mx-auto w-full max-w-7xl px-4 sm:px-6"
      >
        <div className="mb-6 flex items-end justify-between gap-4">
          <h2
            id="latest-heading"
            className="text-2xl font-semibold tracking-tight"
          >
            New on RentTrace
          </h2>
          <Link
            href={Route.listings}
            className="text-sm font-medium underline underline-offset-2"
          >
            Browse all rentals
          </Link>
        </div>
        {listings.length === 0 ? (
          <Suspense fallback={null}>
            <NothingListed />
          </Suspense>
        ) : (
          <LatestListings listings={listings} />
        )}
      </section>

      <Suspense fallback={null}>
        <TwoSides />
      </Suspense>
    </>
  );
}

const GRID_COLUMNS: Record<number, string> = {
  1: "lg:grid-cols-1 lg:max-w-sm",
  2: "lg:grid-cols-2",
  3: "lg:grid-cols-3",
  4: "lg:grid-cols-4",
};

function LatestListings({
  listings,
}: Readonly<{ listings: ListingSummary[] }>) {
  if (listings.length >= LATEST_COUNT) {
    const [featured, ...rest] = listings;
    return (
      <ul className="grid gap-x-6 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 lg:grid-rows-2 lg:gap-y-6">
        <ListingCard
          listing={featured}
          featured
          priority
          className="sm:col-span-2 lg:row-span-2"
        />
        {rest.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </ul>
    );
  }
  return (
    <ul
      className={`grid gap-x-6 gap-y-10 sm:grid-cols-2 ${GRID_COLUMNS[listings.length]}`}
    >
      {listings.map((listing) => (
        <ListingCard key={listing.id} listing={listing} />
      ))}
    </ul>
  );
}

async function NothingListed() {
  const viewer = await getViewer();
  const isLandlord = viewer && audienceFor(viewer) === "landlord";

  return (
    <div className="rounded-2xl border border-dashed border-foreground/25 p-10">
      <p className="text-lg font-medium">No rentals are listed yet.</p>
      <p className="mt-1 text-foreground/70">
        New listings appear here as soon as landlords publish them.
      </p>
      {(!viewer || isLandlord) && (
        <ButtonLink
          href={isLandlord ? "/landlord/properties/new" : Route.auth.sign_up}
          className="mt-5"
        >
          {isLandlord ? "Add a property" : "List a property"}
        </ButtonLink>
      )}
    </div>
  );
}

async function TwoSides() {
  const viewer = await getViewer();
  const audience = viewer && audienceFor(viewer);
  const landlordAction = !viewer
    ? { href: Route.auth.sign_up, label: "Create a landlord account" }
    : audience === "landlord"
      ? { href: "/landlord/properties/new", label: "Add a property" }
      : null;

  return (
    <section className="mx-auto mt-24 w-full max-w-7xl px-4 sm:px-6">
      <div className="grid divide-y divide-foreground/15 rounded-2xl border border-foreground/15 lg:grid-cols-2 lg:divide-x lg:divide-y-0">
        <div className="p-8 lg:p-12">
          <h2 className="text-2xl font-semibold tracking-tight">
            Looking for a place?
          </h2>
          <p className="mt-3 max-w-[48ch] text-foreground/70">
            Every listing shows its rent, photos and units up front. Browse
            without an account, then sign in when you want to get in touch.
          </p>
          <ButtonLink href={Route.listings} variant="quiet" className="mt-6">
            Browse rentals
          </ButtonLink>
        </div>
        <div className="p-8 lg:p-12">
          <h2 className="text-2xl font-semibold tracking-tight">
            Renting out a property?
          </h2>
          <p className="mt-3 max-w-[48ch] text-foreground/70">
            Add your units, photos and rent, then publish when you are ready.
            You decide what the public sees.
          </p>
          {landlordAction && (
            <ButtonLink href={landlordAction.href} className="mt-6">
              {landlordAction.label}
            </ButtonLink>
          )}
        </div>
      </div>
    </section>
  );
}
