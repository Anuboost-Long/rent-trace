import { PropertyTypeLabel } from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import type { ListingSummary } from "@/types/listings/models";
import { formatRent } from "@/utils/rent";
import clsx from "clsx";
import { ImageIcon } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

type ListingCardProp = Readonly<{
  listing: ListingSummary;
  featured?: boolean;
  priority?: boolean;
  className?: string;
}>;

export const listingPhotoUrl = (listingId: number, fileId: number) =>
  `/listing-photos/${listingId}/${fileId}`;

export default function ListingCard({
  listing,
  featured,
  priority,
  className,
}: ListingCardProp) {
  return (
    <li className={clsx("group", featured && "h-full", className)}>
      <Link
        href={Route.listing(listing.id)}
        className={clsx(
          "flex flex-col rounded-2xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-foreground",
          featured && "h-full",
        )}
      >
        <span
          className={clsx(
            "relative block overflow-hidden rounded-2xl bg-foreground/5",
            featured ? "min-h-64 flex-1" : "aspect-4/3",
          )}
        >
          {listing.cover_file_id ? (
            <Image
              src={listingPhotoUrl(listing.id, listing.cover_file_id)}
              alt={listing.title}
              fill
              unoptimized
              priority={priority}
              sizes={
                featured
                  ? "(min-width: 1024px) 50vw, 100vw"
                  : "(min-width: 1024px) 25vw, 50vw"
              }
              className="object-cover transition-transform duration-500 group-hover:scale-105 motion-reduce:transition-none"
            />
          ) : (
            <span className="absolute inset-0 flex items-center justify-center">
              <ImageIcon
                aria-hidden
                className="size-8 text-foreground/30"
                strokeWidth={1.5}
              />
            </span>
          )}
          {listing.photo_count > 1 && (
            <span className="absolute right-3 bottom-3 rounded-md bg-background px-2 py-0.5 text-xs font-medium">
              {listing.photo_count} photos
            </span>
          )}
        </span>
        <span className="mt-3 block">
          <span
            className={clsx(
              "block font-medium",
              featured ? "text-xl" : "text-base",
            )}
          >
            {listing.title}
          </span>
          <span className="block text-sm text-foreground/70">
            {listing.suburb} {listing.state} {listing.postcode}
          </span>
          <span className="mt-1 block text-sm">
            {listing.from_rent ? (
              <>
                <span className="font-semibold">
                  From{" "}
                  {formatRent(
                    listing.from_rent.amount,
                    listing.from_rent.frequency,
                  )}
                </span>
                <span className="text-foreground/70">
                  {" "}
                  · {PropertyTypeLabel[listing.property_type]}
                </span>
              </>
            ) : (
              <span className="text-foreground/70">
                {PropertyTypeLabel[listing.property_type]} · Rent on request
              </span>
            )}
          </span>
        </span>
      </Link>
    </li>
  );
}
