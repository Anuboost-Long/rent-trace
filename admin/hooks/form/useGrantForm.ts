"use client";
import { handleGrantPermission } from "@/api/services/access/serve-action";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useGrantForm = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const grant = async (userId: number, permission: string, reason: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleGrantPermission(userId, permission, reason);
    setPending(false);
    setError(error);
    if (!error) {
      router.push(Route.admin.grants);
      router.refresh();
    }
  };

  return { pending, error, grant };
};

export default useGrantForm;
