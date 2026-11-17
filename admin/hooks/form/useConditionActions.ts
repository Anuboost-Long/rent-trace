"use client";
import {
  handleCreateCondition,
  handleDeleteCondition,
  handleUpdateCondition,
} from "@/api/services/conditions/serve-action";
import type { ConditionBody } from "@/types/conditions/models";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useConditionActions = (unitId: number) => {
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

  const save = (id: number | null, body: ConditionBody) =>
    run(
      id === null
        ? handleCreateCondition(unitId, body)
        : handleUpdateCondition(id, body),
    );

  const setShown = (id: number, shown: boolean) =>
    run(handleUpdateCondition(id, { is_shown_to_tenants: shown }));

  const remove = (id: number) => run(handleDeleteCondition(id));

  return {
    pending,
    error,
    clearError: () => setError(null),
    save,
    setShown,
    remove,
  };
};

export default useConditionActions;
