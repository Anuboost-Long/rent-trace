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
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const usePropertyProviders = (propertyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const run = async (
    request: Promise<{ error: ApiFailure | null }>,
    done: string,
  ) => {
    setPending(true);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (error) return false;
    toast.success(done);
    router.refresh();
    return true;
  };

  return {
    pending,
    error,
    clearError: () => setError(null),
    link: (providerIds: number[]) =>
      run(handleLinkProviders(propertyId, providerIds), "Tradesperson linked"),
    update: (providerId: number, body: ProviderLinkBody) =>
      run(
        handleUpdateProviderLink(propertyId, providerId, body),
        "Link updated",
      ),
    unlink: (providerId: number) =>
      run(
        handleUnlinkProvider(propertyId, providerId),
        "Tradesperson unlinked",
      ),
  };
};

export default usePropertyProviders;
