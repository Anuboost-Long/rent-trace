"use client";
import { handleAcceptInvitation } from "@/api/services/tenancies/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { AcceptedInvitation } from "@/types/tenancies/models";
import { useState } from "react";

const useAcceptInvitation = (token: string) => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);
  const [accepted, setAccepted] = useState<AcceptedInvitation | null>(null);

  const accept = async () => {
    setPending(true);
    setError(null);
    const result = await handleAcceptInvitation(token);
    setPending(false);
    setError(result.error);
    setAccepted(result.data);
  };

  return { pending, error, accepted, accept };
};

export default useAcceptInvitation;
