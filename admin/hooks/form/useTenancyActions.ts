"use client";
import { handleTenancyAction } from "@/api/services/tenancies/serve-action";
import type { TenancyAction, TenancyAudience } from "@/types/tenancies/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const DONE: Record<TenancyAction, string> = {
  activate: "Tenancy started",
  end: "Tenancy ended",
  cancel: "Tenancy cancelled",
};

const useTenancyActions = (audience: TenancyAudience, tenancyId: number) => {
  const router = useRouter();
  const [action, setAction] = useState<TenancyAction | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const cancel = () => {
    setAction(null);
    setError(null);
  };

  const confirm = async () => {
    if (!action) return;
    setPending(true);
    const { error } = await handleTenancyAction(tenancyId, action, audience);
    setPending(false);
    setError(error);
    if (error) return;
    toast.success(DONE[action]);
    setAction(null);
    router.refresh();
  };

  return { action, setAction, pending, error, confirm, cancel };
};

export default useTenancyActions;
