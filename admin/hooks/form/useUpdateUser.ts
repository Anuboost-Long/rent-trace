"use client";
import { handleUpdateUser } from "@/api/services/users/serve-action";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import type { UpdateUserBody } from "@/types/users/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useUpdateUser = (userId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const updateUser = async (body: UpdateUserBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleUpdateUser(userId, body);
    setPending(false);
    setError(error);
    if (data) router.push(Route.admin.user(userId));
  };

  return { pending, error, updateUser };
};

export default useUpdateUser;
