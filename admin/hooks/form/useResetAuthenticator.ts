"use client";
import { handleResetAuthenticator } from "@/api/services/users/serve-action";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useResetAuthenticator = (userId: number) => {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const close = () => {
    setOpen(false);
    setError(null);
  };

  const reset = async (reason: string) => {
    setPending(true);
    const { error } = await handleResetAuthenticator(userId, reason);
    setPending(false);
    setError(error);
    if (error) return;
    setOpen(false);
    router.refresh();
  };

  return { open, setOpen, pending, error, close, reset };
};

export default useResetAuthenticator;
