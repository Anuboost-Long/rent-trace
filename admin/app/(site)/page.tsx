import {
  handleGetListings,
  handleGetPlaces,
} from "@/api/services/listings/serve-action";
import ButtonLink from "@/components/common/button-link";
import BrowseByPlace from "@/components/site/browse-by-place";
import BrowseByType from "@/components/site/browse-by-type";
import FeaturedListing from "@/components/site/featured-listing";
import ListingCard from "@/components/site/listing-card";
import RentalRecord from "@/components/site/rental-record";
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
  const [places, latest, viewer] = await Promise.all([
    handleGetPlaces(),
    handleGetListings({ page_size: LATEST_COUNT }),
    getViewer(),
  ]);
  const listings = latest.data?.results ?? [];
  const tenant = viewer && audienceFor(viewer) === "tenant" ? viewer : null;
  const featured = listings.find(hasCover);
  const rest = listings.filter((listing) => listing !== featured);

  return (
    <>
      <section className="mx-auto w-full max-w-7xl px-4 pt-10 pb-10 sm:px-6 lg:pt-16">
        {tenant && (
          <p className="mb-4 text-sm text-foreground/70">
            Welcome back, {tenant.first_name}.{" "}
            <Link
              href={Route.tenant.index}
              className="font-medium text-foreground underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground"
            >
              Go to your tenancy
            </Link>
          </p>
        )}
        <h1 className="max-w-4xl text-4xl leading-none font-semibold tracking-tighter text-balance sm:text-6xl lg:text-7xl">
          Rent with a record you can trust.
        </h1>
        <p className="mt-5 max-w-[52ch] text-lg text-foreground/70">
          Every rental shows its rent, photos and units up front.
          {!viewer && " No account needed to look around."}
        </p>
        <div className="mt-8">
          <SearchForm places={places.data ?? []} />
        </div>
        <BrowseByType />
      </section>

      {featured && (
        <section
          aria-label="Newest rental"
          className="mx-auto w-full max-w-7xl px-4 sm:px-6"
        >
          <FeaturedListing listing={featured} />
        </section>
      )}

      {rest.length > 0 && (
        <section
          aria-labelledby="latest-heading"
          className="mx-auto mt-16 w-full max-w-7xl px-4 sm:px-6"
        >
          <h2
            id="latest-heading"
            className="mb-6 text-2xl font-semibold tracking-tight"
          >
            New on RentTrace
          </h2>
          <ul
            className={`grid gap-x-6 gap-y-10 sm:grid-cols-2 ${GRID_COLUMNS[rest.length]}`}
          >
            {rest.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </ul>
        </section>
      )}

      {listings.length === 0 && (
        <section className="mx-auto w-full max-w-7xl px-4 sm:px-6">
          <Suspense fallback={null}>
            <NothingListed />
          </Suspense>
        </section>
      )}

      <BrowseByPlace places={places.data ?? []} />

      <RentalRecord />

      <Suspense fallback={null}>
        <TwoSides />
      </Suspense>
    </>
  );
}

const hasCover = (
  listing: ListingSummary,
): listing is ListingSummary & { cover_file_id: number } =>
  listing.cover_file_id !== null;

const GRID_COLUMNS: Record<number, string> = {
  1: "lg:grid-cols-1 lg:max-w-sm",
  2: "lg:grid-cols-2",
  3: "lg:grid-cols-3",
  4: "lg:grid-cols-4",
};

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

const panelButton =
  "mt-8 inline-flex h-11 items-center rounded-lg px-5 text-sm font-semibold hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-background";
const solidPanelButton = `${panelButton} bg-background text-foreground`;
const outlinePanelButton = `${panelButton} border border-background/30 text-background`;

async function TwoSides() {
  const viewer = await getViewer();
  const audience = viewer && audienceFor(viewer);
  const landlordAction = !viewer
    ? { href: Route.auth.sign_up, label: "Create a landlord account" }
    : audience === "landlord"
      ? { href: "/landlord/properties/new", label: "Add a property" }
      : null;

  return (
    <section className="mx-auto mt-24 mb-24 w-full max-w-7xl px-4 sm:px-6">
      <div className="grid divide-y divide-background/20 overflow-hidden rounded-3xl bg-foreground text-background lg:grid-cols-2 lg:divide-x lg:divide-y-0">
        <div className="p-8 lg:p-14">
          <h2 className="text-3xl font-semibold tracking-tight">
            Looking for a place?
          </h2>
          <p className="mt-3 max-w-[44ch] text-background/70">
            Every listing shows its rent, photos and units up front. Browse
            without an account, then sign in when you want to get in touch.
          </p>
          <Link href={Route.listings} className={solidPanelButton}>
            Browse rentals
          </Link>
        </div>
        {audience === "tenant" ? (
          <div className="p-8 lg:p-14">
            <h2 className="text-3xl font-semibold tracking-tight">
              Already renting?
            </h2>
            <p className="mt-3 max-w-[44ch] text-background/70">
              See your rent, bond and landlord, and report anything that needs
              fixing.
            </p>
            <Link href={Route.tenant.index} className={outlinePanelButton}>
              Go to your tenancy
            </Link>
          </div>
        ) : (
          <div className="p-8 lg:p-14">
            <h2 className="text-3xl font-semibold tracking-tight">
              Renting out a property?
            </h2>
            <p className="mt-3 max-w-[44ch] text-background/70">
              Add your units, photos and rent, then publish when you are ready.
              You decide what the public sees.
            </p>
            {landlordAction && (
              <Link href={landlordAction.href} className={outlinePanelButton}>
                {landlordAction.label}
              </Link>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
