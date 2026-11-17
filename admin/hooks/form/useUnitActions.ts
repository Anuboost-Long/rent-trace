"use client";
import {
  handleCreateUnit,
  handleDeleteUnit,
  handleUpdateUnit,
} from "@/api/services/properties/serve-action";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import type { PropertyAudience, UnitBody } from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useUnitActions = (
  propertyId: number,
  audience: PropertyAudience = "admin",
) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const run = async (request: Promise<ActionResult<unknown>>) => {
    setPending(true);
    setError(null);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (!error) router.refresh();
    return !error;
  };

  const saveUnit = (unitId: number | null, body: UnitBody) =>
    run(
      unitId === null
        ? handleCreateUnit(propertyId, body, audience)
        : handleUpdateUnit(propertyId, unitId, body, audience),
    );

  const removeUnit = (unitId: number) =>
    run(handleDeleteUnit(propertyId, unitId, audience));

  return {
    pending,
    error,
    clearError: () => setError(null),
    saveUnit,
    removeUnit,
  };
};

export default useUnitActions;
