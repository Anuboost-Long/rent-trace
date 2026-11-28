"use client";
import {
  handleForgotPassword,
  handleResetPassword,
} from "@/api/services/auth/serve-action";
import type { ActionResult } from "@/types/api/common";
import type { Message, ResetPasswordBody } from "@/types/auth/models";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";

const usePasswordReset = () => {
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();
  const [notice, setNotice] = useState("");

  const run = async (request: Promise<ActionResult<Message>>) => {
    setPending(true);
    setError(null);
    const { data, error } = await request;
    setPending(false);
    setError(error);
    if (data) setNotice(data.detail);
    return data !== null;
  };

  return {
    pending,
    error,
    notice,
    requestLink: (email: string) => run(handleForgotPassword(email)),
    reset: (body: ResetPasswordBody) => run(handleResetPassword(body)),
  };
};

export default usePasswordReset;
