"use client";
import { PropertyRoutes } from "@/constants/properties";
import type { ActionResult } from "@/types/api/common";
import type {
  PropertyAudience,
  PropertyDetail,
} from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const useSaveProperty = <Body>(
  submit: (body: Body) => Promise<ActionResult<PropertyDetail>>,
  audience: PropertyAudience = "admin",
) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const save = async (
    body: Body,
    afterSave?: (saved: PropertyDetail) => Promise<boolean>,
  ) => {
    setPending(true);
    setError(null);
    const { data, error } = await submit(body);
    setError(error);
    const proceed = data ? ((await afterSave?.(data)) ?? true) : false;
    setPending(false);
    if (data) toast.success("Property saved");
    if (data && proceed) router.push(PropertyRoutes[audience].detail(data.id));
  };

  return { pending, error, save };
};

export default useSaveProperty;
