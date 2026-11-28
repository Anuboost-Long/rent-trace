"use client";
import { handleGrantPermission } from "@/api/services/access/serve-action";
import { Route } from "@/constants/web-routes";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useGrantForm = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const grant = async (userId: number, permission: string, reason: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleGrantPermission(userId, permission, reason);
    setPending(false);
    setError(error);
    if (!error) {
      toast.success("Permission granted");
      router.push(Route.admin.grants);
      router.refresh();
    }
  };

  return { pending, error, grant };
};

export default useGrantForm;
