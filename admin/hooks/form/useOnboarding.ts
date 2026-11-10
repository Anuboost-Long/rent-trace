"use client";
import { handleCompleteOnboarding } from "@/api/services/auth/serve-action";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import type { OnboardingBody } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useOnboarding = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const complete = async (body: OnboardingBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleCompleteOnboarding(body);
    setPending(false);
    setError(error);
    if (data) router.replace(Route.home);
  };

  return { pending, error, complete };
};

export default useOnboarding;
