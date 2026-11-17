"use client";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import type { PropertyFile } from "@/types/properties/models";
import { fileUrl } from "@/utils/property-files";
import { Check, Pencil, X } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

import HoverDeleteButton from "./hover-delete-button";

type PhotoTileProp = Readonly<{
  audience: string;
  propertyId: number;
  unitId?: number;
  file: PropertyFile;
  canManage: boolean;
  busy: boolean;
  removed: boolean;
  onMakeCover: () => void;
  onSaveCaption: (caption: string) => Promise<boolean>;
  onRemove: () => void;
  onUndoRemoval: () => void;
}>;

export default function PhotoTile({
  audience,
  propertyId,
  unitId,
  file,
  canManage,
  busy,
  removed,
  onMakeCover,
  onSaveCaption,
  onRemove,
  onUndoRemoval,
}: PhotoTileProp) {
  const [editing, setEditing] = useState(false);
  const description = file.caption ?? file.original_name;

  return (
    <li className="group overflow-hidden rounded-xl border border-foreground/15">
      <div className="relative aspect-4/3 bg-foreground/5">
        <Image
          src={fileUrl(audience, propertyId, file.id, unitId)}
          alt={description}
          fill
          unoptimized
          sizes="(min-width: 640px) 33vw, 50vw"
          className="object-cover"
        />
        {file.is_cover && !removed && (
          <span className="absolute top-2 left-2 rounded-md border border-foreground/15 bg-background px-2 py-0.5 text-xs font-medium">
            Cover
          </span>
        )}
        {canManage && !removed && !editing && (
          <HoverDeleteButton
            label={`Remove ${description}`}
            onClick={onRemove}
          />
        )}
        {removed && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/85 text-sm">
            <p className="font-medium">Removed when you save</p>
            <Button variant="quiet" size="sm" onClick={onUndoRemoval}>
              Undo
            </Button>
          </div>
        )}
      </div>
      <div className="space-y-2 p-3">
        {editing ? (
          <form
            onSubmit={async (event) => {
              event.preventDefault();
              const caption = String(
                new FormData(event.currentTarget).get("caption") ?? "",
              );
              if (await onSaveCaption(caption)) setEditing(false);
            }}
            className="flex items-end gap-2"
          >
            <TextInput
              label="Caption"
              name="caption"
              defaultValue={file.caption ?? ""}
              maxLength={200}
              autoFocus
            />
            <Button
              type="submit"
              size="icon"
              aria-label="Save caption"
              pending={busy}
            >
              <Check aria-hidden className="size-4" />
            </Button>
            <Button
              variant="quiet"
              size="icon"
              aria-label="Cancel"
              onClick={() => setEditing(false)}
            >
              <X aria-hidden className="size-4" />
            </Button>
          </form>
        ) : (
          <p className="truncate text-sm">
            {file.caption ?? (
              <span className="text-foreground/60">No caption</span>
            )}
          </p>
        )}
        {canManage && !editing && !removed && (
          <div className="flex items-center gap-2">
            {!file.is_cover && (
              <Button
                variant="quiet"
                size="sm"
                onClick={onMakeCover}
                disabled={busy}
              >
                Make cover
              </Button>
            )}
            <Button
              variant="quiet"
              size="icon"
              className="ml-auto"
              aria-label={`Edit caption of ${description}`}
              title="Edit caption"
              onClick={() => setEditing(true)}
            >
              <Pencil aria-hidden className="size-4" />
            </Button>
          </div>
        )}
      </div>
    </li>
  );
}
