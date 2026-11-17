"use client";
import { handleChangeListingStatus } from "@/api/services/properties/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { PropertyAudience } from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useListingStatus = (audience: PropertyAudience, propertyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const change = async (listingStatus: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleChangeListingStatus(
      audience,
      propertyId,
      listingStatus,
    );
    setPending(false);
    setError(error);
    if (!error) router.refresh();
  };

  return { pending, error, change };
};

export default useListingStatus;
