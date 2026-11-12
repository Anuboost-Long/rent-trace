import { Route } from "@/constants/web-routes";
import type { ListingSummary } from "@/types/listings/models";
import Image from "next/image";
import Link from "next/link";

import { listingPhotoUrl } from "./listing-card";

type HeroPhotosProp = Readonly<{ listings: ListingSummary[] }>;

const FILLER_SEEDS = [
  "renttrace-living-room",
  "renttrace-kitchen",
  "renttrace-street",
];

const fillerUrl = (seed: string) =>
  `https://picsum.photos/seed/${seed}/900/1100`;

export default function HeroPhotos({ listings }: HeroPhotosProp) {
  const real = listings
    .filter((listing) => listing.cover_file_id !== null)
    .slice(0, 3)
    .map((listing) => ({
      src: listingPhotoUrl(listing.id, listing.cover_file_id as number),
      alt: listing.title,
      href: Route.listing(listing.id),
    }));
  const tiles = [
    ...real,
    ...FILLER_SEEDS.slice(real.length).map((seed) => ({
      src: fillerUrl(seed),
      alt: "",
      href: null,
    })),
  ];
  const [tall, upper, lower] = tiles;

  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4">
      <Tile tile={tall} className="aspect-3/4" priority />
      <div className="flex flex-col gap-3 pt-8 sm:gap-4 sm:pt-12">
        <Tile tile={upper} className="aspect-4/5" />
        <Tile tile={lower} className="aspect-square" />
      </div>
    </div>
  );
}

type TileProp = Readonly<{
  tile: { src: string; alt: string; href: string | null };
  className: string;
  priority?: boolean;
}>;

function Tile({ tile, className, priority }: TileProp) {
  const image = (
    <span
      className={`relative block overflow-hidden rounded-2xl bg-foreground/5 ${className}`}
    >
      <Image
        src={tile.src}
        alt={tile.alt}
        fill
        unoptimized
        priority={priority}
        sizes="(min-width: 1024px) 20vw, 45vw"
        className="object-cover"
      />
    </span>
  );
  return tile.href ? (
    <Link
      href={tile.href}
      className="block rounded-2xl focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground"
    >
      {image}
    </Link>
  ) : (
    image
  );
}
