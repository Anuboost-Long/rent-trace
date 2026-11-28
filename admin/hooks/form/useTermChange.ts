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
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useTermChange = (tenancyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const finish = (failure: ApiFailure | null, done: string) => {
    setPending(false);
    setError(failure);
    if (!failure) {
      toast.success(done);
      router.refresh();
    }
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
    return finish(
      error,
      answer === "approve" ? "Change approved" : "Change declined",
    );
  };

  const withdraw = async (changeId: number, audience: TenancyAudience) => {
    setPending(true);
    setError(null);
    const { error } = await handleWithdrawTermChange(
      tenancyId,
      changeId,
      audience,
    );
    return finish(error, "Proposal withdrawn");
  };

  const clearError = () => setError(null);

  return { pending, error, respond, withdraw, clearError };
};

export default useTermChange;
