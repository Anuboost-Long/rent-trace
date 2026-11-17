"use client";
import { handleDeleteProvider } from "@/api/services/providers/serve-action";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useDeleteProvider = (providerId: number) => {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const cancel = () => {
    setConfirming(false);
    setError(null);
  };

  const confirm = async () => {
    setPending(true);
    const { error } = await handleDeleteProvider(providerId);
    setPending(false);
    setError(error);
    if (error) return;
    router.replace(Route.landlord.providers);
    router.refresh();
  };

  return { confirming, setConfirming, pending, error, confirm, cancel };
};

export default useDeleteProvider;
