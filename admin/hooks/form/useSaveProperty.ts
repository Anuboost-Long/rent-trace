"use client";
import { PropertyRoutes } from "@/constants/properties";
import type { ActionResult, ApiFailure } from "@/types/api/common";
import type {
  PropertyAudience,
  PropertyDetail,
} from "@/types/properties/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useSaveProperty = <Body>(
  submit: (body: Body) => Promise<ActionResult<PropertyDetail>>,
  audience: PropertyAudience = "admin",
) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

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
    if (data && proceed) router.push(PropertyRoutes[audience].detail(data.id));
  };

  return { pending, error, save };
};

export default useSaveProperty;
