"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import usePropertyFiles from "@/hooks/form/usePropertyFiles";
import type { PropertyAudience, PropertyFile } from "@/types/properties/models";
import { fileUrl, formatBytes } from "@/utils/property-files";
import { useAtomValue } from "jotai";
import { FileText, Trash2 } from "lucide-react";
import { useId } from "react";

import FileDropzone from "./file-dropzone";
import PhotoTile from "./photo-tile";
import StagedDocumentRow from "./staged-document-row";
import StagedPhotoTile from "./staged-photo-tile";

type PropertyFilesSectionProp = Readonly<{
  audience: PropertyAudience;
  propertyId: number;
  unitId?: number;
  files: PropertyFile[];
  managePermission: string;
}>;

const summarise = (adding: number, removing: number) =>
  [
    adding > 0 && `${adding} ${adding === 1 ? "file" : "files"} to add`,
    removing > 0 && `${removing} to remove`,
  ]
    .filter(Boolean)
    .join(", ");

export default function PropertyFilesSection({
  audience,
  propertyId,
  unitId,
  files,
  managePermission,
}: PropertyFilesSectionProp) {
  const me = useAtomValue(UserAtom);
  const canManage = me?.permissions.includes(managePermission) ?? false;
  const api = usePropertyFiles(audience, propertyId, files, unitId);
  const headingId = useId();
  const { staged } = api;
  const photos = files.filter((file) => file.kind === "PHOTO");
  const documents = files.filter((file) => file.kind === "DOCUMENT");
  const stagedPhotos = staged.items.filter((item) => item.kind === "PHOTO");
  const stagedDocuments = staged.items.filter(
    (item) => item.kind === "DOCUMENT",
  );

  return (
    <section aria-labelledby={headingId} className="mt-10">
      <h2 id={headingId} className="text-lg font-semibold">
        Photos and files
      </h2>

      {canManage && (
        <div className="mt-4 space-y-3">
          <FileDropzone
            onFiles={staged.add}
            disabled={api.saving}
            busyLabel={
              api.uploading ? `Uploading ${api.uploading}…` : undefined
            }
          />
          {staged.rejected.length > 0 && (
            <ul role="alert" className="space-y-0.5 text-sm text-red-600">
              {staged.rejected.map((message) => (
                <li key={message}>{message}</li>
              ))}
            </ul>
          )}
          {api.dirty && (
            <div
              role="status"
              className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-foreground/40 px-4 py-3"
            >
              <p className="text-sm font-medium">
                Not saved yet:{" "}
                {summarise(staged.items.length, api.removedIds.length)}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="quiet"
                  size="sm"
                  onClick={api.discard}
                  disabled={api.saving}
                >
                  Discard
                </Button>
                <Button size="sm" onClick={api.save} pending={api.saving}>
                  {api.saving ? "Saving…" : "Save changes"}
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      <h3 className="mt-8 text-sm font-semibold">Photos ({photos.length})</h3>
      {photos.length === 0 && stagedPhotos.length === 0 ? (
        <p className="mt-2 text-foreground/70">
          No photos yet. The first one you add becomes the cover.
        </p>
      ) : (
        <ul className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
          {photos.map((photo) => (
            <PhotoTile
              key={photo.id}
              audience={audience}
              propertyId={propertyId}
              unitId={unitId}
              file={photo}
              canManage={canManage}
              busy={api.pending}
              removed={api.removedIds.includes(photo.id)}
              onMakeCover={() => api.setCover(photo.id)}
              onSaveCaption={(caption) => api.saveCaption(photo.id, caption)}
              onRemove={() => api.markRemoval(photo.id)}
              onUndoRemoval={() => api.undoRemoval(photo.id)}
            />
          ))}
          {stagedPhotos.map((item) => (
            <StagedPhotoTile
              key={item.id}
              item={item}
              badge="New"
              onRemove={() => staged.remove(item.id)}
            />
          ))}
        </ul>
      )}

      <h3 className="mt-8 text-sm font-semibold">
        Documents ({documents.length})
      </h3>
      {documents.length === 0 && stagedDocuments.length === 0 ? (
        <p className="mt-2 text-foreground/70">
          No documents yet. Add PDFs such as ownership papers or floor plans.
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
          {documents.map((document) => {
            const removed = api.removedIds.includes(document.id);
            return (
              <li key={document.id} className="flex items-center gap-3 p-4">
                <FileText
                  aria-hidden
                  className="size-5 shrink-0"
                  strokeWidth={1.5}
                />
                <div className="min-w-0 flex-1">
                  <a
                    href={fileUrl(audience, propertyId, document.id, unitId)}
                    target="_blank"
                    rel="noopener"
                    className={`block truncate font-medium underline-offset-2 hover:underline ${removed ? "line-through opacity-60" : ""}`}
                  >
                    {document.original_name}
                  </a>
                  <p className="text-sm text-foreground/70">
                    {removed
                      ? "Removed when you save"
                      : formatBytes(document.size_bytes)}
                  </p>
                </div>
                {canManage &&
                  (removed ? (
                    <Button
                      variant="quiet"
                      size="sm"
                      onClick={() => api.undoRemoval(document.id)}
                    >
                      Undo
                    </Button>
                  ) : (
                    <Button
                      variant="quiet"
                      size="icon"
                      aria-label={`Remove ${document.original_name}`}
                      title="Remove"
                      onClick={() => api.markRemoval(document.id)}
                    >
                      <Trash2 aria-hidden className="size-4" />
                    </Button>
                  ))}
              </li>
            );
          })}
          {stagedDocuments.map((item) => (
            <StagedDocumentRow
              key={item.id}
              item={item}
              onRemove={() => staged.remove(item.id)}
            />
          ))}
        </ul>
      )}

      {api.failures.length > 0 && (
        <div
          role="alert"
          className="mt-4 rounded-xl border border-red-600 p-4 text-sm"
        >
          <p className="font-medium text-red-600">
            {api.failures.length === 1
              ? "1 change wasn't saved"
              : `${api.failures.length} changes weren't saved`}
          </p>
          <ul className="mt-1 space-y-0.5">
            {api.failures.map((failure) => (
              <li key={failure.id}>
                {failure.name}: {failure.message}
              </li>
            ))}
          </ul>
          <p className="mt-2 text-foreground/70">
            They are still listed above, so you can try saving again.
          </p>
          <Button
            variant="quiet"
            size="sm"
            className="mt-3"
            onClick={api.clearFailures}
          >
            Dismiss
          </Button>
        </div>
      )}
    </section>
  );
}
