"use server";
import { EndPoints } from "@/api/api-config";
import { ApiServiceServer } from "@/api/api-helper";
import type { Page } from "@/types/access/models";
import type { Ban, ListFilters } from "@/types/security/models";
import { handleSSRActionError } from "@/utils/server-side-error-handler";

const redirectOnUnauth = { redirectOnUnauth: true };

export const handleGetBans = async (params: ListFilters = {}) => {
  try {
    const data = await ApiServiceServer<Page<Ban>>({
      url: EndPoints.bans.list,
      method: "GET",
      params,
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};

export const handleLiftBan = async (id: number, reason: string) => {
  try {
    const data = await ApiServiceServer<Ban>({
      url: EndPoints.bans.lift(id),
      method: "POST",
      data: { reason },
    });
    return { data, error: null };
  } catch (error) {
    return handleSSRActionError(error, redirectOnUnauth);
  }
};
