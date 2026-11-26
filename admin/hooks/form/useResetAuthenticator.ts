"use client";
import {
  handleResendAuthenticatorNotice,
  handleResetAuthenticator,
} from "@/api/services/users/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useResetAuthenticator = (userId: number) => {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);
  const [emailSent, setEmailSent] = useState<boolean | null>(null);
  const [resending, setResending] = useState(false);

  const close = () => {
    setOpen(false);
    setError(null);
  };

  const reset = async (reason: string) => {
    setPending(true);
    const { data, error } = await handleResetAuthenticator(userId, reason);
    setPending(false);
    setError(error);
    if (error) return;
    setEmailSent(data.notice_sent);
    setOpen(false);
    router.refresh();
  };

  const resend = async () => {
    setResending(true);
    const { data, error } = await handleResendAuthenticatorNotice(userId);
    setResending(false);
    setEmailSent(error ? false : data.notice_sent);
  };

  return {
    open,
    setOpen,
    pending,
    error,
    close,
    reset,
    emailSent,
    resending,
    resend,
  };
};

export default useResetAuthenticator;
