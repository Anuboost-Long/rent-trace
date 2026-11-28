"use client";
import { handleCompleteOnboarding } from "@/api/services/auth/serve-action";
import { homePathFor } from "@/constants/audience";
import type { OnboardingBody } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";

const useOnboarding = () => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const complete = async (body: OnboardingBody) => {
    setPending(true);
    setError(null);
    const { data, error } = await handleCompleteOnboarding(body);
    setPending(false);
    setError(error);
    if (data) router.replace(homePathFor(data));
  };

  return { pending, error, complete };
};

export default useOnboarding;
