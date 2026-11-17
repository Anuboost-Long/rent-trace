"use client";
import {
  handleCancelContactRequest,
  handleRespondToContactRequest,
} from "@/api/services/contact-requests/serve-action";
import type { RequestAction } from "@/constants/contact-requests";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const send = (
  id: number,
  action: RequestAction,
): Promise<ActionResult<unknown>> =>
  action === "cancel"
    ? handleCancelContactRequest(id)
    : handleRespondToContactRequest(id, action);

const useContactRequestAction = (requestId: number) => {
  const router = useRouter();
  const [action, setAction] = useState<RequestAction | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

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
    setAction(null);
    router.refresh();
  };

  return { action, setAction, pending, error, confirm, cancel };
};

export default useContactRequestAction;
