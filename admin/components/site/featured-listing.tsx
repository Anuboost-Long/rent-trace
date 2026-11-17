import { PropertyTypeLabel } from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import type { ListingSummary } from "@/types/listings/models";
import { formatRent } from "@/utils/rent";
import Image from "next/image";
import Link from "next/link";

import { listingPhotoUrl } from "./listing-card";

type FeaturedListingProp = Readonly<{
  listing: ListingSummary & { cover_file_id: number };
}>;

export default function FeaturedListing({ listing }: FeaturedListingProp) {
  return (
    <Link
      href={Route.listing(listing.id)}
      className="group relative block aspect-4/5 overflow-hidden rounded-3xl bg-foreground/5 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-foreground sm:aspect-video lg:aspect-21/9"
    >
      <Image
        src={listingPhotoUrl(listing.id, listing.cover_file_id)}
        alt=""
        fill
        priority
        unoptimized
        sizes="(min-width: 1280px) 1216px, 100vw"
        className="object-cover transition-transform duration-700 group-hover:scale-105 motion-reduce:transition-none"
      />
      <span
        aria-hidden
        className="absolute inset-0 bg-linear-to-t from-black/75 via-black/10 to-transparent"
      />
      <span className="absolute inset-x-0 bottom-0 flex flex-wrap items-end justify-between gap-5 p-6 text-white sm:p-10">
        <span>
          <span className="block text-3xl font-semibold tracking-tight text-balance sm:text-5xl">
            {listing.title}
          </span>
          <span className="mt-2 block text-white/80">
            {listing.suburb} {listing.state} {listing.postcode}
            {" · "}
            {PropertyTypeLabel[listing.property_type]}
          </span>
          <span className="mt-1 block text-lg font-semibold">
            {listing.from_rent
              ? `From ${formatRent(listing.from_rent.amount, listing.from_rent.frequency)}`
              : "Rent on request"}
          </span>
        </span>
        <span className="inline-flex h-11 items-center rounded-lg bg-white px-5 text-sm font-semibold text-black">
          View rental
        </span>
      </span>
    </Link>
  );
}
