"use client";
import { handleAcceptInvitation } from "@/api/services/tenancies/serve-action";
import type { AcceptedInvitation } from "@/types/tenancies/models";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useAcceptInvitation = (token: string) => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();
  const [accepted, setAccepted] = useState<AcceptedInvitation | null>(null);

  const accept = async () => {
    setPending(true);
    setError(null);
    const result = await handleAcceptInvitation(token);
    setPending(false);
    setError(result.error);
    setAccepted(result.data);
    if (result.data) toast.success("Invitation accepted");
  };

  return { pending, error, accepted, accept };
};

export default useAcceptInvitation;
