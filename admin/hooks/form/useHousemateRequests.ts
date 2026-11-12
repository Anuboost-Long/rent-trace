"use client";
import {
  handleRequestHousemate,
  handleWithdrawHousemate,
} from "@/api/services/tenancies/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useHousemateRequests = (tenancyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const finish = (failure: ApiFailure | null) => {
    setPending(false);
    setError(failure);
    if (!failure) router.refresh();
    return !failure;
  };

  const request = async (email: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleRequestHousemate(tenancyId, email);
    return finish(error);
  };

  const withdraw = async (invitationId: number) => {
    setPending(true);
    setError(null);
    const { error } = await handleWithdrawHousemate(tenancyId, invitationId);
    return finish(error);
  };

  return { pending, error, request, withdraw };
};

export default useHousemateRequests;
