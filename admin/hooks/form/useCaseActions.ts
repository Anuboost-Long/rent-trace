"use client";
import { handleDecideCase } from "@/api/services/evidence/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useCaseActions = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

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
    if (!error) router.refresh();
    return !error;
  };

  return { pending, error, clearError: () => setError(null), decide };
};

export default useCaseActions;
