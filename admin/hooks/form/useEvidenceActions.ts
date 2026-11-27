"use client";
import {
  handleAddEvidencePhoto,
  handleAnswerEvidence,
  handleEscalateEvidence,
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
    submit: async (tenancyId: number, body: EvidenceBody, photos: File[]) => {
      setPending(true);
      setError(null);
      const { data, error: submitError } = await handleSubmitEvidence(
        tenancyId,
        body,
      );
      let failure = submitError;
      if (data) {
        for (const photo of photos) {
          const added = await handleAddEvidencePhoto(tenancyId, data.id, photo);
          if (added.error) {
            failure = added.error;
            break;
          }
        }
      }
      setPending(false);
      setError(failure);
      if (data) router.refresh();
      return data !== null;
    },
    withdraw: (tenancyId: number, id: number) =>
      run(handleWithdrawEvidence(tenancyId, id)),
    escalate: (id: number, reason: string, tenancyId?: number) =>
      run(handleEscalateEvidence(id, reason, tenancyId)),
    approve: (id: number) =>
      run(handleAnswerEvidence(id, "approve", crypto.randomUUID())),
    reject: (id: number, reason: string) =>
      run(handleAnswerEvidence(id, "reject", crypto.randomUUID(), reason)),
  };
};

export default useEvidenceActions;
