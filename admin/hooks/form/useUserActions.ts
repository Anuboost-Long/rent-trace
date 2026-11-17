"use client";
import {
  handleActivateUser,
  handleDeactivateUser,
  handleDeleteUser,
} from "@/api/services/users/serve-action";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

export type UserAction = "activate" | "deactivate" | "delete";

const requests: Record<
  UserAction,
  (id: number) => Promise<ActionResult<unknown>>
> = {
  activate: handleActivateUser,
  deactivate: handleDeactivateUser,
  delete: handleDeleteUser,
};

const useUserActions = (userId: number, afterDelete?: () => void) => {
  const router = useRouter();
  const [action, setAction] = useState<UserAction | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const cancel = () => {
    setAction(null);
    setError(null);
  };

  const confirm = async () => {
    if (!action) return;
    setPending(true);
    const { error } = await requests[action](userId);
    setPending(false);
    setError(error);
    if (error) return;
    setAction(null);
    if (action === "delete" && afterDelete) afterDelete();
    else router.refresh();
  };

  return { action, setAction, pending, error, confirm, cancel };
};

export default useUserActions;
