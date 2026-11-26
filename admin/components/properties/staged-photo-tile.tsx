import type { PendingFile } from "@/hooks/form/useStagedFiles";
import Image from "next/image";

import HoverDeleteButton from "./hover-delete-button";

type StagedPhotoTileProp = Readonly<{
  item: PendingFile;
  badge: string;
  onRemove: () => void;
}>;

export default function StagedPhotoTile({
  item,
  badge,
  onRemove,
}: StagedPhotoTileProp) {
  return (
    <li className="group relative aspect-4/3 overflow-hidden rounded-xl border border-dashed border-strong bg-subtle">
      {item.previewUrl && (
        <Image
          src={item.previewUrl}
          alt={item.file.name}
          fill
          unoptimized
          sizes="(min-width: 640px) 33vw, 50vw"
          className="object-cover"
        />
      )}
      <span className="absolute top-2 left-2 rounded-md border border-default bg-background px-2 py-0.5 text-xs font-medium">
        {badge}
      </span>
      <HoverDeleteButton
        label={`Remove ${item.file.name}`}
        onClick={onRemove}
      />
    </li>
  );
}
