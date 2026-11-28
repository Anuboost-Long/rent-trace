"use client";
import Button from "@/components/common/button";
import useIssuePhotos from "@/hooks/form/useIssuePhotos";
import type {
  IssuePhoto,
  MaintenanceAudience,
} from "@/types/maintenance/models";
import { ImagePlus, X } from "lucide-react";
import Image from "next/image";
import { useRef } from "react";

type IssuePhotosProp = Readonly<{
  issueId: number;
  audience: MaintenanceAudience;
  photos: IssuePhoto[];
  canAdd: boolean;
}>;

export default function IssuePhotos({
  issueId,
  audience,
  photos,
  canAdd,
}: IssuePhotosProp) {
  const { pending, add, remove } = useIssuePhotos(issueId);
  const picker = useRef<HTMLInputElement>(null);

  if (photos.length === 0 && !canAdd) return null;

  return (
    <section aria-labelledby="photos-heading" className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="photos-heading" className="text-lg font-semibold">
          Photos
        </h2>
        {canAdd && (
          <>
            <input
              ref={picker}
              type="file"
              accept="image/jpeg,image/png"
              className="sr-only"
              tabIndex={-1}
              aria-label="Choose a photo"
              onChange={async (event) => {
                const photo = event.target.files?.[0];
                event.target.value = "";
                if (photo) await add(photo);
              }}
            />
            <Button
              size="sm"
              variant="secondary"
              className="gap-2"
              pending={pending}
              onClick={() => picker.current?.click()}
            >
              <ImagePlus aria-hidden className="size-4" />
              Add a photo
            </Button>
          </>
        )}
      </div>
      {photos.length === 0 ? (
        <p className="mt-3 max-w-[65ch] text-body-sm text-fg-secondary">
          A photo of the problem helps the landlord and any tradesperson. JPEG
          or PNG, up to 10 MB.
        </p>
      ) : (
        <ul className="mt-3 flex flex-wrap gap-3">
          {photos.map((photo) => {
            const src = `/issue-photos/${audience}/${photo.id}?issue=${issueId}`;
            return (
              <li key={photo.id} className="relative">
                <a
                  href={src}
                  target="_blank"
                  rel="noreferrer"
                  title={`${photo.name} · added by ${photo.added_by}`}
                  className="block overflow-hidden rounded-lg border border-default focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
                >
                  <Image
                    src={src}
                    alt={photo.caption ?? photo.name}
                    width={112}
                    height={112}
                    unoptimized
                    className="size-28 object-cover"
                  />
                </a>
                {photo.is_mine && canAdd && (
                  <button
                    type="button"
                    aria-label={`Remove ${photo.name}`}
                    disabled={pending}
                    onClick={() => remove(photo.id)}
                    className="absolute -top-2 -right-2 grid size-6 place-items-center rounded-full border border-default bg-background text-fg-secondary shadow-sm hover:text-error focus-visible:outline-2 focus-visible:outline-brand-border"
                  >
                    <X aria-hidden className="size-3.5" />
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
