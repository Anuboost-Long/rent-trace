"use client";
import { handleCreateBan } from "@/api/services/bans/serve-action";
import {
  handleActivateUser,
  handleDeactivateUser,
  handleDeleteUser,
} from "@/api/services/users/serve-action";
import type { ActionResult } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

export type UserAction = "activate" | "deactivate" | "ban" | "delete";

const requests: Record<
  UserAction,
  (id: number, reason: string) => Promise<ActionResult<unknown>>
> = {
  activate: (id, reason) => handleActivateUser(id, reason || undefined),
  deactivate: (id, reason) => handleDeactivateUser(id, reason),
  ban: (id, reason) =>
    handleCreateBan({ ban_type: "ACCOUNT", user_id: id, reason }),
  delete: (id) => handleDeleteUser(id),
};

const DONE: Record<UserAction, string> = {
  activate: "Account reactivated",
  deactivate: "Account suspended",
  ban: "Account banned",
  delete: "Account deleted",
};

const useUserActions = (userId: number, afterDelete?: () => void) => {
  const router = useRouter();
  const [action, setAction] = useState<UserAction | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const cancel = () => {
    setAction(null);
    setError(null);
  };

  const confirm = async (reason = "") => {
    if (!action) return;
    setPending(true);
    const { error } = await requests[action](userId, reason);
    setPending(false);
    setError(error);
    if (error) return;
    toast.success(DONE[action]);
    setAction(null);
    if (action === "delete" && afterDelete) afterDelete();
    else router.refresh();
  };

  return { action, setAction, pending, error, confirm, cancel };
};

export default useUserActions;
