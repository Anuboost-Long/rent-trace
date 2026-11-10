"use client";

import { handleVerifyEmail } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import Button from "@/components/common/button";
import { Route } from "@/constants/web-routes";
import Link from "next/link";
import { useState } from "react";

type Status = "idle" | "confirming" | "verified" | "invalid" | "retry";

export default function ConfirmEmail({ token }: Readonly<{ token: string }>) {
  const [status, setStatus] = useState<Status>(token ? "idle" : "invalid");
  const [retryMessage, setRetryMessage] = useState("");

  async function confirm() {
    setStatus("confirming");
    const { error } = await handleVerifyEmail(token);
    if (!error) return setStatus("verified");
    if (error.status === 400) return setStatus("invalid");
    setRetryMessage(error.message);
    setStatus("retry");
  }

  switch (status) {
    case "verified":
      return (
        <AuthCard
          heading="Email verified"
          message="You can now sign in to RentTrace."
        >
          <Link href={Route.auth.sign_in} className="font-medium underline">
            Go to sign in
          </Link>
        </AuthCard>
      );
    case "invalid":
      return (
        <AuthCard
          heading="Link expired"
          message="This link is invalid or has expired. Sign in to get a new verification link."
        >
          <Link href={Route.auth.sign_in} className="font-medium underline">
            Go to sign in
          </Link>
        </AuthCard>
      );
    default:
      return (
        <AuthCard
          heading="Verify your email"
          message={
            status === "retry"
              ? retryMessage
              : "Confirm your email address to finish signing up."
          }
        >
          <Button onClick={confirm} pending={status === "confirming"}>
            {status === "confirming" ? "Confirming…" : "Confirm email"}
          </Button>
        </AuthCard>
      );
  }
}
