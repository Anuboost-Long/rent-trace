"use client";
import clsx from "clsx";
import { ChevronLeft, ChevronRight, ImageIcon } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

type GalleryPhoto = { id: number; url: string; caption: string | null };

type ListingGalleryProp = Readonly<{
  title: string;
  photos: GalleryPhoto[];
  priority?: boolean;
}>;

export default function ListingGallery({
  title,
  photos,
  priority,
}: ListingGalleryProp) {
  const [index, setIndex] = useState(0);

  if (photos.length === 0) {
    return (
      <div className="flex aspect-16/10 items-center justify-center rounded-2xl bg-foreground/5">
        <ImageIcon
          aria-hidden
          className="size-10 text-foreground/30"
          strokeWidth={1.5}
        />
        <span className="sr-only">No photos yet</span>
      </div>
    );
  }

  const current = photos[index];
  const go = (step: number) =>
    setIndex((value) => (value + step + photos.length) % photos.length);

  return (
    <div>
      <div className="relative aspect-16/10 overflow-hidden rounded-2xl bg-foreground/5">
        <Image
          key={current.id}
          src={current.url}
          alt={current.caption ?? title}
          fill
          unoptimized
          priority={priority}
          sizes="(min-width: 1024px) 60vw, 100vw"
          className="animate-panel-in object-cover motion-reduce:animate-none"
        />
        {photos.length > 1 && (
          <>
            <button
              type="button"
              aria-label="Previous photo"
              onClick={() => go(-1)}
              className="absolute top-1/2 left-3 flex size-9 -translate-y-1/2 items-center justify-center rounded-full border border-foreground/15 bg-background hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground"
            >
              <ChevronLeft aria-hidden className="size-5" />
            </button>
            <button
              type="button"
              aria-label="Next photo"
              onClick={() => go(1)}
              className="absolute top-1/2 right-3 flex size-9 -translate-y-1/2 items-center justify-center rounded-full border border-foreground/15 bg-background hover:bg-foreground hover:text-background focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground"
            >
              <ChevronRight aria-hidden className="size-5" />
            </button>
            <span className="absolute right-3 bottom-3 rounded-md bg-background px-2 py-0.5 text-xs font-medium">
              {index + 1} of {photos.length}
            </span>
          </>
        )}
      </div>
      {photos.length > 1 && (
        <ul className="mt-3 grid grid-cols-5 gap-2 sm:grid-cols-6">
          {photos.map((photo, position) => (
            <li key={photo.id}>
              <button
                type="button"
                aria-label={`Show photo ${position + 1}`}
                aria-current={position === index}
                onClick={() => setIndex(position)}
                className={clsx(
                  "relative block aspect-square w-full overflow-hidden rounded-lg",
                  "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground",
                  position === index
                    ? "ring-2 ring-foreground"
                    : "opacity-70 hover:opacity-100",
                )}
              >
                <Image
                  src={photo.url}
                  alt=""
                  fill
                  unoptimized
                  sizes="120px"
                  className="object-cover"
                />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
