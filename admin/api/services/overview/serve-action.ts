"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Overview } from "@/types/overview/models";
import type { TenancyAudience } from "@/types/tenancies/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

export const handleGetOverview = async (audience: TenancyAudience) => {
  try {
    const data = await ApiServiceServer<Overview>({
      url:
        audience === "landlord"
          ? EndPoints.landlord_overview
          : EndPoints.overview,
      method: "GET",
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, { redirectOnUnauth: true });
  }
};
