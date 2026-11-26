import type { EvidenceAudience, EvidencePhoto } from "@/types/evidence/models";
import Image from "next/image";

type EvidencePhotosProp = Readonly<{
  photos: EvidencePhoto[];
  audience: EvidenceAudience | "admin";
  tenancyId: number;
}>;

export default function EvidencePhotos({
  photos,
  audience,
  tenancyId,
}: EvidencePhotosProp) {
  if (photos.length === 0) return null;

  return (
    <ul className="mt-2 flex flex-wrap gap-2">
      {photos.map((photo) => {
        const src = `/evidence-photos/${audience}/${photo.id}?tenancy=${tenancyId}`;
        return (
          <li key={photo.id}>
            <a
              href={src}
              target="_blank"
              rel="noreferrer"
              title={photo.name}
              className="block overflow-hidden rounded-lg border border-default focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
            >
              <Image
                src={src}
                alt={photo.name}
                width={64}
                height={64}
                unoptimized
                className="size-16 object-cover"
              />
            </a>
          </li>
        );
      })}
    </ul>
  );
}
