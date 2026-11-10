"use client";
import {
  handleGrantPermission,
  handleRevokePermission,
} from "@/api/services/access/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useGrants = (userId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const grant = async (permission: string, reason: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleGrantPermission(userId, permission, reason);
    setPending(false);
    setError(error);
    if (!error) router.refresh();
    return !error;
  };

  const revoke = async (permission: string) => {
    setPending(true);
    setError(null);
    const { error } = await handleRevokePermission(userId, permission);
    setPending(false);
    setError(error);
    if (!error) router.refresh();
    return !error;
  };

  return { pending, error, grant, revoke };
};

export default useGrants;
