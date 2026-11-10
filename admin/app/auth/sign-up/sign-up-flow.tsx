"use client";
import AuthCard from "@/components/common/auth-card";
import { useState } from "react";

import CheckEmail from "./check-email";
import SignUpForm from "./sign-up-form";

type SignUpFlowProp = Readonly<{ google: React.ReactNode }>;

export default function SignUpFlow({ google }: SignUpFlowProp) {
  const [sentTo, setSentTo] = useState<string | null>(null);

  if (sentTo) {
    return (
      <AuthCard heading="Check your email">
        <CheckEmail email={sentTo} onChangeEmail={() => setSentTo(null)} />
      </AuthCard>
    );
  }

  return (
    <AuthCard heading="Create your account">
      <SignUpForm onSent={setSentTo} />
      {google}
    </AuthCard>
  );
}
