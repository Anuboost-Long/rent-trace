"use client";
import { handleDecideDocumentCase } from "@/api/services/documents/serve-action";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";
import { useRouter } from "next/navigation";
import { useState } from "react";

const DONE = {
  approve: "Version confirmed",
  reject: "Flag upheld",
} as const;

const useDocumentCaseDecision = () => {
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
    const { error } = await handleDecideDocumentCase(
      id,
      action,
      crypto.randomUUID(),
      reason,
    );
    setPending(false);
    setError(error);
    if (!error) {
      toast.success(DONE[action]);
      router.refresh();
    }
    return !error;
  };

  return { pending, error, clearError: () => setError(null), decide };
};

export default useDocumentCaseDecision;
