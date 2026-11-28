"use client";
import SelectInput from "@/components/common/inputs/select-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { ACCEPTED_FILES, DocumentTypeLabel } from "@/constants/documents";
import type { ApiFailure } from "@/types/api/common";
import type { DocumentType, UploadFields } from "@/types/documents/models";
import { useState } from "react";

type UploadDialogProp = Readonly<{
  heading: string;
  confirmLabel: string;
  types: DocumentType[] | null;
  initialTitle?: string;
  pending: boolean;
  error: ApiFailure | null;
  onSubmit: (fields: UploadFields, file: File) => void;
  onCancel: () => void;
}>;

export default function UploadDialog({
  heading,
  confirmLabel,
  types,
  initialTitle = "",
  pending,
  error,
  onSubmit,
  onCancel,
}: UploadDialogProp) {
  const [type, setType] = useState<DocumentType>(types?.[0] ?? "OTHER");
  const [title, setTitle] = useState(initialTitle);
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);

  return (
    <ConfirmDialog
      open
      title={heading}
      message="A PDF, JPEG or PNG file, up to 10 MB."
      confirmLabel={confirmLabel}
      pending={pending}
      confirmDisabled={title.trim() === "" || file === null}
      error={error?.message}
      onConfirm={() =>
        file &&
        onSubmit(
          {
            document_type: type,
            title: title.trim(),
            description: description.trim(),
          },
          file,
        )
      }
      onCancel={onCancel}
    >
      <div className="space-y-4">
        {types && (
          <SelectInput
            name="document_type"
            label="What is it?"
            value={type}
            onValueChange={(value) => setType(value as DocumentType)}
            options={types.map((value) => ({
              value,
              label: DocumentTypeLabel[value],
            }))}
          />
        )}
        <TextInput
          name="title"
          label="Title"
          value={title}
          maxLength={200}
          onChange={(event) => setTitle(event.target.value)}
          error={error?.fields.title}
          required
        />
        <TextArea
          name="description"
          label="Description (optional)"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
        <div className="flex flex-col gap-1.5">
          <label htmlFor="document-file" className="text-body-sm font-medium">
            File
          </label>
          <input
            id="document-file"
            type="file"
            accept={ACCEPTED_FILES}
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            className="block w-full rounded-lg border border-strong bg-background text-body-sm file:mr-3 file:h-10 file:border-0 file:bg-brand-subtle file:px-4 file:font-medium file:text-fg-brand"
          />
          {error?.fields.file && (
            <p role="alert" className="text-body-sm text-error">
              {error.fields.file}
            </p>
          )}
        </div>
      </div>
    </ConfirmDialog>
  );
}
