"use client";
import {
  handleAddRoleMember,
  handleRemoveRoleMember,
} from "@/api/services/access/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useRoleMembers = (roleCode: string) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const run = async (request: Promise<{ error: ApiFailure | null }>) => {
    setPending(true);
    setError(null);
    const { error } = await request;
    setPending(false);
    setError(error);
    if (!error) router.refresh();
    return !error;
  };

  const add = (userId: number) => run(handleAddRoleMember(roleCode, userId));
  const remove = (userId: number) =>
    run(handleRemoveRoleMember(roleCode, userId));

  return { pending, error, add, remove };
};

export default useRoleMembers;
