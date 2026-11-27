"use client";
import {
  handleRemoveProfilePicture,
  handleSetProfilePicture,
  handleUpdateProfile,
} from "@/api/services/auth/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { ProfileBody } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

export type PictureChange = { file: File } | { remove: true } | null;

const applyPicture = (change: PictureChange) => {
  if (change === null) return null;
  if ("remove" in change) return handleRemoveProfilePicture();
  const formData = new FormData();
  formData.set("file", change.file);
  return handleSetProfilePicture(formData);
};

const useUpdateProfile = (onSaved: () => void) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const save = async (body: ProfileBody, picture: PictureChange = null) => {
    setPending(true);
    setError(null);
    const pictureResult = await applyPicture(picture);
    const { data, error } = pictureResult?.error
      ? { data: null, error: pictureResult.error }
      : await handleUpdateProfile(body);
    setPending(false);
    setError(error);
    if (!data) return;
    router.refresh();
    onSaved();
  };

  return { pending, error, clearError: () => setError(null), save };
};

export default useUpdateProfile;
