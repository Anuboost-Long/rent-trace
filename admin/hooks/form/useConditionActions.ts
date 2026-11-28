"use client";
import {
  handleCreateCondition,
  handleDeleteCondition,
  handleUpdateCondition,
} from "@/api/services/conditions/serve-action";
import type { ConditionBody } from "@/types/conditions/models";
import type { ActionResult } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useConditionActions = (unitId: number) => {
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

  const save = (id: number | null, body: ConditionBody) =>
    run(
      id === null
        ? handleCreateCondition(unitId, body)
        : handleUpdateCondition(id, body),
      id === null ? "Note added" : "Note saved",
    );

  const setShown = (id: number, shown: boolean) =>
    run(
      handleUpdateCondition(id, { is_shown_to_tenants: shown }),
      shown ? "Note shown to tenants" : "Note hidden from tenants",
    );

  const remove = (id: number) => run(handleDeleteCondition(id), "Note removed");

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
