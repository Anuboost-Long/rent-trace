"use client";
import { handleUpdateTenancy } from "@/api/services/tenancies/serve-action";
import { TenancyRoutes } from "@/constants/tenancies";
import type {
  TenancyAudience,
  UpdateTenancyBody,
} from "@/types/tenancies/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useUpdateTenancy = (audience: TenancyAudience, tenancyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const save = async (body: UpdateTenancyBody) => {
    setPending(true);
    setError(null);
    const { error } = await handleUpdateTenancy(tenancyId, body, audience);
    setPending(false);
    setError(error);
    if (error) return;
    toast.success("Tenancy updated");
    router.push(TenancyRoutes[audience].detail(tenancyId));
    router.refresh();
  };

  return { pending, error, save };
};

export default useUpdateTenancy;
