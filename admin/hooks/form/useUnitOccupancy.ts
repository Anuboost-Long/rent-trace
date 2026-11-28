"use client";
import { handleChangeUnitOccupancy } from "@/api/services/properties/serve-action";
import type { PropertyAudience } from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useUnitOccupancy = (
  audience: PropertyAudience,
  propertyId: number,
  unitId: number,
) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const change = async (occupancyStatus: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleChangeUnitOccupancy(
      propertyId,
      unitId,
      occupancyStatus,
      audience,
    );
    setPending(false);
    setError(error);
    if (!error) {
      toast.success("Unit status updated");
      router.refresh();
    }
  };

  return { pending, error, change };
};

export default useUnitOccupancy;
