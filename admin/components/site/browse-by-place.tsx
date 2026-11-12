import { Route } from "@/constants/web-routes";
import type { Place } from "@/types/listings/models";
import Link from "next/link";

const PLACE_COUNT = 8;

const placeHref = ({ state, suburb }: Place) =>
  `${Route.listings}?${new URLSearchParams({ state, suburb })}`;

export default function BrowseByPlace({
  places,
}: Readonly<{ places: Place[] }>) {
  const popular = places
    .toSorted((a, b) => b.listings - a.listings)
    .slice(0, PLACE_COUNT);

  return (
    <section
      aria-labelledby="places-heading"
      className="mx-auto mt-24 w-full max-w-7xl px-4 sm:px-6"
    >
      <div className="mb-6 flex items-end justify-between gap-4">
        <h2
          id="places-heading"
          className="text-2xl font-semibold tracking-tight"
        >
          Browse by suburb
        </h2>
        <Link
          href={Route.listings}
          className="text-sm font-medium underline underline-offset-2"
        >
          Browse all rentals
        </Link>
      </div>
      {popular.length > 0 && (
        <ul className="grid border-t border-foreground/15 sm:grid-cols-2 sm:gap-x-12">
          {popular.map((place) => (
            <li
              key={`${place.state}-${place.suburb}`}
              className="border-b border-foreground/15"
            >
              <Link
                href={placeHref(place)}
                className="group flex items-baseline justify-between gap-4 py-5 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground"
              >
                <span className="text-lg font-medium group-hover:underline group-hover:underline-offset-4">
                  {place.suburb}
                  <span className="text-foreground/60"> {place.state}</span>
                </span>
                <span className="text-sm text-foreground/60">
                  {place.listings}{" "}
                  {place.listings === 1 ? "listing" : "listings"}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
