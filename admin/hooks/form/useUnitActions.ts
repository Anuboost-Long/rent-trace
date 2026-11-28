"use client";
import {
  handleCreateUnit,
  handleDeleteUnit,
  handleUpdateUnit,
} from "@/api/services/properties/serve-action";
import type { ActionResult } from "@/types/api/common";
import type { PropertyAudience, UnitBody } from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useUnitActions = (
  propertyId: number,
  audience: PropertyAudience = "admin",
) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const run = async (request: Promise<ActionResult<unknown>>, done: string) => {
    setPending(true);
    setError(null);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (!error) {
      toast.success(done);
      router.refresh();
    }
    return !error;
  };

  const saveUnit = (unitId: number | null, body: UnitBody) =>
    run(
      unitId === null
        ? handleCreateUnit(propertyId, body, audience)
        : handleUpdateUnit(propertyId, unitId, body, audience),
      unitId === null ? "Unit added" : "Unit saved",
    );

  const removeUnit = (unitId: number) =>
    run(handleDeleteUnit(propertyId, unitId, audience), "Unit removed");

  return {
    pending,
    error,
    clearError: () => setError(null),
    saveUnit,
    removeUnit,
  };
};

export default useUnitActions;
