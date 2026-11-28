"use client";
import {
  handleAddIssuePhoto,
  handleRemoveIssuePhoto,
} from "@/api/services/maintenance/serve-action";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useIssuePhotos = (issueId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const finish = (failure: Parameters<typeof setError>[0], done: string) => {
    setPending(false);
    setError(failure);
    if (!failure) {
      toast.success(done);
      router.refresh();
    }
  };

  const add = async (photo: File) => {
    setPending(true);
    setError(null);
    const formData = new FormData();
    formData.set("file", photo);
    const { error } = await handleAddIssuePhoto(issueId, formData);
    finish(error, "Photo added");
  };

  const remove = async (fileId: number) => {
    setPending(true);
    setError(null);
    const { error } = await handleRemoveIssuePhoto(issueId, fileId);
    finish(error, "Photo removed");
  };

  return { pending, error, add, remove };
};

export default useIssuePhotos;
