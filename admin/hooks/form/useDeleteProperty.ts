"use client";
import { handleDeleteProperty } from "@/api/services/properties/serve-action";
import { Route } from "@/constants/web-routes";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useDeleteProperty = (propertyId: number) => {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const cancel = () => {
    setConfirming(false);
    setError(null);
  };

  const confirm = async () => {
    setPending(true);
    const { error } = await handleDeleteProperty(propertyId);
    setPending(false);
    setError(error);
    if (!error) router.replace(Route.admin.properties);
  };

  return { confirming, setConfirming, pending, error, confirm, cancel };
};

export default useDeleteProperty;
