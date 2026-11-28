"use client";
import {
  handleResendVerification,
  handleSignIn,
  handleSignUp,
} from "@/api/services/auth/serve-action";
import { homePathFor } from "@/constants/audience";
import type { ActionResult } from "@/types/api/common";
import type { SignInBody, SignUpBody } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";

const useAuth = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();
  const [notice, setNotice] = useState("");

  const run = async <T>(request: Promise<ActionResult<T>>) => {
    setPending(true);
    setError(null);
    setNotice("");
    const { data, error } = await request;
    setPending(false);
    setError(error);
    return data;
  };

  const signIn = async (body: SignInBody, redirectTo?: string) => {
    const user = await run(handleSignIn(body));
    if (!user) return;
    router.replace(redirectTo ?? homePathFor(user));
  };

  const signUp = async (body: SignUpBody) => {
    const message = await run(handleSignUp(body));
    return message !== null;
  };

  const resendVerification = async (email: string) => {
    const message = await run(handleResendVerification(email));
    if (message) setNotice(message.detail);
  };

  return { pending, error, notice, signIn, signUp, resendVerification };
};

export default useAuth;
