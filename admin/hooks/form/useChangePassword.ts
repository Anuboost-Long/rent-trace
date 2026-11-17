"use client";
import { handleChangePassword } from "@/api/services/auth/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type { ChangePasswordBody } from "@/types/auth/models";
import { useState } from "react";

const useChangePassword = () => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);
  const [notice, setNotice] = useState("");

  const change = async (body: ChangePasswordBody) => {
    setPending(true);
    setError(null);
    setNotice("");
    const { data, error } = await handleChangePassword(body);
    setPending(false);
    setError(error);
    if (data) setNotice(data.detail);
    return data !== null;
  };

  return { pending, error, notice, change };
};

export default useChangePassword;
