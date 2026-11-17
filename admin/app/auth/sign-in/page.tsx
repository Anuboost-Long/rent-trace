import AuthCard from "@/components/common/auth-card";
import GoogleSignIn from "@/components/common/google-sign-in";
import type { Metadata } from "next";
import { Suspense } from "react";

import SignInForm from "./sign-in-form";

export const metadata: Metadata = { title: "Sign in · RentTrace" };

export default function SignInPage({
  searchParams,
}: PageProps<"/auth/sign-in">) {
  return (
    <AuthCard heading="Sign in">
      <Suspense>
        <RedirectAwareForm searchParams={searchParams} />
      </Suspense>
      <GoogleSignIn label="Sign in with Google" />
    </AuthCard>
  );
}

async function RedirectAwareForm({
  searchParams,
}: Readonly<Pick<PageProps<"/auth/sign-in">, "searchParams">>) {
  const { redirect } = await searchParams;
  const isLocalPath =
    typeof redirect === "string" &&
    redirect.startsWith("/") &&
    !redirect.startsWith("//");
  return <SignInForm redirectTo={isLocalPath ? redirect : undefined} />;
}
