"use client";
import { handleChangeUnitOccupancy } from "@/api/services/properties/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { PropertyAudience } from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useUnitOccupancy = (
  audience: PropertyAudience,
  propertyId: number,
  unitId: number,
) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

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
    if (!error) router.refresh();
  };

  return { pending, error, change };
};

export default useUnitOccupancy;
