"use client";
import {
  handleAddEvidencePhoto,
  handleAnswerEvidence,
  handleEscalateEvidence,
  handleSubmitEvidence,
  handleWithdrawEvidence,
} from "@/api/services/evidence/serve-action";
import type { ActionResult } from "@/types/api/common";
import type { EvidenceBody } from "@/types/evidence/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useEvidenceActions = () => {
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
      if (data) {
        toast.success(
          failure
            ? "Report sent, but a photo could not be added"
            : "Report sent",
        );
        router.refresh();
      }
      return data !== null;
    },
    withdraw: (tenancyId: number, id: number) =>
      run(handleWithdrawEvidence(tenancyId, id), "Report withdrawn"),
    escalate: (id: number, reason: string, tenancyId?: number) =>
      run(
        handleEscalateEvidence(id, reason, tenancyId),
        "Sent to an admin to decide",
      ),
    approve: (id: number) =>
      run(
        handleAnswerEvidence(id, "approve", crypto.randomUUID()),
        "Report approved",
      ),
    reject: (id: number, reason: string) =>
      run(
        handleAnswerEvidence(id, "reject", crypto.randomUUID(), reason),
        "Report rejected",
      ),
  };
};

export default useEvidenceActions;
