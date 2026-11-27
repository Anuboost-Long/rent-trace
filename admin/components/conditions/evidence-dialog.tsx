"use client";
import DateInput from "@/components/common/inputs/date-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import type { ApiFailure } from "@/types/api/common";
import type { EvidenceBody } from "@/types/evidence/models";
import { todayIso } from "@/utils/calendar";
import { ImagePlus, X } from "lucide-react";
import { useRef, useState } from "react";

const MAX_PHOTOS = 5;

type EvidenceDialogProp = Readonly<{
  pending: boolean;
  error: ApiFailure | null;
  onSend: (body: EvidenceBody, photos: File[]) => void;
  onCancel: () => void;
}>;

export default function EvidenceDialog({
  pending,
  error,
  onSend,
  onCancel,
}: EvidenceDialogProp) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [seenOn, setSeenOn] = useState(todayIso());
  const [photos, setPhotos] = useState<File[]>([]);
  const picker = useRef<HTMLInputElement>(null);
  const fields = error?.fields ?? {};

  return (
    <ConfirmDialog
      open
      title="Report a condition"
      message="Your landlord reviews it. You can withdraw it until they answer."
      confirmLabel="Send report"
      pending={pending}
      confirmDisabled={title.trim() === "" || seenOn === ""}
      error={
        error && Object.keys(fields).length === 0 ? error.message : undefined
      }
      onConfirm={() =>
        onSend(
          {
            title: title.trim(),
            description: description.trim(),
            observed_at: `${seenOn}T00:00:00Z`,
          },
          photos,
        )
      }
      onCancel={onCancel}
    >
      <div className="space-y-4">
        <TextInput
          label="What it is"
          name="title"
          placeholder="Damp patch in the bedroom"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          error={fields.title}
          required
        />
        <TextArea
          label="What you saw"
          name="description"
          placeholder="On the wall near the window, about the size of a plate"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          error={fields.description}
        />
        <DateInput
          label="Seen on"
          name="observed_at"
          defaultValue={seenOn}
          required
          onValueChange={setSeenOn}
          error={fields.observed_at}
        />
        <div>
          <p className="text-body-sm font-medium">Photos</p>
          <input
            ref={picker}
            type="file"
            accept="image/jpeg,image/png"
            multiple
            hidden
            onChange={(event) => {
              const picked = Array.from(event.target.files ?? []);
              setPhotos((current) =>
                [...current, ...picked].slice(0, MAX_PHOTOS),
              );
              event.target.value = "";
            }}
          />
          <ul className="mt-2 flex flex-wrap gap-2">
            {photos.map((photo, index) => (
              <li
                key={`${photo.name}-${photo.size}-${index}`}
                className="flex items-center gap-1 rounded-full border border-default bg-subtle py-1 pr-1 pl-3 text-caption"
              >
                <span className="max-w-32 truncate">{photo.name}</span>
                <button
                  type="button"
                  aria-label={`Remove ${photo.name}`}
                  onClick={() =>
                    setPhotos((current) =>
                      current.filter((_, i) => i !== index),
                    )
                  }
                  className="grid size-5 place-items-center rounded-full hover:bg-muted focus-visible:outline-2 focus-visible:outline-brand-border"
                >
                  <X aria-hidden className="size-3" />
                </button>
              </li>
            ))}
            {photos.length < MAX_PHOTOS && (
              <li>
                <button
                  type="button"
                  onClick={() => picker.current?.click()}
                  className="inline-flex h-8 items-center gap-1.5 rounded-full border border-dashed border-strong px-3 text-caption text-fg-brand hover:bg-brand-subtle focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
                >
                  <ImagePlus aria-hidden className="size-4" />
                  Add photos
                </button>
              </li>
            )}
          </ul>
          <p className="mt-1.5 text-caption text-fg-tertiary">
            Up to {MAX_PHOTOS} JPEG or PNG images, 10 MB each.
          </p>
        </div>
      </div>
    </ConfirmDialog>
  );
}
