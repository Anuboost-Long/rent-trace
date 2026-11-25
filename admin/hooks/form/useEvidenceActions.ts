"use client";
import {
  handleAnswerEvidence,
  handleSubmitEvidence,
  handleWithdrawEvidence,
} from "@/api/services/evidence/serve-action";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import type { EvidenceBody } from "@/types/evidence/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useEvidenceActions = () => {
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

  return {
    pending,
    error,
    clearError: () => setError(null),
    submit: (tenancyId: number, body: EvidenceBody) =>
      run(handleSubmitEvidence(tenancyId, body)),
    withdraw: (tenancyId: number, id: number) =>
      run(handleWithdrawEvidence(tenancyId, id)),
    approve: (id: number) =>
      run(handleAnswerEvidence(id, "approve", crypto.randomUUID())),
    reject: (id: number, reason: string) =>
      run(handleAnswerEvidence(id, "reject", crypto.randomUUID(), reason)),
  };
};

export default useEvidenceActions;
