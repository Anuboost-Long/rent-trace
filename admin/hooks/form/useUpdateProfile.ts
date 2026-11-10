"use client";
import { handleUpdateProfile } from "@/api/services/auth/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { ProfileBody } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useUpdateProfile = (onSaved: () => void) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const save = async (body: ProfileBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleUpdateProfile(body);
    setPending(false);
    setError(error);
    if (!data) return;
    router.refresh();
    onSaved();
  };

  return { pending, error, clearError: () => setError(null), save };
};

export default useUpdateProfile;
