import { handleGetMyContactRequests } from "@/api/services/contact-requests/serve-action";
import { handleGetListing } from "@/api/services/listings/serve-action";
import ButtonLink from "@/components/common/button-link";
import ContactCard from "@/components/contact-requests/contact-card";
import RequestContactForm from "@/components/contact-requests/request-contact-form";
import Breadcrumbs from "@/components/layout/breadcrumbs";
import { listingPhotoUrl } from "@/components/site/listing-card";
import ListingGallery from "@/components/site/listing-gallery";
import { CardGridSkeleton } from "@/components/site/skeletons";
import { audienceFor } from "@/constants/audience";
import { OPEN_REQUEST_STATUSES } from "@/constants/contact-requests";
import {
  OccupancyLabel,
  PropertyTypeLabel,
  UnitTypeLabel,
} from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import type { ListingDetail, ListingPhoto } from "@/types/listings/models";
import { formatRent } from "@/utils/rent";
import { getViewer } from "@/utils/viewer";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Suspense } from "react";

export const metadata: Metadata = { title: "Rental · RentTrace" };

export default function ListingPage({ params }: PageProps<"/properties/[id]">) {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6">
      <Suspense fallback={<CardGridSkeleton count={2} />}>
        <Listing params={params} />
      </Suspense>
    </div>
  );
}

const galleryPhotos = (listingId: number, photos: ListingPhoto[]) =>
  photos.map((photo) => ({
    id: photo.id,
    url: listingPhotoUrl(listingId, photo.id),
    caption: photo.caption,
  }));

const OCCUPANCY_COPY: Record<string, string> = {
  ...OccupancyLabel,
  VACANT: "Available now",
};

async function Listing({
  params,
}: Readonly<Pick<PageProps<"/properties/[id]">, "params">>) {
  const { id } = await params;
  const { data: listing, error } = await handleGetListing(id);
  if (error?.status === 404) notFound();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  return (
    <>
      <Breadcrumbs
        trail={[
          { label: "Rentals", href: Route.listings },
          { label: listing.title },
        ]}
      />
      <div className="mt-6 grid gap-10 lg:grid-cols-12 lg:gap-14">
        <div className="lg:col-span-8">
          <ListingGallery
            title={listing.title}
            photos={galleryPhotos(listing.id, listing.photos)}
            priority
          />
          <h1 className="mt-8 text-3xl font-semibold tracking-tight">
            {listing.title}
          </h1>
          <p className="mt-1 text-foreground/70">
            {listing.suburb} {listing.state} {listing.postcode} ·{" "}
            {PropertyTypeLabel[listing.property_type]}
          </p>
          {listing.public_description && (
            <p className="mt-6 max-w-[65ch] leading-relaxed whitespace-pre-line text-foreground/80">
              {listing.public_description}
            </p>
          )}
          <Units listing={listing} />
        </div>
        <aside className="lg:col-span-4">
          <Suspense fallback={null}>
            <EnquiryPanel listing={listing} />
          </Suspense>
        </aside>
      </div>
    </>
  );
}

function Units({ listing }: Readonly<{ listing: ListingDetail }>) {
  return (
    <section aria-labelledby="units-heading" className="mt-10">
      <h2 id="units-heading" className="text-xl font-semibold tracking-tight">
        Available units
      </h2>
      <ul className="mt-4 divide-y divide-foreground/15 rounded-2xl border border-foreground/15">
        {listing.units.map((unit) => (
          <li key={unit.id} className="p-5">
            <div className="flex flex-wrap items-start justify-between gap-x-6 gap-y-1">
              <div className="min-w-0">
                <p className="font-medium">{unit.name}</p>
                <p className="text-sm text-foreground/70">
                  {UnitTypeLabel[unit.unit_type]},{" "}
                  {OCCUPANCY_COPY[unit.occupancy_status]}
                </p>
                {unit.description && (
                  <p className="mt-2 max-w-[60ch] text-sm text-foreground/80">
                    {unit.description}
                  </p>
                )}
              </div>
              <p className="font-semibold">
                {unit.rent
                  ? formatRent(unit.rent.amount, unit.rent.frequency)
                  : "Rent on request"}
              </p>
            </div>
            {unit.photos.length > 0 && (
              <div className="mt-4 max-w-lg">
                <ListingGallery
                  title={`${listing.title}, ${unit.name}`}
                  photos={galleryPhotos(listing.id, unit.photos)}
                />
              </div>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

async function TenantRequest({
  listing,
}: Readonly<{ listing: ListingDetail }>) {
  const { data } = await handleGetMyContactRequests({ page_size: 100 });
  const open = data?.results.find(
    (request) =>
      request.listing.id === listing.id &&
      OPEN_REQUEST_STATUSES.includes(request.status),
  );
  if (!open)
    return <RequestContactForm listingId={listing.id} units={listing.units} />;

  return (
    <div className="mt-4 space-y-3 text-sm">
      {open.landlord ? (
        <>
          <p className="text-foreground/70">
            The landlord accepted. Here&apos;s how to reach them:
          </p>
          <ContactCard contact={open.landlord} />
        </>
      ) : (
        <p className="text-foreground/70">
          Request sent. We&apos;ll email you when the landlord answers.
        </p>
      )}
      <Link
        href={Route.tenant.requests}
        className="inline-block font-medium underline underline-offset-2"
      >
        View your requests
      </Link>
    </div>
  );
}

async function EnquiryPanel({ listing }: Readonly<{ listing: ListingDetail }>) {
  const viewer = await getViewer();
  const audience = viewer && audienceFor(viewer);
  const signInHref = `${Route.auth.sign_in}?redirect=${encodeURIComponent(Route.listing(listing.id))}`;

  return (
    <div className="rounded-2xl border border-foreground/15 p-6 lg:sticky lg:top-24">
      {listing.from_rent ? (
        <>
          <p className="text-sm text-foreground/70">From</p>
          <p className="text-2xl font-semibold tracking-tight">
            {formatRent(listing.from_rent.amount, listing.from_rent.frequency)}
          </p>
        </>
      ) : (
        <p className="text-2xl font-semibold tracking-tight">Rent on request</p>
      )}
      {listing.listed_by && (
        <p className="mt-3 text-sm text-foreground/70">
          Listed by {listing.listed_by}
        </p>
      )}
      {!viewer && (
        <>
          <p className="mt-4 text-sm text-foreground/70">
            Sign in to get in touch about this place.
          </p>
          <ButtonLink href={signInHref} className="mt-4 w-full">
            Sign in to get in touch
          </ButtonLink>
          <ButtonLink
            href={Route.auth.sign_up}
            variant="quiet"
            className="mt-2 w-full"
          >
            Create an account
          </ButtonLink>
        </>
      )}
      {viewer && audience === "tenant" && <TenantRequest listing={listing} />}
      {viewer && audience !== "tenant" && (
        <p className="mt-4 text-sm text-foreground/70">
          This is how the listing looks to the public.
        </p>
      )}
    </div>
  );
}
