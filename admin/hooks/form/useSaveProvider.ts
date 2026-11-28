"use client";
import {
  handleCreateProvider,
  handleUpdateProvider,
} from "@/api/services/providers/serve-action";
import { Route } from "@/constants/web-routes";
import type { ProviderBody } from "@/types/providers/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useSaveProvider = (providerId?: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const save = async (body: ProviderBody) => {
    setPending(true);
    setError(null);
    const { error } = providerId
      ? await handleUpdateProvider(providerId, body)
      : await handleCreateProvider(body);
    setPending(false);
    setError(error);
    if (error) return;
    toast.success("Tradesperson saved");
    router.push(Route.landlord.providers);
    router.refresh();
  };

  return { pending, error, save };
};

export default useSaveProvider;
