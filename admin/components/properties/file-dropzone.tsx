"use client";
import { ACCEPT_ALL } from "@/utils/property-files";
import clsx from "clsx";
import { ImagePlus } from "lucide-react";
import { useState } from "react";

type FileDropzoneProp = Readonly<{
  onFiles: (files: File[]) => void;
  busyLabel?: string;
  disabled?: boolean;
}>;

export default function FileDropzone({
  onFiles,
  busyLabel,
  disabled,
}: FileDropzoneProp) {
  const [dragging, setDragging] = useState(false);
  const blocked = disabled || Boolean(busyLabel);

  return (
    <label
      onDragEnter={(event) => {
        event.preventDefault();
        if (!blocked) setDragging(true);
      }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
          setDragging(false);
        }
      }}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        const dropped = Array.from(event.dataTransfer.files);
        if (!blocked && dropped.length > 0) onFiles(dropped);
      }}
      className={clsx(
        "flex cursor-pointer flex-col items-center gap-3 rounded-2xl border-2 border-dashed px-6 py-10 text-center",
        "transition-colors motion-reduce:transition-none",
        dragging
          ? "border-brand-border bg-subtle"
          : "border-strong hover:border-fg-tertiary",
        "has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-brand-border",
        blocked && "pointer-events-none opacity-60",
      )}
    >
      <span className="flex size-12 items-center justify-center rounded-xl border border-default bg-background">
        <ImagePlus aria-hidden className="size-6" strokeWidth={1.5} />
      </span>
      <span className="block">
        <span className="block font-medium">
          {busyLabel ??
            (dragging ? "Drop to add" : "Drag photos and PDFs here")}
        </span>
        <span className="mt-0.5 block text-sm text-fg-secondary">
          {busyLabel ? (
            "Please wait a moment."
          ) : (
            <>
              or <span className="font-medium underline">browse files</span>
            </>
          )}
        </span>
      </span>
      <span className="block text-sm text-fg-tertiary">
        JPEG or PNG photos and PDF documents, up to 10 MB each
      </span>
      <input
        type="file"
        multiple
        accept={ACCEPT_ALL}
        disabled={blocked}
        className="sr-only"
        onChange={(event) => {
          const picked = Array.from(event.target.files ?? []);
          event.target.value = "";
          if (picked.length > 0) onFiles(picked);
        }}
      />
    </label>
  );
}
