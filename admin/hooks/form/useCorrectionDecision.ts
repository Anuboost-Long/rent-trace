"use client";
import { handleDecideCorrection } from "@/api/services/corrections/serve-action";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";
import { useRouter } from "next/navigation";
import { useState } from "react";

const DONE = {
  approve: "Correction approved",
  reject: "Correction rejected",
} as const;

const useCorrectionDecision = (id: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const decide = async (action: "approve" | "reject", reason: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleDecideCorrection(
      id,
      action,
      crypto.randomUUID(),
      reason.trim(),
    );
    setPending(false);
    setError(error);
    if (!error) {
      toast.success(DONE[action]);
      router.refresh();
    }
    return !error;
  };

  return { pending, error, decide };
};

export default useCorrectionDecision;
