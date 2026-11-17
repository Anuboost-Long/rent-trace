"use client";
import {
  handleRespondTermChange,
  handleWithdrawTermChange,
} from "@/api/services/tenancies/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type {
  TenancyAudience,
  TermChangeAnswer,
} from "@/types/tenancies/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useTermChange = (tenancyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const finish = (failure: ApiFailure | null) => {
    setPending(false);
    setError(failure);
    if (!failure) router.refresh();
    return !failure;
  };

  const respond = async (changeId: number, answer: TermChangeAnswer) => {
    setPending(true);
    setError(null);
    const { error } = await handleRespondTermChange(
      tenancyId,
      changeId,
      answer,
    );
    return finish(error);
  };

  const withdraw = async (changeId: number, audience: TenancyAudience) => {
    setPending(true);
    setError(null);
    const { error } = await handleWithdrawTermChange(
      tenancyId,
      changeId,
      audience,
    );
    return finish(error);
  };

  const clearError = () => setError(null);

  return { pending, error, respond, withdraw, clearError };
};

export default useTermChange;
