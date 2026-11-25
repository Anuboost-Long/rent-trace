import type { StagedFiles } from "@/hooks/form/useStagedFiles";

import FileDropzone from "./file-dropzone";
import StagedDocumentRow from "./staged-document-row";
import StagedPhotoTile from "./staged-photo-tile";

type FilePickerProp = Readonly<{
  staged: StagedFiles;
  disabled?: boolean;
}>;

export default function FilePicker({ staged, disabled }: FilePickerProp) {
  const photos = staged.items.filter((item) => item.kind === "PHOTO");
  const documents = staged.items.filter((item) => item.kind === "DOCUMENT");

  return (
    <fieldset className="flex flex-col gap-3" disabled={disabled}>
      <legend className="mb-1 text-sm font-semibold">
        Photos and files (optional)
      </legend>
      <FileDropzone onFiles={staged.add} disabled={disabled} />
      <p className="text-sm text-fg-secondary">
        Files stay here until you create the property. The first photo becomes
        the cover.
      </p>
      {staged.rejected.length > 0 && (
        <ul role="alert" className="space-y-0.5 text-sm text-error">
          {staged.rejected.map((message) => (
            <li key={message}>{message}</li>
          ))}
        </ul>
      )}
      {photos.length > 0 && (
        <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {photos.map((item, index) => (
            <StagedPhotoTile
              key={item.id}
              item={item}
              badge={index === 0 ? "Cover" : "New"}
              onRemove={() => staged.remove(item.id)}
            />
          ))}
        </ul>
      )}
      {documents.length > 0 && (
        <ul className="divide-y divide-default rounded-xl border border-default">
          {documents.map((item) => (
            <StagedDocumentRow
              key={item.id}
              item={item}
              onRemove={() => staged.remove(item.id)}
            />
          ))}
        </ul>
      )}
    </fieldset>
  );
}
