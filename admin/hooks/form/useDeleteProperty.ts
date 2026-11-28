"use client";
import { handleDeleteProperty } from "@/api/services/properties/serve-action";
import { Route } from "@/constants/web-routes";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useDeleteProperty = (propertyId: number) => {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const cancel = () => {
    setConfirming(false);
    setError(null);
  };

  const confirm = async () => {
    setPending(true);
    const { error } = await handleDeleteProperty(propertyId);
    setPending(false);
    setError(error);
    if (!error) {
      toast.success("Property removed");
      router.replace(Route.admin.properties);
    }
  };

  return { confirming, setConfirming, pending, error, confirm, cancel };
};

export default useDeleteProperty;
