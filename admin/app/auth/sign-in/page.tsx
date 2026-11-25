import AuthCard from "@/components/common/auth-card";
import GoogleSignIn from "@/components/common/google-sign-in";
import { SESSION_ENDED } from "@/constants/security";
import type { Metadata } from "next";
import { Suspense } from "react";

import SignInForm from "./sign-in-form";

export const metadata: Metadata = { title: "Log in · RentTrace" };

export default function SignInPage({
  searchParams,
}: PageProps<"/auth/sign-in">) {
  return (
    <AuthCard
      heading="Log in"
      message="Your tenancy records, agreements and requests in one place."
    >
      <Suspense>
        <RedirectAwareForm searchParams={searchParams} />
      </Suspense>
      <GoogleSignIn label="Log in with Google" />
    </AuthCard>
  );
}

async function RedirectAwareForm({
  searchParams,
}: Readonly<Pick<PageProps<"/auth/sign-in">, "searchParams">>) {
  const { redirect, reason } = await searchParams;
  const isLocalPath =
    typeof redirect === "string" &&
    redirect.startsWith("/") &&
    !redirect.startsWith("//");
  return (
    <SignInForm
      redirectTo={isLocalPath ? redirect : undefined}
      sessionEnded={reason === SESSION_ENDED}
    />
  );
}
