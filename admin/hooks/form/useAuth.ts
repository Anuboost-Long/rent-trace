"use client";
import {
  handleResendVerification,
  handleSignIn,
  handleSignUp,
} from "@/api/services/auth/serve-action";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import type { SignInBody, SignUpBody } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useAuth = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);
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

  const signIn = async (body: SignInBody, redirectTo: string) => {
    const user = await run(handleSignIn(body));
    if (!user) return;
    router.replace(redirectTo);
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
