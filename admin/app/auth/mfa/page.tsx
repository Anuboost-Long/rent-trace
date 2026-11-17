import { handleGetMe } from "@/api/services/auth/serve-action";
import { audienceFor } from "@/constants/navigation";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import MfaForm from "./mfa-form";

export const metadata: Metadata = {
  title: "Two-step verification · RentTrace",
  referrer: "no-referrer",
  robots: { index: false },
};

export default function MfaPage() {
  return (
    <Suspense>
      <PendingMfa />
    </Suspense>
  );
}

async function PendingMfa() {
  const { data: user } = await handleGetMe();
  const status = user!.mfa_status;
  if (status === "NOT_REQUIRED" || status === "VERIFIED") {
    redirect(Route.home);
  }
  const audience = audienceFor(user!) ?? "admin";
  return <MfaForm status={status} destination={`/${audience}`} />;
}
