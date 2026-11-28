"use client";
import { handleChangeListingStatus } from "@/api/services/properties/serve-action";
import type { PropertyAudience } from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useListingStatus = (audience: PropertyAudience, propertyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

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
    if (!error) {
      toast.success("Listing status updated");
      router.refresh();
    }
  };

  return { pending, error, change };
};

export default useListingStatus;
