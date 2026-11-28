"use client";
import {
  handleRequestHousemate,
  handleWithdrawHousemate,
} from "@/api/services/tenancies/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useHousemateRequests = (tenancyId: number) => {
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

  const request = async (email: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleRequestHousemate(tenancyId, email);
    return finish(error, "Request sent");
  };

  const withdraw = async (invitationId: number) => {
    setPending(true);
    setError(null);
    const { error } = await handleWithdrawHousemate(tenancyId, invitationId);
    return finish(error, "Request withdrawn");
  };

  return { pending, error, request, withdraw };
};

export default useHousemateRequests;
