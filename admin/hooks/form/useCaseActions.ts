"use client";
import { handleDecideCase } from "@/api/services/evidence/serve-action";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useCaseActions = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const decide = async (
    id: number,
    action: "approve" | "reject",
    reason: string,
  ) => {
    setPending(true);
    setError(null);
    const { error } = await handleDecideCase(
      id,
      action,
      crypto.randomUUID(),
      reason,
    );
    setPending(false);
    setError(error);
    if (!error) {
      toast.success(
        action === "approve" ? "Report approved" : "Report rejected",
      );
      router.refresh();
    }
    return !error;
  };

  return { pending, error, clearError: () => setError(null), decide };
};

export default useCaseActions;
