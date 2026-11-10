"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Suburb } from "@/types/locations/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

export const handleSearchSuburbs = async (state: string, q: string) => {
  try {
    const data = await ApiServiceServer<Suburb[]>({
      url: EndPoints.locations.suburbs,
      method: "GET",
      params: { state, q },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, { redirectOnUnauth: true });
  }
};
