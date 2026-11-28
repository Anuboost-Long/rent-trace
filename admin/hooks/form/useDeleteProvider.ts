"use client";
import { handleDeleteProvider } from "@/api/services/providers/serve-action";
import { Route } from "@/constants/web-routes";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useDeleteProvider = (providerId: number) => {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

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
    toast.success("Tradesperson removed");
    router.replace(Route.landlord.providers);
    router.refresh();
  };

  return { confirming, setConfirming, pending, error, confirm, cancel };
};

export default useDeleteProvider;
