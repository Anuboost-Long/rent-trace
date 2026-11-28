"use client";
import { handleChangePassword } from "@/api/services/auth/serve-action";
import type { ChangePasswordBody } from "@/types/auth/models";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useChangePassword = () => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();
  const [notice, setNotice] = useState("");

  const change = async (body: ChangePasswordBody) => {
    setPending(true);
    setError(null);
    setNotice("");
    const { data, error } = await handleChangePassword(body);
    setPending(false);
    setError(error);
    if (data) {
      setNotice(data.detail);
      toast.success(data.detail);
    }
    return data !== null;
  };

  return { pending, error, notice, change };
};

export default useChangePassword;
