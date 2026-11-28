"use client";
import {
  handleCancelContactRequest,
  handleRespondToContactRequest,
} from "@/api/services/contact-requests/serve-action";
import type { RequestAction } from "@/constants/contact-requests";
import type { ActionResult } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const send = (
  id: number,
  action: RequestAction,
): Promise<ActionResult<unknown>> =>
  action === "cancel"
    ? handleCancelContactRequest(id)
    : handleRespondToContactRequest(id, action);

const DONE: Record<RequestAction, string> = {
  cancel: "Request cancelled",
  accept: "Request accepted",
  decline: "Request declined",
  revoke: "Access revoked",
};

const useContactRequestAction = (requestId: number) => {
  const router = useRouter();
  const [action, setAction] = useState<RequestAction | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const cancel = () => {
    setAction(null);
    setError(null);
  };

  const confirm = async () => {
    if (!action) return;
    setPending(true);
    const { error } = await send(requestId, action);
    setPending(false);
    setError(error);
    if (error) return;
    toast.success(DONE[action]);
    setAction(null);
    router.refresh();
  };

  return { action, setAction, pending, error, confirm, cancel };
};

export default useContactRequestAction;
