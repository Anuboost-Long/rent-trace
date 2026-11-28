"use client";
import {
  handleDeletePropertyFile,
  handleUpdatePropertyFile,
  handleUploadPropertyFile,
} from "@/api/services/properties/serve-action";
import type { ActionResult } from "@/types/api/common";
import type {
  PropertyAudience,
  PropertyFile,
  PropertyFileKind,
} from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import useStagedFiles from "./useStagedFiles";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

export type UploadFailure = { id: string; name: string; message: string };

export const uploadPropertyFiles = async (
  audience: PropertyAudience,
  propertyId: number,
  files: { id: string; file: File; kind: PropertyFileKind }[],
  onStart?: (name: string) => void,
  unitId?: number,
) => {
  const failures: UploadFailure[] = [];
  for (const { id, file, kind } of files) {
    onStart?.(file.name);
    const form = new FormData();
    form.set("file", file);
    form.set("kind", kind);
    const { error } = await handleUploadPropertyFile(
      audience,
      propertyId,
      form,
      unitId,
    );
    if (error) {
      failures.push({
        id,
        name: file.name,
        message: error.fields.file ?? error.message,
      });
    }
  }
  return failures;
};

const usePropertyFiles = (
  audience: PropertyAudience,
  propertyId: number,
  files: PropertyFile[],
  unitId?: number,
) => {
  const router = useRouter();
  const staged = useStagedFiles();
  const [removedIds, setRemovedIds] = useState<number[]>([]);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState("");
  const [failures, setFailures] = useState<UploadFailure[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const dirty = staged.items.length > 0 || removedIds.length > 0;

  useEffect(() => {
    if (!dirty) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);

  const save = async () => {
    setSaving(true);
    setFailures([]);
    const failed: UploadFailure[] = [];
    const notRemoved: number[] = [];
    for (const id of removedIds) {
      const { error } = await handleDeletePropertyFile(
        audience,
        propertyId,
        id,
        unitId,
      );
      if (error) {
        notRemoved.push(id);
        failed.push({
          id: String(id),
          name: files.find((file) => file.id === id)?.original_name ?? "A file",
          message: error.message,
        });
      }
    }
    const notUploaded = await uploadPropertyFiles(
      audience,
      propertyId,
      staged.items,
      setUploading,
      unitId,
    );
    setUploading("");
    staged.keepOnly(notUploaded.map((failure) => failure.id));
    setRemovedIds(notRemoved);
    setFailures([...failed, ...notUploaded]);
    setSaving(false);
    const uploaded = staged.items.length - notUploaded.length;
    const removed = removedIds.length - notRemoved.length;
    if (uploaded > 0)
      toast.success(`${uploaded} file${uploaded === 1 ? "" : "s"} uploaded`);
    if (removed > 0)
      toast.success(`${removed} file${removed === 1 ? "" : "s"} removed`);
    if (failed.length + notUploaded.length > 0) {
      toast.error("Some files could not be saved. See the list for why.");
    }
    router.refresh();
  };

  const discard = () => {
    staged.clear();
    setRemovedIds([]);
    setFailures([]);
  };

  const run = async (request: Promise<ActionResult<unknown>>, done: string) => {
    setPending(true);
    setError(null);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (!error) {
      toast.success(done);
      router.refresh();
    }
    return !error;
  };

  return {
    staged,
    removedIds,
    markRemoval: (fileId: number) =>
      setRemovedIds((current) => [...current, fileId]),
    undoRemoval: (fileId: number) =>
      setRemovedIds((current) => current.filter((id) => id !== fileId)),
    dirty,
    saving,
    uploading,
    save,
    discard,
    failures,
    clearFailures: () => setFailures([]),
    pending,
    error,
    setCover: (fileId: number) =>
      run(
        handleUpdatePropertyFile(
          audience,
          propertyId,
          fileId,
          { is_cover: true },
          unitId,
        ),
        "Cover photo set",
      ),
    saveCaption: (fileId: number, caption: string) =>
      run(
        handleUpdatePropertyFile(
          audience,
          propertyId,
          fileId,
          { caption },
          unitId,
        ),
        "Caption saved",
      ),
  };
};

export default usePropertyFiles;
