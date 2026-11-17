"use client";
import {
  handleCreateProvider,
  handleUpdateProvider,
} from "@/api/services/providers/serve-action";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import type { ProviderBody } from "@/types/providers/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useSaveProvider = (providerId?: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const save = async (body: ProviderBody) => {
    setPending(true);
    setError(null);
    const { error } = providerId
      ? await handleUpdateProvider(providerId, body)
      : await handleCreateProvider(body);
    setPending(false);
    setError(error);
    if (error) return;
    router.push(Route.landlord.providers);
    router.refresh();
  };

  return { pending, error, save };
};

export default useSaveProvider;
