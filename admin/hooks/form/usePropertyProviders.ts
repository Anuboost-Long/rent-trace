"use client";
import {
  handleLinkProviders,
  handleUnlinkProvider,
  handleUpdateProviderLink,
} from "@/api/services/providers/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { ProviderLinkBody } from "@/types/providers/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const usePropertyProviders = (propertyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const run = async (request: Promise<{ error: ApiFailure | null }>) => {
    setPending(true);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (error) return false;
    router.refresh();
    return true;
  };

  return {
    pending,
    error,
    clearError: () => setError(null),
    link: (providerIds: number[]) =>
      run(handleLinkProviders(propertyId, providerIds)),
    update: (providerId: number, body: ProviderLinkBody) =>
      run(handleUpdateProviderLink(propertyId, providerId, body)),
    unlink: (providerId: number) =>
      run(handleUnlinkProvider(propertyId, providerId)),
  };
};

export default usePropertyProviders;
