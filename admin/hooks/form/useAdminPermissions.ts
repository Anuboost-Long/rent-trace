"use client";
import {
  handleGrantPermission,
  handleRevokePermission,
} from "@/api/services/access/serve-action";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

type Change = { grant: string[]; revoke: string[] };

// Saves switch changes on an admin's permissions as direct grants and revokes, one call per
// permission, all with the same reason. Stops at the first failure.
const useAdminPermissions = (userId: number, afterSave: () => void) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const save = async ({ grant, revoke }: Change, reason: string) => {
    setPending(true);
    setError(null);
    const calls = [
      ...grant.map((code) => () => handleGrantPermission(userId, code, reason)),
      ...revoke.map(
        (code) => () => handleRevokePermission(userId, code, reason),
      ),
    ];
    for (const call of calls) {
      const { error } = await call();
      if (error) {
        setPending(false);
        setError(error);
        router.refresh();
        return;
      }
    }
    setPending(false);
    toast.success("Permissions updated");
    router.refresh();
    afterSave();
  };

  return { pending, error, save };
};

export default useAdminPermissions;
