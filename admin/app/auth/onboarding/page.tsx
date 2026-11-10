import { handleGetMe } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import OnboardingForm from "./onboarding-form";

export const metadata: Metadata = {
  title: "Finish setting up · RentTrace",
  robots: { index: false },
};

export default function OnboardingPage() {
  return (
    <Suspense>
      <PendingOnboarding />
    </Suspense>
  );
}

async function PendingOnboarding() {
  const { data: user } = await handleGetMe();
  if (user!.roles.length > 0) redirect(Route.home);

  return (
    <AuthCard
      heading="Finish setting up"
      message="Confirm your name and tell us how you'll use RentTrace."
    >
      <OnboardingForm firstName={user!.first_name} lastName={user!.last_name} />
    </AuthCard>
  );
}
