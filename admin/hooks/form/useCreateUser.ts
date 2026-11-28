"use client";
import { handleCreateUser } from "@/api/services/users/serve-action";
import { Route } from "@/constants/web-routes";
import type { CreateUserBody } from "@/types/users/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useCreateUser = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const createUser = async (body: CreateUserBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleCreateUser(body);
    setPending(false);
    setError(error);
    if (data) {
      toast.success("Account created");
      router.push(Route.admin.user(data.id));
    }
  };

  return { pending, error, createUser };
};

export default useCreateUser;
