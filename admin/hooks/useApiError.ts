"use client";
import type { ApiFailure } from "@/types/api/common";
import { toast } from "@/utils/toast";
import { useState } from "react";

/** Holds the last failure for the form, and raises an alert whenever a new one arrives. */
const useApiError = () => {
  const [error, setValue] = useState<ApiFailure | null>(null);

  const setError = (failure: ApiFailure | null) => {
    setValue(failure);
    if (failure) toast.error(failure.message);
  };

  return [error, setError] as const;
};

export default useApiError;
